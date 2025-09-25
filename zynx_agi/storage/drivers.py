"""
Storage drivers for different deployment scenarios
Supports local, cloud, and hybrid storage configurations
"""

import hashlib
import json
import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import asyncio
import aiofiles
from cryptography.fernet import Fernet


class StorageDriver(ABC):
    """Abstract base class for storage drivers"""
    
    def __init__(self, base_path: str, encryption_key: Optional[str] = None):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.fernet = Fernet(encryption_key.encode()) if encryption_key else None
    
    @abstractmethod
    async def store_artifact(self, artifact_id: str, data: bytes, metadata: Dict[str, Any]) -> str:
        """Store an artifact and return its hash"""
        pass
    
    @abstractmethod
    async def retrieve_artifact(self, artifact_id: str) -> Optional[bytes]:
        """Retrieve an artifact by ID"""
        pass
    
    @abstractmethod
    async def store_log(self, log_entry: Dict[str, Any]) -> str:
        """Store a log entry"""
        pass
    
    @abstractmethod
    async def get_logs(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Retrieve logs within time range"""
        pass
    
    def _generate_hash(self, data: bytes) -> str:
        """Generate SHA-256 hash for data integrity"""
        return hashlib.sha256(data).hexdigest()
    
    def _encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data if encryption is enabled"""
        if self.fernet:
            return self.fernet.encrypt(data)
        return data
    
    def _decrypt_data(self, data: bytes) -> bytes:
        """Decrypt data if encryption is enabled"""
        if self.fernet:
            return self.fernet.decrypt(data)
        return data


class LocalStorageDriver(StorageDriver):
    """Local filesystem storage driver with ZPDL compliance"""
    
    def __init__(self, base_path: str = "./storage", encryption_key: Optional[str] = None):
        super().__init__(base_path, encryption_key)
        self.artifacts_path = self.base_path / "artifacts"
        self.logs_path = self.base_path / "logs"
        self.metadata_path = self.base_path / "metadata"
        
        # Create subdirectories
        for path in [self.artifacts_path, self.logs_path, self.metadata_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    async def store_artifact(self, artifact_id: str, data: bytes, metadata: Dict[str, Any]) -> str:
        """Store artifact with SHA-256 hash validation"""
        # Generate hash for integrity
        data_hash = self._generate_hash(data)
        
        # Encrypt data if enabled
        encrypted_data = self._encrypt_data(data)
        
        # Store artifact
        artifact_path = self.artifacts_path / f"{artifact_id}.bin"
        async with aiofiles.open(artifact_path, 'wb') as f:
            await f.write(encrypted_data)
        
        # Store metadata with hash
        metadata_with_hash = {
            **metadata,
            "hash": data_hash,
            "stored_at": datetime.utcnow().isoformat(),
            "encrypted": self.fernet is not None,
            "size": len(data),
            "artifact_id": artifact_id
        }
        
        metadata_path = self.metadata_path / f"{artifact_id}.json"
        async with aiofiles.open(metadata_path, 'w') as f:
            await f.write(json.dumps(metadata_with_hash, indent=2))
        
        return data_hash
    
    async def retrieve_artifact(self, artifact_id: str) -> Optional[bytes]:
        """Retrieve artifact with hash validation"""
        artifact_path = self.artifacts_path / f"{artifact_id}.bin"
        metadata_path = self.metadata_path / f"{artifact_id}.json"
        
        if not artifact_path.exists() or not metadata_path.exists():
            return None
        
        # Load metadata
        async with aiofiles.open(metadata_path, 'r') as f:
            metadata = json.loads(await f.read())
        
        # Load artifact
        async with aiofiles.open(artifact_path, 'rb') as f:
            encrypted_data = await f.read()
        
        # Decrypt if needed
        data = self._decrypt_data(encrypted_data)
        
        # Validate hash
        current_hash = self._generate_hash(data)
        if current_hash != metadata.get("hash"):
            raise ValueError(f"Hash mismatch for artifact {artifact_id}")
        
        return data
    
    async def store_log(self, log_entry: Dict[str, Any]) -> str:
        """Store log entry with timestamp and hash"""
        timestamp = datetime.utcnow()
        log_entry["timestamp"] = timestamp.isoformat()
        log_entry["log_id"] = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"
        
        # Convert to JSON and hash
        log_data = json.dumps(log_entry, ensure_ascii=False, indent=2).encode()
        log_hash = self._generate_hash(log_data)
        log_entry["hash"] = log_hash
        
        # Store in daily log file
        log_file = self.logs_path / f"{timestamp.strftime('%Y-%m-%d')}.jsonl"
        async with aiofiles.open(log_file, 'a', encoding='utf-8') as f:
            await f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        return log_hash
    
    async def get_logs(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Retrieve logs within time range"""
        logs = []
        current_date = start_time.date()
        
        while current_date <= end_time.date():
            log_file = self.logs_path / f"{current_date.strftime('%Y-%m-%d')}.jsonl"
            
            if log_file.exists():
                async with aiofiles.open(log_file, 'r', encoding='utf-8') as f:
                    async for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            log_entry = json.loads(line)
                            entry_time = datetime.fromisoformat(log_entry["timestamp"])
                            
                            if start_time <= entry_time <= end_time:
                                logs.append(log_entry)
                        except (json.JSONDecodeError, KeyError, ValueError):
                            continue
            
            # Move to next day
            current_date = current_date + timedelta(days=1)
        
        return sorted(logs, key=lambda x: x["timestamp"])


class CloudStorageDriver(StorageDriver):
    """Cloud storage driver for scalable deployment"""
    
    def __init__(self, base_path: str, cloud_config: Dict[str, Any], encryption_key: Optional[str] = None):
        super().__init__(base_path, encryption_key)
        self.cloud_config = cloud_config
        # TODO: Implement specific cloud provider integration (AWS S3, GCP, Azure)
    
    async def store_artifact(self, artifact_id: str, data: bytes, metadata: Dict[str, Any]) -> str:
        """Store artifact in cloud storage"""
        # For now, fallback to local storage
        # TODO: Implement cloud-specific storage logic
        local_driver = LocalStorageDriver(str(self.base_path), 
                                         self.fernet.key.decode() if self.fernet else None)
        return await local_driver.store_artifact(artifact_id, data, metadata)
    
    async def retrieve_artifact(self, artifact_id: str) -> Optional[bytes]:
        """Retrieve artifact from cloud storage"""
        # For now, fallback to local storage
        # TODO: Implement cloud-specific retrieval logic
        local_driver = LocalStorageDriver(str(self.base_path),
                                         self.fernet.key.decode() if self.fernet else None)
        return await local_driver.retrieve_artifact(artifact_id)
    
    async def store_log(self, log_entry: Dict[str, Any]) -> str:
        """Store log in cloud storage"""
        # For now, fallback to local storage
        # TODO: Implement cloud-specific logging
        local_driver = LocalStorageDriver(str(self.base_path),
                                         self.fernet.key.decode() if self.fernet else None)
        return await local_driver.store_log(log_entry)
    
    async def get_logs(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Retrieve logs from cloud storage"""
        # For now, fallback to local storage
        # TODO: Implement cloud-specific log retrieval
        local_driver = LocalStorageDriver(str(self.base_path),
                                         self.fernet.key.decode() if self.fernet else None)
        return await local_driver.get_logs(start_time, end_time)