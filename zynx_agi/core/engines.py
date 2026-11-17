"""
ZYNX Core Modular Engines

Modular preparation interfaces for future integration of:
- Intelligence Engine
- Reasoning Engine
- Strategy Engine
- Evolution Engine
- Chanont Theory Engine (developing project specification)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class EngineDescriptor:
    """Immutable metadata describing a ZYNX Core engine module."""

    engine_id: str
    name: str
    status: str
    description: str


class BaseZynxEngine(ABC):
    """Abstract base interface for modular ZYNX Core engines."""

    engine_id: str
    name: str
    status: str = "ready"
    description: str = ""

    def describe(self) -> Dict[str, Any]:
        """Return structured engine metadata without fabricated benchmarks."""
        return {
            "engine_id": self.engine_id,
            "name": self.name,
            "status": self.status,
            "description": self.description,
        }

    @abstractmethod
    def inspect_context(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Inspect request context and return structured engine metadata."""


class IntelligenceEngine(BaseZynxEngine):
    """Modular integration slot for language/cultural intelligence routing."""

    engine_id = "intelligence"
    name = "Intelligence Engine"
    status = "ready"
    description = "Modular context-routing interface for cultural and linguistic signals."

    def inspect_context(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        message = str(payload.get("message", ""))
        has_thai = any(0x0E00 <= ord(ch) <= 0x0E7F for ch in message)
        return {
            "engine_id": self.engine_id,
            "status": self.status,
            "detected_script": "thai" if has_thai else "latin_or_other",
            "message_length": len(message),
        }


class ReasoningEngine(BaseZynxEngine):
    """Modular integration slot for structured multi-step reasoning pipelines."""

    engine_id = "reasoning"
    name = "Reasoning Engine"
    status = "ready"
    description = "Modular interface for structured prompt decomposition and reasoning."

    def inspect_context(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        history = payload.get("conversation_history") or []
        return {
            "engine_id": self.engine_id,
            "status": self.status,
            "history_turns": len(history) if isinstance(history, list) else 0,
            "mode": payload.get("domain") or "general",
        }


class StrategyEngine(BaseZynxEngine):
    """Modular integration slot for provider selection and execution strategy."""

    engine_id = "strategy"
    name = "Strategy Engine"
    status = "ready"
    description = "Modular provider-selection and fallback strategy interface."

    def inspect_context(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "engine_id": self.engine_id,
            "status": self.status,
            "requested_model": payload.get("model") or "auto",
            "fallback_enabled": True,
        }


class EvolutionEngine(BaseZynxEngine):
    """Modular integration slot for interaction observation and iterative feedback."""

    engine_id = "evolution"
    name = "Evolution Engine"
    status = "ready"
    description = "Modular hook for safe telemetry and iterative quality feedback."

    def inspect_context(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "engine_id": self.engine_id,
            "status": self.status,
            "observation_hook": "metadata_observer_available",
        }


class ChanontTheoryEngine(BaseZynxEngine):
    """
    Placeholder integration interface for Chanont Theory.

    Note: Chanont Theory is an active, developing project specification.
    This module intentionally provides only an extensible structural interface
    without inventing unapproved theoretical definitions or claiming AGI status.
    """

    engine_id = "chanont_theory"
    name = "Chanont Theory Engine"
    status = "specification_in_development"
    description = (
        "Extensible specification hook under active development by the project owner."
    )

    def inspect_context(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "engine_id": self.engine_id,
            "status": self.status,
            "specification_ready": False,
            "note": "Developing project specification interface.",
        }


class ZynxCoreRegistry:
    """Registry coordinating all modular ZYNX Core engines."""

    def __init__(self) -> None:
        self._engines: List[BaseZynxEngine] = [
            IntelligenceEngine(),
            ReasoningEngine(),
            StrategyEngine(),
            EvolutionEngine(),
            ChanontTheoryEngine(),
        ]

    def list_engines(self) -> List[Dict[str, Any]]:
        """Return metadata descriptors for all registered engines."""
        return [engine.describe() for engine in self._engines]

    def status_summary(self) -> Dict[str, str]:
        """Return a mapping of engine_id to current readiness status."""
        return {engine.engine_id: engine.status for engine in self._engines}

    def inspect_all(self, payload: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Run non-destructive context inspection across all core engines."""
        return {
            engine.engine_id: engine.inspect_context(payload)
            for engine in self._engines
        }


core_registry = ZynxCoreRegistry()
