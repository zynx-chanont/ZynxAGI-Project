"""
Zynx-Metadata Module - Autonomous IP Tracking & Observer
========================================================

A self-contained module for intellectual property tracking,
attribution management, and defensive publication generation.

Usage:
    from zynx_agi.modules.zynx_metadata import ZynxMetadataModule
    
    metadata = ZynxMetadataModule(storage_path="/path/to/logs")
    
    result = await metadata.observe_interaction(
        agent_name="deeja",
        user_input="I discovered a new pattern",
        agent_response="That's interesting!"
    )
"""

from .agent import ZynxMetadataModule
from .config import ZynxMetadataConfig
from .models import (
    ZynxMetadataRecord,
    IntentDetector,
    MetadataObservation
)

__all__ = [
    "ZynxMetadataModule",
    "ZynxMetadataConfig",
    "ZynxMetadataRecord",
    "IntentDetector",
    "MetadataObservation"
]
