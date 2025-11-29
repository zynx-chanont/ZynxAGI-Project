"""
Metadata Schema Lock + Attribution System
=========================================

Provides cryptographic schema locking and centralized attribution management
for the Zynx AGI platform.

First discovered and created by Chanont Wankaew (Zynx)
License: ZPDL v1.0 © Chanont Wankaew
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class SchemaLockStatus(str, Enum):
    """Status of a schema lock"""
    UNLOCKED = "unlocked"
    LOCKED = "locked"
    IMMUTABLE = "immutable"


class AttributionInfo(BaseModel):
    """Attribution information for tracked content"""
    author: str = "Chanont Wankaew"
    organization: str = "Zynx Thailand"
    ip_notice: str = "First discovered and created by Chanont Wankaew (Zynx)"
    license: str = "ZPDL v1.0 © Chanont Wankaew"
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))


class SchemaDefinition(BaseModel):
    """Definition of a metadata schema with lock support"""
    name: str
    version: str
    required_fields: List[str]
    optional_fields: List[str] = Field(default_factory=list)
    field_types: Dict[str, str] = Field(default_factory=dict)
    description: str = ""
    status: SchemaLockStatus = SchemaLockStatus.UNLOCKED
    lock_hash: Optional[str] = None
    lock_timestamp: Optional[str] = None
    attribution: Optional[AttributionInfo] = None


class MetadataSchemaLock:
    """
    Cryptographic schema locking system for immutable metadata definitions.
    
    Provides:
    - Schema registration with version control
    - Cryptographic locking with SHA-256 hashes
    - Integrity verification
    - Lock status tracking
    
    Example:
        >>> lock_manager = MetadataSchemaLock()
        >>> schema = lock_manager.register_schema(
        ...     name="session_metadata",
        ...     version="1.0.0",
        ...     required_fields=["session_id", "created_at"]
        ... )
        >>> lock_manager.lock_schema("session_metadata")
        >>> assert lock_manager.verify_integrity("session_metadata")
    """
    
    def __init__(self, auto_attribute: bool = True):
        """
        Initialize the schema lock manager.
        
        Args:
            auto_attribute: Whether to automatically add attribution to schemas
        """
        self._schemas: Dict[str, SchemaDefinition] = {}
        self._lock_history: List[Dict[str, Any]] = []
        self._auto_attribute = auto_attribute
        
        logger.info("MetadataSchemaLock initialized")
    
    def _compute_hash(self, data: Dict[str, Any]) -> str:
        """Compute SHA-256 hash of data"""
        # Sort keys for deterministic hashing
        serialized = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()
    
    def register_schema(
        self,
        name: str,
        version: str,
        required_fields: List[str],
        optional_fields: Optional[List[str]] = None,
        field_types: Optional[Dict[str, str]] = None,
        description: str = ""
    ) -> SchemaDefinition:
        """
        Register a new metadata schema.
        
        Args:
            name: Unique schema name
            version: Schema version (e.g., "1.0.0")
            required_fields: List of required field names
            optional_fields: List of optional field names
            field_types: Dict mapping field names to type names
            description: Human-readable description
            
        Returns:
            The registered SchemaDefinition
            
        Raises:
            ValueError: If schema already exists and is locked
        """
        if name in self._schemas:
            existing = self._schemas[name]
            if existing.status in (SchemaLockStatus.LOCKED, SchemaLockStatus.IMMUTABLE):
                raise ValueError(
                    f"Schema '{name}' is {existing.status.value} and cannot be modified"
                )
        
        attribution = AttributionInfo() if self._auto_attribute else None
        
        schema = SchemaDefinition(
            name=name,
            version=version,
            required_fields=required_fields,
            optional_fields=optional_fields or [],
            field_types=field_types or {},
            description=description,
            attribution=attribution
        )
        
        self._schemas[name] = schema
        logger.info(f"Schema '{name}' v{version} registered")
        
        return schema
    
    def lock_schema(self, name: str, make_immutable: bool = False) -> Dict[str, Any]:
        """
        Lock a schema to prevent modifications.
        
        Args:
            name: Schema name to lock
            make_immutable: If True, schema becomes permanently immutable
            
        Returns:
            Lock result containing hash and timestamp
            
        Raises:
            KeyError: If schema doesn't exist
            ValueError: If schema is already immutable
        """
        if name not in self._schemas:
            raise KeyError(f"Schema '{name}' not found")
        
        schema = self._schemas[name]
        
        if schema.status == SchemaLockStatus.IMMUTABLE:
            raise ValueError(f"Schema '{name}' is immutable and cannot be relocked")
        
        # Compute hash of schema definition (excluding lock-related fields)
        hash_data = {
            "name": schema.name,
            "version": schema.version,
            "required_fields": schema.required_fields,
            "optional_fields": schema.optional_fields,
            "field_types": schema.field_types,
            "description": schema.description
        }
        
        lock_hash = self._compute_hash(hash_data)
        lock_timestamp = datetime.now(timezone.utc).isoformat()
        
        schema.lock_hash = lock_hash
        schema.lock_timestamp = lock_timestamp
        schema.status = (
            SchemaLockStatus.IMMUTABLE if make_immutable 
            else SchemaLockStatus.LOCKED
        )
        
        # Record lock event
        lock_event = {
            "schema_name": name,
            "action": "lock",
            "status": schema.status.value,
            "hash": lock_hash,
            "timestamp": lock_timestamp,
            "attribution": schema.attribution.model_dump() if schema.attribution else None
        }
        self._lock_history.append(lock_event)
        
        logger.info(f"Schema '{name}' locked with hash: {lock_hash[:16]}...")
        
        return {
            "schema_name": name,
            "lock_hash": lock_hash,
            "lock_timestamp": lock_timestamp,
            "status": schema.status.value,
            "immutable": schema.status == SchemaLockStatus.IMMUTABLE
        }
    
    def verify_integrity(self, name: str) -> Dict[str, Any]:
        """
        Verify the integrity of a locked schema.
        
        Args:
            name: Schema name to verify
            
        Returns:
            Verification result with status and details
            
        Raises:
            KeyError: If schema doesn't exist
        """
        if name not in self._schemas:
            raise KeyError(f"Schema '{name}' not found")
        
        schema = self._schemas[name]
        
        if schema.status == SchemaLockStatus.UNLOCKED:
            return {
                "schema_name": name,
                "verified": False,
                "reason": "Schema is not locked",
                "status": schema.status.value
            }
        
        # Recompute hash
        hash_data = {
            "name": schema.name,
            "version": schema.version,
            "required_fields": schema.required_fields,
            "optional_fields": schema.optional_fields,
            "field_types": schema.field_types,
            "description": schema.description
        }
        
        current_hash = self._compute_hash(hash_data)
        is_valid = current_hash == schema.lock_hash
        
        result = {
            "schema_name": name,
            "verified": is_valid,
            "status": schema.status.value,
            "expected_hash": schema.lock_hash,
            "computed_hash": current_hash,
            "lock_timestamp": schema.lock_timestamp
        }
        
        if not is_valid:
            result["reason"] = "Hash mismatch - schema may have been tampered with"
            logger.warning(f"Schema '{name}' integrity check FAILED")
        else:
            logger.info(f"Schema '{name}' integrity check PASSED")
        
        return result
    
    def validate_metadata(
        self, 
        schema_name: str, 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate metadata against a schema.
        
        Args:
            schema_name: Name of schema to validate against
            metadata: Metadata dictionary to validate
            
        Returns:
            Validation result with errors if any
        """
        if schema_name not in self._schemas:
            return {
                "valid": False,
                "error": f"Schema '{schema_name}' not found",
                "missing_fields": [],
                "invalid_types": []
            }
        
        schema = self._schemas[schema_name]
        missing_fields = []
        invalid_types = []
        
        # Check required fields
        for field in schema.required_fields:
            if field not in metadata:
                missing_fields.append(field)
        
        # Check field types if specified
        for field, expected_type in schema.field_types.items():
            if field in metadata:
                actual_type = type(metadata[field]).__name__
                if actual_type != expected_type:
                    invalid_types.append({
                        "field": field,
                        "expected": expected_type,
                        "actual": actual_type
                    })
        
        is_valid = len(missing_fields) == 0 and len(invalid_types) == 0
        
        return {
            "valid": is_valid,
            "schema_name": schema_name,
            "schema_version": schema.version,
            "schema_status": schema.status.value,
            "missing_fields": missing_fields,
            "invalid_types": invalid_types,
            "attribution": schema.attribution.model_dump() if schema.attribution else None
        }
    
    def get_schema(self, name: str) -> Optional[SchemaDefinition]:
        """Get a schema by name"""
        return self._schemas.get(name)
    
    def list_schemas(self) -> List[Dict[str, Any]]:
        """List all registered schemas"""
        return [
            {
                "name": schema.name,
                "version": schema.version,
                "status": schema.status.value,
                "locked": schema.status != SchemaLockStatus.UNLOCKED,
                "immutable": schema.status == SchemaLockStatus.IMMUTABLE,
                "field_count": len(schema.required_fields) + len(schema.optional_fields)
            }
            for schema in self._schemas.values()
        ]
    
    def get_lock_history(self) -> List[Dict[str, Any]]:
        """Get the history of lock operations"""
        return self._lock_history.copy()


class AttributionManager:
    """
    Centralized attribution management for the Zynx AGI platform.
    
    Provides:
    - Automatic attribution embedding
    - Attribution verification
    - Attribution reports
    
    Example:
        >>> manager = AttributionManager()
        >>> content = {"text": "Hello world"}
        >>> attributed = manager.embed_attribution(content)
        >>> assert "attribution" in attributed
    """
    
    DEFAULT_AUTHOR = "Chanont Wankaew"
    DEFAULT_ORGANIZATION = "Zynx Thailand"
    DEFAULT_LICENSE = "ZPDL v1.0 © Chanont Wankaew"
    DEFAULT_IP_NOTICE = "First discovered and created by Chanont Wankaew (Zynx)"
    
    def __init__(
        self,
        author: Optional[str] = None,
        organization: Optional[str] = None,
        license_text: Optional[str] = None,
        ip_notice: Optional[str] = None
    ):
        """
        Initialize the attribution manager.
        
        Args:
            author: Default author name
            organization: Default organization
            license_text: Default license text
            ip_notice: Default IP notice
        """
        self._author = author or self.DEFAULT_AUTHOR
        self._organization = organization or self.DEFAULT_ORGANIZATION
        self._license = license_text or self.DEFAULT_LICENSE
        self._ip_notice = ip_notice or self.DEFAULT_IP_NOTICE
        self._attribution_log: List[Dict[str, Any]] = []
        
        logger.info("AttributionManager initialized")
    
    def create_attribution(
        self,
        author: Optional[str] = None,
        organization: Optional[str] = None,
        license_text: Optional[str] = None,
        ip_notice: Optional[str] = None,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> AttributionInfo:
        """
        Create an attribution record.
        
        Args:
            author: Override default author
            organization: Override default organization
            license_text: Override default license
            ip_notice: Override default IP notice
            additional_info: Additional attribution information
            
        Returns:
            AttributionInfo instance
        """
        attribution = AttributionInfo(
            author=author or self._author,
            organization=organization or self._organization,
            license=license_text or self._license,
            ip_notice=ip_notice or self._ip_notice
        )
        
        return attribution
    
    def embed_attribution(
        self,
        content: Dict[str, Any],
        attribution: Optional[AttributionInfo] = None
    ) -> Dict[str, Any]:
        """
        Embed attribution metadata into content.
        
        Args:
            content: Content dictionary to embed attribution into
            attribution: Optional custom attribution info
            
        Returns:
            Content with embedded attribution
        """
        if attribution is None:
            attribution = self.create_attribution()
        
        # Create attributed content
        attributed_content = content.copy()
        attributed_content["_attribution"] = {
            "author": attribution.author,
            "organization": attribution.organization,
            "license": attribution.license,
            "ip_notice": attribution.ip_notice,
            "created_at": attribution.created_at,
            "uuid": attribution.uuid
        }
        
        # Compute content hash for verification
        content_hash = hashlib.sha256(
            json.dumps(content, sort_keys=True, ensure_ascii=False).encode('utf-8')
        ).hexdigest()
        
        attributed_content["_attribution"]["content_hash"] = content_hash
        
        # Log attribution
        self._attribution_log.append({
            "uuid": attribution.uuid,
            "content_hash": content_hash,
            "timestamp": attribution.created_at,
            "author": attribution.author
        })
        
        logger.debug(f"Attribution embedded with UUID: {attribution.uuid}")
        
        return attributed_content
    
    def verify_attribution(self, attributed_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify the attribution of content.
        
        Args:
            attributed_content: Content with embedded attribution
            
        Returns:
            Verification result
        """
        if "_attribution" not in attributed_content:
            return {
                "verified": False,
                "reason": "No attribution found in content",
                "has_attribution": False
            }
        
        attribution = attributed_content["_attribution"]
        
        # Extract original content (without attribution)
        original_content = {
            k: v for k, v in attributed_content.items() 
            if k != "_attribution"
        }
        
        # Recompute hash
        computed_hash = hashlib.sha256(
            json.dumps(original_content, sort_keys=True, ensure_ascii=False).encode('utf-8')
        ).hexdigest()
        
        stored_hash = attribution.get("content_hash", "")
        is_valid = computed_hash == stored_hash
        
        result = {
            "verified": is_valid,
            "has_attribution": True,
            "author": attribution.get("author"),
            "organization": attribution.get("organization"),
            "license": attribution.get("license"),
            "uuid": attribution.get("uuid"),
            "expected_hash": stored_hash,
            "computed_hash": computed_hash
        }
        
        if not is_valid:
            result["reason"] = "Content hash mismatch - content may have been modified"
            logger.warning(f"Attribution verification FAILED for UUID: {attribution.get('uuid')}")
        else:
            logger.info(f"Attribution verification PASSED for UUID: {attribution.get('uuid')}")
        
        return result
    
    def generate_attribution_report(self) -> Dict[str, Any]:
        """
        Generate a report of all attributions.
        
        Returns:
            Attribution report with statistics
        """
        return {
            "total_attributions": len(self._attribution_log),
            "default_author": self._author,
            "default_organization": self._organization,
            "default_license": self._license,
            "ip_notice": self._ip_notice,
            "attribution_log": self._attribution_log.copy(),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    def get_attribution_by_uuid(self, attr_uuid: str) -> Optional[Dict[str, Any]]:
        """Get attribution info by UUID"""
        for entry in self._attribution_log:
            if entry.get("uuid") == attr_uuid:
                return entry
        return None


# Default instances for global access
_default_schema_lock: Optional[MetadataSchemaLock] = None
_default_attribution_manager: Optional[AttributionManager] = None


def get_schema_lock() -> MetadataSchemaLock:
    """Get the default schema lock instance"""
    global _default_schema_lock
    if _default_schema_lock is None:
        _default_schema_lock = MetadataSchemaLock()
    return _default_schema_lock


def get_attribution_manager() -> AttributionManager:
    """Get the default attribution manager instance"""
    global _default_attribution_manager
    if _default_attribution_manager is None:
        _default_attribution_manager = AttributionManager()
    return _default_attribution_manager


# Pre-defined standard schemas
def register_standard_schemas(lock_manager: Optional[MetadataSchemaLock] = None) -> None:
    """
    Register and lock standard Zynx metadata schemas.
    
    Args:
        lock_manager: Optional schema lock manager instance
    """
    if lock_manager is None:
        lock_manager = get_schema_lock()
    
    # Session metadata schema
    lock_manager.register_schema(
        name="session_metadata",
        version="1.0.0",
        required_fields=[
            "session_id",
            "created_at",
            "user_id",
            "compliance_status"
        ],
        optional_fields=[
            "cultural_context",
            "emotional_analysis",
            "ai_platform_used",
            "empathy_score"
        ],
        field_types={
            "session_id": "str",
            "created_at": "str",
            "user_id": "str",
            "compliance_status": "str"
        },
        description="Standard schema for session metadata tracking"
    )
    lock_manager.lock_schema("session_metadata")
    
    # Artifact metadata schema
    lock_manager.register_schema(
        name="artifact_metadata",
        version="1.0.0",
        required_fields=[
            "artifact_id",
            "hash",
            "created_at",
            "content_type",
            "compliance_info"
        ],
        optional_fields=[
            "source",
            "tags",
            "cultural_markers",
            "emotional_context"
        ],
        field_types={
            "artifact_id": "str",
            "hash": "str",
            "created_at": "str",
            "content_type": "str"
        },
        description="Standard schema for artifact metadata"
    )
    lock_manager.lock_schema("artifact_metadata")
    
    # Attribution metadata schema
    lock_manager.register_schema(
        name="attribution_metadata",
        version="1.0.0",
        required_fields=[
            "uuid",
            "author",
            "license",
            "created_at"
        ],
        optional_fields=[
            "organization",
            "ip_notice",
            "content_hash"
        ],
        field_types={
            "uuid": "str",
            "author": "str",
            "license": "str",
            "created_at": "str"
        },
        description="Standard schema for attribution metadata"
    )
    lock_manager.lock_schema("attribution_metadata", make_immutable=True)
    
    logger.info("Standard schemas registered and locked")
