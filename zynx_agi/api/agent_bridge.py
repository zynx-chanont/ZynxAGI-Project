from __future__ import annotations

import os
import secrets
from typing import Any, Literal

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field

from ..ecosystem.ecosystem_manager import EcosystemManager

router = APIRouter(prefix="/api/v1/agents", tags=["agent-bridge"])
_ALLOWED_ACTIONS = {
    "zynx_main": {"chat", "session", "compliance"},
    "deeja": {"chat", "analyze", "cultural", "emotional", "empathy", "translate"},
    "zynx_metadata": {"metadata", "compliance", "session"},
}
_ALIASES = {"zynx_main": "zynx", "deeja": "deeja", "zynx_metadata": "metadata"}


def _authorize(token: str | None) -> None:
    expected = os.getenv("ZYNXAGI_AGENT_API_TOKEN", "")
    if not expected:
        raise HTTPException(status_code=503, detail="Agent bridge is disabled: service token is not configured")
    if not secrets.compare_digest(expected, token or ""):
        raise HTTPException(status_code=401, detail="Invalid service token")


def _manager(request: Request) -> EcosystemManager:
    manager = getattr(request.app.state, "ecosystem_manager", None)
    if manager is None or not manager.initialized:
        raise HTTPException(status_code=503, detail="ZynxAGI ecosystem is not initialized")
    return manager


class AgentDispatchIn(BaseModel):
    agent_id: Literal["zynx_main", "deeja", "zynx_metadata"]
    action: str = "chat"
    message: str = Field(min_length=1, max_length=12000)
    payload: dict[str, Any] = Field(default_factory=dict)


@router.get("/status")
async def agent_status(request: Request, x_zynxagi_token: str | None = Header(default=None)):
    _authorize(x_zynxagi_token)
    manager = _manager(request)
    registry = manager.agent_registry.get_registry_status()
    agents_health = await manager.agent_registry.health_check_all_agents()
    dispatcher_ready = manager.mcp_dispatcher is not None
    healthy = bool(registry.get("initialized")) and bool(agents_health.get("overall_healthy")) and dispatcher_ready
    health = {
        "healthy": healthy,
        "components": {
            "agent_registry": {"status": "healthy" if registry.get("initialized") else "unhealthy"},
            "agents": agents_health,
            "mcp_dispatcher": {"status": "healthy" if dispatcher_ready else "unhealthy"},
        },
    }
    return {
        "initialized": manager.initialized,
        "agents": manager.agent_registry.list_agents(),
        "capabilities": manager.agent_registry.list_capabilities(),
        "health": health,
    }


@router.post("/dispatch")
async def dispatch_agent(
    body: AgentDispatchIn,
    request: Request,
    x_zynxagi_token: str | None = Header(default=None),
):
    _authorize(x_zynxagi_token)
    manager = _manager(request)
    if body.action not in _ALLOWED_ACTIONS[body.agent_id]:
        raise HTTPException(status_code=422, detail=f"Action '{body.action}' is not allowed for {body.agent_id}")

    # The existing MCPDispatcher parses /agent:action commands and invokes
    # the registered agent capability. Keep that as the single dispatch path.
    command = f"/{_ALIASES[body.agent_id]}:{body.action} {body.message}"
    dispatch_request = {**body.payload, "message": command, "agent_forge_input": body.message}
    if body.agent_id == "zynx_metadata":
        dispatch_request.setdefault("data", {"content": body.message, **body.payload})
    elif body.agent_id == "zynx_main" and body.action == "compliance":
        dispatch_request.setdefault("content", body.message)
    result = await manager.process_request(dispatch_request)
    if not result.get("success"):
        raise HTTPException(status_code=502, detail={"message": "ZynxAGI dispatcher rejected the request", "result": result})
    return {
        "status": "dispatched",
        "agent_id": result.get("agent_id", body.agent_id),
        "success": result["success"],
        "response": result.get("response"),
        "metadata": result.get("metadata"),
        "timestamp": result.get("timestamp"),
        "processing_time_ms": result.get("processing_time_ms"),
        "compliance_info": result.get("compliance_info"),
    }
