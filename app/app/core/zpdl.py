"""
ZPDL (Zynx Provenance Data Language) Helper

Provides utilities for generating metadata with Asia/Bangkok timestamps
and SHA256 hashing for IP provenance tracking.
"""

import hashlib
import json
from datetime import datetime
from typing import Any, Dict
import pytz


def get_bangkok_timestamp() -> str:
    """Generate Asia/Bangkok timezone timestamp."""
    bangkok_tz = pytz.timezone('Asia/Bangkok')
    return datetime.now(bangkok_tz).isoformat()


def sha256_hash(data: str) -> str:
    """Generate SHA256 hash of data."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def generate_zpdl_metadata(
    content: str,
    artifact_type: str = "unknown",
    author: str = "Chanont Wankaew",
    additional_metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Generate ZPDL metadata for an artifact.
    
    Args:
        content: The artifact content to hash
        artifact_type: Type of artifact (e.g., "document", "code", "config")
        author: Author of the artifact
        additional_metadata: Additional metadata to include
        
    Returns:
        Dictionary containing ZPDL metadata
    """
    if additional_metadata is None:
        additional_metadata = {}
        
    metadata = {
        "zpdl_version": "1.0",
        "timestamp": get_bangkok_timestamp(),
        "sha256": sha256_hash(content),
        "artifact_type": artifact_type,
        "author": author,
        "provenance": {
            "source": "Zynx AGI Core Foundation",
            "project": "ZynxAGI-Project",
            "repository": "zynx-chanont/ZynxAGI-Project"
        },
        **additional_metadata
    }
    
    return metadata


def zpdl_hash_object(obj: Dict[str, Any]) -> str:
    """Generate SHA256 hash of a JSON object for ZPDL tracking."""
    json_str = json.dumps(obj, sort_keys=True, separators=(',', ':'))
    return sha256_hash(json_str)