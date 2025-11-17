"""
Tests for OpenAI Export Functionality
Tests export of prompts, configurations, and agent definitions
"""

import pytest
import pytest_asyncio
import asyncio
from zynx_agi.storage.openai_exporter import OpenAIExporter
from zynx_agi.storage.drivers import MemoryStorageDriver
from zynx_agi.storage.artifact_manager import ArtifactManager
from zynx_agi.agents.deeja_agent import DeejaAgent
from zynx_agi.agents.zynx_main_agent import ZynxMainAgent


@pytest.fixture
def storage_driver():
    """Create a memory storage driver for testing"""
    return MemoryStorageDriver()


@pytest.fixture
def artifact_manager(storage_driver):
    """Create an artifact manager for testing"""
    return ArtifactManager(storage_driver)


@pytest.fixture
def openai_exporter(storage_driver, artifact_manager):
    """Create an OpenAI exporter for testing"""
    return OpenAIExporter(storage_driver, artifact_manager)


@pytest_asyncio.fixture
async def sample_agents():
    """Create sample agents for testing"""
    deeja = DeejaAgent()
    await deeja.initialize()
    
    zynx_main = ZynxMainAgent()
    await zynx_main.initialize()
    
    return [deeja, zynx_main]


@pytest.mark.asyncio
async def test_export_all_assets(openai_exporter, sample_agents):
    """Test exporting all OpenAI assets"""
    result = await openai_exporter.export_all_assets(
        agents=sample_agents,
        include_system_prompts=True,
        include_model_configs=True,
        include_agent_definitions=True
    )
    
    assert result["export_success"] is True
    assert "artifact_id" in result
    assert "exported_at" in result
    assert result["summary"]["system_prompts_count"] > 0
    assert result["summary"]["model_configs_count"] > 0
    assert result["summary"]["agent_definitions_count"] == 2


@pytest.mark.asyncio
async def test_export_prompts_only(openai_exporter, sample_agents):
    """Test exporting only system prompts"""
    result = await openai_exporter.export_prompts_only(agents=sample_agents)
    
    assert result["export_success"] is True
    assert "artifact_id" in result
    assert result["prompts_count"] > 0


@pytest.mark.asyncio
async def test_export_configs_only(openai_exporter):
    """Test exporting only model configurations"""
    result = await openai_exporter.export_configs_only()
    
    assert result["export_success"] is True
    assert "artifact_id" in result
    assert result["configs_count"] >= 3  # Should have at least 3 configs


@pytest.mark.asyncio
async def test_export_agents_only(openai_exporter, sample_agents):
    """Test exporting only agent definitions"""
    result = await openai_exporter.export_agents_only(agents=sample_agents)
    
    assert result["export_success"] is True
    assert "artifact_id" in result
    assert result["agents_count"] == 2


@pytest.mark.asyncio
async def test_import_assets(openai_exporter, sample_agents):
    """Test importing exported assets"""
    # First export
    export_result = await openai_exporter.export_all_assets(
        agents=sample_agents,
        include_system_prompts=True,
        include_model_configs=True,
        include_agent_definitions=True
    )
    
    artifact_id = export_result["artifact_id"]
    
    # Then import
    import_result = await openai_exporter.import_assets(artifact_id)
    
    assert import_result["import_success"] is True
    assert import_result["summary"]["prompts_imported"] > 0
    assert import_result["summary"]["configs_imported"] >= 3
    assert import_result["summary"]["agents_imported"] == 2


@pytest.mark.asyncio
async def test_export_prompts_structure(openai_exporter, sample_agents):
    """Test that exported prompts have correct structure"""
    result = await openai_exporter.export_prompts_only(agents=sample_agents)
    artifact_id = result["artifact_id"]
    
    # Retrieve the artifact to check structure
    from zynx_agi.storage.artifact_manager import ArtifactManager
    import json
    
    artifact = await openai_exporter.artifacts.retrieve_artifact(artifact_id)
    data = json.loads(artifact["content"].decode())
    
    assert "export_metadata" in data
    assert "system_prompts" in data
    assert "common" in data["system_prompts"]
    assert "cultural_awareness_prompt" in data["system_prompts"]["common"]
    assert "thai_cultural_prompt" in data["system_prompts"]["common"]


@pytest.mark.asyncio
async def test_export_configs_structure(openai_exporter):
    """Test that exported configs have correct structure"""
    result = await openai_exporter.export_configs_only()
    artifact_id = result["artifact_id"]
    
    # Retrieve the artifact to check structure
    import json
    
    artifact = await openai_exporter.artifacts.retrieve_artifact(artifact_id)
    data = json.loads(artifact["content"].decode())
    
    assert "export_metadata" in data
    assert "model_configurations" in data
    assert "default_openai_config" in data["model_configurations"]
    assert "cultural_config" in data["model_configurations"]
    assert "empathy_config" in data["model_configurations"]
    
    # Check config structure
    default_config = data["model_configurations"]["default_openai_config"]
    assert "model" in default_config
    assert "temperature" in default_config
    assert "max_tokens" in default_config


@pytest.mark.asyncio
async def test_export_agents_structure(openai_exporter, sample_agents):
    """Test that exported agents have correct structure"""
    result = await openai_exporter.export_agents_only(agents=sample_agents)
    artifact_id = result["artifact_id"]
    
    # Retrieve the artifact to check structure
    import json
    
    artifact = await openai_exporter.artifacts.retrieve_artifact(artifact_id)
    data = json.loads(artifact["content"].decode())
    
    assert "export_metadata" in data
    assert "agent_definitions" in data
    assert "deeja" in data["agent_definitions"]
    
    # Check agent definition structure
    deeja_def = data["agent_definitions"]["deeja"]
    assert "agent_id" in deeja_def
    assert "agent_type" in deeja_def
    assert "capabilities" in deeja_def
    assert "active" in deeja_def
    assert isinstance(deeja_def["capabilities"], list)
    assert len(deeja_def["capabilities"]) > 0


@pytest.mark.asyncio
async def test_export_without_agents(openai_exporter):
    """Test exporting prompts and configs without agent data"""
    result = await openai_exporter.export_all_assets(
        agents=None,
        include_system_prompts=True,
        include_model_configs=True,
        include_agent_definitions=False
    )
    
    assert result["export_success"] is True
    assert result["summary"]["agent_definitions_count"] == 0
    assert result["summary"]["system_prompts_count"] > 0  # Should still have common prompts
    assert result["summary"]["model_configs_count"] > 0


@pytest.mark.asyncio
async def test_import_nonexistent_artifact(openai_exporter):
    """Test importing from a non-existent artifact"""
    with pytest.raises(ValueError, match="not found"):
        await openai_exporter.import_assets("nonexistent_artifact_id")
