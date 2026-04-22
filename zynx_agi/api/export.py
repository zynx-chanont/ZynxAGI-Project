"""
Export API Endpoints
Provides REST API for exporting OpenAI prompts, configurations, and agent definitions
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..storage.openai_exporter import OpenAIExporter
from ..storage.drivers import MemoryStorageDriver
from ..storage.artifact_manager import ArtifactManager
from ..agents.agent_registry import AgentRegistry
from ..agents.deeja_agent import DeejaAgent
from ..agents.zynx_main_agent import ZynxMainAgent
from ..agents.metadata_agent import ZynxMetadataAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/export", tags=["export"])

# Initialize storage and export components
storage_driver = MemoryStorageDriver()
artifact_manager = ArtifactManager(storage_driver)
openai_exporter = OpenAIExporter(storage_driver, artifact_manager)


class ExportRequest(BaseModel):
    """Request model for export operations"""
    export_type: str = Field(..., description="Type of export: 'all', 'prompts', 'configs', or 'agents'")
    include_agents: bool = Field(True, description="Whether to include agent data")
    agent_ids: Optional[List[str]] = Field(None, description="Specific agent IDs to export (optional)")


class ExportResponse(BaseModel):
    """Response model for export operations"""
    success: bool
    artifact_id: str
    exported_at: str
    summary: Dict[str, Any]
    download_url: Optional[str] = None


async def get_agents_for_export(agent_ids: Optional[List[str]] = None) -> List[Any]:
    """Get agents to export based on requested IDs"""
    # Create sample agents for export
    agents = []
    
    # Always include core agents if no specific IDs requested
    if not agent_ids or "deeja" in agent_ids:
        deeja = DeejaAgent()
        await deeja.initialize()
        agents.append(deeja)
    
    if not agent_ids or "zynx_main" in agent_ids:
        zynx_main = ZynxMainAgent()
        await zynx_main.initialize()
        agents.append(zynx_main)
    
    if not agent_ids or "zynx_metadata" in agent_ids:
        zynx_metadata = ZynxMetadataAgent()
        await zynx_metadata.initialize()
        agents.append(zynx_metadata)
    
    return agents


@router.post("/openai", response_model=ExportResponse)
async def export_openai_assets(request: ExportRequest):
    """
    Export OpenAI assets (prompts, configs, and/or agents)
    
    - **export_type**: Type of export - 'all', 'prompts', 'configs', or 'agents'
    - **include_agents**: Whether to include agent definitions
    - **agent_ids**: Optional list of specific agent IDs to export
    
    Returns export artifact ID and summary
    """
    try:
        logger.info(f"Starting OpenAI export of type: {request.export_type}")
        
        agents = None
        if request.include_agents:
            agents = await get_agents_for_export(request.agent_ids)
        
        # Perform export based on type
        if request.export_type == "all":
            result = await openai_exporter.export_all_assets(
                agents=agents,
                include_system_prompts=True,
                include_model_configs=True,
                include_agent_definitions=request.include_agents
            )
        elif request.export_type == "prompts":
            result = await openai_exporter.export_prompts_only(agents=agents)
        elif request.export_type == "configs":
            result = await openai_exporter.export_configs_only()
        elif request.export_type == "agents":
            if not agents:
                agents = await get_agents_for_export(request.agent_ids)
            result = await openai_exporter.export_agents_only(agents=agents)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid export_type: {request.export_type}. Must be 'all', 'prompts', 'configs', or 'agents'"
            )
        
        if not result.get("export_success"):
            raise HTTPException(status_code=500, detail="Export failed")
        
        return ExportResponse(
            success=True,
            artifact_id=result["artifact_id"],
            exported_at=result["exported_at"],
            summary=result.get("summary", {}),
            download_url=f"/api/v1/export/download/{result['artifact_id']}"
        )
        
    except Exception as e:
        logger.error(f"Error during OpenAI export: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")


@router.get("/openai/prompts")
async def export_openai_prompts():
    """
    Export only OpenAI system prompts
    
    Returns all system prompts used by agents and configurations
    """
    try:
        result = await openai_exporter.export_prompts_only()
        
        return {
            "success": True,
            "artifact_id": result["artifact_id"],
            "exported_at": result["exported_at"],
            "prompts_count": result["prompts_count"],
            "download_url": f"/api/v1/export/download/{result['artifact_id']}"
        }
    except Exception as e:
        logger.error(f"Error exporting prompts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prompts export error: {str(e)}")


@router.get("/openai/configs")
async def export_openai_configs():
    """
    Export only OpenAI model configurations
    
    Returns all model configurations including temperature, max_tokens, etc.
    """
    try:
        result = await openai_exporter.export_configs_only()
        
        return {
            "success": True,
            "artifact_id": result["artifact_id"],
            "exported_at": result["exported_at"],
            "configs_count": result["configs_count"],
            "download_url": f"/api/v1/export/download/{result['artifact_id']}"
        }
    except Exception as e:
        logger.error(f"Error exporting configs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Configs export error: {str(e)}")


@router.get("/openai/agents")
async def export_openai_agents(agent_ids: Optional[str] = None):
    """
    Export only agent definitions
    
    - **agent_ids**: Comma-separated list of agent IDs to export (optional)
    
    Returns agent definitions with their configurations and capabilities
    """
    try:
        agent_id_list = agent_ids.split(",") if agent_ids else None
        agents = await get_agents_for_export(agent_id_list)
        
        if not agents:
            raise HTTPException(status_code=400, detail="No agents found to export")
        
        result = await openai_exporter.export_agents_only(agents=agents)
        
        return {
            "success": True,
            "artifact_id": result["artifact_id"],
            "exported_at": result["exported_at"],
            "agents_count": result["agents_count"],
            "download_url": f"/api/v1/export/download/{result['artifact_id']}"
        }
    except Exception as e:
        logger.error(f"Error exporting agents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agents export error: {str(e)}")


@router.get("/download/{artifact_id}")
async def download_export(artifact_id: str):
    """
    Download exported artifact by ID
    
    Returns the exported data in JSON format
    """
    try:
        artifact = await artifact_manager.retrieve_artifact(artifact_id)
        
        if not artifact:
            raise HTTPException(status_code=404, detail=f"Artifact {artifact_id} not found")
        
        # Parse and return the artifact content
        import json
        content = json.loads(artifact["content"].decode())
        
        return {
            "success": True,
            "artifact_id": artifact_id,
            "data": content,
            "metadata": artifact.get("metadata", {})
        }
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding artifact {artifact_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Invalid artifact format")
    except Exception as e:
        logger.error(f"Error downloading artifact: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")


@router.post("/import/{artifact_id}")
async def import_openai_assets(artifact_id: str):
    """
    Import OpenAI assets from a previously exported artifact
    
    Restores prompts, configurations, and agent definitions from export
    """
    try:
        result = await openai_exporter.import_assets(artifact_id)
        
        return {
            "success": True,
            "artifact_id": artifact_id,
            "imported_at": result["imported_at"],
            "original_export_date": result["original_export_date"],
            "summary": result["summary"]
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error importing assets: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Import error: {str(e)}")


@router.get("/list")
async def list_exports():
    """
    List all available export artifacts
    
    Returns a list of all exported artifacts with metadata
    """
    try:
        # Get all artifacts with export tags
        all_artifacts = await artifact_manager.list_artifacts(tags=["export", "openai"])
        
        return {
            "success": True,
            "total_exports": len(all_artifacts),
            "exports": all_artifacts
        }
    except Exception as e:
        logger.error(f"Error listing exports: {str(e)}")
        raise HTTPException(status_code=500, detail=f"List error: {str(e)}")


@router.get("/status")
async def export_status():
    """
    Get export system status
    
    Returns information about available export capabilities
    """
    return {
        "success": True,
        "export_system": "operational",
        "available_export_types": ["all", "prompts", "configs", "agents"],
        "supported_formats": ["json"],
        "storage_backend": "memory",
        "version": "1.0.0"
    }
