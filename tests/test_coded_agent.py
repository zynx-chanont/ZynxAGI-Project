"""
Tests for CodeD Agent functionality
"""

import pytest
import asyncio
from zynx_agi.agents.coded_agent import CodeDAgent
from zynx_agi.agents.agent_registry import registry, AgentManifest

@pytest.fixture
def coded_agent():
    """Fixture to create a CodeD agent instance"""
    return CodeDAgent()

@pytest.mark.asyncio
async def test_coded_agent_initialization(coded_agent):
    """Test CodeD agent initializes correctly"""
    assert coded_agent.agent_id == "coded"
    assert coded_agent.name == "CodeD"
    assert coded_agent.mcp_command == "/coded"
    assert "code_generation" in coded_agent.get_capabilities()

@pytest.mark.asyncio 
async def test_code_generation_hello_world(coded_agent):
    """Test basic code generation functionality"""
    response = await coded_agent.process_request("generate hello world in python")
    
    assert response["success"] == True
    assert response["response_type"] == "code_generation"
    assert "print" in response["generated_code"]
    assert response["language"] == "python"

@pytest.mark.asyncio
async def test_debug_analysis(coded_agent):
    """Test debugging analysis functionality"""
    response = await coded_agent.process_request("I'm getting a NameError: 'x' is not defined")
    
    assert response["success"] == True
    assert response["response_type"] == "debug_analysis"
    assert len(response["suggestions"]) > 0
    assert any("variable" in suggestion.lower() for suggestion in response["suggestions"])

@pytest.mark.asyncio
async def test_code_review(coded_agent):
    """Test code review functionality"""
    code_snippet = """```python
def bad_function():
    x = 1
    y = 2
    return x + y
```"""
    
    response = await coded_agent.process_request(f"review this code: {code_snippet}")
    
    assert response["success"] == True
    assert response["response_type"] == "code_review"
    assert "feedback" in response
    assert response["language"] == "python"

@pytest.mark.asyncio
async def test_documentation_generation(coded_agent):
    """Test documentation generation"""
    code_snippet = """```python
def calculate_sum(a, b):
    return a + b
```"""
    
    response = await coded_agent.process_request(f"document this function: {code_snippet}")
    
    assert response["success"] == True
    assert response["response_type"] == "documentation"
    assert "documentation" in response
    assert '"""' in response["documentation"]

@pytest.mark.asyncio
async def test_optimization_suggestions(coded_agent):
    """Test code optimization suggestions"""
    response = await coded_agent.process_request("optimize my code for better performance")
    
    assert response["success"] == True
    assert response["response_type"] == "optimization"
    assert "optimizations" in response
    assert len(response["optimizations"]) > 0

@pytest.mark.asyncio
async def test_general_help(coded_agent):
    """Test general coding help"""
    response = await coded_agent.process_request("what can you help me with?")
    
    assert response["success"] == True
    assert response["response_type"] == "general_help"
    assert "CodeD" in response["message"]
    assert "capabilities" in response

@pytest.mark.asyncio
async def test_error_handling(coded_agent):
    """Test error handling in agent"""
    # This should not raise an exception
    response = await coded_agent.process_request("")
    
    # Should handle empty input gracefully
    assert "success" in response

def test_agent_registration():
    """Test agent can be registered in registry"""
    coded_agent = CodeDAgent()
    manifest = AgentManifest({
        "name": "CodeD",
        "version": "1.0.0",
        "description": "Test agent",
        "capabilities": coded_agent.get_capabilities()
    })
    
    success = registry.register_agent("test_coded", manifest, coded_agent)
    assert success == True
    
    # Check if agent is retrievable
    retrieved_agent = registry.get_agent_instance("test_coded")
    assert retrieved_agent is not None
    assert retrieved_agent.agent_id == "coded"
    
    # Clean up
    registry.unregister_agent("test_coded")

def test_language_detection(coded_agent):
    """Test programming language detection"""
    # Test Python detection
    python_code = "def hello(): print('world')"
    lang = coded_agent._detect_language(python_code)
    assert lang == "python"
    
    # Test JavaScript detection  
    js_code = "function hello() { console.log('world'); }"
    lang = coded_agent._detect_language(js_code)
    assert lang == "javascript"

def test_request_type_detection(coded_agent):
    """Test detection of different request types"""
    # Test code generation detection
    assert coded_agent._detect_request_type("generate a function") == "code_generation"
    assert coded_agent._detect_request_type("write code for") == "code_generation"
    
    # Test debug detection
    assert coded_agent._detect_request_type("fix this error") == "debug_analysis"
    assert coded_agent._detect_request_type("I have a bug") == "debug_analysis"
    
    # Test review detection
    assert coded_agent._detect_request_type("review my code") == "code_review"
    assert coded_agent._detect_request_type("check this code") == "code_review"

if __name__ == "__main__":
    # Simple test runner
    pytest.main([__file__, "-v"])