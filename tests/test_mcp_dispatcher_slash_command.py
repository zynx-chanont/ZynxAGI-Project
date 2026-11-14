import asyncio
from zynx_agi.agents.base_agent import AgentCapability, AgentResponse
from zynx_agi.agents.mcp_dispatcher import MCPDispatcher

class FakeAgent:
    def __init__(self):
        self.received=None
    async def execute_capability(self,capability,data):
        self.received=(capability,data)
        return AgentResponse(success=True,agent_id="deeja",response_data={"ok":True},timestamp="test")
    async def process_request(self,request):
        return AgentResponse(success=True,agent_id="deeja",response_data={"ok":True},timestamp="test")

class FakeRegistry:
    def __init__(self,agent): self.agent=agent
    def get_agent(self,agent_id): return self.agent if agent_id=="deeja" else None

def test_slash_command_passes_parsed_text_to_agent():
    agent=FakeAgent()
    dispatcher=MCPDispatcher(FakeRegistry(agent))
    response=asyncio.run(dispatcher.dispatch_request({"message":"/deeja:analyze สวัสดีค่ะ"}))
    assert response.success is True
    capability,data=agent.received
    assert capability==AgentCapability.CULTURAL_ANALYSIS
    assert data["message"]=="สวัสดีค่ะ"
    assert data["command"]=="/deeja:analyze สวัสดีค่ะ"
    assert data["params"]=="สวัสดีค่ะ"
