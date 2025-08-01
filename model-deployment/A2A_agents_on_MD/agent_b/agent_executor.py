from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

class OCIRealmFinderAgent:
    """Finds the OCI functioning realms and their status"""

    async def invoke(self) -> str:
        return '🟨 Old Realms status 🟨: OC1 ✅, OC2 ✅, OC3 ✅'


class OCIRealmFinderAgentExecutor(AgentExecutor):
    """Test AgentProxy Implementation."""

    def __init__(self):
        self.agent = OCIRealmFinderAgent()

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
