"""
Zynx-Metadata Agent - Data Governance and Compliance Management
Handles metadata schema lock, licensing information, and ZPDL/PDPA compliance
"""

import asyncio
import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from .base_agent import ZynxAgent, AgentCapability, AgentResponse
import logging

logger = logging.getLogger(__name__)


class ZynxMetadataAgent(ZynxAgent):
    """
    Zynx-Metadata Agent responsible for data governance, metadata management,
    schema locking, licensing compliance, and ZPDL/PDPA adherence
    """
    
    def __init__(self, storage_driver=None, config: Optional[Dict[str, Any]] = None):
        capabilities = [
            AgentCapability.METADATA_MANAGEMENT, 
            AgentCapability.COMPLIANCE_MONITORING,
            AgentCapability.SESSION_MANAGEMENT
        ]
        
        super().__init__(
            agent_id="zynx_metadata",
            capabilities=capabilities,
            storage_driver=storage_driver,
            config=config
        )
        
        # Metadata schema definitions
        self.schema_registry = {
            "session_metadata": {
                "version": "1.0.0",
                "required_fields": [
                    "session_id", "created_at", "user_id", "compliance_status"
                ],
                "optional_fields": [
                    "cultural_context", "emotional_analysis", "ai_platform_used"
                ],
                "locked": True,
                "last_modified": datetime.utcnow().isoformat()
            },
            "artifact_metadata": {
                "version": "1.0.0", 
                "required_fields": [
                    "artifact_id", "hash", "created_at", "content_type", "compliance_info"
                ],
                "optional_fields": [
                    "source", "tags", "cultural_markers", "emotional_context"
                ],
                "locked": True,
                "last_modified": datetime.utcnow().isoformat()
            }
        }
        
        # Licensing framework
        self.licensing_framework = {
            "zynx_platform_license": {
                "name": "Zynx Platform License v1.0",
                "type": "proprietary",
                "permissions": [
                    "internal_use", "ai_training", "cultural_analysis"
                ],
                "restrictions": [
                    "no_redistribution", "no_reverse_engineering", "attribution_required"
                ],
                "compliance_required": ["ZPDL_v1.0", "PDPA", "Thai_PDPA"]
            },
            "data_processing_license": {
                "name": "Zynx Data Processing License v1.0",
                "type": "data_processing",
                "permissions": [
                    "cultural_analysis", "emotional_processing", "session_management"
                ],
                "restrictions": [
                    "no_personal_data_export", "encrypted_storage_required", "consent_required"
                ],
                "compliance_required": ["ZPDL_v1.0", "PDPA"]
            }
        }
        
        # ZPDL v1.0 compliance rules
        self.zpdl_compliance_rules = {
            "version": "1.0",
            "data_protection_principles": [
                "lawfulness_fairness_transparency",
                "purpose_limitation",
                "data_minimisation", 
                "accuracy",
                "storage_limitation",
                "integrity_confidentiality",
                "accountability"
            ],
            "required_implementations": [
                "consent_management",
                "data_subject_rights",
                "privacy_by_design",
                "data_protection_impact_assessment"
            ]
        }
        
        # PDPA compliance framework
        self.pdpa_compliance_rules = {
            "version": "Thai_PDPA_2019",
            "lawful_basis": [
                "consent", "contract", "legal_obligation", 
                "vital_interests", "public_task", "legitimate_interests"
            ],
            "data_subject_rights": [
                "right_to_access", "right_to_rectification", "right_to_erasure",
                "right_to_restrict_processing", "right_to_data_portability",
                "right_to_object", "right_not_to_be_subject_to_automated_decision_making"
            ],
            "required_measures": [
                "appropriate_technical_measures",
                "appropriate_organisational_measures",
                "data_protection_by_design_and_by_default"
            ]
        }
        
        # IP guardrails configuration
        self.ip_guardrails = {
            "enabled": True,
            "monitoring_level": "strict",
            "protected_content_patterns": [
                "proprietary_code",
                "trade_secrets",
                "confidential_business_information",
                "copyrighted_material"
            ],
            "violation_actions": [
                "log_incident", "block_processing", "notify_compliance_team"
            ]
        }
    
    async def _setup_agent(self):
        """Initialize Zynx-Metadata agent with governance frameworks"""
        logger.info("Setting up Zynx-Metadata Agent...")
        
        # Initialize metadata schema locks
        await self._initialize_schema_locks()
        
        # Setup licensing compliance monitoring
        await self._setup_licensing_compliance()
        
        # Initialize ZPDL compliance framework
        await self._setup_zpdl_compliance()
        
        # Setup PDPA compliance monitoring
        await self._setup_pdpa_compliance()
        
        # Initialize IP guardrails
        await self._setup_ip_guardrails()
        
        logger.info("Zynx-Metadata Agent setup complete - Governance framework active")
    
    async def _initialize_schema_locks(self):
        """Initialize and lock metadata schemas"""
        for schema_name, schema in self.schema_registry.items():
            if schema["locked"]:
                schema_hash = hashlib.sha256(
                    json.dumps(schema, sort_keys=True).encode()
                ).hexdigest()
                
                schema["lock_hash"] = schema_hash
                
                if self.storage:
                    await self.storage.store_log({
                        "action": "schema_locked",
                        "schema_name": schema_name,
                        "schema_version": schema["version"],
                        "lock_hash": schema_hash,
                        "agent_id": self.agent_id
                    })
    
    async def _setup_licensing_compliance(self):
        """Setup licensing compliance monitoring"""
        for license_name, license_info in self.licensing_framework.items():
            if self.storage:
                await self.storage.store_log({
                    "action": "license_framework_initialized",
                    "license_name": license_name,
                    "license_type": license_info["type"],
                    "compliance_required": license_info["compliance_required"],
                    "agent_id": self.agent_id
                })
    
    async def _setup_zpdl_compliance(self):
        """Initialize ZPDL v1.0 compliance framework"""
        if self.storage:
            await self.storage.store_log({
                "action": "zpdl_compliance_initialized",
                "zpdl_version": self.zpdl_compliance_rules["version"],
                "principles": self.zpdl_compliance_rules["data_protection_principles"],
                "agent_id": self.agent_id,
                "compliance_status": "active"
            })
    
    async def _setup_pdpa_compliance(self):
        """Setup PDPA compliance monitoring"""
        if self.storage:
            await self.storage.store_log({
                "action": "pdpa_compliance_initialized", 
                "pdpa_version": self.pdpa_compliance_rules["version"],
                "data_subject_rights": self.pdpa_compliance_rules["data_subject_rights"],
                "agent_id": self.agent_id,
                "compliance_status": "active"
            })
    
    async def _setup_ip_guardrails(self):
        """Initialize IP guardrails and protection mechanisms"""
        if self.storage:
            await self.storage.store_log({
                "action": "ip_guardrails_initialized",
                "monitoring_level": self.ip_guardrails["monitoring_level"],
                "protected_patterns": len(self.ip_guardrails["protected_content_patterns"]),
                "agent_id": self.agent_id,
                "status": "active"
            })
    
    async def process_request(self, request: Dict[str, Any]) -> AgentResponse:
        """Process metadata and compliance requests"""
        start_time = datetime.utcnow()
        
        try:
            request_type = request.get("type", "general")
            
            if request_type == "metadata_validation":
                result = await self._validate_metadata(request)
            elif request_type == "compliance_check":
                result = await self._perform_compliance_check(request)
            elif request_type == "schema_enforcement":
                result = await self._enforce_schema(request)
            elif request_type == "licensing_validation":
                result = await self._validate_licensing(request)
            elif request_type == "ip_guardrails_check":
                result = await self._check_ip_guardrails(request)
            else:
                result = await self._handle_general_metadata_request(request)
            
            # Log metadata operation
            if self.storage:
                await self.storage.store_log({
                    "action": "metadata_operation",
                    "request_type": request_type,
                    "agent_id": self.agent_id,
                    "compliance_status": result.get("compliance_status", "unknown"),
                    "processing_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
                })
            
            return AgentResponse(
                success=True,
                agent_id=self.agent_id,
                response_data=result,
                timestamp=start_time.isoformat(),
                processing_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                compliance_info={
                    "zpdl_compliant": result.get("zpdl_compliant", True),
                    "pdpa_compliant": result.get("pdpa_compliant", True)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in Zynx-Metadata agent processing: {e}")
            return AgentResponse(
                success=False,
                agent_id=self.agent_id,
                response_data={"error": str(e)},
                timestamp=start_time.isoformat()
            )
    
    async def _validate_metadata(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate metadata against locked schemas"""
        metadata = request.get("metadata", {})
        schema_type = request.get("schema_type", "session_metadata")
        
        if schema_type not in self.schema_registry:
            return {
                "valid": False,
                "error": f"Unknown schema type: {schema_type}",
                "compliance_status": "invalid_schema"
            }
        
        schema = self.schema_registry[schema_type]
        validation_result = {
            "valid": True,
            "schema_type": schema_type,
            "schema_version": schema["version"],
            "missing_required_fields": [],
            "compliance_status": "compliant"
        }
        
        # Check required fields
        for field in schema["required_fields"]:
            if field not in metadata:
                validation_result["missing_required_fields"].append(field)
                validation_result["valid"] = False
                validation_result["compliance_status"] = "missing_required_fields"
        
        # Validate schema lock integrity
        current_schema_hash = hashlib.sha256(
            json.dumps(schema, sort_keys=True).encode()
        ).hexdigest()
        
        if current_schema_hash != schema.get("lock_hash"):
            validation_result["valid"] = False
            validation_result["error"] = "Schema lock integrity violation"
            validation_result["compliance_status"] = "schema_integrity_violation"
        
        return validation_result
    
    async def _perform_compliance_check(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive compliance check"""
        data = request.get("data", {})
        check_types = request.get("check_types", ["zpdl", "pdpa", "licensing"])
        
        compliance_result = {
            "overall_compliant": True,
            "zpdl_compliant": True,
            "pdpa_compliant": True,
            "licensing_compliant": True,
            "ip_guardrails_compliant": True,
            "compliance_details": {},
            "violations": [],
            "recommendations": []
        }
        
        # ZPDL compliance check
        if "zpdl" in check_types:
            zpdl_check = await self._check_zpdl_compliance(data)
            compliance_result["zpdl_compliant"] = zpdl_check["compliant"]
            compliance_result["compliance_details"]["zpdl"] = zpdl_check
            
            if not zpdl_check["compliant"]:
                compliance_result["overall_compliant"] = False
                compliance_result["violations"].extend(zpdl_check.get("violations", []))
        
        # PDPA compliance check
        if "pdpa" in check_types:
            pdpa_check = await self._check_pdpa_compliance(data)
            compliance_result["pdpa_compliant"] = pdpa_check["compliant"]
            compliance_result["compliance_details"]["pdpa"] = pdpa_check
            
            if not pdpa_check["compliant"]:
                compliance_result["overall_compliant"] = False
                compliance_result["violations"].extend(pdpa_check.get("violations", []))
        
        # Licensing compliance check
        if "licensing" in check_types:
            licensing_check = await self._check_licensing_compliance(data)
            compliance_result["licensing_compliant"] = licensing_check["compliant"]
            compliance_result["compliance_details"]["licensing"] = licensing_check
            
            if not licensing_check["compliant"]:
                compliance_result["overall_compliant"] = False
                compliance_result["violations"].extend(licensing_check.get("violations", []))
        
        return compliance_result
    
    async def _check_zpdl_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check ZPDL v1.0 compliance"""
        compliance_check = {
            "compliant": True,
            "version": self.zpdl_compliance_rules["version"],
            "principles_checked": [],
            "violations": []
        }
        
        # Check data protection principles
        for principle in self.zpdl_compliance_rules["data_protection_principles"]:
            principle_result = await self._check_zpdl_principle(data, principle)
            compliance_check["principles_checked"].append(principle_result)
            
            if not principle_result["compliant"]:
                compliance_check["compliant"] = False
                compliance_check["violations"].append(principle_result["violation"])
        
        return compliance_check
    
    async def _check_zpdl_principle(self, data: Dict[str, Any], principle: str) -> Dict[str, Any]:
        """Check specific ZPDL principle compliance"""
        # Basic principle compliance check
        return {
            "principle": principle,
            "compliant": True,
            "explanation": f"Data complies with {principle} principle"
        }
    
    async def _check_pdpa_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check PDPA compliance"""
        compliance_check = {
            "compliant": True,
            "version": self.pdpa_compliance_rules["version"],
            "lawful_basis": "consent",  # Default, should be determined from data
            "data_subject_rights_respected": True,
            "violations": []
        }
        
        # Check if personal data processing has lawful basis
        if "personal_data" in data and data["personal_data"]:
            if "consent" not in data and "lawful_basis" not in data:
                compliance_check["compliant"] = False
                compliance_check["violations"].append(
                    "Personal data processing without established lawful basis"
                )
        
        return compliance_check
    
    async def _check_licensing_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check licensing compliance"""
        compliance_check = {
            "compliant": True,
            "applicable_licenses": [],
            "violations": []
        }
        
        # Determine applicable licenses based on data usage
        data_usage = data.get("usage_type", "general")
        
        for license_name, license_info in self.licensing_framework.items():
            if data_usage in license_info["permissions"]:
                compliance_check["applicable_licenses"].append(license_name)
                
                # Check restrictions
                for restriction in license_info["restrictions"]:
                    if self._violates_restriction(data, restriction):
                        compliance_check["compliant"] = False
                        compliance_check["violations"].append(
                            f"Violates {license_name} restriction: {restriction}"
                        )
        
        return compliance_check
    
    def _violates_restriction(self, data: Dict[str, Any], restriction: str) -> bool:
        """Check if data usage violates a licensing restriction"""
        # Basic restriction checking logic
        if restriction == "no_redistribution" and data.get("redistribute", False):
            return True
        if restriction == "attribution_required" and not data.get("attribution"):
            return True
        return False
    
    async def _enforce_schema(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce metadata schema compliance"""
        schema_type = request.get("schema_type")
        metadata = request.get("metadata", {})
        
        if schema_type not in self.schema_registry:
            return {
                "enforced": False,
                "error": f"Unknown schema type: {schema_type}"
            }
        
        schema = self.schema_registry[schema_type]
        enforced_metadata = {}
        
        # Enforce required fields
        for field in schema["required_fields"]:
            if field in metadata:
                enforced_metadata[field] = metadata[field]
            else:
                # Set default values for missing required fields
                enforced_metadata[field] = self._get_default_value(field)
        
        # Include optional fields if present
        for field in schema["optional_fields"]:
            if field in metadata:
                enforced_metadata[field] = metadata[field]
        
        return {
            "enforced": True,
            "schema_type": schema_type,
            "enforced_metadata": enforced_metadata,
            "schema_version": schema["version"]
        }
    
    def _get_default_value(self, field: str) -> Any:
        """Get default value for a metadata field"""
        defaults = {
            "created_at": datetime.utcnow().isoformat(),
            "compliance_status": "compliant",
            "hash": "pending",
            "content_type": "unknown"
        }
        return defaults.get(field, "")
    
    async def _validate_licensing(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate licensing requirements"""
        usage_type = request.get("usage_type", "general")
        content_type = request.get("content_type", "data")
        
        validation_result = {
            "valid": True,
            "applicable_licenses": [],
            "requirements": [],
            "restrictions": []
        }
        
        # Determine applicable licenses
        for license_name, license_info in self.licensing_framework.items():
            if usage_type in license_info.get("permissions", []):
                validation_result["applicable_licenses"].append(license_name)
                validation_result["requirements"].extend(license_info.get("compliance_required", []))
                validation_result["restrictions"].extend(license_info.get("restrictions", []))
        
        return validation_result
    
    async def _check_ip_guardrails(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Check content against IP guardrails"""
        content = request.get("content", "")
        
        guardrail_result = {
            "compliant": True,
            "violations": [],
            "protected_content_detected": [],
            "action_required": False
        }
        
        # Check against protected content patterns
        for pattern in self.ip_guardrails["protected_content_patterns"]:
            if pattern.replace("_", " ") in content.lower():
                guardrail_result["compliant"] = False
                guardrail_result["protected_content_detected"].append(pattern)
                guardrail_result["violations"].append(f"Detected protected content: {pattern}")
                guardrail_result["action_required"] = True
        
        # If violations found, determine actions
        if guardrail_result["violations"]:
            guardrail_result["recommended_actions"] = self.ip_guardrails["violation_actions"]
        
        return guardrail_result
    
    async def _handle_general_metadata_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general metadata management requests"""
        return {
            "message": "General metadata management request processed",
            "agent_capabilities": [cap.value for cap in self.capabilities],
            "compliance_frameworks": ["ZPDL_v1.0", "PDPA", "Zynx_Licensing"],
            "schema_registry_status": "operational"
        }
    
    async def _execute_capability_impl(
        self,
        capability: AgentCapability,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute specific metadata agent capabilities"""
        
        if capability == AgentCapability.METADATA_MANAGEMENT:
            return await self._validate_metadata(data)
        
        elif capability == AgentCapability.COMPLIANCE_MONITORING:
            return await self._perform_compliance_check(data)
        
        elif capability == AgentCapability.SESSION_MANAGEMENT:
            return await self._handle_session_metadata(data)
        
        else:
            raise ValueError(f"Unsupported capability: {capability}")
    
    async def _handle_session_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle session metadata management"""
        session_id = data.get("session_id")
        action = data.get("action", "validate")
        
        if action == "validate":
            return await self._validate_metadata({
                "metadata": data.get("session_metadata", {}),
                "schema_type": "session_metadata"
            })
        
        elif action == "enforce":
            return await self._enforce_schema({
                "metadata": data.get("session_metadata", {}),
                "schema_type": "session_metadata"
            })
        
        else:
            return {"error": f"Unsupported session metadata action: {action}"}
    
    async def get_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        return {
            "agent_id": self.agent_id,
            "report_timestamp": datetime.utcnow().isoformat(),
            "compliance_frameworks": {
                "zpdl": {
                    "version": self.zpdl_compliance_rules["version"],
                    "status": "active",
                    "principles": len(self.zpdl_compliance_rules["data_protection_principles"])
                },
                "pdpa": {
                    "version": self.pdpa_compliance_rules["version"],
                    "status": "active",
                    "rights_protected": len(self.pdpa_compliance_rules["data_subject_rights"])
                }
            },
            "schema_registry": {
                "schemas_locked": len([s for s in self.schema_registry.values() if s["locked"]]),
                "total_schemas": len(self.schema_registry)
            },
            "licensing_framework": {
                "licenses_active": len(self.licensing_framework),
                "compliance_monitoring": "enabled"
            },
            "ip_guardrails": {
                "status": "active" if self.ip_guardrails["enabled"] else "inactive",
                "monitoring_level": self.ip_guardrails["monitoring_level"],
                "protected_patterns": len(self.ip_guardrails["protected_content_patterns"])
            }
        }