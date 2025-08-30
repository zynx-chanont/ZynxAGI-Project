import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from zynx_agi.api.llm_gateway import LLMProviderManager, LLMGatewayRequest
from zynx_agi.security.pii_scrubber import PIIScrubber
from zynx_agi.ai_platforms.base_adapter import LLMRequest, LLMResponse

class TestLLMGateway:
    """Test LLM Gateway functionality"""
    
    @pytest.mark.asyncio
    async def test_pii_scrubber_email_detection(self):
        """Test PII scrubber can detect and redact email addresses"""
        scrubber = PIIScrubber()
        text = "Please contact me at john.doe@example.com for more information."
        
        result = scrubber.detect_pii(text)
        
        assert result.has_pii
        assert 'email' in result.detected_types
        assert '[EMAIL_REDACTED]' in result.redacted_text
        assert 'john.doe@example.com' not in result.redacted_text
    
    @pytest.mark.asyncio
    async def test_pii_scrubber_phone_detection(self):
        """Test PII scrubber can detect and redact phone numbers"""
        scrubber = PIIScrubber()
        text = "Call me at +66-81-234-5678 or 02-123-4567"
        
        result = scrubber.detect_pii(text)
        
        assert result.has_pii
        assert 'phone_th' in result.detected_types
        assert '[PHONE_REDACTED]' in result.redacted_text
    
    @pytest.mark.asyncio
    async def test_pii_scrubber_thai_name_detection(self):
        """Test PII scrubber can detect Thai names"""
        scrubber = PIIScrubber()
        text = "สวัสดีครับ คุณสมชาย จันทร์เพ็ญ"
        
        result = scrubber.detect_pii(text)
        
        assert result.has_pii
        assert 'thai_name_pattern' in result.detected_types
        assert '[ชื่อ_ถูกซ่อน]' in result.redacted_text
    
    @pytest.mark.asyncio
    async def test_pii_scrubber_no_pii(self):
        """Test PII scrubber with clean text"""
        scrubber = PIIScrubber()
        text = "This is a clean message with no personal information."
        
        result = scrubber.detect_pii(text)
        
        assert not result.has_pii
        assert len(result.detected_types) == 0
        assert result.redacted_text == text
    
    @pytest.mark.asyncio
    async def test_provider_manager_initialization(self):
        """Test LLM Provider Manager initializes correctly"""
        manager = LLMProviderManager()
        
        assert 'openai' in manager.providers
        assert 'zynx_local' in manager.providers
        assert manager.fallback_order == ['openai', 'zynx_local']
    
    @pytest.mark.asyncio
    async def test_provider_availability_check(self):
        """Test provider availability checking"""
        manager = LLMProviderManager()
        
        # Mock the providers to return availability
        with patch.object(manager.providers['openai'], 'is_available', return_value=True):
            with patch.object(manager.providers['zynx_local'], 'is_available', return_value=False):
                provider = await manager.get_provider()
                assert provider == 'openai'
    
    @pytest.mark.asyncio
    async def test_llm_gateway_request_processing(self):
        """Test complete LLM Gateway request processing"""
        manager = LLMProviderManager()
        
        # Create test request
        request = LLMGatewayRequest(
            message="Hello, how are you?",
            provider="openai",
            temperature=0.7,
            max_tokens=100
        )
        
        # Mock the OpenAI adapter
        mock_response = LLMResponse(
            text="I'm doing well, thank you!",
            model="gpt-3.5-turbo",
            provider="openai",
            usage={"prompt_tokens": 5, "completion_tokens": 7, "total_tokens": 12},
            processing_time_ms=150.0
        )
        
        with patch.object(manager.providers['openai'], 'is_available', return_value=True):
            with patch.object(manager.providers['openai'], 'generate_response', return_value=mock_response):
                with patch.object(manager.providers['openai'], 'estimate_cost', return_value=0.002):
                    
                    response = await manager.generate_response(request)
                    
                    assert response.text == "I'm doing well, thank you!"
                    assert response.provider == "openai"
                    assert response.usage["total_tokens"] == 12
                    assert response.cost_estimate == 0.002
                    assert not response.pii_detected  # Clean message
    
    @pytest.mark.asyncio
    async def test_llm_gateway_pii_request_processing(self):
        """Test LLM Gateway with PII in request"""
        manager = LLMProviderManager()
        
        # Create request with PII
        request = LLMGatewayRequest(
            message="My email is john@example.com and I need help.",
            provider="openai"
        )
        
        # Mock the OpenAI adapter
        mock_response = LLMResponse(
            text="I can help you with your request.",
            model="gpt-3.5-turbo", 
            provider="openai",
            usage={"prompt_tokens": 8, "completion_tokens": 8, "total_tokens": 16},
            processing_time_ms=200.0
        )
        
        with patch.object(manager.providers['openai'], 'is_available', return_value=True):
            with patch.object(manager.providers['openai'], 'generate_response', return_value=mock_response):
                with patch.object(manager.providers['openai'], 'estimate_cost', return_value=0.003):
                    
                    response = await manager.generate_response(request)
                    
                    assert response.pii_detected  # PII was detected
                    assert "john@example.com" not in response.text  # Email should not leak to response
    
    def test_cross_border_compliance_check(self):
        """Test cross-border compliance checking"""
        scrubber = PIIScrubber()
        
        # Test with PII data
        request_with_pii = {"message": "My email is test@example.com"}
        compliance = scrubber.check_cross_border_compliance(request_with_pii)
        
        assert compliance["checks_required"]
        assert compliance["dpia_required"]
        assert "PII detected" in str(compliance["requirements"])
        
        # Test with clean data
        request_clean = {"message": "Hello world"}
        compliance_clean = scrubber.check_cross_border_compliance(request_clean)
        
        assert compliance_clean["checks_required"]
        assert not compliance_clean["dpia_required"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])