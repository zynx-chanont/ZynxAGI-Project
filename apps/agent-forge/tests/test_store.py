import pytest
from agent_forge.store import Store

@pytest.fixture
def store(tmp_path):
    return Store(str(tmp_path / "test.db"))

def test_project_context_and_memory_persist(store):
    project=store.create_project("test-project",{"goal":"ship safely"})
    assert store.get_project(project["id"])["context"]["goal"]=="ship safely"
    item=store.add_memory(project["id"],"note","architecture uses adapters",{"source":"test"})
    assert store.search_memory(project["id"],"adapters")[0]["id"]==item["id"]

def test_approval_is_single_decision(store):
    project=store.create_project("approval-test",{})
    run=store.create_run(project["id"],"review proposal","zynx_main")
    approval=store.request_approval(run["id"],"deploy",{"environment":"staging"},"tester")
    assert store.decide_approval(approval["id"],"approved","reviewer")["status"]=="approved"
    with pytest.raises(ValueError):
        store.decide_approval(approval["id"],"rejected","reviewer")

def test_audit_chain_links_events(store):
    store.create_project("audit-test",{})
    events=store.list_audit()
    assert events[0]["event_hash"]
    assert events[0]["previous_hash"]=="GENESIS"
