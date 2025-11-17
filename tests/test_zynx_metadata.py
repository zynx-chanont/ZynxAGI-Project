"""
Test for Zynx-Metadata Agent
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from zynx_agi.agents.zynx_metadata import ZynxMetadataAgent, observe_interaction, IntentDetector


@pytest.fixture
def temp_storage():
    """Create temporary storage for tests"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.mark.asyncio
async def test_intent_detection():
    """Test intent detection functionality"""
    # Test discover intent
    assert IntentDetector.detect_intent("I discovered a new algorithm") == "discover"
    assert IntentDetector.detect_intent("We found an interesting pattern") == "discover"
    
    # Test invent intent
    assert IntentDetector.detect_intent("Let's create a new solution") == "create"
    assert IntentDetector.detect_intent("I want to invent something") == "invent"
    
    # Test develop intent
    assert IntentDetector.detect_intent("We need to develop this further") == "develop"
    assert IntentDetector.detect_intent("Let's improve the system") == "develop"
    
    # Test no intent
    assert IntentDetector.detect_intent("Hello, how are you?") is None


@pytest.mark.asyncio
async def test_zynx_metadata_agent_creation(temp_storage):
    """Test Zynx-Metadata agent initialization"""
    agent = ZynxMetadataAgent(storage_path=temp_storage)
    
    # Check storage structure
    assert (temp_storage / "json").exists()
    assert (temp_storage / "markdown").exists()
    assert (temp_storage / "pdf").exists()
    assert (temp_storage / "hash_manifests").exists()


@pytest.mark.asyncio
async def test_observe_interaction_with_intent(temp_storage):
    """Test observing an interaction with detectable intent"""
    agent = ZynxMetadataAgent(storage_path=temp_storage)
    
    user_input = "I want to create a new AI agent"
    agent_response = "Great! Let's build an innovative solution together."
    
    metadata = await agent.observe_agent_interaction(
        agent_name="test_agent",
        user_input=user_input,
        agent_response=agent_response,
        additional_context={"test": True}
    )
    
    # Should detect 'create' intent
    assert metadata is not None
    assert metadata.intent_detected == "create"
    assert metadata.ip_notice == "First discovered and created by Chanont Waenkaew (Zynx)"
    assert metadata.license == "ZPDL v1.0 © Chanont Waenkaew"
    assert metadata.sha256 is not None
    assert metadata.uuid is not None
    
    # Check files were created
    json_files = list((temp_storage / "json").glob("*.json"))
    md_files = list((temp_storage / "markdown").glob("*.md"))
    manifest_files = list((temp_storage / "hash_manifests").glob("*.json"))
    
    assert len(json_files) == 1
    assert len(md_files) == 1
    assert len(manifest_files) == 1


@pytest.mark.asyncio
async def test_observe_interaction_no_intent(temp_storage):
    """Test observing an interaction without detectable intent"""
    agent = ZynxMetadataAgent(storage_path=temp_storage)
    
    user_input = "Hello, how are you today?"
    agent_response = "I'm doing well, thank you for asking!"
    
    metadata = await agent.observe_agent_interaction(
        agent_name="test_agent",
        user_input=user_input,
        agent_response=agent_response
    )
    
    # Should not detect intent
    assert metadata is None
    
    # No files should be created
    json_files = list((temp_storage / "json").glob("*.json"))
    assert len(json_files) == 0


@pytest.mark.asyncio
async def test_metadata_structure():
    """Test metadata structure and required fields"""
    metadata = await observe_interaction(
        agent_name="test_agent",
        user_input="Let's invent something new",
        agent_response="Excellent idea! Here's my proposal."
    )
    
    if metadata:  # Only test if intent was detected
        # Test required attribution
        assert "First discovered and created by Chanont Waenkaew (Zynx)" in metadata.ip_notice
        assert "ZPDL v1.0" in metadata.license
        assert "Chanont Waenkaew" in metadata.license
        
        # Test timestamp format (should be Asia/Bangkok timezone)
        assert metadata.created_at is not None
        assert "+" in metadata.created_at or "T" in metadata.created_at
        
        # Test UUID format
        assert len(metadata.uuid) == 36  # Standard UUID length
        assert metadata.uuid.count('-') == 4  # Standard UUID format


@pytest.mark.asyncio
async def test_session_tracking(temp_storage):
    """Test session tracking functionality"""
    agent = ZynxMetadataAgent(storage_path=temp_storage)
    
    # Create multiple interactions
    metadata1 = await agent.observe_agent_interaction(
        "agent1", "I want to create something", "Let's build it!"
    )
    metadata2 = await agent.observe_agent_interaction(
        "agent2", "Let's develop this idea", "Great approach!"
    )
    
    # Check active sessions
    sessions = agent.list_active_sessions()
    assert len(sessions) == 2
    assert metadata1.uuid in sessions
    assert metadata2.uuid in sessions
    
    # Test session retrieval
    retrieved = agent.get_session_metadata(metadata1.uuid)
    assert retrieved.intent_detected == metadata1.intent_detected


@pytest.mark.asyncio
async def test_defensive_publication(temp_storage):
    """Test defensive publication generation"""
    agent = ZynxMetadataAgent(storage_path=temp_storage)
    
    # Create an interaction
    metadata = await agent.observe_agent_interaction(
        "test_agent", "I discovered a new algorithm", "That's revolutionary!"
    )
    
    if metadata:
        # Generate defensive publication
        pub_path = await agent.generate_defensive_publication(metadata.uuid)
        assert pub_path is not None
        
        # Check publication file exists
        assert Path(pub_path).exists()
        
        # Check publication content
        with open(pub_path, 'r') as f:
            publication = json.load(f)
        
        assert publication["inventor"] == "Chanont Waenkaew"
        assert publication["organization"] == "Zynx Thailand"
        assert publication["uuid"] == metadata.uuid
        assert publication["sha256_proof"] == metadata.sha256


if __name__ == "__main__":
    # Run a simple test
    async def simple_test():
        print("Testing Zynx-Metadata Agent...")
        
        # Test intent detection
        intent = IntentDetector.detect_intent("I want to create a new innovation")
        print(f"Intent detected: {intent}")
        
        # Test observation
        metadata = await observe_interaction(
            "test_agent",
            "Let's invent something revolutionary",
            "Here's my innovative solution!"
        )
        
        if metadata:
            print(f"Observation successful - UUID: {metadata.uuid}")
            print(f"Intent: {metadata.intent_detected}")
            print(f"Attribution: {metadata.ip_notice}")
            print(f"License: {metadata.license}")
        else:
            print("No intent detected in test interaction")
    
    asyncio.run(simple_test())