"""
Deployment Configuration for Zynx AGI Ecosystem
Handles different deployment modes: local, cloud, hybrid
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum


class DeploymentMode(str, Enum):
    """Supported deployment modes"""
    LOCAL = "local"
    CLOUD = "cloud" 
    HYBRID = "hybrid"


class CloudProvider(str, Enum):
    """Supported cloud providers"""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    SELF_HOSTED = "self_hosted"


@dataclass
class StorageConfig:
    """Storage configuration for different deployment modes"""
    type: str = "local"  # local, cloud, hybrid
    base_path: str = "./storage"
    encryption_enabled: bool = True
    encryption_key: Optional[str] = None
    cloud_config: Optional[Dict[str, Any]] = None
    backup_enabled: bool = True
    compression_enabled: bool = True


@dataclass  
class SecurityConfig:
    """Security and compliance configuration"""
    zpdl_compliance: bool = True
    pdpa_compliance: bool = True
    ip_guardrails_enabled: bool = True
    metadata_schema_locked: bool = True
    licensing_enforcement: bool = True
    audit_logging: bool = True


@dataclass
class AgentConfig:
    """Configuration for individual agents"""
    enabled: bool = True
    config: Dict[str, Any] = None
    resource_limits: Optional[Dict[str, Any]] = None
    scaling_config: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration"""
    enabled: bool = True
    metrics_collection: bool = True
    health_checks: bool = True
    performance_monitoring: bool = True
    cultural_intelligence_metrics: bool = True
    logging_level: str = "INFO"


class DeploymentConfig:
    """
    Main deployment configuration for Zynx AGI ecosystem
    Provides configuration for different deployment scenarios
    """
    
    def __init__(
        self,
        deployment_mode: DeploymentMode = DeploymentMode.HYBRID,
        cloud_provider: Optional[CloudProvider] = None
    ):
        self.deployment_mode = deployment_mode
        self.cloud_provider = cloud_provider or CloudProvider.SELF_HOSTED
        
        # Core configurations
        self.storage = StorageConfig()
        self.security = SecurityConfig()
        self.monitoring = MonitoringConfig()
        
        # Agent configurations
        self.agents = {
            "zynx_main": AgentConfig(),
            "deeja": AgentConfig(),
            "zynx_metadata": AgentConfig()
        }
        
        # Platform configurations
        self.platform = {
            "api_host": "0.0.0.0",
            "api_port": 8000,
            "worker_processes": 1,
            "max_concurrent_requests": 100,
            "request_timeout": 30,
            "enable_cors": True,
            "allowed_origins": [
                "http://localhost:3000",
                "http://localhost:5173",
                "https://zynxdata.com"
            ]
        }
        
        # Apply deployment-specific configurations
        self._apply_deployment_specific_config()
    
    def _apply_deployment_specific_config(self):
        """Apply configuration based on deployment mode"""
        
        if self.deployment_mode == DeploymentMode.LOCAL:
            self._configure_local_deployment()
        elif self.deployment_mode == DeploymentMode.CLOUD:
            self._configure_cloud_deployment()
        elif self.deployment_mode == DeploymentMode.HYBRID:
            self._configure_hybrid_deployment()
    
    def _configure_local_deployment(self):
        """Configure for local deployment"""
        # Storage: Local filesystem
        self.storage.type = "local"
        self.storage.base_path = "./storage"
        self.storage.cloud_config = None
        
        # Platform: Single instance
        self.platform["worker_processes"] = 1
        self.platform["max_concurrent_requests"] = 50
        
        # Agents: Basic configuration
        for agent_config in self.agents.values():
            agent_config.resource_limits = {
                "memory_mb": 1024,
                "cpu_cores": 1
            }
            agent_config.scaling_config = None
    
    def _configure_cloud_deployment(self):
        """Configure for cloud deployment"""
        # Storage: Cloud-based
        self.storage.type = "cloud"
        self.storage.base_path = "/app/storage"
        self.storage.cloud_config = {
            "provider": self.cloud_provider.value,
            "bucket_name": "zynx-agi-storage",
            "region": "us-west-2"
        }
        
        # Platform: Multi-instance
        self.platform["worker_processes"] = 4
        self.platform["max_concurrent_requests"] = 500
        
        # Agents: Scalable configuration
        for agent_config in self.agents.values():
            agent_config.resource_limits = {
                "memory_mb": 4096,
                "cpu_cores": 2
            }
            agent_config.scaling_config = {
                "min_instances": 1,
                "max_instances": 10,
                "target_cpu_utilization": 70
            }
    
    def _configure_hybrid_deployment(self):
        """Configure for hybrid deployment"""
        # Storage: Hybrid (local primary, cloud backup)
        self.storage.type = "hybrid"
        self.storage.base_path = "./storage"
        self.storage.cloud_config = {
            "provider": self.cloud_provider.value,
            "backup_bucket": "zynx-agi-backup",
            "sync_interval": 300  # 5 minutes
        }
        
        # Platform: Moderate scaling
        self.platform["worker_processes"] = 2
        self.platform["max_concurrent_requests"] = 200
        
        # Agents: Balanced configuration
        for agent_config in self.agents.values():
            agent_config.resource_limits = {
                "memory_mb": 2048,
                "cpu_cores": 1
            }
            agent_config.scaling_config = {
                "min_instances": 1,
                "max_instances": 5,
                "target_cpu_utilization": 80
            }
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Get storage configuration as dictionary"""
        return {
            "type": self.storage.type,
            "base_path": self.storage.base_path,
            "encryption_enabled": self.storage.encryption_enabled,
            "encryption_key": self.storage.encryption_key,
            "cloud_config": self.storage.cloud_config,
            "backup_enabled": self.storage.backup_enabled,
            "compression_enabled": self.storage.compression_enabled
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration as dictionary"""
        return {
            "zpdl_compliance": self.security.zpdl_compliance,
            "pdpa_compliance": self.security.pdpa_compliance,
            "ip_guardrails_enabled": self.security.ip_guardrails_enabled,
            "metadata_schema_locked": self.security.metadata_schema_locked,
            "licensing_enforcement": self.security.licensing_enforcement,
            "audit_logging": self.security.audit_logging
        }
    
    def get_agent_config(self, agent_id: str) -> Dict[str, Any]:
        """Get configuration for specific agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Unknown agent: {agent_id}")
        
        agent_config = self.agents[agent_id]
        return {
            "enabled": agent_config.enabled,
            "config": agent_config.config,
            "resource_limits": agent_config.resource_limits,
            "scaling_config": agent_config.scaling_config
        }
    
    def get_platform_config(self) -> Dict[str, Any]:
        """Get platform configuration as dictionary"""
        return self.platform.copy()
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration as dictionary"""
        return {
            "enabled": self.monitoring.enabled,
            "metrics_collection": self.monitoring.metrics_collection,
            "health_checks": self.monitoring.health_checks,
            "performance_monitoring": self.monitoring.performance_monitoring,
            "cultural_intelligence_metrics": self.monitoring.cultural_intelligence_metrics,
            "logging_level": self.monitoring.logging_level
        }
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete configuration as dictionary"""
        return {
            "deployment_mode": self.deployment_mode.value,
            "cloud_provider": self.cloud_provider.value,
            "storage": self.get_storage_config(),
            "security": self.get_security_config(),
            "monitoring": self.get_monitoring_config(),
            "platform": self.get_platform_config(),
            "agents": {
                agent_id: self.get_agent_config(agent_id)
                for agent_id in self.agents.keys()
            }
        }
    
    def update_agent_config(self, agent_id: str, config_updates: Dict[str, Any]):
        """Update configuration for specific agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Unknown agent: {agent_id}")
        
        self.agents[agent_id].config.update(config_updates)
    
    def enable_enhanced_security(self):
        """Enable enhanced security features"""
        self.security.zpdl_compliance = True
        self.security.pdpa_compliance = True
        self.security.ip_guardrails_enabled = True
        self.security.metadata_schema_locked = True
        self.security.licensing_enforcement = True
        self.security.audit_logging = True
        
        # Enhanced storage encryption
        self.storage.encryption_enabled = True
        
        # Enhanced monitoring
        self.monitoring.performance_monitoring = True
        self.monitoring.cultural_intelligence_metrics = True
    
    def configure_for_production(self):
        """Apply production-ready configuration"""
        # Enhanced security
        self.enable_enhanced_security()
        
        # Production platform settings
        self.platform.update({
            "worker_processes": 4,
            "max_concurrent_requests": 1000,
            "request_timeout": 60,
            "enable_cors": True
        })
        
        # Production monitoring
        self.monitoring.enabled = True
        self.monitoring.metrics_collection = True
        self.monitoring.health_checks = True
        self.monitoring.logging_level = "INFO"
        
        # Production storage
        self.storage.backup_enabled = True
        self.storage.compression_enabled = True
    
    def configure_for_development(self):
        """Apply development-friendly configuration"""
        # Relaxed security for development
        self.security.ip_guardrails_enabled = False
        self.security.licensing_enforcement = False
        
        # Development platform settings
        self.platform.update({
            "worker_processes": 1,
            "max_concurrent_requests": 50,
            "request_timeout": 30
        })
        
        # Development monitoring
        self.monitoring.logging_level = "DEBUG"
        
        # Local storage for development
        self.storage.type = "local"
        self.storage.cloud_config = None
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Check required fields
        if not self.storage.base_path:
            issues.append("Storage base path is required")
        
        if self.storage.encryption_enabled and not self.storage.encryption_key:
            issues.append("Encryption key is required when encryption is enabled")
        
        if self.deployment_mode == DeploymentMode.CLOUD and not self.storage.cloud_config:
            issues.append("Cloud configuration is required for cloud deployment")
        
        # Check agent configurations
        for agent_id, agent_config in self.agents.items():
            if not agent_config.enabled:
                continue
            
            if agent_config.resource_limits:
                limits = agent_config.resource_limits
                if limits.get("memory_mb", 0) < 512:
                    issues.append(f"Agent {agent_id} memory limit too low (min 512MB)")
                
                if limits.get("cpu_cores", 0) < 0.5:
                    issues.append(f"Agent {agent_id} CPU limit too low (min 0.5 cores)")
        
        # Check platform configuration
        if self.platform["max_concurrent_requests"] < 1:
            issues.append("Max concurrent requests must be at least 1")
        
        if self.platform["request_timeout"] < 5:
            issues.append("Request timeout too low (min 5 seconds)")
        
        return issues
    
    @classmethod
    def create_local_config(cls) -> 'DeploymentConfig':
        """Create configuration optimized for local development"""
        config = cls(DeploymentMode.LOCAL)
        config.configure_for_development()
        return config
    
    @classmethod
    def create_production_config(
        cls, 
        cloud_provider: CloudProvider = CloudProvider.AWS
    ) -> 'DeploymentConfig':
        """Create configuration optimized for production"""
        config = cls(DeploymentMode.HYBRID, cloud_provider)
        config.configure_for_production()
        return config
    
    @classmethod
    def create_cloud_config(
        cls, 
        cloud_provider: CloudProvider = CloudProvider.AWS
    ) -> 'DeploymentConfig':
        """Create configuration for full cloud deployment"""
        config = cls(DeploymentMode.CLOUD, cloud_provider)
        config.configure_for_production()
        return config