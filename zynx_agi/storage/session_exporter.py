"""
Session Data Exporter for OpenAI and other AI platform sessions
Handles migration and backup of conversation data, prompts, and configurations
"""

import json
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from .drivers import StorageDriver
from .artifact_manager import ArtifactManager


class SessionDataExporter:
    """Exports and imports AI session data with full configuration preservation"""
    
    def __init__(self, storage_driver: StorageDriver, artifact_manager: ArtifactManager):
        self.storage = storage_driver
        self.artifacts = artifact_manager
    
    async def export_openai_session(
        self, 
        session_data: Dict[str, Any],
        include_system_instructions: bool = True,
        include_model_config: bool = True
    ) -> Dict[str, Any]:
        """Export OpenAI session with full configuration"""
        export_timestamp = datetime.utcnow()
        
        # Structure the export data
        export_data = {
            "export_metadata": {
                "exported_at": export_timestamp.isoformat(),
                "source_platform": "openai",
                "exporter_version": "1.0.0",
                "compliance": ["ZPDL_v1.0", "PDPA"],
                "format_version": "zynx_session_v1"
            },
            "session_info": {
                "session_id": session_data.get("session_id"),
                "created_at": session_data.get("created_at"),
                "last_modified": session_data.get("last_modified"),
                "total_messages": len(session_data.get("messages", [])),
                "model_used": session_data.get("model", "unknown")
            },
            "messages": [],
            "system_instructions": None,
            "model_configuration": None,
            "custom_instructions": None,
            "metadata": session_data.get("metadata", {})
        }
        
        # Export messages with enhanced metadata
        for i, message in enumerate(session_data.get("messages", [])):
            exported_message = {
                "message_id": f"msg_{i:04d}",
                "role": message.get("role"),
                "content": message.get("content"),
                "timestamp": message.get("timestamp"),
                "token_count": message.get("token_count"),
                "model_used": message.get("model"),
                "finish_reason": message.get("finish_reason"),
                "metadata": message.get("metadata", {})
            }
            export_data["messages"].append(exported_message)
        
        # Include system instructions if requested
        if include_system_instructions and "system_instructions" in session_data:
            export_data["system_instructions"] = {
                "content": session_data["system_instructions"],
                "last_updated": session_data.get("system_instructions_updated"),
                "version": session_data.get("system_instructions_version", "1.0")
            }
        
        # Include model configuration if requested
        if include_model_config and "model_config" in session_data:
            export_data["model_configuration"] = {
                "model": session_data["model_config"].get("model"),
                "temperature": session_data["model_config"].get("temperature"),
                "max_tokens": session_data["model_config"].get("max_tokens"),
                "top_p": session_data["model_config"].get("top_p"),
                "frequency_penalty": session_data["model_config"].get("frequency_penalty"),
                "presence_penalty": session_data["model_config"].get("presence_penalty"),
                "stop_sequences": session_data["model_config"].get("stop"),
                "custom_parameters": session_data["model_config"].get("custom", {})
            }
        
        # Store as artifact
        export_json = json.dumps(export_data, ensure_ascii=False, indent=2).encode()
        artifact_info = await self.artifacts.store_artifact(
            "openai_session_export",
            export_json,
            {
                "source_session_id": session_data.get("session_id"),
                "exported_at": export_timestamp.isoformat(),
                "message_count": len(export_data["messages"]),
                "content_type": "application/json",
                "tags": ["session_export", "openai", "backup"]
            }
        )
        
        return {
            "export_success": True,
            "artifact_id": artifact_info["artifact_id"],
            "artifact_hash": artifact_info["hash"],
            "export_size": artifact_info["size"],
            "exported_at": export_timestamp.isoformat(),
            "message_count": len(export_data["messages"])
        }
    
    async def import_session_data(self, artifact_id: str) -> Dict[str, Any]:
        """Import session data from stored artifact"""
        artifact = await self.artifacts.retrieve_artifact(artifact_id)
        if not artifact:
            raise ValueError(f"Session export artifact {artifact_id} not found")
        
        try:
            session_data = json.loads(artifact["content"].decode())
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in session export: {e}")
        
        # Validate format
        if session_data.get("export_metadata", {}).get("format_version") != "zynx_session_v1":
            raise ValueError("Unsupported session export format")
        
        return {
            "import_success": True,
            "session_data": session_data,
            "imported_at": datetime.utcnow().isoformat(),
            "original_export_date": session_data["export_metadata"]["exported_at"],
            "message_count": len(session_data.get("messages", []))
        }
    
    async def export_all_sessions(
        self, 
        sessions: List[Dict[str, Any]],
        batch_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Export multiple sessions as a batch"""
        if not batch_name:
            batch_name = f"batch_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        export_results = []
        total_messages = 0
        
        for session in sessions:
            try:
                result = await self.export_openai_session(session)
                export_results.append(result)
                total_messages += result["message_count"]
            except Exception as e:
                export_results.append({
                    "export_success": False,
                    "session_id": session.get("session_id"),
                    "error": str(e)
                })
        
        # Create batch summary
        batch_summary = {
            "batch_name": batch_name,
            "exported_at": datetime.utcnow().isoformat(),
            "total_sessions": len(sessions),
            "successful_exports": len([r for r in export_results if r.get("export_success")]),
            "failed_exports": len([r for r in export_results if not r.get("export_success")]),
            "total_messages": total_messages,
            "results": export_results
        }
        
        # Store batch summary as artifact
        summary_json = json.dumps(batch_summary, ensure_ascii=False, indent=2).encode()
        batch_artifact = await self.artifacts.store_artifact(
            "session_batch_export",
            summary_json,
            {
                "batch_name": batch_name,
                "session_count": len(sessions),
                "content_type": "application/json",
                "tags": ["batch_export", "session_summary"]
            }
        )
        
        return {
            "batch_export_success": True,
            "batch_artifact_id": batch_artifact["artifact_id"],
            "summary": batch_summary
        }
    
    async def create_configuration_backup(
        self, 
        prompts: Dict[str, str],
        system_instructions: Dict[str, str],
        model_configs: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create a backup of all configurations and prompts"""
        backup_data = {
            "backup_metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "backup_type": "configuration",
                "version": "1.0.0",
                "compliance": ["ZPDL_v1.0", "PDPA"]
            },
            "prompts": prompts,
            "system_instructions": system_instructions,
            "model_configurations": model_configs,
            "backup_statistics": {
                "prompt_count": len(prompts),
                "system_instruction_count": len(system_instructions),
                "model_config_count": len(model_configs)
            }
        }
        
        # Store as artifact
        backup_json = json.dumps(backup_data, ensure_ascii=False, indent=2).encode()
        artifact_info = await self.artifacts.store_artifact(
            "configuration_backup",
            backup_json,
            {
                "backup_type": "configuration",
                "prompt_count": len(prompts),
                "content_type": "application/json",
                "tags": ["configuration", "backup", "prompts", "system_instructions"]
            }
        )
        
        return {
            "backup_success": True,
            "artifact_id": artifact_info["artifact_id"],
            "backup_size": artifact_info["size"],
            "statistics": backup_data["backup_statistics"]
        }