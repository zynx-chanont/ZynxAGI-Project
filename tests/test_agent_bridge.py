from fastapi.testclient import TestClient
from zynx_agi.main import app

class FakeRegistry:
    def list_agents(self):
        return [{"agent_id":"deeja","active":True,"capabilities":["chat"]}]
    def list_capabilities(self):
        return {"chat":["deeja"]}

class FakeManager:
    initialized=True
    agent_registry=FakeRegistry()
    async def _perform_ecosystem_health_check(self):
        return {"healthy":True,"components":{"mcp_dispatcher":{"status":"healthy"}}}
    async def process_request(self,request):
        assert request["message"].startswith("/deeja:chat ")
        assert request["agent_forge_input"]=="สวัสดี"
        return {"success":True,"response":{"text":"hello"},"agent_id":"deeja","metadata":{}}
    async def shutdown_ecosystem(self):
        return None

def test_agent_bridge_requires_service_token(monkeypatch):
    monkeypatch.setenv("ZYNXAGI_AGENT_API_TOKEN","bridge-secret")
    app.state.ecosystem_manager=FakeManager()
    with TestClient(app) as client:
        response=client.get("/api/v1/agents/status")
        assert response.status_code==401
        response=client.get("/api/v1/agents/status",headers={"X-ZynxAGI-Token":"bridge-secret"})
        assert response.status_code==200
        assert response.json()["initialized"] is True

def test_agent_bridge_dispatches_through_ecosystem_manager(monkeypatch):
    monkeypatch.setenv("ZYNXAGI_AGENT_API_TOKEN","bridge-secret")
    app.state.ecosystem_manager=FakeManager()
    with TestClient(app) as client:
        response=client.post("/api/v1/agents/dispatch",
            headers={"X-ZynxAGI-Token":"bridge-secret"},
            json={"agent_id":"deeja","action":"chat","message":"สวัสดี","payload":{"locale":"th-TH"}})
        assert response.status_code==200
        assert response.json()["status"]=="dispatched"
        assert response.json()["agent_id"]=="deeja"

def test_agent_bridge_rejects_unsupported_action(monkeypatch):
    monkeypatch.setenv("ZYNXAGI_AGENT_API_TOKEN","bridge-secret")
    app.state.ecosystem_manager=FakeManager()
    with TestClient(app) as client:
        response=client.post("/api/v1/agents/dispatch",
            headers={"X-ZynxAGI-Token":"bridge-secret"},
            json={"agent_id":"deeja","action":"delete","message":"not allowed"})
        assert response.status_code==422
