"""
Zynx-Metadata Module - Configuration
"""

from typing import Optional
from pathlib import Path
from pydantic import BaseModel, Field


class ZynxMetadataConfig(BaseModel):
    """Configuration for Zynx-Metadata module"""
    
    # Module identification
    module_id: str = "zynx_metadata"
    module_name: str = "Zynx-Metadata Observer"
    version: str = "1.0.0"
    
    # Storage Configuration
    storage_path: Path = Field(default_factory=lambda: Path("./zynx_logs"))
    
    # Output formats
    generate_json: bool = True
    generate_markdown: bool = True
    generate_pdf: bool = False  # PDF generation is optional
    generate_hash_manifest: bool = True
    
    # Intent detection configuration
    auto_detect_intent: bool = True
    intent_triggers_enabled: bool = True
    
    # Attribution configuration
    auto_embed_attribution: bool = True
    default_author: str = "Chanont Waenkaew"
    default_organization: str = "Zynx Thailand"
    default_license: str = "ZPDL v1.0 © Chanont Waenkaew"
    ip_notice: str = "First discovered and created by Chanont Waenkaew (Zynx)"
    
    # Timezone
    timezone: str = "Asia/Bangkok"
    
    # Defensive publication
    auto_generate_defensive_publications: bool = False
    
    # Logging Configuration
    log_level: str = "INFO"
    log_observations: bool = True
    
    class Config:
        extra = "allow"
