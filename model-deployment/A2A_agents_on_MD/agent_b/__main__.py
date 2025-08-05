import uvicorn
import os

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from starlette.responses import JSONResponse
from starlette.applications import Starlette
from starlette.requests import Request

class MumbaiWeatherAgent:
    """Provides Mumbai weather information"""

    async def invoke(self) -> str:
        return 'Mumbai Weather: 28°C, Partly Cloudy, Humidity: 75%, Wind: 12 km/h'


class MumbaiWeatherAgentExecutor(AgentExecutor):
    """Mumbai Weather Agent Implementation."""

    def __init__(self):
        self.agent = MumbaiWeatherAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        result = await self.agent.invoke()
        await event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')

class PrefixDispatcher:
    def __init__(self, app, prefix="/a2a"):
        self.app = app
        self.prefix = prefix

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"].startswith(self.prefix + "/"):
            # Rewrite path: /a2a/foo -> /foo
            scope = dict(scope)
            scope["path"] = scope["path"][len(self.prefix):]
            if not scope["path"]:
                scope["path"] = "/"
        await self.app(scope, receive, send)

if __name__ == '__main__':
    
    # agent_a_url = os.getenv('AGENT_A_URL')
    agent_b_url = os.getenv('AGENT_B_URL')

    skill = AgentSkill(
        id='mumbai_weather',
        name='Returns Mumbai weather information',
        description='just returns current Mumbai weather information',
        tags=['mumbai', 'weather', 'temperature'],
        examples=['what is the weather in Mumbai?', 'get Mumbai weather'],
    )

    public_agent_card = AgentCard(
        name='Mumbai Weather Agent',
        description='Just a Mumbai weather agent',
        # url='http://localhost:9998/a2a/',
        url = agent_b_url,
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
        supportsAuthenticatedExtendedCard=False,
    )

    request_handler = DefaultRequestHandler(
        agent_executor=MumbaiWeatherAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler,
    )

    # get underlying Starlette app
    app = server.build()

    # Wrap with PrefixDispatcher for /a2a
    prefix_app = PrefixDispatcher(app, prefix="/a2a")

    # Starlette app for /health
    starlette_app = Starlette()

    @starlette_app.route("/health")
    async def health(request: Request):
        return JSONResponse({"status": "ok"})

    # Compose both: /health handled by Starlette, everything else by prefix_app
    async def main_app(scope, receive, send):
        if scope["type"] == "http" and scope["path"].startswith("/health"):
            await starlette_app(scope, receive, send)
        else:
            await prefix_app(scope, receive, send)

    uvicorn.run(main_app, host='0.0.0.0', port=9998)



