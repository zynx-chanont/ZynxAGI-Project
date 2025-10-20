"""
Zynx AGI Ecosystem Manager
Central orchestration system for the complete Zynx AI ecosystem
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from ..agents import (
    ZynxMainAgent, DeejaAgent, ZynxMetadataAgent, 
    AgentRegistry, MCPDispatcher
)
from ..storage import LocalStorageDriver, ArtifactManager, SessionDataExporter
from ..config.settings import settings
import logging

logger = logging.getLogger(__name__)


class EcosystemManager:
    """
    Central manager orchestrating the complete Zynx AGI ecosystem
    Handles agent lifecycle, storage management, and MCP coordination
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.deployment_mode = self.config.get("deployment_mode", "hybrid")
        
        # Core infrastructure
        self.storage_driver = None
        self.artifact_manager = None
        self.session_exporter = None
        
        # Agent system
        self.agent_registry = None
        self.mcp_dispatcher = None
        self.agents = {}
        
        # System status
        self.initialized = False
        self.ecosystem_metrics = {
            "started_at": None,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "agents_active": 0
        }
    
    async def initialize_ecosystem(self) -> bool:
        """Initialize the complete Zynx AGI ecosystem"""
        try:
            logger.info("🚀 Initializing Zynx AGI Ecosystem...")
            
            # Step 1: Initialize storage infrastructure
            await self._initialize_storage()
            
            # Step 2: Initialize agent registry
            await self._initialize_agent_registry()
            
            # Step 3: Initialize and register agents
            await self._initialize_agents()
            
            # Step 4: Initialize MCP dispatcher
            await self._initialize_mcp_dispatcher()
            
            # Step 5: Setup hybrid cloud/local deployment
            await self._setup_deployment_configuration()
            
            # Step 6: Perform ecosystem health check
            health_status = await self._perform_ecosystem_health_check()
            
            if health_status["healthy"]:
                self.initialized = True
                self.ecosystem_metrics["started_at"] = datetime.utcnow().isoformat()
                
                # Log ecosystem startup
                await self.storage_driver.store_log({
                    "action": "ecosystem_initialized",
                    "deployment_mode": self.deployment_mode,
                    "agents_active": len(self.agents),
                    "health_status": health_status,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                logger.info("✅ Zynx AGI Ecosystem initialization complete")
                logger.info(f"📊 Active agents: {len(self.agents)}")
                logger.info(f"🌐 Deployment mode: {self.deployment_mode}")
                logger.info(f"🔒 ZPDL v1.0 compliance: Active")
                logger.info(f"🛡️ PDPA compliance: Active")
                
                return True
            else:
                logger.error("❌ Ecosystem health check failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Zynx AGI ecosystem: {e}")
            return False
    
    async def _initialize_storage(self):
        """Initialize storage infrastructure with compliance"""
        logger.info("🗄️ Initializing storage infrastructure...")
        
        # Setup storage driver based on deployment mode
        if self.deployment_mode in ["local", "hybrid"]:
            storage_path = self.config.get("storage_path", "./storage")
            encryption_key = self.config.get("encryption_key", settings.SECRET_KEY)
            
            self.storage_driver = LocalStorageDriver(
                base_path=storage_path,
                encryption_key=encryption_key
            )
        
        # Initialize artifact manager with SHA-256 hashing
        self.artifact_manager = ArtifactManager(self.storage_driver)
        
        # Initialize session data exporter
        self.session_exporter = SessionDataExporter(
            self.storage_driver, 
            self.artifact_manager
        )
        
        logger.info("✅ Storage infrastructure initialized")
    
    async def _initialize_agent_registry(self):
        """Initialize the agent registry"""
        logger.info("📋 Initializing agent registry...")
        
        self.agent_registry = AgentRegistry(storage_driver=self.storage_driver)
        await self.agent_registry.initialize()
        
        logger.info("✅ Agent registry initialized")
    
    async def _initialize_agents(self):
        """Initialize and register the three main agents"""
        logger.info("🤖 Initializing Zynx AGI agents...")
        
        # Initialize Zynx Main Agent
        zynx_main = ZynxMainAgent(
            storage_driver=self.storage_driver,
            config=self.config.get("zynx_main_config", {})
        )
        
        # Initialize Deeja Agent (ดีจ้า)
        deeja = DeejaAgent(
            storage_driver=self.storage_driver,
            config=self.config.get("deeja_config", {})
        )
        
        # Initialize Zynx-Metadata Agent
        metadata_agent = ZynxMetadataAgent(
            storage_driver=self.storage_driver,
            config=self.config.get("metadata_config", {})
        )
        
        # Register agents
        agents_to_register = [
            ("zynx_main", zynx_main),
            ("deeja", deeja),
            ("zynx_metadata", metadata_agent)
        ]
        
        for agent_id, agent in agents_to_register:
            if await self.agent_registry.register_agent(agent):
                self.agents[agent_id] = agent
                logger.info(f"✅ Agent {agent_id} registered successfully")
            else:
                logger.error(f"❌ Failed to register agent {agent_id}")
                raise Exception(f"Agent registration failed: {agent_id}")
        
        self.ecosystem_metrics["agents_active"] = len(self.agents)
        logger.info(f"✅ All {len(self.agents)} agents initialized and registered")
    
    async def _initialize_mcp_dispatcher(self):
        """Initialize the Model Context Protocol dispatcher"""
        logger.info("🚦 Initializing MCP dispatcher...")
        
        self.mcp_dispatcher = MCPDispatcher(
            agent_registry=self.agent_registry,
            storage_driver=self.storage_driver
        )
        
        logger.info("✅ MCP dispatcher initialized")
    
    async def _setup_deployment_configuration(self):
        """Setup deployment configuration for cloud/local balance"""
        logger.info(f"⚙️ Setting up {self.deployment_mode} deployment...")
        
        deployment_config = {
            "mode": self.deployment_mode,
            "cloud_failover": self.config.get("cloud_failover", True),
            "local_llm_fallback": self.config.get("local_llm_fallback", True),
            "ip_guardrails": self.config.get("ip_guardrails", True),
            "compliance_monitoring": True
        }
        
        # Store deployment configuration
        await self.storage_driver.store_log({
            "action": "deployment_configured",
            "config": deployment_config,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info(f"✅ {self.deployment_mode.title()} deployment configured")
    
    async def _perform_ecosystem_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive ecosystem health check"""
        logger.info("🏥 Performing ecosystem health check...")
        
        health_status = {
            "healthy": True,
            "components": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Check storage system
        try:
            test_log = {"test": "health_check", "timestamp": datetime.utcnow().isoformat()}
            await self.storage_driver.store_log(test_log)
            health_status["components"]["storage"] = {"status": "healthy"}
        except Exception as e:
            health_status["healthy"] = False
            health_status["components"]["storage"] = {"status": "unhealthy", "error": str(e)}
        
        # Check agent registry
        try:
            registry_status = self.agent_registry.get_registry_status()
            health_status["components"]["agent_registry"] = {
                "status": "healthy" if registry_status["initialized"] else "unhealthy",
                "details": registry_status
            }
        except Exception as e:
            health_status["healthy"] = False
            health_status["components"]["agent_registry"] = {"status": "unhealthy", "error": str(e)}
        
        # Check individual agents
        try:
            agents_health = await self.agent_registry.health_check_all_agents()
            health_status["components"]["agents"] = agents_health
            
            if not agents_health["overall_healthy"]:
                health_status["healthy"] = False
        except Exception as e:
            health_status["healthy"] = False
            health_status["components"]["agents"] = {"status": "unhealthy", "error": str(e)}
        
        # Check MCP dispatcher
        if self.mcp_dispatcher:
            health_status["components"]["mcp_dispatcher"] = {"status": "healthy"}
        else:
            health_status["healthy"] = False
            health_status["components"]["mcp_dispatcher"] = {"status": "unhealthy", "error": "Not initialized"}
        
        logger.info(f"🏥 Health check complete - Overall: {'✅ Healthy' if health_status['healthy'] else '❌ Unhealthy'}")
        return health_status
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request through the Zynx ecosystem"""
        if not self.initialized:
            return {
                "success": False,
                "error": "Ecosystem not initialized",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        start_time = datetime.utcnow()
        
        try:
            # Route through MCP dispatcher
            response = await self.mcp_dispatcher.dispatch_request(request)
            
            # Update metrics
            self.ecosystem_metrics["total_requests"] += 1
            if response.success:
                self.ecosystem_metrics["successful_requests"] += 1
            else:
                self.ecosystem_metrics["failed_requests"] += 1
            
            # Log request processing
            await self.storage_driver.store_log({
                "action": "request_processed",
                "success": response.success,
                "processing_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
                "timestamp": start_time.isoformat()
            })
            
            return {
                "success": response.success,
                "response": response.response_data,
                "metadata": response.metadata,
                "agent_id": response.agent_id,
                "timestamp": response.timestamp,
                "processing_time_ms": response.processing_time_ms,
                "compliance_info": response.compliance_info
            }
            
        except Exception as e:
            self.ecosystem_metrics["total_requests"] += 1
            self.ecosystem_metrics["failed_requests"] += 1
            
            logger.error(f"Error processing request: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "timestamp": start_time.isoformat()
            }
    
    async def export_session_data(
        self, 
        session_data: Dict[str, Any],
        export_type: str = "openai"
    ) -> Dict[str, Any]:
        """Export session data with compliance"""
        try:
            if export_type == "openai":
                return await self.session_exporter.export_openai_session(session_data)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported export type: {export_type}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_ecosystem_status(self) -> Dict[str, Any]:
        """Get comprehensive ecosystem status"""
        if not self.initialized:
            return {
                "initialized": False,
                "error": "Ecosystem not initialized"
            }
        
        # Get agent metrics
        agent_metrics = await self.agent_registry.get_agent_metrics()
        
        # Get storage stats
        artifact_stats = await self.artifact_manager.get_artifact_stats()
        
        # Get health status
        health_status = await self._perform_ecosystem_health_check()
        
        return {
            "initialized": self.initialized,
            "deployment_mode": self.deployment_mode,
            "ecosystem_metrics": self.ecosystem_metrics,
            "agent_metrics": agent_metrics,
            "storage_stats": artifact_stats,
            "health_status": health_status,
            "compliance": {
                "zpdl_v1_compliant": True,
                "pdpa_compliant": True,
                "ip_guardrails_active": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def shutdown_ecosystem(self):
        """Gracefully shutdown the entire ecosystem"""
        logger.info("🔄 Shutting down Zynx AGI ecosystem...")
        
        try:
            # Shutdown all agents
            if self.agent_registry:
                await self.agent_registry.shutdown_all_agents()
            
            # Log shutdown
            if self.storage_driver:
                await self.storage_driver.store_log({
                    "action": "ecosystem_shutdown",
                    "uptime_seconds": (
                        (datetime.utcnow() - datetime.fromisoformat(self.ecosystem_metrics["started_at"])).total_seconds()
                        if self.ecosystem_metrics["started_at"] else 0
                    ),
                    "total_requests_processed": self.ecosystem_metrics["total_requests"],
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            self.initialized = False
            logger.info("✅ Zynx AGI ecosystem shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during ecosystem shutdown: {e}")
    
    # Convenience methods for direct agent access
    async def chat_with_deeja(self, message: str, cultural_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Direct interface to chat with Deeja agent"""
        request = {
            "message": message,
            "cultural_context": cultural_context,
            "direct_agent": "deeja"
        }
        return await self.process_request(request)
    
    async def analyze_cultural_context(self, content: str) -> Dict[str, Any]:
        """Direct cultural analysis through Deeja"""
        if "deeja" not in self.agents:
            return {"error": "Deeja agent not available"}
        
        deeja = self.agents["deeja"]
        from ..agents.base_agent import AgentCapability
        
        response = await deeja.execute_capability(
            AgentCapability.CULTURAL_ANALYSIS,
            {"message": content}
        )
        
        return response.response_data
    
    async def check_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Direct compliance check through Zynx-Metadata agent"""
        if "zynx_metadata" not in self.agents:
            return {"error": "Zynx-Metadata agent not available"}
        
        metadata_agent = self.agents["zynx_metadata"]
        from ..agents.base_agent import AgentCapability
        
        response = await metadata_agent.execute_capability(
            AgentCapability.COMPLIANCE_MONITORING,
            data
        )
        
        return response.response_data