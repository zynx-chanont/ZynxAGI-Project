"""
ZynxAGI - Thai Cultural Intelligence Platform
"""

__version__ = "0.1.0"
__author__ = "ZynxAGI Team"
__email__ = "contact@zynxagi.com"

# Import main components
from .main import app
from .config.settings import settings

__all__ = ["app", "settings"]
