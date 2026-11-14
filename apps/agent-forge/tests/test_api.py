from fastapi.testclient import TestClient
from agent_forge.api import app

def test_health_is_public():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "zynx-agent-forge"

def test_project_memory_and_approval_api(tmp_path, monkeypatch):
    from agent_forge import api
    api.store = api.Store(str(tmp_path / "api.db"))
    api.orchestrator.store = api.store
    monkeypatch.setenv("AGENT_FORGE_API_TOKEN", "test-token")
    headers = {"X-Agent-Forge-Token": "test-token"}
    with TestClient(app) as client:
        project = client.post("/api/projects", headers=headers, json={"name":"integration","context":{"owner":"qa"}})
        assert project.status_code == 200
        pid = project.json()["id"]
        memory = client.post(f"/api/projects/{pid}/memory", headers=headers, json={"content":"verified adapter contract"})
        assert memory.status_code == 200
        assert client.get(f"/api/projects/{pid}/memory?q=adapter", headers=headers).json()["memories"]
        run = client.post("/api/runs", headers=headers, json={"project_id":pid,"task":"hello","agent_id":"deeja"})
        assert run.status_code == 200
        assert run.json()["status"] == "needs_integration"
        approval = client.post("/api/approvals", headers=headers, json={"run_id":run.json()["id"],"action":"deploy"})
        assert approval.status_code == 200
        decided = client.post(f"/api/approvals/{approval.json()['id']}/decision", headers=headers, json={"decision":"approved"})
        assert decided.status_code == 200
