"""
ZynxAGI Modules
===============

Self-contained, modular agent implementations.

Each module is an independent, reusable component that can be instantiated
and used without requiring the full ZynxAGI platform.
"""

from .zynx import ZynxModule
from .deeja import DeejaModule
from .zynx_metadata import ZynxMetadataModule

__all__ = [
    "ZynxModule",
    "DeejaModule",
    "ZynxMetadataModule"
]
