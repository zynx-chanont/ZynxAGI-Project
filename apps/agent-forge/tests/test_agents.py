import asyncio
import httpx
from agent_forge.agents import AgentRegistry

class FakeResponse:
    def __init__(self,status_code=200,payload=None):
        self.status_code=status_code
        self._payload=payload or {}
    def json(self): return self._payload
    def raise_for_status(self):
        if self.status_code>=400: raise httpx.HTTPStatusError("bad response",request=None,response=None)

class FakeClient:
    def __init__(self,*args,**kwargs): self.calls=[]
    async def __aenter__(self): return self
    async def __aexit__(self,*args): return None
    async def get(self,url,**kwargs):
        self.calls.append(("GET",url,kwargs))
        return FakeResponse(payload={"initialized":True,"agents":[{"agent_id":"deeja"}]})
    async def post(self,url,**kwargs):
        self.calls.append(("POST",url,kwargs))
        return FakeResponse(payload={"status":"dispatched","success":True,"agent_id":"deeja","response":{"ok":True}})

def test_dispatch_uses_real_zynxagi_bridge_contract(monkeypatch):
    import agent_forge.agents as module
    monkeypatch.setenv("ZYNXAGI_BASE_URL","http://zynxagi:8000")
    monkeypatch.setenv("ZYNXAGI_AGENT_API_TOKEN","secret")
    fake=FakeClient()
    monkeypatch.setattr(module.httpx,"AsyncClient",lambda **kwargs:fake)
    registry=AgentRegistry()
    result=asyncio.run(registry.dispatch("deeja","สวัสดี",{"locale":"th-TH"},"chat"))
    assert result["status"]=="dispatched"
    method,url,kwargs=fake.calls[0]
    assert method=="POST"
    assert url=="http://zynxagi:8000/api/v1/agents/dispatch"
    assert kwargs["headers"]["X-ZynxAGI-Token"]=="secret"
    assert kwargs["json"]=={"agent_id":"deeja","action":"chat","message":"สวัสดี","payload":{"locale":"th-TH"}}

def test_health_fails_closed_without_service_token(monkeypatch):
    monkeypatch.delenv("ZYNXAGI_AGENT_API_TOKEN",raising=False)
    status=asyncio.run(AgentRegistry().health())
    assert status["zynxagi"]=="not_configured"
