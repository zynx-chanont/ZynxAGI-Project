from __future__ import annotations
from .store import Store
from .agents import AgentRegistry
from .routing import ModelRouter

class Orchestrator:
    def __init__(self,store:Store,agents:AgentRegistry,router:ModelRouter):
        self.store,self.agents,self.router=store,agents,router
    async def submit(self,project_id:str,task:str,agent_id:str="zynx_main",provider:str|None=None,action:str|None=None):
        project=self.store.get_project(project_id)
        if not project: raise ValueError("Project not found")
        run=self.store.create_run(project_id,task,agent_id)
        self.store.set_run(run["id"],"running")
        try:
            specialist=await self.agents.dispatch(agent_id,task,project["context"],action)
            model_result=None
            if provider:
                model_result=await self.router.generate(task,provider)
            result={"specialist":specialist,"model":model_result}
            return self.store.set_run(run["id"],"completed",result)
        except Exception as exc:
            return self.store.set_run(run["id"],"failed",error=f"{type(exc).__name__}: {exc}")
