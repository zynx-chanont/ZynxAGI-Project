"""
Zynx Storage Configuration
SSD + Remote WORM Bucket Storage System
Author: Chanont Wankaew
© 2025 Zynx Thailand. All rights reserved.
"""

import hashlib
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field
import aiofiles
import asyncio

logger = logging.getLogger(__name__)

class StorageConfig(BaseModel):
    """Storage configuration model"""
    ssd_path: str = Field(default="./data/storage/ssd")
    worm_bucket_path: str = Field(default="./data/storage/worm")
    temp_path: str = Field(default="./tmp/zynx_temp")
    max_file_size_mb: int = Field(default=100)
    retention_days: int = Field(default=2555)  # 7 years for IP protection
    encryption_enabled: bool = Field(default=True)

class WORMEntry(BaseModel):
    """Write-Once-Read-Many entry model"""
    entry_id: str
    original_hash: str
    storage_path: str
    created_at: datetime
    author: str = Field(default="Chanont Wankaew")
    immutable: bool = Field(default=True)
    zpdl_compliant: bool = Field(default=True)

class ZynxStorage(BaseModel):
    """
    Zynx Storage System
    SSD for active data + WORM bucket for defensive publications
    """
    
    config: StorageConfig = Field(default_factory=StorageConfig)
    author: str = Field(default="Chanont Wankaew")
    copyright: str = Field(default="© 2025 Zynx Thailand. All rights reserved.")
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Internal tracking
    worm_registry: Dict[str, WORMEntry] = Field(default_factory=dict)
    
    class Config:
        extra = "forbid"
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        super().__init__(**data)
        self._ensure_storage_directories()
        logger.info(f"ZynxStorage initialized - {self.author}")
    
    def _ensure_storage_directories(self):
        """Ensure all storage directories exist"""
        directories = [
            self.config.ssd_path,
            self.config.worm_bucket_path,
            self.config.temp_path
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.info(f"Storage directory ensured: {directory}")
    
    async def store_ssd(
        self,
        data: Union[str, bytes, Dict[str, Any]],
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store data on SSD for active access"""
        
        # Convert data to bytes if needed
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        elif isinstance(data, dict):
            data_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
        else:
            data_bytes = data
        
        # Generate hash for integrity
        data_hash = hashlib.sha256(data_bytes).hexdigest()
        
        # Create storage path
        storage_path = Path(self.config.ssd_path) / filename
        
        # Store data
        async with aiofiles.open(storage_path, 'wb') as f:
            await f.write(data_bytes)
        
        # Store metadata if provided
        if metadata:
            metadata_path = storage_path.with_suffix('.meta.json')
            metadata_with_hash = {
                **metadata,
                "data_hash": data_hash,
                "stored_at": datetime.now().isoformat(),
                "author": self.author,
                "storage_type": "ssd"
            }
            
            async with aiofiles.open(metadata_path, 'w') as f:
                await f.write(json.dumps(metadata_with_hash, ensure_ascii=False, indent=2))
        
        logger.info(f"Data stored to SSD: {storage_path} (hash: {data_hash[:16]}...)")
        return data_hash
    
    async def store_worm(
        self,
        data: Union[str, bytes, Dict[str, Any]],
        entry_id: str,
        defensive_publication: bool = True
    ) -> WORMEntry:
        """Store data in WORM bucket for immutable storage"""
        
        # Convert data to bytes if needed
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        elif isinstance(data, dict):
            data_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
        else:
            data_bytes = data
        
        # Generate hash for integrity
        original_hash = hashlib.sha256(data_bytes).hexdigest()
        
        # Check if already exists (WORM principle)
        if entry_id in self.worm_registry:
            raise ValueError(f"WORM entry {entry_id} already exists - cannot overwrite")
        
        # Create WORM storage path with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        worm_filename = f"{entry_id}_{timestamp}_{original_hash[:16]}.worm"
        storage_path = Path(self.config.worm_bucket_path) / worm_filename
        
        # Store data (write-once)
        async with aiofiles.open(storage_path, 'wb') as f:
            await f.write(data_bytes)
        
        # Make file read-only (simulate WORM)
        os.chmod(storage_path, 0o444)
        
        # Create WORM entry
        worm_entry = WORMEntry(
            entry_id=entry_id,
            original_hash=original_hash,
            storage_path=str(storage_path),
            created_at=datetime.now(),
            author=self.author
        )
        
        # Register entry
        self.worm_registry[entry_id] = worm_entry
        
        # Store registry
        await self._save_worm_registry()
        
        if defensive_publication:
            await self._create_defensive_publication_record(worm_entry)
        
        logger.info(f"Data stored to WORM: {storage_path} (entry: {entry_id})")
        return worm_entry
    
    async def _save_worm_registry(self):
        """Save WORM registry to persistent storage"""
        registry_path = Path(self.config.worm_bucket_path) / "worm_registry.json"
        
        # Convert registry to serializable format
        registry_data = {
            "registry": {
                entry_id: {
                    "entry_id": entry.entry_id,
                    "original_hash": entry.original_hash,
                    "storage_path": entry.storage_path,
                    "created_at": entry.created_at.isoformat(),
                    "author": entry.author,
                    "immutable": entry.immutable,
                    "zpdl_compliant": entry.zpdl_compliant
                }
                for entry_id, entry in self.worm_registry.items()
            },
            "last_updated": datetime.now().isoformat(),
            "author": self.author
        }
        
        async with aiofiles.open(registry_path, 'w') as f:
            await f.write(json.dumps(registry_data, ensure_ascii=False, indent=2))
    
    async def _create_defensive_publication_record(self, worm_entry: WORMEntry):
        """Create defensive publication record for IP protection"""
        publication_record = {
            "type": "defensive_publication",
            "entry_id": worm_entry.entry_id,
            "content_hash": worm_entry.original_hash,
            "storage_path": worm_entry.storage_path,
            "author": self.author,
            "copyright": self.copyright,
            "publication_timestamp": datetime.now().isoformat(),
            "worm_compliant": True,
            "zpdl_version": "1.0",
            "immutable_proof": hashlib.sha256(
                f"{worm_entry.entry_id}{worm_entry.original_hash}{self.author}".encode()
            ).hexdigest()
        }
        
        # Store publication record in WORM
        publication_id = f"pub_{worm_entry.entry_id}"
        await self.store_worm(
            publication_record,
            publication_id,
            defensive_publication=False  # Avoid recursion
        )
        
        logger.info(f"Defensive publication created: {publication_id}")
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage system statistics"""
        ssd_path = Path(self.config.ssd_path)
        worm_path = Path(self.config.worm_bucket_path)
        
        # Calculate directory sizes (simplified)
        ssd_files = list(ssd_path.glob("*")) if ssd_path.exists() else []
        worm_files = list(worm_path.glob("*.worm")) if worm_path.exists() else []
        
        return {
            "ssd_storage": {
                "path": str(ssd_path),
                "file_count": len(ssd_files),
                "active": True
            },
            "worm_storage": {
                "path": str(worm_path),
                "entry_count": len(self.worm_registry),
                "file_count": len(worm_files),
                "immutable": True
            },
            "system_info": {
                "author": self.author,
                "copyright": self.copyright,
                "uptime": (datetime.now() - self.created_at).total_seconds()
            },
            "timestamp": datetime.now().isoformat()
        }