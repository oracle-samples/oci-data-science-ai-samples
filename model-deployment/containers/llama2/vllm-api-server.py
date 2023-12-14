import argparse
import json
from typing import AsyncGenerator

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse
import uvicorn
from uvicorn.config import LOGGING_CONFIG

from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.sampling_params import SamplingParams
from vllm.utils import random_uuid

import torch
import yaml

TIMEOUT_KEEP_ALIVE = 5  # seconds.
TIMEOUT_TO_PREVENT_DEADLOCK = 1  # seconds.
app = FastAPI()


@app.get("/health")
async def health():
    return {"status":"success"}

@app.post("/predict")
async def generate(request: Request) -> Response:
    """Generate completion for the request. The specification is same as Text Generation Inference

    The request should be a JSON object with the following fields:
    - inputs: the prompt to use for the generation.
    - stream: whether to stream the results or not.
    - parameters: the sampling parameters (See `SamplingParams` for details).
    """
    request_dict = await request.json()
    prompt = request_dict.pop("inputs", None)
    parameters = request_dict.pop("parameters", {})
    params = {}

    if "max_new_tokens" in parameters:
        params["max_tokens"] = parameters.pop("max_new_tokens")

    if "temperature" in parameters:
        params["temperature"] = parameters.pop("temperature")

    if "top_p" in parameters:
        params["top_p"] = parameters.pop("top_p")

    if not "use_beam_search" in parameters:
        params["use_beam_search"] = False
        params["n"] = 1

    stream = request_dict.pop("stream", False)
    sampling_params = SamplingParams(**params)
    request_id = random_uuid()
    results_generator = engine.generate(prompt, sampling_params, request_id)

    # Streaming case
    async def stream_results() -> AsyncGenerator[bytes, None]:
        async for request_output in results_generator:
            prompt = request_output.prompt
            text_outputs = [prompt + output.text for output in request_output.outputs]
            ret = {"text": text_outputs}
            yield (json.dumps(ret) + "\0").encode("utf-8")

    async def abort_request() -> None:
        await engine.abort(request_id)

    if stream:
        background_tasks = BackgroundTasks()
        # Abort the request if the client disconnects.
        background_tasks.add_task(abort_request)
        return StreamingResponse(stream_results(), background=background_tasks)

    # Non-streaming case
    final_output = None
    async for request_output in results_generator:
        if await request.is_disconnected():
            # Abort the request if the client disconnects.
            await engine.abort(request_id)
            return Response(status_code=499)
        final_output = request_output

    assert final_output is not None
    prompt = final_output.prompt
    # text_outputs = [prompt + output.text for output in final_output.outputs]
    generated_text = "".join(output.text for output in final_output.outputs)
    # ret = {"generated_text": text_outputs}
    ret = {"generated_text": generated_text}
    return JSONResponse(ret)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=80)
    parser.add_argument("--log-config", default=None)
    parser = AsyncEngineArgs.add_cli_args(parser)
    args = parser.parse_args()

    engine_args = AsyncEngineArgs.from_cli_args(args)
    engine = AsyncLLMEngine.from_engine_args(engine_args)

    LOGGING_CONFIG["formatters"]["default"][
        "fmt"
    ] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    log_config = LOGGING_CONFIG
    if args.log_config:
        with open(args.log_config) as cf:
            print(f"Override log config of uvicorn with {args.log_config}", flush=True)
            log_config = yaml.load(cf, Loader=yaml.SafeLoader)
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_config=log_config,
        timeout_keep_alive=TIMEOUT_KEEP_ALIVE,
    )
