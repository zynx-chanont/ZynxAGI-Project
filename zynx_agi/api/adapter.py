"""
ZynxAGI - Gateway-to-Core Adapter API Router (Gate 3 Implementation)
===================================================================
Provides normalized HTTP endpoints matching the Zynx Gateway client specifications:
- GET  /agents
- GET  /agents/{agent_id}/health
- POST /agents/{agent_id}/invoke

RFC 9457 Problem Details standard is implemented for all error responses.
"""

from datetime import datetime
import logging
import time
from typing import Any, Dict, List, Optional
import uuid

from fastapi import APIRouter, Depends, Header, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..modules.deeja.agent import DeejaModule
from ..modules.deeja.models import DeejaRequest
from ..modules.zynx.agent import ZynxModule
from ..modules.zynx.models import ZynxRequest
from ..security.auth import verify_service_token

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Agents Adapter"])

# Lazy singletons for module execution
_zynx_module: Optional[ZynxModule] = None
_deeja_module: Optional[DeejaModule] = None


async def get_zynx_module() -> ZynxModule:
    global _zynx_module
    if _zynx_module is None:
        _zynx_module = ZynxModule()
        await _zynx_module.initialize()
    return _zynx_module


async def get_deeja_module() -> DeejaModule:
    global _deeja_module
    if _deeja_module is None:
        _deeja_module = DeejaModule()
        await _deeja_module.initialize()
    return _deeja_module


def rfc9457_problem_response(
    status_code: int,
    title: str,
    detail: str,
    instance: str,
    trace_id: str,
    error_type: Optional[str] = None,
) -> JSONResponse:
    """Construct an RFC 9457 compliant Problem Details JSON response."""
    if error_type is None:
        error_slug = title.lower().replace(" ", "-")
        error_type = f"https://api.zynx.ai/errors/{error_slug}"

    problem_body = {
        "type": error_type,
        "title": title,
        "status": status_code,
        "detail": detail,
        "error": detail,
        "instance": instance,
        "traceId": trace_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    return JSONResponse(
        status_code=status_code,
        media_type="application/problem+json",
        content=problem_body,
    )


class InvokeOptions(BaseModel):
    timeoutMs: Optional[int] = Field(default=30000, ge=100, le=120000)
    maxTokens: Optional[int] = Field(default=2048, ge=1, le=8192)


class InvokePayload(BaseModel):
    input: Dict[str, Any]
    sessionId: Optional[str] = None
    streaming: Optional[bool] = False
    options: Optional[InvokeOptions] = None


class AgentSummary(BaseModel):
    id: str
    name: str
    status: str
    category: str
    role: str
    backendRoute: str
    tenantScope: str = "global"
    allowedRoles: List[str] = ["admin", "engineer", "viewer", "agent"]


class ListAgentsResponse(BaseModel):
    agents: List[AgentSummary]


CORE_HOSTED_AGENTS: List[AgentSummary] = [
    AgentSummary(
        id="zynx",
        name="Zynx Universal Orchestrator",
        status="published",
        category="orchestration",
        role="Universal AI Orchestration and Intelligent Multi-Platform Routing",
        backendRoute="/agents/zynx/invoke",
    ),
    AgentSummary(
        id="deeja",
        name="Deeja (ดีจ้า)",
        status="published",
        category="cultural",
        role="Emotional AI & Thai Cultural-Emotional Intelligence Engine",
        backendRoute="/agents/deeja/invoke",
    ),
]


@router.get("/agents", response_model=ListAgentsResponse)
@router.get("/api/v1/agents", response_model=ListAgentsResponse)
async def list_agents(
    _token: str = Depends(verify_service_token),
) -> ListAgentsResponse:
    """List agents hosted by the Python Core platform."""
    return ListAgentsResponse(agents=CORE_HOSTED_AGENTS)


@router.get("/agents/{agent_id}/health")
@router.get("/api/v1/agents/{agent_id}/health")
async def get_agent_health(
    agent_id: str,
    request: Request,
    _token: str = Depends(verify_service_token),
    x_zynx_trace_id: Optional[str] = Header(None),
) -> Any:
    """Retrieve health and readiness status for a specific Core-hosted agent."""
    trace_id = x_zynx_trace_id or f"tr-{uuid.uuid4().hex[:9]}"
    norm_id = agent_id.strip().lower()

    if norm_id in ("zynx", "zynx-main", "orchestrator", "task-planner"):
        try:
            mod = await get_zynx_module()
            status_data = await mod.get_status()
            return {
                "agentId": agent_id,
                "status": "healthy" if status_data.get("active") else "initializing",
                "details": status_data,
                "traceId": trace_id,
            }
        except Exception as exc:
            logger.error("Health check error for ZynxModule: %s", exc)
            return rfc9457_problem_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                title="Agent Health Error",
                detail=f"Failed to check health for agent '{agent_id}': {str(exc)}",
                instance=str(request.url.path),
                trace_id=trace_id,
            )

    elif norm_id in ("deeja", "deeja-cultural", "cultural"):
        try:
            mod = await get_deeja_module()
            status_data = await mod.get_status()
            return {
                "agentId": agent_id,
                "status": "healthy" if status_data.get("active") else "initializing",
                "details": status_data,
                "traceId": trace_id,
            }
        except Exception as exc:
            logger.error("Health check error for DeejaModule: %s", exc)
            return rfc9457_problem_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                title="Agent Health Error",
                detail=f"Failed to check health for agent '{agent_id}': {str(exc)}",
                instance=str(request.url.path),
                trace_id=trace_id,
            )

    else:
        return rfc9457_problem_response(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Agent Not Found",
            detail=f"Agent '{agent_id}' is not hosted by Python Core adapter. Core hosts: ['zynx', 'deeja'].",
            instance=str(request.url.path),
            trace_id=trace_id,
        )


@router.post("/agents/{agent_id}/invoke")
@router.post("/api/v1/agents/{agent_id}/invoke")
async def invoke_agent(
    agent_id: str,
    payload: InvokePayload,
    request: Request,
    _token: str = Depends(verify_service_token),
    x_zynx_trace_id: Optional[str] = Header(None),
    x_zynx_tenant_id: Optional[str] = Header(None),
    x_zynx_user_id: Optional[str] = Header(None),
) -> Any:
    """Invoke a Core-hosted agent with standardized payload and RFC 9457 error contracts."""
    start_ts = time.perf_counter()
    trace_id = x_zynx_trace_id or f"tr-{uuid.uuid4().hex[:9]}"
    tenant_id = x_zynx_tenant_id or "dev"
    user_id = x_zynx_user_id or "anonymous"
    norm_id = agent_id.strip().lower()

    # Extract message / goal from payload.input
    raw_message = (
        payload.input.get("message")
        or payload.input.get("goal")
        or payload.input.get("task")
        or payload.input.get("input")
        or (payload.input.get("context", {}).get("goal") if isinstance(payload.input.get("context"), dict) else None)
        or (payload.input.get("context", {}).get("input") if isinstance(payload.input.get("context"), dict) else None)
        or "Execute task"
    )
    message_str = str(raw_message).strip() if raw_message else "Zynx agent execution"

    # Build unified context
    input_context = payload.input.get("context")
    context: Dict[str, Any] = dict(input_context) if isinstance(input_context, dict) else {}
    context["tenant_id"] = tenant_id
    context["user_id"] = user_id
    context["trace_id"] = trace_id
    if payload.sessionId:
        context["session_id"] = payload.sessionId

    if norm_id in ("zynx", "zynx-main", "orchestrator", "task-planner"):
        try:
            mod = await get_zynx_module()
            zynx_req = ZynxRequest(
                message=message_str,
                context=context,
                session_id=payload.sessionId,
                metadata=payload.input,
            )
            res = await mod.process(zynx_req)
            duration_ms = res.processing_time_ms or round((time.perf_counter() - start_ts) * 1000, 2)

            return {
                "agentId": agent_id,
                "sessionId": payload.sessionId,
                "traceId": trace_id,
                "output": {
                    "success": res.success,
                    "message": res.message,
                    "data": res.data,
                    "platformUsed": res.platform_used,
                    "routingDecision": res.routing_decision,
                    "complianceInfo": res.compliance_info,
                    "error": res.error,
                },
                "meta": {
                    "durationMs": duration_ms,
                    "tokensUsed": 0,
                    "modelUsed": res.platform_used or "zynx-orchestration-engine",
                    "traceId": trace_id,
                },
            }
        except Exception as exc:
            logger.error("Execution error invoking Zynx agent: %s", exc)
            return rfc9457_problem_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                title="Agent Execution Failed",
                detail=f"Agent '{agent_id}' execution failed: {str(exc)}",
                instance=str(request.url.path),
                trace_id=trace_id,
            )

    elif norm_id in ("deeja", "deeja-cultural", "cultural"):
        try:
            mod = await get_deeja_module()
            deeja_req = DeejaRequest(
                message=message_str,
                context=context,
                language=str(payload.input.get("language") or "") or None,
                formality_hint=str(payload.input.get("formality_hint") or "") or None,
            )
            res = await mod.process(deeja_req)
            duration_ms = res.processing_time_ms or round((time.perf_counter() - start_ts) * 1000, 2)

            return {
                "agentId": agent_id,
                "sessionId": payload.sessionId,
                "traceId": trace_id,
                "output": {
                    "success": res.success,
                    "message": res.message,
                    "culturalAnalysis": res.cultural_analysis.model_dump() if res.cultural_analysis else None,
                    "emotionalAnalysis": res.emotional_analysis.model_dump() if res.emotional_analysis else None,
                    "empathyScore": res.empathy_score,
                    "responseLanguage": res.response_language,
                    "culturalAppropriateness": res.cultural_appropriateness,
                    "ethicalAssessment": res.ethical_assessment,
                    "error": res.error,
                },
                "meta": {
                    "durationMs": duration_ms,
                    "tokensUsed": 0,
                    "modelUsed": "deeja-cultural-engine",
                    "traceId": trace_id,
                },
            }
        except Exception as exc:
            logger.error("Execution error invoking Deeja agent: %s", exc)
            return rfc9457_problem_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                title="Agent Execution Failed",
                detail=f"Agent '{agent_id}' execution failed: {str(exc)}",
                instance=str(request.url.path),
                trace_id=trace_id,
            )

    else:
        return rfc9457_problem_response(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Agent Not Found",
            detail=f"Agent '{agent_id}' is not hosted by Python Core adapter. Core hosts: ['zynx', 'deeja'].",
            instance=str(request.url.path),
            trace_id=trace_id,
        )
