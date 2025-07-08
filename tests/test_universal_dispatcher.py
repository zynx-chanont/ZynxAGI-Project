import pytest
from zynx_agi.core.universal_dispatcher import UniversalDispatcher
from zynx_agi.cultural.thai_cultural_engine import ThaiCulturalContext # For type hinting if needed

@pytest.mark.asyncio
async def test_dispatch_cultural_analysis():
    """Test dispatching a cultural analysis message."""
    dispatcher = UniversalDispatcher()

    message = {
        "type": "cultural_analysis",
        "text": "สวัสดีครับ นี่เป็นการทดสอบ",
        "context_type": "formal",
        "adjust_response": False  # Do not adjust, just analyze
    }

    result = await dispatcher.dispatch(message)

    assert result is not None
    assert result["status"] == "success"
    assert "data" in result

    data = result["data"]
    assert "original_text" in data
    assert data["original_text"] == "สวัสดีครับ นี่เป็นการทดสอบ"
    assert "adjusted_text" in data # Will be same as original_text because adjust_response is False
    assert data["adjusted_text"] == "สวัสดีครับ นี่เป็นการทดสอบ"
    assert "cultural_context" in data

    cultural_context_data = data["cultural_context"]
    assert "formality_level" in cultural_context_data
    assert "politeness_level" in cultural_context_data
    assert cultural_context_data["politeness_level"] > 0.7 # "ครับ" should make it polite
    assert "detected_particles" in cultural_context_data
    assert "ครับ" in cultural_context_data["detected_particles"]
    assert "suggestions" in cultural_context_data

@pytest.mark.asyncio
async def test_dispatch_unknown_handler():
    """Test dispatching a message with an unknown handler type."""
    dispatcher = UniversalDispatcher()

    message = {
        "type": "unknown_service_type",
        "data": "some data"
    }

    result = await dispatcher.dispatch(message)

    assert result is not None
    assert result["status"] == "error"
    assert "message" in result
    assert "No handler found for type: unknown_service_type" in result["message"]

@pytest.mark.asyncio
async def test_dispatch_handler_missing_process_method():
    """Test dispatching to a handler that doesn't have a process method."""
    dispatcher = UniversalDispatcher()

    class BadHandler:
        pass # No process method

    bad_handler_instance = BadHandler()
    dispatcher.register_handler("bad_handler", bad_handler_instance)

    message = {
        "type": "bad_handler",
        "data": "some data"
    }

    result = await dispatcher.dispatch(message)

    assert result is not None
    assert result["status"] == "error"
    assert "message" in result
    # The error message will be something like 'BadHandler' object has no attribute 'process'
    assert "'BadHandler' object has no attribute 'process'" in result["message"]
