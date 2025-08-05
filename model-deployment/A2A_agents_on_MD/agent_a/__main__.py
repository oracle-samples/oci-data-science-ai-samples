import uvicorn
import os
import logging
from typing import Any
from uuid import uuid4
import httpx
import oci
import json
import asyncio
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    MessageSendParams,
    SendMessageRequest,
    SendStreamingMessageRequest,
)
from starlette.responses import JSONResponse
from starlette.applications import Starlette
from starlette.requests import Request

# OCI Authentication Classes
class OCISignerAuth(httpx.Auth):
    def __init__(self, signer):
        self.signer = signer
    def auth_flow(self, request):
        import requests
        req = requests.Request(
            method=request.method,
            url=str(request.url),
            headers=dict(request.headers),
            data=request.content
        ).prepare()
        self.signer(req)
        for k, v in req.headers.items():
            request.headers[k] = v
        yield request

def get_auth():
    PROFILE_NAME = 'default'
    SECURITY_TOKEN_FILE_KEY = 'security_token_file'
    KEY_FILE_KEY = 'key_file'
    config = oci.config.from_file(profile_name=PROFILE_NAME)
    token_file = config[SECURITY_TOKEN_FILE_KEY]
    with open(token_file, 'r') as f:
        token = f.read()
    private_key = oci.signer.load_private_key_from_file(config[KEY_FILE_KEY])
    signer = oci.auth.signers.SecurityTokenSigner(token, private_key)
    return OCISignerAuth(signer)

def get_auth_rps():
    print(f'[DEBUG] Getting RPS auth')
    rps = oci.auth.signers.get_resource_principals_signer()
    print(f'[DEBUG] RPS auth: {rps}')
    print(f'[DEBUG] RPS token: {rps.get_security_token()}')
    return OCISignerAuth(rps)

# Agent Communication Function
async def get_agent_answer(base_url: str, question: str) -> str:
    print(f'[DEBUG] Sending request to other agent: {base_url}')
    PUBLIC_AGENT_CARD_PATH = '/.well-known/agent.json'
    async with httpx.AsyncClient(auth=get_auth_rps(), verify=False, headers={"Content-Length": "0"}) as httpx_client:
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
        )
        _public_card = await resolver.get_agent_card()
        print(f'[DEBUG] Resolved agent card: {_public_card}')
        client = A2AClient(
            httpx_client=httpx_client, agent_card=_public_card
        )
        send_message_payload: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [
                    {'kind': 'text', 'text': question}
                ],
                'messageId': uuid4().hex,
            },
        }
        request = SendMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )
        response = await client.send_message(request)
        print(f'[DEBUG] Response: {response}')
        try:
            parts = response.result.message.parts
            for part in parts:
                if 'text' in part:
                    return part['text']
            return str(response.model_dump(mode='json', exclude_none=True))
        except Exception:
            return str(response.model_dump(mode='json', exclude_none=True))

# Agent Classes
class WeatherAgent:
    """Gets weather information for cities, with one city from this agent and another from the other agent."""

    def __init__(self):
        agent_b_url = os.getenv('AGENT_B_URL')
        self.other_agent_url = agent_b_url

    async def invoke(self) -> dict:
        # Get string information from the other agent
        other_agent_result = await get_agent_answer(self.other_agent_url, "Please provide some information")
        # Weather information for Bengaluru from this agent
        this_agent_result = '🌤️ Bengaluru Weather: 25°C, Partly Cloudy, Humidity: 70%, Wind: 8 km/h'
        return {
            "this_agent_result": this_agent_result,
            "other_agent_result": other_agent_result
        }

class WeatherAgentExecutor(AgentExecutor):
    """Test AgentProxy Implementation that delegates to the agent's invoke method."""

    def __init__(self):
        self.agent = WeatherAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        result = await self.agent.invoke()
        # Serialize the result dict for output, preserving Unicode (emojis)
        await event_queue.enqueue_event(new_agent_text_message(json.dumps(result, indent=2, ensure_ascii=False)))

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')

# Application Setup Classes
class PrefixDispatcher:
    def __init__(self, app, prefix="/a2a"):
        self.app = app
        self.prefix = prefix

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"].startswith(self.prefix + "/"):
            scope = dict(scope)
            scope["path"] = scope["path"][len(self.prefix):]
            if not scope["path"]:
                scope["path"] = "/"
        await self.app(scope, receive, send)


# Main Application
if __name__ == '__main__':
    agent_a_url = os.getenv('AGENT_A_URL')

    skill = AgentSkill(
        id='bengaluru_weather_agent',
        name='Returns weather information for Bengaluru',
        description='returns weather information for Bengaluru and collaborates with other agents for additional information',
        tags=['weather', 'bengaluru', 'temperature', 'collaboration'],
        examples=['what is the weather in Bengaluru?', 'get Bengaluru weather information'],
    )

    public_agent_card = AgentCard(
        name='Bengaluru Weather Agent',
        description='A weather information agent for Bengaluru that collaborates with other agents',
        url=agent_a_url,
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
        supportsAuthenticatedExtendedCard=False,
    )

    request_handler = DefaultRequestHandler(
        agent_executor=WeatherAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler,
    )

    app = server.build()
    prefix_app = PrefixDispatcher(app, prefix="/a2a")
    starlette_app = Starlette()

    @starlette_app.route("/health")
    async def health(request: Request):
        return JSONResponse({"status": "ok"})

    async def main_app(scope, receive, send):
        if scope["type"] == "http" and scope["path"].startswith("/health"):
            await starlette_app(scope, receive, send)
        else:
            await prefix_app(scope, receive, send)

    uvicorn.run(main_app, host='0.0.0.0', port=9999)
