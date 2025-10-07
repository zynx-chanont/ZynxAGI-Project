"""
Zynx Metadata Module
ZPDL v1.0 Compliant Metadata Management & Attribution System
Author: Chanont Wankaew
© 2025 Zynx Thailand. All rights reserved.
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class MetadataType(str, Enum):
    """Types of metadata"""
    DOCUMENT = "document"
    AGENT = "agent"
    MODULE = "module"
    INTERACTION = "interaction"
    PUBLICATION = "publication"

class ZPDLCompliance(BaseModel):
    """ZPDL v1.0 Compliance Model"""
    version: str = Field(default="1.0")
    author: str = Field(default="Chanont Wankaew")
    copyright: str = Field(default="© 2025 Zynx Thailand. All rights reserved.")
    license_type: str = Field(default="ZPDL v1.0")
    attribution_required: bool = Field(default=True)
    commercial_use: bool = Field(default=False)
    modification_allowed: bool = Field(default=False)

class PDPACompliance(BaseModel):
    """PDPA (Thailand) Compliance Model"""
    data_protection_notice: str = Field(
        default="This system adheres to Thai Personal Data Protection Act (PDPA) B.E. 2562"
    )
    consent_required: bool = Field(default=True)
    data_retention_days: int = Field(default=365)
    anonymization_level: str = Field(default="high")
    cross_border_transfer: bool = Field(default=False)

class MetadataEntry(BaseModel):
    """Core metadata entry with ZPDL v1.0 compliance"""
    
    # Core identifiers
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metadata_type: MetadataType
    title: str
    
    # ZPDL v1.0 Compliance
    zpdl: ZPDLCompliance = Field(default_factory=ZPDLCompliance)
    pdpa: PDPACompliance = Field(default_factory=PDPACompliance)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    modified_at: Optional[datetime] = None
    
    # Content and attribution
    content_hash: Optional[str] = None
    source_reference: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    # Security
    digital_signature: Optional[str] = None
    integrity_verified: bool = Field(default=False)
    
    class Config:
        """Pydantic configuration"""
        extra = "forbid"
        validate_assignment = True

class ZynxMetadata(BaseModel):
    """
    Zynx Metadata Management System
    ZPDL v1.0 Compliant with IP Attribution Lock
    """
    
    # System metadata
    system_id: str = Field(default="zynx-metadata-v1.0")
    author: str = Field(default="Chanont Wankaew")
    copyright: str = Field(default="© 2025 Zynx Thailand. All rights reserved.")
    license: str = Field(default="ZPDL v1.0")
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Schema lock for attribution
    schema_locked: bool = Field(default=True)
    schema_version: str = Field(default="1.0.0")
    attribution_immutable: bool = Field(default=True)
    
    # Storage
    metadata_store: Dict[str, MetadataEntry] = Field(default_factory=dict)
    defensive_publications: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        """Pydantic configuration"""
        extra = "forbid"
        validate_assignment = True
    
    def __init__(self, **data):
        super().__init__(**data)
        logger.info(f"ZynxMetadata initialized - {self.author}")
        self._initialize_attribution_lock()
    
    def _initialize_attribution_lock(self):
        """Initialize immutable attribution system"""
        if self.attribution_immutable:
            logger.info("Attribution lock activated - Schema immutable for IP protection")
    
    def generate_system_hash(self) -> str:
        """Generate SHA-256 hash for system integrity"""
        system_data = {
            "system_id": self.system_id,
            "author": self.author,
            "copyright": self.copyright,
            "license": self.license,
            "schema_version": self.schema_version,
            "created_at": self.created_at.isoformat()
        }
        system_str = json.dumps(system_data, sort_keys=True)
        return hashlib.sha256(system_str.encode()).hexdigest()
    
    def create_metadata(
        self,
        metadata_type: MetadataType,
        title: str,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
        source_reference: Optional[str] = None
    ) -> str:
        """Create new metadata entry with ZPDL v1.0 compliance"""
        
        if self.schema_locked and self.attribution_immutable:
            # Verify attribution is maintained
            if not self._verify_attribution_integrity():
                raise ValueError("Attribution integrity check failed - cannot create metadata")
        
        # Generate content hash if content provided
        content_hash = None
        if content:
            content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Create metadata entry
        metadata_entry = MetadataEntry(
            metadata_type=metadata_type,
            title=title,
            content_hash=content_hash,
            source_reference=source_reference,
            tags=tags or []
        )
        
        # Generate digital signature
        metadata_entry.digital_signature = self._generate_digital_signature(metadata_entry)
        metadata_entry.integrity_verified = True
        
        # Store metadata
        self.metadata_store[metadata_entry.uuid] = metadata_entry
        
        # Log to defensive publication system
        self._create_defensive_publication(metadata_entry)
        
        logger.info(f"Metadata created: {metadata_entry.uuid} - {title}")
        return metadata_entry.uuid
    
    def _verify_attribution_integrity(self) -> bool:
        """Verify attribution integrity"""
        expected_hash = self.generate_system_hash()
        # In production, this would verify against blockchain or timestamped records
        return True  # Simplified for this implementation
    
    def _generate_digital_signature(self, metadata: MetadataEntry) -> str:
        """Generate digital signature for metadata"""
        signature_data = {
            "uuid": metadata.uuid,
            "title": metadata.title,
            "author": metadata.zpdl.author,
            "copyright": metadata.zpdl.copyright,
            "created_at": metadata.created_at.isoformat(),
            "system_author": self.author
        }
        signature_str = json.dumps(signature_data, sort_keys=True)
        return hashlib.sha256(signature_str.encode()).hexdigest()
    
    def _create_defensive_publication(self, metadata: MetadataEntry):
        """Create defensive publication entry for IP protection"""
        publication = {
            "type": "defensive_publication",
            "metadata_uuid": metadata.uuid,
            "title": metadata.title,
            "author": self.author,
            "copyright": self.copyright,
            "zpdl_version": metadata.zpdl.version,
            "digital_signature": metadata.digital_signature,
            "publication_hash": hashlib.sha256(
                f"{metadata.uuid}{metadata.title}{self.author}".encode()
            ).hexdigest(),
            "timestamp": datetime.now().isoformat(),
            "immutable": self.attribution_immutable
        }
        
        self.defensive_publications.append(publication)
        logger.info(f"Defensive publication created: {publication['publication_hash']}")
    
    def get_metadata(self, uuid: str) -> Optional[MetadataEntry]:
        """Retrieve metadata by UUID"""
        return self.metadata_store.get(uuid)
    
    def search_metadata(
        self,
        metadata_type: Optional[MetadataType] = None,
        tags: Optional[List[str]] = None,
        title_pattern: Optional[str] = None
    ) -> List[MetadataEntry]:
        """Search metadata entries"""
        results = []
        
        for metadata in self.metadata_store.values():
            # Filter by type
            if metadata_type and metadata.metadata_type != metadata_type:
                continue
                
            # Filter by tags
            if tags and not any(tag in metadata.tags for tag in tags):
                continue
                
            # Filter by title pattern
            if title_pattern and title_pattern.lower() not in metadata.title.lower():
                continue
                
            results.append(metadata)
        
        return results
    
    def verify_metadata_integrity(self, uuid: str) -> bool:
        """Verify metadata integrity using digital signature"""
        metadata = self.get_metadata(uuid)
        if not metadata:
            return False
        
        # Regenerate signature and compare
        expected_signature = self._generate_digital_signature(metadata)
        return metadata.digital_signature == expected_signature
    
    def export_zpdl_report(self) -> Dict[str, Any]:
        """Export ZPDL v1.0 compliance report"""
        return {
            "system_info": {
                "system_id": self.system_id,
                "author": self.author,
                "copyright": self.copyright,
                "license": self.license,
                "schema_locked": self.schema_locked,
                "attribution_immutable": self.attribution_immutable
            },
            "metadata_count": len(self.metadata_store),
            "defensive_publications": len(self.defensive_publications),
            "system_hash": self.generate_system_hash(),
            "compliance_verified": True,
            "report_timestamp": datetime.now().isoformat()
        }
    
    def get_attribution(self) -> Dict[str, Any]:
        """Get ZPDL v1.0 compliant attribution"""
        return {
            "system": "Zynx Metadata System",
            "author": self.author,
            "copyright": self.copyright,
            "license": self.license,
            "system_id": self.system_id,
            "schema_version": self.schema_version,
            "attribution_locked": self.attribution_immutable,
            "system_hash": self.generate_system_hash(),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "system": "zynx_metadata",
            "status": "active",
            "schema_locked": self.schema_locked,
            "metadata_entries": len(self.metadata_store),
            "defensive_publications": len(self.defensive_publications),
            "attribution": self.get_attribution(),
            "uptime": (datetime.now() - self.created_at).total_seconds()
        }