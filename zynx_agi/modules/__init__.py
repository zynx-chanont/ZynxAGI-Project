"""
Zynx AGI Module Structure
ZPDL v1.0 Compliant Module Architecture
Author: Chanont Wankaew
© 2025 Zynx Thailand. All rights reserved.
"""

from .zynx_core import ZynxCore
from .deeja import DeejaAgent  
from .metadata import ZynxMetadata

__version__ = "1.0.0"
__author__ = "Chanont Wankaew"
__copyright__ = "© 2025 Zynx Thailand. All rights reserved."
__license__ = "ZPDL v1.0"

__all__ = [
    "ZynxCore",
    "DeejaAgent", 
    "ZynxMetadata"
]