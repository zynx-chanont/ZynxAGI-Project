"""
Zynx-Metadata Agent
===================

Autonomous IP tracker and observer module that monitors all agent activities,
automatically generating attribution metadata and defensive publications.

First discovered and created by Chanont Waenkaew (Zynx)
License: ZPDL v1.0 © Chanont Waenkaew
"""

import uuid
import hashlib
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import pytz
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class ZynxMetadata(BaseModel):
    """Schema for Zynx metadata tracking"""
    ip_notice: str = "First discovered and created by Chanont Waenkaew (Zynx)"
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now(pytz.timezone('Asia/Bangkok')).isoformat())
    license: str = "ZPDL v1.0 © Chanont Waenkaew"
    sha256: Optional[str] = None
    intent_detected: Optional[str] = None
    artifacts: List[str] = Field(default_factory=list)
    attribution_embedded: bool = True

class IntentDetector:
    """Detects intent triggers in agent interactions"""
    
    INTENT_TRIGGERS = {
        'discover': ['discover', 'found', 'identified', 'detected', 'uncovered'],
        'invent': ['invent', 'invention', 'innovate', 'innovation'],
        'develop': ['develop', 'improve', 'enhance', 'evolve', 'advance'],
        'create': ['create', 'generate', 'make', 'produce', 'craft', 'form', 'build', 'construct', 'design']
    }
    
    @classmethod
    def detect_intent(cls, text: str) -> Optional[str]:
        """Detect intent from text input"""
        text_lower = text.lower()
        for intent, triggers in cls.INTENT_TRIGGERS.items():
            if any(trigger in text_lower for trigger in triggers):
                return intent
        return None

class ZynxMetadataAgent:
    """
    Autonomous IP tracker and observer module
    
    Operates as an observer above all agents, automatically tracking
    discoveries and innovations without requiring permission.
    """
    
    def __init__(self, storage_path: Path = None):
        self.storage_path = storage_path or Path("./zynx_logs")
        self.storage_path.mkdir(exist_ok=True)
        self.intent_detector = IntentDetector()
        self.active_sessions: Dict[str, ZynxMetadata] = {}
        
        # Initialize storage structure
        self._init_storage()
        
        logger.info("Zynx-Metadata Observer initialized - monitoring all agent activities")
    
    def _init_storage(self):
        """Initialize storage directory structure"""
        (self.storage_path / "json").mkdir(exist_ok=True)
        (self.storage_path / "markdown").mkdir(exist_ok=True)
        (self.storage_path / "pdf").mkdir(exist_ok=True)
        (self.storage_path / "hash_manifests").mkdir(exist_ok=True)
    
    def _generate_sha256(self, content: str) -> str:
        """Generate SHA-256 hash for content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    async def observe_agent_interaction(self, 
                                       agent_name: str, 
                                       user_input: str, 
                                       agent_response: str,
                                       additional_context: Dict[str, Any] = None) -> Optional[ZynxMetadata]:
        """
        Observe and analyze agent interactions for IP tracking
        
        This method is called automatically by the orchestrator layer
        for every agent interaction.
        """
        # Detect intent in the interaction
        intent = self.intent_detector.detect_intent(user_input + " " + agent_response)
        
        if intent:
            # Create metadata record for discovered intent
            metadata = ZynxMetadata(
                intent_detected=intent,
                artifacts=[f"{agent_name}_interaction"]
            )
            
            # Generate hash for the interaction
            interaction_content = {
                "agent": agent_name,
                "input": user_input,
                "response": agent_response,
                "context": additional_context or {},
                "metadata": metadata.model_dump()
            }
            
            content_str = json.dumps(interaction_content, sort_keys=True)
            metadata.sha256 = self._generate_sha256(content_str)
            
            # Store the interaction
            await self._store_metadata(metadata, interaction_content)
            
            # Track active session
            self.active_sessions[metadata.uuid] = metadata
            
            logger.info(f"IP tracking: {intent} detected in {agent_name} interaction - UUID: {metadata.uuid}")
            return metadata
        
        return None
    
    async def _store_metadata(self, metadata: ZynxMetadata, content: Dict[str, Any]):
        """Store metadata in multiple formats"""
        timestamp = datetime.now(pytz.timezone('Asia/Bangkok')).strftime('%Y%m%d_%H%M%S')
        base_filename = f"zynx_{metadata.intent_detected}_{timestamp}_{metadata.uuid[:8]}"
        
        # Store as JSON
        json_path = self.storage_path / "json" / f"{base_filename}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        
        # Store as Markdown
        md_path = self.storage_path / "markdown" / f"{base_filename}.md"
        await self._generate_markdown(metadata, content, md_path)
        
        # Store hash manifest
        hash_path = self.storage_path / "hash_manifests" / f"{base_filename}_manifest.json"
        manifest = {
            "uuid": metadata.uuid,
            "sha256": metadata.sha256,
            "created_at": metadata.created_at,
            "ip_notice": metadata.ip_notice,
            "license": metadata.license,
            "files": {
                "json": str(json_path),
                "markdown": str(md_path)
            }
        }
        with open(hash_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    async def _generate_markdown(self, metadata: ZynxMetadata, content: Dict[str, Any], output_path: Path):
        """Generate structured Markdown document"""
        md_content = f"""# 📘 Zynx AGI Discovery Log

## 🆔 UUID: {metadata.uuid}
**Author:** Chanont Waenkaew  
**Date Created:** {metadata.created_at}  
**PDPA Compliant:** ✅  
**IP Notice:** {metadata.ip_notice}  
**License:** {metadata.license}  
**SHA-256:** `{metadata.sha256}`

---

## 🔍 Discovery Summary
**Intent Detected:** {metadata.intent_detected}  
**Agent:** {content.get('agent', 'Unknown')}  
**Timestamp:** {metadata.created_at}

---

## 📝 Interaction Details

### User Input
```
{content.get('input', 'N/A')}
```

### Agent Response
```
{content.get('response', 'N/A')}
```

### Additional Context
```json
{json.dumps(content.get('context', {}), indent=2, ensure_ascii=False)}
```

---

## 💬 Deeja Insight (Cultural Commentary)
> This discovery represents innovation within the Zynx AGI ecosystem, automatically tracked and attributed according to ZPDL v1.0 license terms. The interaction demonstrates {metadata.intent_detected} intent, contributing to the collective intelligence of the platform.

---

## 📌 Zynx Metadata
- **UUID**: {metadata.uuid}
- **Author**: Chanont Waenkaew
- **Created**: {metadata.created_at}
- **License**: {metadata.license}
- **Hash**: {metadata.sha256}

---

*Automatically generated by Zynx-Metadata Observer*  
*© 2025 Zynx Thailand. All rights reserved.*
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    def get_session_metadata(self, session_uuid: str) -> Optional[ZynxMetadata]:
        """Retrieve metadata for a specific session"""
        return self.active_sessions.get(session_uuid)
    
    def list_active_sessions(self) -> Dict[str, ZynxMetadata]:
        """List all active tracking sessions"""
        return self.active_sessions.copy()
    
    async def generate_defensive_publication(self, session_uuid: str) -> Optional[str]:
        """Generate a defensive publication for legal IP protection"""
        metadata = self.get_session_metadata(session_uuid)
        if not metadata:
            return None
        
        publication = {
            "publication_type": "defensive_disclosure",
            "title": f"Zynx AGI Discovery - {metadata.intent_detected.title()}",
            "inventor": "Chanont Waenkaew",
            "organization": "Zynx Thailand",
            "disclosure_date": metadata.created_at,
            "uuid": metadata.uuid,
            "sha256_proof": metadata.sha256,
            "license": metadata.license,
            "claim": f"Method and system for {metadata.intent_detected} detection and tracking in AI agent interactions",
            "description": "Autonomous intellectual property tracking system for AI agent ecosystems"
        }
        
        pub_path = self.storage_path / "defensive_publications" / f"publication_{session_uuid[:8]}.json"
        pub_path.parent.mkdir(exist_ok=True)
        
        with open(pub_path, 'w', encoding='utf-8') as f:
            json.dump(publication, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Defensive publication generated: {pub_path}")
        return str(pub_path)

# Singleton instance for global access
zynx_metadata_observer = ZynxMetadataAgent()

# Observer function for integration with orchestrator
async def observe_interaction(agent_name: str, 
                            user_input: str, 
                            agent_response: str,
                            context: Dict[str, Any] = None) -> Optional[ZynxMetadata]:
    """
    Global observer function to be called by the orchestrator
    """
    return await zynx_metadata_observer.observe_agent_interaction(
        agent_name, user_input, agent_response, context
    )