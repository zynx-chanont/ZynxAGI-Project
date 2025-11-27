"""
Zynx-Metadata Module - Data Models
"""

import uuid
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
import pytz


class ZynxMetadataRecord(BaseModel):
    """Schema for Zynx metadata tracking"""
    ip_notice: str = "First discovered and created by Chanont Waenkaew (Zynx)"
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(
        default_factory=lambda: datetime.now(pytz.timezone('Asia/Bangkok')).isoformat()
    )
    license: str = "ZPDL v1.0 © Chanont Waenkaew"
    sha256: Optional[str] = None
    intent_detected: Optional[str] = None
    artifacts: List[str] = Field(default_factory=list)
    attribution_embedded: bool = True


class MetadataObservation(BaseModel):
    """Observation result from metadata tracking"""
    tracked: bool
    metadata: Optional[ZynxMetadataRecord] = None
    intent_detected: Optional[str] = None
    storage_paths: Optional[Dict[str, str]] = None


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


class DefensivePublication(BaseModel):
    """Defensive publication for IP protection"""
    publication_type: str = "defensive_disclosure"
    title: str
    inventor: str = "Chanont Waenkaew"
    organization: str = "Zynx Thailand"
    disclosure_date: str
    uuid: str
    sha256_proof: str
    license: str
    claim: str
    description: str
