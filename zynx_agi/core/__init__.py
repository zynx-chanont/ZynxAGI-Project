"""
Core functionality package for ZynxAGI

This package provides core functionality including:
- Universal Dispatcher for agent coordination
- Session Manager for session handling
- Schema Lock for metadata schema locking and attribution
"""

from .engines import (
    BaseZynxEngine,
    ChanontTheoryEngine,
    EngineDescriptor,
    EvolutionEngine,
    IntelligenceEngine,
    ReasoningEngine,
    StrategyEngine,
    ZynxCoreRegistry,
    core_registry,
)
from .schema_lock import (
    MetadataSchemaLock,
    AttributionManager,
    AttributionInfo,
    SchemaDefinition,
    SchemaLockStatus,
    get_schema_lock,
    get_attribution_manager,
    register_standard_schemas
)

__all__ = [
    "BaseZynxEngine",
    "ChanontTheoryEngine",
    "EngineDescriptor",
    "EvolutionEngine",
    "IntelligenceEngine",
    "ReasoningEngine",
    "StrategyEngine",
    "ZynxCoreRegistry",
    "core_registry",
    "MetadataSchemaLock",
    "AttributionManager",
    "AttributionInfo",
    "SchemaDefinition",
    "SchemaLockStatus",
    "get_schema_lock",
    "get_attribution_manager",
    "register_standard_schemas",
] 