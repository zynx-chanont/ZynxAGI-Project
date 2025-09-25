"""
Zynx AGI Agent System
Core implementation of the three main agents: Zynx, Deeja, and Zynx-Metadata
"""

from .base_agent import ZynxAgent, AgentCapability, AgentResponse
from .zynx_main_agent import ZynxMainAgent
from .deeja_agent import DeejaAgent  
from .metadata_agent import ZynxMetadataAgent
from .mcp_dispatcher import MCPDispatcher
from .agent_registry import AgentRegistry

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
