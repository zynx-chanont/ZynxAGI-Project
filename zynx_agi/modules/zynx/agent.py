"""
Zynx Module - Main Agent Implementation
========================================

Self-contained module for universal AI orchestration and platform coordination.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from .config import ZynxConfig
from .models import ZynxRequest, ZynxResponse, PlatformStatus


logger = logging.getLogger(__name__)


class ZynxModule:
    """
    Zynx Universal AI Orchestration Module
    
    A self-contained, independently usable module for:
    - AI platform orchestration
    - Intelligent routing and dispatching
    - Compliance monitoring (IP guardrails, ZPDL, PDPA)
    - Session management
    
    Example:
        >>> zynx = ZynxModule()
        >>> await zynx.initialize()
        >>> response = await zynx.process(ZynxRequest(message="Hello"))
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Zynx module
        
        Args:
            config: Optional configuration dictionary or ZynxConfig instance
        """
        if isinstance(config, ZynxConfig):
            self.config = config
        else:
            self.config = ZynxConfig(**(config or {}))
        
        self.module_id = self.config.module_id
        self.active = False
        self.platforms = {}
        self.sessions = {}
        
        # Setup logging
        self.logger = logging.getLogger(f"{__name__}.{self.module_id}")
        self.logger.setLevel(getattr(logging, self.config.log_level))
    
    async def initialize(self) -> None:
        """Initialize the Zynx module"""
        self.logger.info(f"Initializing Zynx module: {self.module_id}")
        
        # Initialize AI platforms
        await self._initialize_platforms()
        
        # Setup orchestration rules
        await self._setup_orchestration()
        
        # Initialize compliance monitoring
        await self._setup_compliance()
        
        self.active = True
        self.logger.info("Zynx module initialization complete")
    
    async def _initialize_platforms(self) -> None:
        """Initialize AI platform connections"""
        for platform_name, platform_config in self.config.ai_platforms.items():
            try:
                self.platforms[platform_name] = {
                    **platform_config,
                    "initialized": True,
                    "last_check": datetime.utcnow().isoformat()
                }
                self.logger.info(f"Platform {platform_name} initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize {platform_name}: {e}")
                self.platforms[platform_name] = {
                    **platform_config,
                    "status": "error",
                    "error": str(e),
                    "initialized": False
                }
    
    async def _setup_orchestration(self) -> None:
        """Setup orchestration rules"""
        self.orchestration_rules = self.config.orchestration_rules.copy()
        self.logger.info(f"Orchestration rules configured: {self.orchestration_rules}")
    
    async def _setup_compliance(self) -> None:
        """Setup compliance monitoring"""
        if self.config.storage_enabled:
            self.logger.info("Compliance monitoring initialized")
    
    async def process(self, request: ZynxRequest) -> ZynxResponse:
        """
        Process a request through Zynx orchestration
        
        Args:
            request: ZynxRequest containing message and context
            
        Returns:
            ZynxResponse with processing results
        """
        if not self.active:
            await self.initialize()
        
        start_time = datetime.utcnow()
        
        try:
            # Analyze request for routing
            routing_decision = await self._analyze_request(request)
            
            # Apply IP guardrails if enabled
            if self.orchestration_rules.get("ip_guardrails_enabled", True):
                compliance_check = await self._check_compliance(request)
                if not compliance_check["compliant"]:
                    return ZynxResponse(
                        success=False,
                        message="Request blocked by IP guardrails",
                        error=compliance_check["reason"],
                        compliance_info=compliance_check
                    )
            
            # Route to appropriate platform
            result = await self._route_request(request, routing_decision)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return ZynxResponse(
                success=True,
                message=result.get("message", "Request processed successfully"),
                data=result,
                platform_used=routing_decision.get("recommended_platform"),
                routing_decision=routing_decision,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Error processing request: {e}")
            return ZynxResponse(
                success=False,
                message="Processing failed",
                error=str(e)
            )
    
    async def _analyze_request(self, request: ZynxRequest) -> Dict[str, Any]:
        """Analyze request to determine optimal routing"""
        analysis = {
            "requires_cultural_intelligence": False,
            "requires_emotional_analysis": False,
            "complexity_level": "low",
            "recommended_platform": "openai",
            "fallback_required": False
        }
        
        message = request.message.lower()
        
        # Check for Thai cultural context
        thai_indicators = ["ค่ะ", "ครับ", "สวัสดี", "เจ้าค่ะ", "กรุงเทพ", "ไทย"]
        if any(indicator in request.message for indicator in thai_indicators):
            analysis["requires_cultural_intelligence"] = True
            analysis["recommended_platform"] = "deeja_integration"
        
        # Check for emotional context
        emotional_indicators = ["feeling", "emotion", "sad", "happy", "angry", "frustrated"]
        if any(indicator in message for indicator in emotional_indicators):
            analysis["requires_emotional_analysis"] = True
        
        # Determine complexity
        word_count = len(request.message.split())
        if word_count > 100:
            analysis["complexity_level"] = "high"
        elif word_count > 30:
            analysis["complexity_level"] = "medium"
        
        return analysis
    
    async def _check_compliance(self, request: ZynxRequest) -> Dict[str, Any]:
        """Check request against compliance rules"""
        compliance = {
            "compliant": True,
            "reason": None,
            "zpdl_check": True,
            "pdpa_check": True
        }
        
        # Check for prohibited content patterns
        prohibited_patterns = [
            "copyright infringement",
            "proprietary code",
            "confidential information",
            "trade secret"
        ]
        
        message_lower = request.message.lower()
        for pattern in prohibited_patterns:
            if pattern in message_lower:
                compliance["compliant"] = False
                compliance["reason"] = f"Contains potentially prohibited content: {pattern}"
                compliance["zpdl_check"] = False
                break
        
        return compliance
    
    async def _route_request(
        self,
        request: ZynxRequest,
        routing_decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route request to appropriate platform"""
        
        platform = routing_decision["recommended_platform"]
        
        # For cultural intelligence requirements
        if routing_decision["requires_cultural_intelligence"]:
            return {
                "message": "Cultural intelligence processing (Deeja integration)",
                "requires_deeja": True,
                "platform_used": "deeja_integration"
            }
        
        # For emotional analysis requirements
        if routing_decision["requires_emotional_analysis"]:
            return {
                "message": "Emotional intelligence processing",
                "emotional_analysis": "Available through Deeja",
                "platform_used": "emotional_ai"
            }
        
        # Standard routing
        return {
            "message": f"Response to: {request.message}",
            "platform_used": platform,
            "processing_mode": "zynx_orchestrated"
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get module status"""
        return {
            "module_id": self.module_id,
            "active": self.active,
            "platforms": self.platforms,
            "orchestration_rules": self.orchestration_rules,
            "config": self.config.model_dump()
        }
    
    async def shutdown(self) -> None:
        """Shutdown the module"""
        self.logger.info("Shutting down Zynx module")
        self.active = False
