import argparse
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
import uvicorn
from uvicorn.config import LOGGING_CONFIG

from modules import sdxl
import yaml

TIMEOUT_KEEP_ALIVE = 5  # seconds.
TIMEOUT_TO_PREVENT_DEADLOCK = 1  # seconds.
app = FastAPI()


@app.get("/health")
async def health():
    return {"status":"success"}

@app.post("/predict")
async def generate(request: Request) -> Response:
    data = await request.json()
    text = data.pop("prompt", None)
    negative_text = data.pop("negative_prompt", None)
    seed = data.pop("seed", 100)
    base_steps = data.pop("base_steps", 30)
    refiner_steps = data.pop("refiner_steps", 20)
    width = data.pop("width", 512)
    height = data.pop("height", 512)

    import base64
    from io import BytesIO
    buffered = BytesIO()
    image = sdxl.generate_from_text(text, negative_text, seed, base_steps, refiner_steps, width=width, height=height)
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    ret = {"result": img_str}
    return JSONResponse(ret)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--log-config", default=None)
    args = parser.parse_args()

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
     
