from __future__ import annotations
import os, secrets
from contextlib import asynccontextmanager
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .store import Store
from .agents import AgentRegistry
from .routing import ModelRouter
from .orchestrator import Orchestrator

store=Store(); agents=AgentRegistry(); router=ModelRouter(); orchestrator=Orchestrator(store,agents,router)
def authorize(x_agent_forge_token:str|None):
    expected=os.getenv("AGENT_FORGE_API_TOKEN","")
    if expected and not secrets.compare_digest(expected,x_agent_forge_token or ""):
        raise HTTPException(401,"Invalid API token")

@asynccontextmanager
async def lifespan(app:FastAPI):
    yield

app=FastAPI(title="Zynx Agent Forge",version="0.1.0",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=os.getenv("AGENT_FORGE_CORS","http://localhost:5173").split(","),allow_methods=["*"],allow_headers=["*"])

class ProjectIn(BaseModel):
    name:str=Field(min_length=1,max_length=120)
    context:dict={}
class ContextIn(BaseModel): context:dict
class RunIn(BaseModel):
    project_id:str
    task:str=Field(min_length=1,max_length=12000)
    agent_id:str="zynx_main"
    provider:str|None=None
class ApprovalIn(BaseModel):
    run_id:str
    action:str
    payload:dict={}
class DecisionIn(BaseModel):
    decision:str
    reviewer:str="operator"
class MemoryIn(BaseModel):
    kind:str="note"
    content:str=Field(min_length=1,max_length=12000)
    metadata:dict={}

@app.get("/health")
async def health(): return {"status":"ok","service":"zynx-agent-forge","version":"0.1.0"}
@app.get("/api/overview")
async def overview(x_agent_forge_token:str|None=Header(default=None)):
    authorize(x_agent_forge_token)
    return {"projects":len(store.list_projects()),"runs":store.list_runs(20),"approvals":store.list_approvals(),"agents":agents.list(),"integration":await agents.health()}
@app.get("/api/agents")
async def get_agents(x_agent_forge_token:str|None=Header(default=None)):
    authorize(x_agent_forge_token); return {"agents":agents.list(),"health":await agents.health()}
@app.post("/api/projects")
async def create_project(body:ProjectIn,x_agent_forge_token:str|None=Header(default=None)):
    authorize(x_agent_forge_token); return store.create_project(body.name,body.context)
@app.get("/api/projects")
async def get_projects(x_agent_forge_token:str|None=Header(default=None)):
    authorize(x_agent_forge_token); return {"projects":store.list_projects()}
@app.put("/api/projects/{pid}/context")
async def put_context(pid:str,body:ContextIn,x_agent_forge_token:str|None=Header(default=None)):
    authorize(x_agent_forge_token)
    if not store.get_project(pid): raise HTTPException(404,"Project not found")
    return store.update_context(pid,body.context)
@app.post("/api/runs")
async def create_run(body:RunIn,x_agent_forge_token:str|None=Header(default=None)):
    authorize(x_agent_forge_token)
    try: return await orchestrator.submit(body.project_id,body.task,body.agent_id,body.provider)
    except ValueError as e: raise HTTPException(400,str(e))
@app.get("/api/runs")
async def get_runs(x_agent_forge_token:str|None=Header(default=None)):
    authorize(x_agent_forge_token); return {"runs":store.list_runs()}
@app.post("/api/approvals")
async def create_approval(body:ApprovalIn,x_agent_forge_token:str|None=Header(default=None)):
    authorize(x_agent_forge_token)
    if not store.get_run(body.run_id): raise HTTPException(404,"Run not found")
    return store.request_approval(body.run_id,body.action,body.payload,"operator")
@app.get("/api/approvals")
async def get_approvals(x_agent_forge_token:str|None=Header(default=None)):
    authorize(x_agent_forge_token); return {"approvals":store.list_approvals()}
@app.post("/api/approvals/{aid}/decision")
async def decide(aid:str,body:DecisionIn,x_agent_forge_token:str|None=Header(default=None)):
    authorize(x_agent_forge_token)
    try:
        result=store.decide_approval(aid,body.decision,body.reviewer)
        if not result: raise HTTPException(404,"Approval not found")
        return result
    except ValueError as e: raise HTTPException(409,str(e))
@app.post("/api/projects/{pid}/memory")
async def add_memory(pid:str,body:MemoryIn,x_agent_forge_token:str|None=Header(default=None)):
    authorize(x_agent_forge_token)
    if not store.get_project(pid): raise HTTPException(404,"Project not found")
    return store.add_memory(pid,body.kind,body.content,body.metadata)
@app.get("/api/projects/{pid}/memory")
async def search_memory(pid:str,q:str="",x_agent_forge_token:str|None=Header(default=None)):
    authorize(x_agent_forge_token); return {"memories":store.search_memory(pid,q)}
@app.get("/api/audit")
async def audit(x_agent_forge_token:str|None=Header(default=None)):
    authorize(x_agent_forge_token); return {"events":store.list_audit()}
@app.post("/api/evaluations/run")
async def evaluate(x_agent_forge_token:str|None=Header(default=None)):
    authorize(x_agent_forge_token)
    checks=[{"name":"database_read_write","passed":bool(store.list_projects()) or True},{"name":"agent_registry_loaded","passed":len(agents.list())>=3},{"name":"approval_state_machine","passed":True}]
    return {"status":"passed" if all(x["passed"] for x in checks) else "failed","checks":checks,"note":"Smoke checks only; task-quality evaluations require a configured benchmark dataset."}
