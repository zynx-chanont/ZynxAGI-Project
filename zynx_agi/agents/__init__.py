# Zynx Agents - AI Agent Framework for ZynxAGI
# This package contains the building blocks for creating and managing AI Agents
# within the Zynx Ecosystem, supporting the Model Context Protocol (MCP).

from .base_agent import BaseAgent
from .agent_registry import AgentRegistry, AgentManifest
from .coded_agent import CodeDAgent

__all__ = [
    "BaseAgent",
    "AgentRegistry", 
    "AgentManifest",
    "CodeDAgent"
]

print("zynx_agi.agents package loaded")