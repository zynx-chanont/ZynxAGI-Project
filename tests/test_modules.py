"""
Test for modular agent implementations
"""

import pytest
import asyncio
import tempfile
from pathlib import Path

from zynx_agi.modules import ZynxModule, DeejaModule, ZynxMetadataModule
from zynx_agi.modules.zynx import ZynxRequest, ZynxResponse
from zynx_agi.modules.deeja import DeejaRequest, DeejaResponse
from zynx_agi.modules.zynx_metadata import ZynxMetadataRecord


class TestZynxModule:
    """Test Zynx module functionality"""
    
    @pytest.mark.asyncio
    async def test_zynx_module_initialization(self):
        """Test Zynx module can be initialized"""
        zynx = ZynxModule()
        await zynx.initialize()
        
        assert zynx.active is True
        assert zynx.module_id == "zynx_main"
    
    @pytest.mark.asyncio
    async def test_zynx_module_process_request(self):
        """Test Zynx module can process requests"""
        zynx = ZynxModule()
        await zynx.initialize()
        
        request = ZynxRequest(message="Hello, Zynx!")
        response = await zynx.process(request)
        
        assert isinstance(response, ZynxResponse)
        assert response.success is True
        assert response.platform_used is not None
    
    @pytest.mark.asyncio
    async def test_zynx_module_thai_routing(self):
        """Test Zynx module routes Thai content appropriately"""
        zynx = ZynxModule()
        await zynx.initialize()
        
        request = ZynxRequest(message="สวัสดีครับ")
        response = await zynx.process(request)
        
        assert response.success is True
        assert response.routing_decision is not None
        assert response.routing_decision["requires_cultural_intelligence"] is True
    
    @pytest.mark.asyncio
    async def test_zynx_module_get_status(self):
        """Test Zynx module status retrieval"""
        zynx = ZynxModule()
        await zynx.initialize()
        
        status = await zynx.get_status()
        
        assert status["module_id"] == "zynx_main"
        assert status["active"] is True
        assert "platforms" in status


class TestDeejaModule:
    """Test Deeja module functionality"""
    
    @pytest.mark.asyncio
    async def test_deeja_module_initialization(self):
        """Test Deeja module can be initialized"""
        deeja = DeejaModule()
        await deeja.initialize()
        
        assert deeja.active is True
        assert deeja.module_id == "deeja"
    
    @pytest.mark.asyncio
    async def test_deeja_module_process_request(self):
        """Test Deeja module can process requests"""
        deeja = DeejaModule()
        await deeja.initialize()
        
        request = DeejaRequest(message="Hello!")
        response = await deeja.process(request)
        
        assert isinstance(response, DeejaResponse)
        assert response.success is True
        assert response.empathy_score is not None
    
    @pytest.mark.asyncio
    async def test_deeja_module_thai_analysis(self):
        """Test Deeja module analyzes Thai content correctly"""
        deeja = DeejaModule()
        await deeja.initialize()
        
        request = DeejaRequest(message="สวัสดีค่ะ ยินดีที่ได้รู้จักค่ะ")
        response = await deeja.process(request)
        
        assert response.success is True
        assert response.cultural_analysis is not None
        assert response.cultural_analysis.language_detected == "thai"
        assert response.cultural_analysis.formality_level > 0.5
    
    @pytest.mark.asyncio
    async def test_deeja_module_empathy_scoring(self):
        """Test Deeja module calculates empathy scores"""
        deeja = DeejaModule()
        await deeja.initialize()
        
        # Test with emotional content
        request = DeejaRequest(message="I'm feeling sad today")
        response = await deeja.process(request)
        
        assert response.success is True
        assert response.empathy_score is not None
        assert response.empathy_score > 0.5
        assert response.emotional_analysis is not None
        assert response.emotional_analysis.empathy_required is True
    
    @pytest.mark.asyncio
    async def test_deeja_module_get_status(self):
        """Test Deeja module status retrieval"""
        deeja = DeejaModule()
        await deeja.initialize()
        
        status = await deeja.get_status()
        
        assert status["module_id"] == "deeja"
        assert status["active"] is True
        assert "empathy_calibration" in status


class TestZynxMetadataModule:
    """Test Zynx-Metadata module functionality"""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.mark.asyncio
    async def test_metadata_module_initialization(self, temp_storage):
        """Test Zynx-Metadata module can be initialized"""
        metadata = ZynxMetadataModule(storage_path=temp_storage)
        await metadata.initialize()
        
        assert metadata.active is True
        assert metadata.module_id == "zynx_metadata"
        assert metadata.storage_path == temp_storage
    
    @pytest.mark.asyncio
    async def test_metadata_module_observe_interaction_with_intent(self, temp_storage):
        """Test Zynx-Metadata module detects and tracks intent"""
        metadata = ZynxMetadataModule(storage_path=temp_storage)
        await metadata.initialize()
        
        observation = await metadata.observe_interaction(
            agent_name="test_agent",
            user_input="I discovered a new algorithm",
            agent_response="That's interesting!"
        )
        
        assert observation.tracked is True
        assert observation.intent_detected == "discover"
        assert observation.metadata is not None
        assert observation.metadata.sha256 is not None
    
    @pytest.mark.asyncio
    async def test_metadata_module_observe_interaction_no_intent(self, temp_storage):
        """Test Zynx-Metadata module doesn't track without intent"""
        metadata = ZynxMetadataModule(storage_path=temp_storage)
        await metadata.initialize()
        
        observation = await metadata.observe_interaction(
            agent_name="test_agent",
            user_input="Hello, how are you?",
            agent_response="I'm doing well, thanks!"
        )
        
        assert observation.tracked is False
        assert observation.intent_detected is None
    
    @pytest.mark.asyncio
    async def test_metadata_module_storage_structure(self, temp_storage):
        """Test Zynx-Metadata module creates proper storage structure"""
        metadata = ZynxMetadataModule(storage_path=temp_storage)
        await metadata.initialize()
        
        assert (temp_storage / "json").exists()
        assert (temp_storage / "markdown").exists()
        assert (temp_storage / "hash_manifests").exists()
    
    @pytest.mark.asyncio
    async def test_metadata_module_get_status(self, temp_storage):
        """Test Zynx-Metadata module status retrieval"""
        metadata = ZynxMetadataModule(storage_path=temp_storage)
        await metadata.initialize()
        
        status = await metadata.get_status()
        
        assert status["module_id"] == "zynx_metadata"
        assert status["active"] is True
        assert "storage_path" in status


class TestModuleInteroperability:
    """Test that modules can work together"""
    
    @pytest.mark.asyncio
    async def test_modules_can_be_used_together(self):
        """Test all three modules can be instantiated and used together"""
        zynx = ZynxModule()
        deeja = DeejaModule()
        metadata = ZynxMetadataModule()
        
        await zynx.initialize()
        await deeja.initialize()
        await metadata.initialize()
        
        assert zynx.active is True
        assert deeja.active is True
        assert metadata.active is True
        
        await zynx.shutdown()
        await deeja.shutdown()
        await metadata.shutdown()
        
        assert zynx.active is False
        assert deeja.active is False
        assert metadata.active is False
