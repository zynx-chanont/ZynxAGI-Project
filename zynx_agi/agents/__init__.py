"""
Zynx AGI Agent System
Core implementation of the three main agents: Zynx, Deeja, and Zynx-Metadata

Note: The agent classes here are maintained for backward compatibility.
For new code, use the modular implementations in zynx_agi.modules
"""

from .base_agent import ZynxAgent, AgentCapability, AgentResponse
from .zynx_main_agent import ZynxMainAgent
from .deeja_agent import DeejaAgent  
from .metadata_agent import ZynxMetadataAgent
from .mcp_dispatcher import MCPDispatcher
from .agent_registry import AgentRegistry

# Also export modular implementations for convenience
try:
    from ..modules import ZynxModule, DeejaModule, ZynxMetadataModule
    _modules_available = True
except ImportError:
    _modules_available = False

__all__ = [
    "ZynxAgent",
    "AgentCapability", 
    "AgentResponse",
    "ZynxMainAgent",
    "DeejaAgent",
    "ZynxMetadataAgent", 
    "MCPDispatcher",
    "AgentRegistry"
]

# Add module exports if available
if _modules_available:
    __all__.extend([
        "ZynxModule",
        "DeejaModule",
        "ZynxMetadataModule"
    ])
