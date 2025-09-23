#!/usr/bin/env python3
"""
ZynxAGI Ecosystem Migration Validation Script
ZPDL v1.0 Compliant Testing Framework
Author: Chanont Wankaew
© 2025 Zynx Thailand. All rights reserved.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from zynx_agi.modules import ZynxCore, DeejaAgent, ZynxMetadata
from zynx_agi.storage import ZynxStorage
from zynx_agi.local_llm import LocalLLMFallback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EcosystemMigrationTest:
    """Comprehensive ecosystem migration validation"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = datetime.now()
        
    async def run_all_tests(self):
        """Run all ecosystem migration tests"""
        logger.info("🚀 Starting ZynxAGI Ecosystem Migration Validation")
        logger.info("=" * 60)
        
        tests = [
            ("Module Initialization", self.test_module_initialization),
            ("ZPDL v1.0 Compliance", self.test_zpdl_compliance),
            ("Metadata System", self.test_metadata_system),
            ("Storage System", self.test_storage_system),
            ("Deeja Agent", self.test_deeja_agent),
            ("Local LLM Fallback", self.test_local_llm_fallback),
            ("Attribution Lock", self.test_attribution_lock),
            ("Defensive Publications", self.test_defensive_publications),
            ("Thai Cultural Intelligence", self.test_thai_cultural_intelligence),
            ("System Integration", self.test_system_integration)
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\n📋 Running: {test_name}")
            try:
                result = await test_func()
                self.test_results[test_name] = {
                    "status": "PASS" if result else "FAIL",
                    "details": f"Test completed with result: {result}"
                }
                status_emoji = "✅" if result else "❌"
                logger.info(f"{status_emoji} {test_name}: {'PASSED' if result else 'FAILED'}")
            except Exception as e:
                self.test_results[test_name] = {
                    "status": "ERROR",
                    "details": str(e)
                }
                logger.error(f"❌ {test_name}: ERROR - {e}")
        
        await self.generate_report()
    
    async def test_module_initialization(self):
        """Test all modules can be initialized"""
        try:
            zynx_core = ZynxCore()
            deeja_agent = DeejaAgent()
            zynx_metadata = ZynxMetadata()
            zynx_storage = ZynxStorage()
            local_llm_fallback = LocalLLMFallback()
            
            # Test initialization
            await zynx_core.initialize()
            
            logger.info("All modules initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Module initialization failed: {e}")
            return False
    
    async def test_zpdl_compliance(self):
        """Test ZPDL v1.0 compliance"""
        try:
            zynx_core = ZynxCore()
            
            attribution = zynx_core.get_attribution()
            
            # Check required fields
            required_fields = ["author", "copyright", "license", "module_id", "metadata_hash"]
            for field in required_fields:
                if field not in attribution:
                    logger.error(f"Missing ZPDL field: {field}")
                    return False
            
            # Check attribution values
            if attribution["author"] != "Chanont Wankaew":
                logger.error("Incorrect author attribution")
                return False
                
            if "© 2025 Zynx Thailand. All rights reserved." not in attribution["copyright"]:
                logger.error("Incorrect copyright attribution")
                return False
                
            if attribution["license"] != "ZPDL v1.0":
                logger.error("Incorrect license")
                return False
            
            logger.info("ZPDL v1.0 compliance verified")
            return True
        except Exception as e:
            logger.error(f"ZPDL compliance test failed: {e}")
            return False
    
    async def test_metadata_system(self):
        """Test metadata system functionality"""
        try:
            zynx_metadata = ZynxMetadata()
            
            # Test metadata creation
            metadata_uuid = zynx_metadata.create_metadata(
                metadata_type="document",
                title="Test Document",
                content="Test content for ecosystem migration",
                tags=["test", "migration", "zpdl"]
            )
            
            # Test metadata retrieval
            metadata = zynx_metadata.get_metadata(metadata_uuid)
            if not metadata:
                logger.error("Failed to retrieve created metadata")
                return False
            
            # Test integrity verification
            integrity_ok = zynx_metadata.verify_metadata_integrity(metadata_uuid)
            if not integrity_ok:
                logger.error("Metadata integrity verification failed")
                return False
            
            # Test ZPDL compliance report
            report = zynx_metadata.export_zpdl_report()
            if not report.get("compliance_verified"):
                logger.error("ZPDL compliance report failed")
                return False
            
            logger.info("Metadata system tests passed")
            return True
        except Exception as e:
            logger.error(f"Metadata system test failed: {e}")
            return False
    
    async def test_storage_system(self):
        """Test storage system (SSD + WORM)"""
        try:
            zynx_storage = ZynxStorage()
            
            # Test SSD storage
            test_data = "Test data for SSD storage"
            ssd_hash = await zynx_storage.store_ssd(
                test_data, 
                "test_file.txt",
                {"test": True, "type": "ecosystem_migration"}
            )
            
            if not ssd_hash:
                logger.error("SSD storage failed")
                return False
            
            # Test WORM storage
            test_publication = {
                "type": "test_publication",
                "content": "Test content for WORM storage",
                "author": "Chanont Wankaew",
                "timestamp": datetime.now().isoformat()
            }
            
            worm_entry = await zynx_storage.store_worm(
                test_publication,
                "test_worm_entry"
            )
            
            if not worm_entry:
                logger.error("WORM storage failed")
                return False
            
            # Test storage statistics
            stats = zynx_storage.get_storage_stats()
            if not stats.get("ssd_storage") or not stats.get("worm_storage"):
                logger.error("Storage statistics incomplete")
                return False
            
            logger.info("Storage system tests passed")
            return True
        except Exception as e:
            logger.error(f"Storage system test failed: {e}")
            return False
    
    async def test_deeja_agent(self):
        """Test Deeja agent functionality"""
        try:
            deeja_agent = DeejaAgent()
            
            # Test Thai message processing
            thai_response = await deeja_agent.process_message("สวัสดีครับ", "casual")
            if not thai_response or not thai_response.text:
                logger.error("Deeja Thai processing failed")
                return False
            
            # Test English message processing
            english_response = await deeja_agent.process_message("Hello", "casual")
            if not english_response or not english_response.text:
                logger.error("Deeja English processing failed")
                return False
            
            # Test empathy scoring
            if thai_response.emotion_score < 0 or thai_response.emotion_score > 1:
                logger.error("Invalid emotion score")
                return False
            
            # Test self-reflection
            reflection = await deeja_agent.self_reflect()
            if not reflection.get("current_empathy"):
                logger.error("Self-reflection failed")
                return False
            
            logger.info("Deeja agent tests passed")
            return True
        except Exception as e:
            logger.error(f"Deeja agent test failed: {e}")
            return False
    
    async def test_local_llm_fallback(self):
        """Test local LLM fallback system"""
        try:
            local_llm = LocalLLMFallback()
            
            # Test fallback functionality
            test_result = await local_llm.test_fallback()
            if not test_result:
                logger.error("Local LLM fallback test failed")
                return False
            
            # Test Thai response
            thai_response = await local_llm.process_local("สวัสดีครับ", thai_context=True)
            if not thai_response.text or thai_response.confidence < 0.5:
                logger.error("Local LLM Thai response failed")
                return False
            
            # Test English response
            english_response = await local_llm.process_local("Hello", thai_context=False)
            if not english_response.text or english_response.confidence < 0.5:
                logger.error("Local LLM English response failed")
                return False
            
            logger.info("Local LLM fallback tests passed")
            return True
        except Exception as e:
            logger.error(f"Local LLM fallback test failed: {e}")
            return False
    
    async def test_attribution_lock(self):
        """Test attribution lock system"""
        try:
            zynx_metadata = ZynxMetadata()
            
            # Verify schema is locked
            if not zynx_metadata.schema_locked:
                logger.error("Schema is not locked")
                return False
            
            # Verify attribution is immutable
            if not zynx_metadata.attribution_immutable:
                logger.error("Attribution is not immutable")
                return False
            
            # Test system hash generation
            system_hash = zynx_metadata.generate_system_hash()
            if not system_hash or len(system_hash) != 64:  # SHA-256 hex
                logger.error("Invalid system hash")
                return False
            
            logger.info("Attribution lock tests passed")
            return True
        except Exception as e:
            logger.error(f"Attribution lock test failed: {e}")
            return False
    
    async def test_defensive_publications(self):
        """Test defensive publication system"""
        try:
            zynx_storage = ZynxStorage()
            
            # Create a defensive publication
            publication_data = {
                "type": "test_defensive_publication",
                "content": "Test content for IP protection",
                "author": "Chanont Wankaew",
                "timestamp": datetime.now().isoformat()
            }
            
            worm_entry = await zynx_storage.store_worm(
                publication_data,
                "defensive_pub_test",
                defensive_publication=True
            )
            
            if not worm_entry.immutable:
                logger.error("Defensive publication not immutable")
                return False
            
            if not worm_entry.zpdl_compliant:
                logger.error("Defensive publication not ZPDL compliant")
                return False
            
            logger.info("Defensive publication tests passed")
            return True
        except Exception as e:
            logger.error(f"Defensive publication test failed: {e}")
            return False
    
    async def test_thai_cultural_intelligence(self):
        """Test Thai cultural intelligence features"""
        try:
            deeja_agent = DeejaAgent()
            
            # Test Thai cultural elements detection
            thai_response = await deeja_agent.process_message("ขอบคุณมากครับ", "formal")
            
            if not thai_response.thai_elements:
                logger.error("Thai elements not detected")
                return False
            
            # Test politeness scoring
            if thai_response.politeness_level < 0.8:  # Should be high for formal Thai
                logger.error("Politeness level too low for formal Thai")
                return False
            
            # Test cultural context
            if not thai_response.cultural_context.startswith("thai"):
                logger.error("Thai cultural context not detected")
                return False
            
            logger.info("Thai cultural intelligence tests passed")
            return True
        except Exception as e:
            logger.error(f"Thai cultural intelligence test failed: {e}")
            return False
    
    async def test_system_integration(self):
        """Test overall system integration"""
        try:
            # Initialize all systems
            zynx_core = ZynxCore()
            deeja_agent = DeejaAgent()
            zynx_metadata = ZynxMetadata()
            zynx_storage = ZynxStorage()
            local_llm = LocalLLMFallback()
            
            # Test integration flow
            await zynx_core.initialize()
            
            # Process a message through Deeja
            message = "สวัสดีครับ ผมต้องการทดสอบระบบ"
            deeja_response = await deeja_agent.process_message(message)
            
            # Store interaction in metadata
            metadata_uuid = zynx_metadata.create_metadata(
                metadata_type="interaction",
                title="Integration Test Interaction",
                content=f"Input: {message}\nResponse: {deeja_response.text}",
                tags=["integration_test", "deeja", "thai"]
            )
            
            # Store in WORM for defensive publication
            interaction_record = {
                "metadata_uuid": metadata_uuid,
                "deeja_response": deeja_response.dict(),
                "attribution": deeja_agent.get_attribution()
            }
            
            await zynx_storage.store_worm(interaction_record, f"integration_test_{metadata_uuid}")
            
            # Test fallback scenario
            await local_llm.activate_fallback("integration_test")
            fallback_response = await local_llm.process_local(message, thai_context=True)
            
            if not fallback_response.text:
                logger.error("Integration fallback failed")
                return False
            
            logger.info("System integration tests passed")
            return True
        except Exception as e:
            logger.error(f"System integration test failed: {e}")
            return False
    
    async def generate_report(self):
        """Generate comprehensive test report"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        passed_tests = sum(1 for result in self.test_results.values() if result["status"] == "PASS")
        total_tests = len(self.test_results)
        
        report = {
            "ecosystem_migration_validation": {
                "author": "Chanont Wankaew",
                "copyright": "© 2025 Zynx Thailand. All rights reserved.",
                "license": "ZPDL v1.0",
                "test_summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": total_tests - passed_tests,
                    "success_rate": f"{(passed_tests/total_tests)*100:.1f}%",
                    "duration_seconds": duration
                },
                "test_results": self.test_results,
                "migration_status": "COMPLETE" if passed_tests == total_tests else "INCOMPLETE",
                "timestamp": end_time.isoformat()
            }
        }
        
        # Save report
        report_path = Path("ecosystem_migration_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info("\n" + "=" * 60)
        logger.info("🎯 ECOSYSTEM MIGRATION VALIDATION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"📊 Results: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
        logger.info(f"⏱️ Duration: {duration:.2f} seconds")
        logger.info(f"📄 Report saved to: {report_path}")
        
        if passed_tests == total_tests:
            logger.info("🎉 ALL TESTS PASSED - ECOSYSTEM MIGRATION SUCCESSFUL!")
            logger.info("✅ ZynxAGI is ready for production deployment")
        else:
            logger.warning("⚠️ SOME TESTS FAILED - Please review the issues above")
            logger.info("🔧 Address the failed tests before production deployment")
        
        logger.info("=" * 60)

async def main():
    """Main test execution"""
    test_runner = EcosystemMigrationTest()
    await test_runner.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())