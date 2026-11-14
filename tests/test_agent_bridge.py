from fastapi.testclient import TestClient
from zynx_agi.main import app

class FakeRegistry:
    def list_agents(self):
        return [{"agent_id":"deeja","active":True,"capabilities":["chat"]}]
    def list_capabilities(self):
        return {"chat":["deeja"]}
    def get_registry_status(self):
        return {"initialized":True}
    async def health_check_all_agents(self):
        return {"overall_healthy":True}

class FakeManager:
    initialized=True
    agent_registry=FakeRegistry()
    mcp_dispatcher=object()
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

def test_real_ecosystem_manager_dispatches_all_three_specialists(tmp_path):
    import asyncio
    from cryptography.fernet import Fernet
    from zynx_agi.ecosystem.ecosystem_manager import EcosystemManager

    async def exercise():
        manager = EcosystemManager(config={
            "deployment_mode": "local",
            "storage_path": str(tmp_path / "ecosystem-storage"),
            "encryption_key": Fernet.generate_key().decode("ascii"),
        })
        assert await manager.initialize_ecosystem() is True
        try:
            deeja = await manager.process_request({"message": "/deeja:analyze สวัสดีค่ะ"})
            assert deeja["success"] is True
            assert deeja["agent_id"] == "deeja"
            assert deeja["response"]["language_detected"] == "thai"

            zynx = await manager.process_request({"message": "/zynx:chat Hello Zynx"})
            assert zynx["success"] is True
            assert zynx["agent_id"] == "zynx_main"
            assert "Hello Zynx" in zynx["response"]["message"]

            metadata = await manager.process_request({
                "message": "/metadata:compliance Check sample metadata",
                "data": {"content": "sample metadata"},
            })
            assert metadata["success"] is True
            assert metadata["agent_id"] == "zynx_metadata"
            assert "overall_compliant" in metadata["response"]
        finally:
            await manager.shutdown_ecosystem()

    asyncio.run(exercise())
