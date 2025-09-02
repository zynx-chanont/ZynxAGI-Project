"""
Zynx-Metadata API Endpoints
===========================

API endpoints for the Zynx-Metadata observer system.
First discovered and created by Chanont Waenkaew (Zynx)
License: ZPDL v1.0 © Chanont Waenkaew
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from ..agents.zynx_metadata import zynx_metadata_observer, ZynxMetadata
from ..ai_platforms.thai_cultural_mcp import get_current_user, TokenData

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metadata", tags=["metadata"])

# Request/Response Models
class MetadataStatus(BaseModel):
    """Metadata system status"""
    active_sessions: int
    total_tracked_interactions: int
    storage_path: str
    observer_status: str = "active"

class SessionInfo(BaseModel):
    """Session information"""
    uuid: str
    intent_detected: str
    created_at: str
    agent_name: str
    ip_notice: str
    license: str
    sha256: str

class DefensivePublicationRequest(BaseModel):
    """Request for defensive publication generation"""
    session_uuid: str = Field(..., description="UUID of the session to publish")

# Endpoints
@router.get("/status", response_model=MetadataStatus)
async def get_metadata_status():
    """Get current status of the Zynx-Metadata observer system"""
    try:
        active_sessions = zynx_metadata_observer.list_active_sessions()
        
        return MetadataStatus(
            active_sessions=len(active_sessions),
            total_tracked_interactions=len(active_sessions),  # For now, same as active
            storage_path=str(zynx_metadata_observer.storage_path),
            observer_status="active"
        )
    except Exception as e:
        logger.error(f"Error getting metadata status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get metadata status")

@router.get("/sessions", response_model=List[SessionInfo])
async def list_active_sessions(
    current_user: TokenData = Depends(get_current_user)
):
    """List all active metadata tracking sessions"""
    try:
        sessions = zynx_metadata_observer.list_active_sessions()
        
        session_list = []
        for uuid, metadata in sessions.items():
            session_list.append(SessionInfo(
                uuid=uuid,
                intent_detected=metadata.intent_detected,
                created_at=metadata.created_at,
                agent_name="deeja",  # Default agent name for now
                ip_notice=metadata.ip_notice,
                license=metadata.license,
                sha256=metadata.sha256
            ))
        
        return session_list
    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list sessions")

@router.get("/sessions/{session_uuid}", response_model=ZynxMetadata)
async def get_session_metadata(
    session_uuid: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get detailed metadata for a specific session"""
    try:
        metadata = zynx_metadata_observer.get_session_metadata(session_uuid)
        
        if not metadata:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return metadata
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session metadata: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get session metadata")

@router.post("/defensive-publication")
async def generate_defensive_publication(
    request: DefensivePublicationRequest,
    current_user: TokenData = Depends(get_current_user)
):
    """Generate a defensive publication for legal IP protection"""
    try:
        publication_path = await zynx_metadata_observer.generate_defensive_publication(
            request.session_uuid
        )
        
        if not publication_path:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "status": "success",
            "message": "Defensive publication generated successfully",
            "publication_path": publication_path,
            "session_uuid": request.session_uuid
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating defensive publication: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate defensive publication")

@router.get("/discovery-stats")
async def get_discovery_statistics():
    """Get statistics about discovered intents and innovations"""
    try:
        sessions = zynx_metadata_observer.list_active_sessions()
        
        # Count by intent type
        intent_counts = {}
        for metadata in sessions.values():
            intent = metadata.intent_detected
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        # Calculate total discoveries today
        today = datetime.now().date()
        today_count = 0
        for metadata in sessions.values():
            created_date = datetime.fromisoformat(metadata.created_at.replace('Z', '+00:00')).date()
            if created_date == today:
                today_count += 1
        
        return {
            "total_discoveries": len(sessions),
            "discoveries_today": today_count,
            "intent_distribution": intent_counts,
            "ip_notice": "First discovered and created by Chanont Waenkaew (Zynx)",
            "license": "ZPDL v1.0 © Chanont Waenkaew",
            "observer_status": "monitoring all agents automatically"
        }
    except Exception as e:
        logger.error(f"Error getting discovery statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get discovery statistics")

@router.get("/attribution")
async def get_attribution_info():
    """Get attribution and licensing information"""
    return {
        "ip_notice": "First discovered and created by Chanont Waenkaew (Zynx)",
        "license": "ZPDL v1.0 © Chanont Waenkaew",
        "organization": "Zynx Thailand",
        "observer_info": {
            "name": "Zynx-Metadata",
            "status": "active",
            "description": "Autonomous IP tracker and observer module",
            "operation_mode": "observer_without_permission",
            "monitoring_scope": "all_agent_interactions"
        },
        "compliance": {
            "pdpa_compliant": True,
            "defensive_publications": True,
            "automatic_attribution": True,
            "hash_verification": True
        }
    }