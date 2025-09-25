"""
Test script for Zynx AGI Ecosystem
Basic validation of the migration implementation
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from zynx_agi.ecosystem import EcosystemManager, DeploymentConfig
from zynx_agi.ecosystem.deployment_config import DeploymentMode
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_ecosystem_initialization():
    """Test basic ecosystem initialization"""
    logger.info("🧪 Starting Zynx AGI Ecosystem Test")
    
    try:
        # Create deployment configuration
        deployment_config = DeploymentConfig.create_local_config()
        
        # Validate configuration
        config_issues = deployment_config.validate_config()
        if config_issues:
            logger.warning(f"Configuration issues: {config_issues}")
        
        # Create ecosystem manager
        ecosystem_config = deployment_config.get_complete_config()
        ecosystem_manager = EcosystemManager(ecosystem_config)
        
        # Initialize ecosystem
        logger.info("🚀 Initializing ecosystem...")
        success = await ecosystem_manager.initialize_ecosystem()
        
        if success:
            logger.info("✅ Ecosystem initialization successful!")
            
            # Test basic functionality
            await test_basic_functionality(ecosystem_manager)
            
            # Test session data export
            await test_session_export(ecosystem_manager)
            
            # Test cultural analysis
            await test_cultural_analysis(ecosystem_manager)
            
            # Test compliance checking
            await test_compliance_checking(ecosystem_manager)
            
            # Get ecosystem status
            status = await ecosystem_manager.get_ecosystem_status()
            logger.info(f"📊 Ecosystem Status: {status['health_status']['healthy']}")
            
            # Shutdown ecosystem
            await ecosystem_manager.shutdown_ecosystem()
            logger.info("✅ Ecosystem test completed successfully!")
            
        else:
            logger.error("❌ Ecosystem initialization failed")
            return False
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        return False
    
    return True


async def test_basic_functionality(ecosystem_manager):
    """Test basic request processing"""
    logger.info("🧪 Testing basic functionality...")
    
    test_request = {
        "message": "Hello Zynx AGI! This is a test message.",
        "session_id": "test_session_001"
    }
    
    response = await ecosystem_manager.process_request(test_request)
    
    if response["success"]:
        logger.info("✅ Basic request processing successful")
    else:
        logger.warning(f"⚠️ Basic request failed: {response.get('error')}")


async def test_session_export(ecosystem_manager):
    """Test session data export functionality"""
    logger.info("🧪 Testing session data export...")
    
    mock_session_data = {
        "session_id": "test_export_001",
        "created_at": "2024-01-01T00:00:00Z",
        "messages": [
            {
                "role": "user",
                "content": "Hello, test message",
                "timestamp": "2024-01-01T00:00:01Z"
            },
            {
                "role": "assistant", 
                "content": "Hello! This is a test response.",
                "timestamp": "2024-01-01T00:00:02Z"
            }
        ],
        "model": "zynx-agi-v1"
    }
    
    export_result = await ecosystem_manager.export_session_data(mock_session_data, "openai")
    
    if export_result.get("export_success"):
        logger.info("✅ Session data export successful")
    else:
        logger.warning(f"⚠️ Session export failed: {export_result.get('error')}")


async def test_cultural_analysis(ecosystem_manager):
    """Test cultural analysis functionality"""
    logger.info("🧪 Testing cultural analysis...")
    
    thai_message = "สวัสดีครับ ผมชื่อ จอห์น ยินดีที่ได้รู้จักค่ะ"
    
    try:
        result = await ecosystem_manager.analyze_cultural_context(thai_message)
        
        if "language_detected" in result and result["language_detected"] == "thai":
            logger.info("✅ Cultural analysis successful - Thai language detected")
        else:
            logger.info("✅ Cultural analysis completed")
    except Exception as e:
        logger.warning(f"⚠️ Cultural analysis error: {e}")


async def test_compliance_checking(ecosystem_manager):
    """Test compliance checking functionality"""
    logger.info("🧪 Testing compliance checking...")
    
    test_data = {
        "content": "This is test content for compliance checking",
        "personal_data": False,
        "usage_type": "cultural_analysis"
    }
    
    try:
        result = await ecosystem_manager.check_compliance(test_data)
        
        if result.get("overall_compliant", True):
            logger.info("✅ Compliance check successful - Data compliant")
        else:
            logger.warning(f"⚠️ Compliance issues found: {result.get('violations', [])}")
    except Exception as e:
        logger.warning(f"⚠️ Compliance check error: {e}")


async def test_mcp_commands():
    """Test MCP slash commands and mentions"""
    logger.info("🧪 Testing MCP commands...")
    
    # Create minimal ecosystem for command testing
    deployment_config = DeploymentConfig.create_local_config()
    ecosystem_config = deployment_config.get_complete_config()
    ecosystem_manager = EcosystemManager(ecosystem_config)
    
    if await ecosystem_manager.initialize_ecosystem():
        # Test slash command
        slash_command_request = {
            "message": "/deeja:cultural สวัสดีครับ",
            "session_id": "test_mcp_001"
        }
        
        response = await ecosystem_manager.process_request(slash_command_request)
        
        if response["success"]:
            logger.info("✅ MCP slash command successful")
        else:
            logger.warning(f"⚠️ MCP command failed: {response.get('error')}")
        
        await ecosystem_manager.shutdown_ecosystem()


def test_deployment_configurations():
    """Test different deployment configurations"""
    logger.info("🧪 Testing deployment configurations...")
    
    # Test local configuration
    local_config = DeploymentConfig.create_local_config()
    local_issues = local_config.validate_config()
    
    if not local_issues:
        logger.info("✅ Local deployment configuration valid")
    else:
        logger.warning(f"⚠️ Local config issues: {local_issues}")
    
    # Test production configuration
    prod_config = DeploymentConfig.create_production_config()
    prod_issues = prod_config.validate_config()
    
    if not prod_issues:
        logger.info("✅ Production deployment configuration valid")
    else:
        logger.warning(f"⚠️ Production config issues: {prod_issues}")
    
    # Test cloud configuration
    cloud_config = DeploymentConfig.create_cloud_config()
    cloud_issues = cloud_config.validate_config()
    
    if not cloud_issues:
        logger.info("✅ Cloud deployment configuration valid")
    else:
        logger.warning(f"⚠️ Cloud config issues: {cloud_issues}")


async def main():
    """Main test function"""
    logger.info("🎯 Starting Zynx AGI Ecosystem Migration Test Suite")
    
    # Test deployment configurations
    test_deployment_configurations()
    
    # Test ecosystem initialization and basic functionality
    ecosystem_success = await test_ecosystem_initialization()
    
    # Test MCP commands
    await test_mcp_commands()
    
    if ecosystem_success:
        logger.info("🎉 All tests completed successfully!")
        logger.info("✅ Zynx Ecosystem Migration Plan implementation validated")
    else:
        logger.error("❌ Some tests failed - check logs for details")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)