"""
Deeja Module (ดีจ้า) - Emotional AI & Cultural Intelligence
===========================================================

A self-contained module for empathetic, culturally-aware interactions
with specialization in Thai cultural understanding.

Usage:
    from zynx_agi.modules.deeja import DeejaModule
    
    deeja = DeejaModule(config={
        "cultural_sensitivity_weight": 0.3
    })
    
    result = await deeja.process({"message": "สวัสดีครับ"})
"""

from .agent import DeejaModule
from .config import DeejaConfig
from .models import DeejaRequest, DeejaResponse, CulturalAnalysis, EmotionalAnalysis

__all__ = [
    "DeejaModule",
    "DeejaConfig",
    "DeejaRequest",
    "DeejaResponse",
    "CulturalAnalysis",
    "EmotionalAnalysis"
]
