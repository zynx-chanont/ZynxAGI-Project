from __future__ import annotations
import os
import httpx

class AgentRegistry:
    """HTTP adapter for the authenticated ZynxAGI MCPDispatcher bridge."""
    def __init__(self):
        self.base=os.getenv("ZYNXAGI_BASE_URL","http://127.0.0.1:8000").rstrip("/")
        self.token=os.getenv("ZYNXAGI_AGENT_API_TOKEN","")
        self.timeout=httpx.Timeout(45,connect=5)
        self.agents={
            "zynx_main":{"kind":"zynxagi_mcp","description":"Zynx Main Agent via existing MCPDispatcher","actions":["chat","session","compliance"]},
            "deeja":{"kind":"zynxagi_mcp","description":"Deeja Agent via existing MCPDispatcher","actions":["chat","analyze","cultural","emotional","empathy","translate"]},
            "zynx_metadata":{"kind":"zynxagi_mcp","description":"Zynx Metadata Agent via existing MCPDispatcher","actions":["metadata","compliance","session"]}
        }
    def list(self):
        return [{"id":key,**value} for key,value in self.agents.items()]
    def _headers(self):
        if not self.token:
            raise RuntimeError("ZYNXAGI_AGENT_API_TOKEN is not configured")
        return {"X-ZynxAGI-Token":self.token}
    async def health(self):
        if not self.token:
            return {"zynxagi":"not_configured","detail":"ZYNXAGI_AGENT_API_TOKEN is missing"}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response=await client.get(self.base+"/api/v1/agents/status",headers=self._headers())
                if response.status_code==200:
                    data=response.json()
                    return {"zynxagi":"healthy" if data.get("initialized") else "degraded",
                            "initialized":data.get("initialized",False),
                            "agents":data.get("agents",[]),
                            "capabilities":data.get("capabilities",{})}
                return {"zynxagi":"unavailable","http_status":response.status_code}
        except Exception as exc:
            return {"zynxagi":"unavailable","detail":type(exc).__name__}
    async def dispatch(self,agent_id:str,task:str,context:dict,action:str|None=None):
        if agent_id not in self.agents:
            raise ValueError("Unknown specialist agent")
        selected_action=action or ("compliance" if agent_id=="zynx_metadata" else "chat")
        if selected_action not in self.agents[agent_id]["actions"]:
            raise ValueError(f"Unsupported action '{selected_action}' for {agent_id}")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response=await client.post(self.base+"/api/v1/agents/dispatch",
                headers=self._headers(),
                json={"agent_id":agent_id,"action":selected_action,"message":task,"payload":context})
            response.raise_for_status()
            data=response.json()
        if data.get("status")!="dispatched" or not data.get("success"):
            raise RuntimeError("ZynxAGI did not confirm successful dispatch")
        return data
