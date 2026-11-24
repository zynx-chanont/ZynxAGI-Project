"""
ZynxAGI - Database Boundary Freeze & Multi-Project Isolation (Gate 4)
========================================================================
Formalizes the architecture decision of Gate 4:
- 5 repository configurations
- 4 distinct hosted Supabase project references
- Zero database consolidation or cross-project table joins
- Strict tenant boundary isolation
"""

import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SupabaseProjectInstance(BaseModel):
    repository: str
    project_id: str
    role: str
    isolation_level: str
    status: str = "FROZEN"


# Verified Empirical Inventory from Phase 2.1 Baseline
FROZEN_DATABASE_INSTANCES: List[SupabaseProjectInstance] = [
    SupabaseProjectInstance(
        repository="Chanont-Wankaew/deeja-chat",
        project_id="zoqgqiophsrugobqogsb",
        role="chat_interface",
        isolation_level="isolated"
    ),
    SupabaseProjectInstance(
        repository="zynx-chanont/deeja-ai",
        project_id="fodfavehcfrehwgyuxte",
        role="cultural_ai",
        isolation_level="isolated"
    ),
    SupabaseProjectInstance(
        repository="zynx-chanont/deejas-cultural-compass",
        project_id="uuvaefwnolpdwtwpuzrn",
        role="cultural_compass",
        isolation_level="shared_infrastructure_instance"
    ),
    SupabaseProjectInstance(
        repository="zynx-chanont/zynx-proof-of-concept",
        project_id="uuvaefwnolpdwtwpuzrn",
        role="poc_gaming_experiments",
        isolation_level="shared_infrastructure_instance"
    ),
    SupabaseProjectInstance(
        repository="zynx-chanont/zynx-infra-suite",
        project_id="jjxrykcuwpdhlwhfzrys",
        role="infrastructure_management",
        isolation_level="isolated"
    )
]


class DatabaseBoundaryPolicy:
    """Enforces database boundary freeze across all Zynx platform components."""

    DATABASE_BOUNDARY_FROZEN: bool = True
    DISALLOWED_OPERATIONS: List[str] = [
        "database_consolidation",
        "cross_project_migration",
        "credential_unification",
        "cross_project_join",
        "dynamic_schema_ddl"
    ]

    @classmethod
    def assert_operation_allowed(cls, operation: str, project_id: Optional[str] = None) -> None:
        """Validate that an operation does not violate the frozen database boundary."""
        op_lower = operation.strip().lower()
        for disallowed in cls.DISALLOWED_OPERATIONS:
            if disallowed in op_lower:
                raise PermissionError(
                    f"Operation '{operation}' is prohibited by Gate 4 Database Boundary Freeze. "
                    f"Project '{project_id or 'all'}' cannot execute consolidation or dynamic DDL."
                )

    @classmethod
    def get_boundary_manifest(cls) -> Dict[str, Any]:
        return {
            "status": "FROZEN",
            "gate": "Gate 4",
            "policy": "Zero database consolidation or cross-project table joins without explicit human approval",
            "project_count": 4,
            "repository_count": 5,
            "instances": [inst.model_dump() for inst in FROZEN_DATABASE_INSTANCES]
        }


def enforce_database_freeze() -> Dict[str, Any]:
    """Activate database boundary freeze and log status."""
    manifest = DatabaseBoundaryPolicy.get_boundary_manifest()
    logger.info("Gate 4: Database Boundary Freeze is ACTIVE across 4 hosted projects (5 repos).")
    return manifest
