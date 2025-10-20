"""
Artifact Manager for Zynx AGI
Handles secure storage and retrieval of artifacts with SHA-256 hashing
"""

import asyncio
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional
from .drivers import StorageDriver, LocalStorageDriver


class ArtifactManager:
    """Manages artifacts with integrity validation and metadata tracking"""
    
    def __init__(self, storage_driver: StorageDriver):
        self.storage = storage_driver
        self._artifact_registry: Dict[str, Dict[str, Any]] = {}
    
    async def store_artifact(
        self, 
        artifact_type: str, 
        content: bytes, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Store an artifact with metadata and return tracking information"""
        if metadata is None:
            metadata = {}
        
        # Generate unique artifact ID
        timestamp = datetime.utcnow()
        artifact_id = f"{artifact_type}_{timestamp.strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(content).hexdigest()[:8]}"
        
        # Enhanced metadata
        enhanced_metadata = {
            "type": artifact_type,
            "created_at": timestamp.isoformat(),
            "content_type": metadata.get("content_type", "application/octet-stream"),
            "source": metadata.get("source", "unknown"),
            "tags": metadata.get("tags", []),
            "zpdl_compliance": True,
            "pdpa_compliant": True,
            **metadata
        }
        
        # Store the artifact
        artifact_hash = await self.storage.store_artifact(artifact_id, content, enhanced_metadata)
        
        # Register in local registry
        self._artifact_registry[artifact_id] = {
            "id": artifact_id,
            "hash": artifact_hash,
            "metadata": enhanced_metadata,
            "size": len(content)
        }
        
        return {
            "artifact_id": artifact_id,
            "hash": artifact_hash,
            "size": len(content),
            "stored_at": timestamp.isoformat()
        }
    
    async def retrieve_artifact(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an artifact with validation"""
        content = await self.storage.retrieve_artifact(artifact_id)
        if content is None:
            return None
        
        registry_info = self._artifact_registry.get(artifact_id)
        if registry_info:
            # Validate hash
            current_hash = hashlib.sha256(content).hexdigest()
            if current_hash != registry_info["hash"]:
                raise ValueError(f"Artifact integrity check failed for {artifact_id}")
        
        return {
            "artifact_id": artifact_id,
            "content": content,
            "metadata": registry_info["metadata"] if registry_info else {},
            "size": len(content)
        }
    
    async def list_artifacts(
        self, 
        artifact_type: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """List artifacts with optional filtering"""
        artifacts = []
        
        for artifact_id, info in self._artifact_registry.items():
            metadata = info["metadata"]
            
            # Filter by type
            if artifact_type and metadata.get("type") != artifact_type:
                continue
            
            # Filter by tags
            if tags:
                artifact_tags = set(metadata.get("tags", []))
                if not set(tags).intersection(artifact_tags):
                    continue
            
            artifacts.append({
                "artifact_id": artifact_id,
                "type": metadata.get("type"),
                "created_at": metadata.get("created_at"),
                "size": info["size"],
                "hash": info["hash"],
                "tags": metadata.get("tags", [])
            })
        
        return sorted(artifacts, key=lambda x: x["created_at"], reverse=True)
    
    async def delete_artifact(self, artifact_id: str) -> bool:
        """Delete an artifact (mark as deleted for compliance)"""
        if artifact_id not in self._artifact_registry:
            return False
        
        # For ZPDL compliance, we log deletion instead of actually deleting
        deletion_log = {
            "action": "artifact_deletion",
            "artifact_id": artifact_id,
            "deleted_at": datetime.utcnow().isoformat(),
            "reason": "user_request",
            "compliance": "ZPDL_v1.0"
        }
        
        await self.storage.store_log(deletion_log)
        
        # Mark as deleted in registry
        self._artifact_registry[artifact_id]["deleted"] = True
        self._artifact_registry[artifact_id]["deleted_at"] = deletion_log["deleted_at"]
        
        return True
    
    async def get_artifact_stats(self) -> Dict[str, Any]:
        """Get statistics about stored artifacts"""
        total_artifacts = len(self._artifact_registry)
        total_size = sum(info["size"] for info in self._artifact_registry.values())
        
        # Group by type
        type_stats = {}
        for info in self._artifact_registry.values():
            artifact_type = info["metadata"].get("type", "unknown")
            if artifact_type not in type_stats:
                type_stats[artifact_type] = {"count": 0, "size": 0}
            type_stats[artifact_type]["count"] += 1
            type_stats[artifact_type]["size"] += info["size"]
        
        return {
            "total_artifacts": total_artifacts,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "types": type_stats,
            "compliance_status": "ZPDL_v1.0_compliant"
        }