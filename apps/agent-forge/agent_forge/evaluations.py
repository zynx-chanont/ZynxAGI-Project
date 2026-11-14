from __future__ import annotations
from .store import Store
from .agents import AgentRegistry

def run_smoke_evaluations(store: Store, agents: AgentRegistry) -> dict:
    checks=[]
    try:
        projects=store.list_projects()
        checks.append({"name":"database_read","passed":isinstance(projects,list)})
        probe=store.create_project("__agent_forge_eval_probe__",{"temporary":True})
        checks.append({"name":"database_write_read","passed":bool(store.get_project(probe["id"]))})
    except Exception as exc:
        checks.append({"name":"database_read_write","passed":False,"detail":type(exc).__name__})
    try:
        ids={agent["id"] for agent in agents.list()}
        checks.append({"name":"specialist_registry","passed":{"zynx_main","deeja","zynx_metadata"}.issubset(ids)})
    except Exception as exc:
        checks.append({"name":"specialist_registry","passed":False,"detail":type(exc).__name__})
    checks.append({"name":"approval_workflow_contract","passed":callable(store.request_approval) and callable(store.decide_approval)})
    passed=all(c["passed"] for c in checks)
    return {"status":"passed" if passed else "failed","checks":checks,
            "scope":"service smoke checks only; no benchmark-based agent quality evaluation is configured"}
