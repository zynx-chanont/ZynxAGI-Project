"""
OpenAI Asset Exporter
Exports prompts, configurations, and agent definitions from OpenAI platform
Supports backup, migration, and configuration management
"""

import json
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from .drivers import StorageDriver
from .artifact_manager import ArtifactManager
from ..agents.base_agent import ZynxAgent, AgentCapability
from ..config.settings import settings
import logging

logger = logging.getLogger(__name__)


class OpenAIExporter:
    """Export OpenAI prompts, configurations, and agent definitions"""
    
    def __init__(self, storage_driver: StorageDriver, artifact_manager: ArtifactManager):
        self.storage = storage_driver
        self.artifacts = artifact_manager
        
    async def export_all_assets(
        self,
        agents: Optional[List[ZynxAgent]] = None,
        include_system_prompts: bool = True,
        include_model_configs: bool = True,
        include_agent_definitions: bool = True
    ) -> Dict[str, Any]:
        """
        Export all OpenAI assets including prompts, configs, and agent definitions
        
        Args:
            agents: List of agents to export (optional)
            include_system_prompts: Include system prompts
            include_model_configs: Include model configurations
            include_agent_definitions: Include agent definitions
            
        Returns:
            Export result with artifact IDs and metadata
        """
        export_timestamp = datetime.utcnow()
        
        logger.info("Starting OpenAI asset export...")
        
        # Collect all assets
        export_data = {
            "export_metadata": {
                "exported_at": export_timestamp.isoformat(),
                "source_platform": "openai",
                "exporter_version": "1.0.0",
                "compliance": ["ZPDL_v1.0", "PDPA"],
                "format_version": "zynx_openai_export_v1"
            },
            "system_prompts": {},
            "model_configurations": {},
            "agent_definitions": {},
            "platform_settings": {}
        }
        
        # Export system prompts
        if include_system_prompts:
            export_data["system_prompts"] = await self._export_system_prompts(agents)
            
        # Export model configurations
        if include_model_configs:
            export_data["model_configurations"] = await self._export_model_configs()
            
        # Export agent definitions
        if include_agent_definitions and agents:
            export_data["agent_definitions"] = await self._export_agent_definitions(agents)
            
        # Export platform settings
        export_data["platform_settings"] = await self._export_platform_settings()
        
        # Store as artifact
        export_json = json.dumps(export_data, ensure_ascii=False, indent=2).encode()
        artifact_info = await self.artifacts.store_artifact(
            "openai_assets_export",
            export_json,
            {
                "export_type": "openai_complete_export",
                "exported_at": export_timestamp.isoformat(),
                "content_type": "application/json",
                "tags": ["openai", "export", "backup", "prompts", "configs", "agents"]
            }
        )
        
        logger.info(f"OpenAI assets exported successfully: {artifact_info['artifact_id']}")
        
        return {
            "export_success": True,
            "artifact_id": artifact_info["artifact_id"],
            "artifact_hash": artifact_info["hash"],
            "export_size": artifact_info["size"],
            "exported_at": export_timestamp.isoformat(),
            "summary": {
                "system_prompts_count": len(export_data["system_prompts"]),
                "model_configs_count": len(export_data["model_configurations"]),
                "agent_definitions_count": len(export_data["agent_definitions"]),
                "platform_settings_exported": True
            }
        }
    
    async def _export_system_prompts(self, agents: Optional[List[ZynxAgent]] = None) -> Dict[str, Any]:
        """Export system prompts from agents and configurations"""
        prompts = {}
        
        # Export prompts from agents if provided
        if agents:
            for agent in agents:
                agent_prompts = await self._extract_agent_prompts(agent)
                if agent_prompts:
                    prompts[agent.agent_id] = agent_prompts
        
        # Add common system prompts
        prompts["common"] = {
            "cultural_awareness_prompt": {
                "content": "You are a culturally aware AI assistant. Respond appropriately while considering cultural context.",
                "language_support": ["en", "th"],
                "purpose": "Base cultural awareness prompt for all agents",
                "version": "1.0.0"
            },
            "thai_cultural_prompt": {
                "content": "คุณเป็นผู้ช่วย AI ที่เข้าใจวัฒนธรรมไทย ตอบสนองอย่างเหมาะสมโดยคำนึงถึงบริบททางวัฒนธรรม",
                "language_support": ["th"],
                "purpose": "Thai cultural awareness prompt",
                "cultural_elements": ["kreng_jai", "sanuk", "mai_pen_rai"],
                "version": "1.0.0"
            },
            "empathy_first_prompt": {
                "content": "Approach every interaction with empathy and understanding. Consider the emotional context and respond with care.",
                "purpose": "Empathy-first philosophy prompt",
                "emotional_intelligence": True,
                "version": "1.0.0"
            }
        }
        
        return prompts
    
    async def _extract_agent_prompts(self, agent: ZynxAgent) -> Dict[str, Any]:
        """Extract prompts from an agent's configuration"""
        prompts = {}
        
        # Check if agent has custom prompts in config
        if hasattr(agent, 'config') and agent.config:
            if 'system_prompt' in agent.config:
                prompts["system_prompt"] = {
                    "content": agent.config['system_prompt'],
                    "agent_id": agent.agent_id,
                    "extracted_at": datetime.utcnow().isoformat()
                }
            
            if 'cultural_prompts' in agent.config:
                prompts["cultural_prompts"] = agent.config['cultural_prompts']
        
        # Extract capability-specific prompts
        for capability in agent.capabilities:
            prompt_key = f"{capability.value}_prompt"
            if hasattr(agent, prompt_key):
                prompts[prompt_key] = {
                    "content": getattr(agent, prompt_key),
                    "capability": capability.value,
                    "agent_id": agent.agent_id
                }
        
        return prompts
    
    async def _export_model_configs(self) -> Dict[str, Any]:
        """Export OpenAI model configurations"""
        configs = {}
        
        # Export default OpenAI configuration from settings
        configs["default_openai_config"] = {
            "model": getattr(settings, 'OPENAI_MODEL', 'gpt-4'),
            "temperature": getattr(settings, 'OPENAI_TEMPERATURE', 0.7),
            "max_tokens": getattr(settings, 'OPENAI_MAX_TOKENS', 1000),
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "configuration_type": "default",
            "purpose": "Default OpenAI API configuration",
            "version": "1.0.0"
        }
        
        # Add cultural context configurations
        configs["cultural_config"] = {
            "model": getattr(settings, 'OPENAI_MODEL', 'gpt-4'),
            "temperature": 0.8,
            "max_tokens": 1500,
            "top_p": 0.95,
            "configuration_type": "cultural_aware",
            "purpose": "Configuration for culturally aware responses",
            "cultural_weight": getattr(settings, 'THAI_CULTURAL_WEIGHT', 0.8),
            "version": "1.0.0"
        }
        
        # Add empathy-optimized configuration
        configs["empathy_config"] = {
            "model": getattr(settings, 'OPENAI_MODEL', 'gpt-4'),
            "temperature": 0.9,
            "max_tokens": 2000,
            "top_p": 0.9,
            "configuration_type": "empathy_optimized",
            "purpose": "Configuration optimized for empathetic responses",
            "empathy_threshold": 0.7,
            "version": "1.0.0"
        }
        
        return configs
    
    async def _export_agent_definitions(self, agents: List[ZynxAgent]) -> Dict[str, Any]:
        """Export agent definitions with their configurations"""
        definitions = {}
        
        for agent in agents:
            definition = {
                "agent_id": agent.agent_id,
                "agent_type": type(agent).__name__,
                "capabilities": [cap.value for cap in agent.capabilities],
                "active": agent.active,
                "configuration": agent.config if hasattr(agent, 'config') else {},
                "metrics": agent.get_metrics(),
                "exported_at": datetime.utcnow().isoformat()
            }
            
            # Add agent-specific metadata
            if hasattr(agent, 'empathy_model'):
                definition["empathy_model"] = agent.empathy_model
            
            if hasattr(agent, 'cultural_contexts'):
                definition["cultural_contexts"] = agent.cultural_contexts
            
            if hasattr(agent, 'ethical_framework'):
                definition["ethical_framework"] = {
                    "principles": agent.ethical_framework.get("principles", []),
                    "thai_values": agent.ethical_framework.get("thai_values", [])
                }
            
            definitions[agent.agent_id] = definition
        
        return definitions
    
    async def _export_platform_settings(self) -> Dict[str, Any]:
        """Export platform-level OpenAI settings"""
        return {
            "api_configuration": {
                "has_api_key": bool(settings.OPENAI_API_KEY),
                "default_model": getattr(settings, 'OPENAI_MODEL', 'gpt-4'),
                "cultural_intelligence_enabled": True,
                "thai_cultural_weight": getattr(settings, 'THAI_CULTURAL_WEIGHT', 0.8),
                "cultural_threshold": getattr(settings, 'DEFAULT_CULTURAL_THRESHOLD', 0.7)
            },
            "compliance": {
                "zpdl_version": "1.0.0",
                "pdpa_compliant": True,
                "data_privacy": "enabled"
            },
            "application": {
                "app_name": settings.APP_NAME,
                "app_version": settings.APP_VERSION,
                "cultural_intelligence_model": getattr(settings, 'CULTURAL_INTELLIGENCE_MODEL', 'deeja-v1')
            }
        }
    
    async def export_prompts_only(self, agents: Optional[List[ZynxAgent]] = None) -> Dict[str, Any]:
        """Export only system prompts"""
        export_timestamp = datetime.utcnow()
        
        export_data = {
            "export_metadata": {
                "exported_at": export_timestamp.isoformat(),
                "export_type": "prompts_only",
                "source_platform": "openai",
                "version": "1.0.0"
            },
            "system_prompts": await self._export_system_prompts(agents)
        }
        
        export_json = json.dumps(export_data, ensure_ascii=False, indent=2).encode()
        artifact_info = await self.artifacts.store_artifact(
            "openai_prompts_export",
            export_json,
            {
                "export_type": "prompts_only",
                "exported_at": export_timestamp.isoformat(),
                "content_type": "application/json",
                "tags": ["openai", "prompts", "export"]
            }
        )
        
        return {
            "export_success": True,
            "artifact_id": artifact_info["artifact_id"],
            "exported_at": export_timestamp.isoformat(),
            "prompts_count": len(export_data["system_prompts"])
        }
    
    async def export_configs_only(self) -> Dict[str, Any]:
        """Export only model configurations"""
        export_timestamp = datetime.utcnow()
        
        export_data = {
            "export_metadata": {
                "exported_at": export_timestamp.isoformat(),
                "export_type": "configs_only",
                "source_platform": "openai",
                "version": "1.0.0"
            },
            "model_configurations": await self._export_model_configs()
        }
        
        export_json = json.dumps(export_data, ensure_ascii=False, indent=2).encode()
        artifact_info = await self.artifacts.store_artifact(
            "openai_configs_export",
            export_json,
            {
                "export_type": "configs_only",
                "exported_at": export_timestamp.isoformat(),
                "content_type": "application/json",
                "tags": ["openai", "configs", "export"]
            }
        )
        
        return {
            "export_success": True,
            "artifact_id": artifact_info["artifact_id"],
            "exported_at": export_timestamp.isoformat(),
            "configs_count": len(export_data["model_configurations"])
        }
    
    async def export_agents_only(self, agents: List[ZynxAgent]) -> Dict[str, Any]:
        """Export only agent definitions"""
        export_timestamp = datetime.utcnow()
        
        export_data = {
            "export_metadata": {
                "exported_at": export_timestamp.isoformat(),
                "export_type": "agents_only",
                "source_platform": "openai",
                "version": "1.0.0"
            },
            "agent_definitions": await self._export_agent_definitions(agents)
        }
        
        export_json = json.dumps(export_data, ensure_ascii=False, indent=2).encode()
        artifact_info = await self.artifacts.store_artifact(
            "openai_agents_export",
            export_json,
            {
                "export_type": "agents_only",
                "exported_at": export_timestamp.isoformat(),
                "content_type": "application/json",
                "tags": ["openai", "agents", "export"]
            }
        )
        
        return {
            "export_success": True,
            "artifact_id": artifact_info["artifact_id"],
            "exported_at": export_timestamp.isoformat(),
            "agents_count": len(export_data["agent_definitions"])
        }
    
    async def import_assets(self, artifact_id: str) -> Dict[str, Any]:
        """Import OpenAI assets from a stored artifact"""
        artifact = await self.artifacts.retrieve_artifact(artifact_id)
        if not artifact:
            raise ValueError(f"Export artifact {artifact_id} not found")
        
        try:
            import_data = json.loads(artifact["content"].decode())
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in export artifact: {e}")
        
        # Validate format
        if import_data.get("export_metadata", {}).get("format_version") != "zynx_openai_export_v1":
            logger.warning("Import format version mismatch - attempting to import anyway")
        
        return {
            "import_success": True,
            "imported_data": import_data,
            "imported_at": datetime.utcnow().isoformat(),
            "original_export_date": import_data["export_metadata"]["exported_at"],
            "summary": {
                "prompts_imported": len(import_data.get("system_prompts", {})),
                "configs_imported": len(import_data.get("model_configurations", {})),
                "agents_imported": len(import_data.get("agent_definitions", {}))
            }
        }
