from __future__ import annotations
import tempfile
from pathlib import Path
from .store import Store
from .agents import AgentRegistry

def run_smoke_evaluations(store: Store, agents: AgentRegistry) -> dict:
    checks=[]
    try:
        with tempfile.TemporaryDirectory() as directory:
            probe_store=Store(str(Path(directory)/"evaluation.db"))
            probe=probe_store.create_project("agent-forge-evaluation-probe",{"temporary":True})
            checks.append({"name":"database_read_write","passed":bool(probe_store.get_project(probe["id"]))})
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
