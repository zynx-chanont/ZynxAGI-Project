"""MCP tool server for Agent Forge. Run: python -m agent_forge.mcp_server"""
import os
from mcp.server.fastmcp import FastMCP
from .store import Store
from .agents import AgentRegistry
from .routing import ModelRouter
from .orchestrator import Orchestrator

mcp=FastMCP("zynx-agent-forge")
store=Store(); agents=AgentRegistry(); orchestrator=Orchestrator(store,agents,ModelRouter())

@mcp.tool()
def list_projects()->list[dict]:
    """List Agent Forge projects and their saved context."""
    return store.list_projects()

@mcp.tool()
def create_project(name:str,context:dict|None=None)->dict:
    """Create a project workspace with persistent context."""
    return store.create_project(name,context or {})

@mcp.tool()
def list_specialist_agents()->list[dict]:
    """List registered Zynx specialist agent adapters."""
    return agents.list()

@mcp.tool()
async def submit_agent_task(project_id:str,task:str,agent_id:str="zynx_main")->dict:
    """Submit a task to the orchestration control plane."""
    return await orchestrator.submit(project_id,task,agent_id)

@mcp.tool()
def request_human_approval(run_id:str,action:str,payload:dict|None=None)->dict:
    """Create a pending approval record. This does not execute the action."""
    if not store.get_run(run_id): raise ValueError("Run not found")
    return store.request_approval(run_id,action,payload or {},"mcp-client")

@mcp.tool()
def search_project_memory(project_id:str,query:str)->list[dict]:
    """Search saved project notes using simple text matching."""
    return store.search_memory(project_id,query)

if __name__=="__main__":
    mcp.run()
