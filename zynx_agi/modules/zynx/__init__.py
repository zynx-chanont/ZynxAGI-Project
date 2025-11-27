"""
Zynx Module - Universal AI Orchestration
=========================================

A self-contained module for AI orchestration, platform coordination,
and intelligent routing across multiple AI platforms.

Usage:
    from zynx_agi.modules.zynx import ZynxModule
    
    zynx = ZynxModule(config={
        "orchestration_rules": {
            "cultural_context_threshold": 0.7
        }
    })
    
    result = await zynx.process({"message": "Hello"})
"""

from .agent import ZynxModule
from .config import ZynxConfig
from .models import ZynxRequest, ZynxResponse

__all__ = [
    "ZynxModule",
    "ZynxConfig",
    "ZynxRequest",
    "ZynxResponse"
]
