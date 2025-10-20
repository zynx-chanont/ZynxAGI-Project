"""
ZynxAGI - Thai Cultural Intelligence Platform
"""

__version__ = "0.1.0"
__author__ = "ZynxAGI Team"
__email__ = "contact@zynxagi.com"

# Import main components conditionally
try:
    from .main import app
    from .config.settings import settings
    __all__ = ["app", "settings"]
except ImportError:
    # For testing without FastAPI
    from .config.settings import settings
    __all__ = ["settings"]
