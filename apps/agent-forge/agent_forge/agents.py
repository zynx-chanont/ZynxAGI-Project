from __future__ import annotations
import os
import httpx

class AgentRegistry:
    def __init__(self):
        self.agents={
            "zynx_main":{"kind":"http","base":os.getenv("ZYNXAGI_BASE_URL","http://127.0.0.1:8000"),"description":"ZynxAGI main ecosystem adapter"},
            "deeja":{"kind":"http","base":os.getenv("ZYNXAGI_BASE_URL","http://127.0.0.1:8000"),"description":"Deeja specialist via ZynxAGI"},
            "zynx_metadata":{"kind":"http","base":os.getenv("ZYNXAGI_BASE_URL","http://127.0.0.1:8000"),"description":"Metadata and compliance specialist"}
        }
    def list(self): return [{"id":k,**v} for k,v in self.agents.items()]
    async def health(self):
        base=os.getenv("ZYNXAGI_BASE_URL","http://127.0.0.1:8000")
        try:
            async with httpx.AsyncClient(timeout=3) as c:
                r=await c.get(base.rstrip("/")+"/health")
                return {"zynxagi":"healthy" if r.is_success else "unavailable","http_status":r.status_code}
        except Exception as e: return {"zynxagi":"unavailable","detail":type(e).__name__}
    async def dispatch(self,agent_id:str,task:str,context:dict):
        if agent_id not in self.agents: raise ValueError("Unknown specialist agent")
        # Adapter intentionally does not guess the legacy request schema. Until a
        # verified endpoint contract is configured, return an explicit integration status.
        base=self.agents[agent_id]["base"]
        return {"status":"adapter_ready_contract_unverified","agent_id":agent_id,"base_url":base,"task_preview":task[:160],"context_keys":list(context.keys()),"next_step":"Verify ZynxAGI agent endpoint contract before enabling live dispatch."}
