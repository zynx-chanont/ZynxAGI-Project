"""
Zynx-Metadata Module - Main Agent Implementation
===============================================

Self-contained module for autonomous IP tracking and attribution management.
"""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pytz

from .config import ZynxMetadataConfig
from .models import (
    ZynxMetadataRecord,
    MetadataObservation,
    IntentDetector,
    DefensivePublication
)


logger = logging.getLogger(__name__)


class ZynxMetadataModule:
    """
    Zynx-Metadata - Autonomous IP Tracking & Observer Module
    
    A self-contained, independently usable module for:
    - Intent detection (discover, invent, develop, create)
    - Automatic attribution and metadata generation
    - Multi-format logging (JSON, Markdown, PDF)
    - SHA-256 hashing and verification
    - Defensive publication generation
    
    Example:
        >>> metadata = ZynxMetadataModule(storage_path="./logs")
        >>> await metadata.initialize()
        >>> result = await metadata.observe_interaction(
        ...     agent_name="deeja",
        ...     user_input="I discovered a new pattern",
        ...     agent_response="That's interesting!"
        ... )
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, storage_path: Optional[Path] = None):
        """
        Initialize Zynx-Metadata module
        
        Args:
            config: Optional configuration dictionary or ZynxMetadataConfig instance
            storage_path: Optional override for storage path
        """
        if isinstance(config, ZynxMetadataConfig):
            self.config = config
        else:
            cfg = config or {}
            if storage_path:
                cfg["storage_path"] = storage_path
            self.config = ZynxMetadataConfig(**cfg)
        
        self.module_id = self.config.module_id
        self.storage_path = Path(self.config.storage_path)
        self.active = False
        self.active_sessions = {}
        self.intent_detector = IntentDetector()
        
        # Setup logging
        self.logger = logging.getLogger(f"{__name__}.{self.module_id}")
        self.logger.setLevel(getattr(logging, self.config.log_level))
    
    async def initialize(self) -> None:
        """Initialize the Zynx-Metadata module"""
        self.logger.info(f"Initializing Zynx-Metadata module: {self.module_id}")
        
        # Create storage directory structure
        await self._init_storage()
        
        self.active = True
        self.logger.info("Zynx-Metadata module initialization complete - IP tracking active")
    
    async def _init_storage(self) -> None:
        """Initialize storage directory structure"""
        self.storage_path.mkdir(exist_ok=True)
        
        if self.config.generate_json:
            (self.storage_path / "json").mkdir(exist_ok=True)
        
        if self.config.generate_markdown:
            (self.storage_path / "markdown").mkdir(exist_ok=True)
        
        if self.config.generate_pdf:
            (self.storage_path / "pdf").mkdir(exist_ok=True)
        
        if self.config.generate_hash_manifest:
            (self.storage_path / "hash_manifests").mkdir(exist_ok=True)
        
        if self.config.auto_generate_defensive_publications:
            (self.storage_path / "defensive_publications").mkdir(exist_ok=True)
        
        self.logger.info(f"Storage initialized at: {self.storage_path}")
    
    def _generate_sha256(self, content: str) -> str:
        """Generate SHA-256 hash for content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    async def observe_interaction(
        self,
        agent_name: str,
        user_input: str,
        agent_response: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> MetadataObservation:
        """
        Observe and analyze agent interactions for IP tracking
        
        Args:
            agent_name: Name of the agent
            user_input: User's input message
            agent_response: Agent's response
            additional_context: Optional additional context
            
        Returns:
            MetadataObservation with tracking results
        """
        if not self.active:
            await self.initialize()
        
        # Detect intent in the interaction
        intent = None
        if self.config.auto_detect_intent:
            intent = self.intent_detector.detect_intent(user_input + " " + agent_response)
        
        if not intent:
            # No intent detected, no tracking needed
            return MetadataObservation(
                tracked=False,
                intent_detected=None
            )
        
        # Create metadata record
        metadata = ZynxMetadataRecord(
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
        storage_paths = await self._store_metadata(metadata, interaction_content)
        
        # Track active session
        self.active_sessions[metadata.uuid] = metadata
        
        self.logger.info(
            f"IP tracking: {intent} detected in {agent_name} interaction - UUID: {metadata.uuid}"
        )
        
        return MetadataObservation(
            tracked=True,
            metadata=metadata,
            intent_detected=intent,
            storage_paths=storage_paths
        )
    
    async def _store_metadata(
        self,
        metadata: ZynxMetadataRecord,
        content: Dict[str, Any]
    ) -> Dict[str, str]:
        """Store metadata in multiple formats"""
        timestamp = datetime.now(pytz.timezone(self.config.timezone)).strftime('%Y%m%d_%H%M%S')
        base_filename = f"zynx_{metadata.intent_detected}_{timestamp}_{metadata.uuid[:8]}"
        
        storage_paths = {}
        
        # Store as JSON
        if self.config.generate_json:
            json_path = self.storage_path / "json" / f"{base_filename}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            storage_paths["json"] = str(json_path)
        
        # Store as Markdown
        if self.config.generate_markdown:
            md_path = self.storage_path / "markdown" / f"{base_filename}.md"
            await self._generate_markdown(metadata, content, md_path)
            storage_paths["markdown"] = str(md_path)
        
        # Store hash manifest
        if self.config.generate_hash_manifest:
            hash_path = self.storage_path / "hash_manifests" / f"{base_filename}_manifest.json"
            manifest = {
                "uuid": metadata.uuid,
                "sha256": metadata.sha256,
                "created_at": metadata.created_at,
                "ip_notice": metadata.ip_notice,
                "license": metadata.license,
                "files": storage_paths.copy()
            }
            with open(hash_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            storage_paths["manifest"] = str(hash_path)
        
        return storage_paths
    
    async def _generate_markdown(
        self,
        metadata: ZynxMetadataRecord,
        content: Dict[str, Any],
        output_path: Path
    ) -> None:
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
    
    async def generate_defensive_publication(self, session_uuid: str) -> Optional[str]:
        """Generate a defensive publication for legal IP protection"""
        metadata = self.active_sessions.get(session_uuid)
        if not metadata:
            return None
        
        publication = DefensivePublication(
            title=f"Zynx AGI Discovery - {metadata.intent_detected.title()}",
            disclosure_date=metadata.created_at,
            uuid=metadata.uuid,
            sha256_proof=metadata.sha256,
            license=metadata.license,
            claim=f"Method and system for {metadata.intent_detected} detection and tracking in AI agent interactions",
            description="Autonomous intellectual property tracking system for AI agent ecosystems"
        )
        
        pub_path = self.storage_path / "defensive_publications" / f"publication_{session_uuid[:8]}.json"
        pub_path.parent.mkdir(exist_ok=True)
        
        with open(pub_path, 'w', encoding='utf-8') as f:
            json.dump(publication.model_dump(), f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Defensive publication generated: {pub_path}")
        return str(pub_path)
    
    async def get_session_metadata(self, session_uuid: str) -> Optional[ZynxMetadataRecord]:
        """Retrieve metadata for a specific session"""
        return self.active_sessions.get(session_uuid)
    
    async def list_active_sessions(self) -> Dict[str, ZynxMetadataRecord]:
        """List all active tracking sessions"""
        return self.active_sessions.copy()
    
    async def get_status(self) -> Dict[str, Any]:
        """Get module status"""
        return {
            "module_id": self.module_id,
            "active": self.active,
            "storage_path": str(self.storage_path),
            "active_sessions_count": len(self.active_sessions),
            "intent_detection_enabled": self.config.auto_detect_intent,
            "config": self.config.model_dump()
        }
    
    async def shutdown(self) -> None:
        """Shutdown the module"""
        self.logger.info("Shutting down Zynx-Metadata module")
        self.active = False
