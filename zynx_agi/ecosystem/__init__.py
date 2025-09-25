"""
Zynx AGI Ecosystem Integration
Orchestrates the complete Zynx ecosystem with all components
"""

from .ecosystem_manager import EcosystemManager
from .deployment_config import DeploymentConfig

__all__ = ["EcosystemManager", "DeploymentConfig"]