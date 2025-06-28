import pytest
from fastapi.testclient import TestClient
from zynx_agi.ai_platforms.thai_cultural_mcp import app, get_current_user, TokenData
from zynx_agi.api.chat import router as chat_router, ChatMessage, CulturalContext, ChatResponse
from fastapi import FastAPI, Depends
from unittest.mock import patch, AsyncMock

# Create test app for chat router
test_app = FastAPI()
test_app.include_router(chat_router)

# Client for the main MCP app (which has /token, /api/v1/cultural/*)
client = TestClient(app)
# Client for the isolated chat app
chat_client = TestClient(test_app)

# Mock authentication for chat_client
async def mock_get_current_user() -> TokenData:
    return TokenData(username="testuser")

test_app.dependency_overrides[get_current_user] = mock_get_current_user

def test_login():
    """Test login endpoint"""
    response = client.post(
        "/token",
        data={"username": "admin", "password": "password"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    return response.json()["access_token"]

def test_cultural_analysis():
    """Test cultural analysis endpoint"""
    token = test_login()
    response = client.post(
        "/api/v1/cultural/analyze",
        json={"text": "สวัสดีครับ ผมชื่อสมชาย"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "formality_level" in data
    assert "politeness_level" in data
    assert "cultural_elements" in data
    assert "detected_particles" in data
    assert "cultural_patterns" in data

def test_cultural_adjustment():
    """Test cultural adjustment endpoint"""
    token = test_login()
    response = client.post(
        "/api/v1/cultural/adjust",
        json={"text": "สวัสดีครับ ผมชื่อสมชาย"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "adjusted_text" in response.json()

@patch('zynx_agi.api.chat.mcp_client.adjust_cultural_context', new_callable=AsyncMock)
@patch('zynx_agi.api.chat.mcp_client.analyze_cultural_context', new_callable=AsyncMock)
def test_chat_endpoint(mock_analyze_cultural_context, mock_adjust_cultural_context):
    """Test chat endpoint"""
    # Setup mocks
    mock_analyze_cultural_context.return_value = {
        "formality_level": 0.5,
        "politeness_level": 0.8,
        "cultural_elements": {"greeting": 1.0},
        "detected_particles": ["ครับ"],
        "cultural_patterns": ["greeting_formal"],
        "suggestions": ["Maintain politeness"]
    }
    mock_adjust_cultural_context.return_value = "สวัสดีครับ สมชาย สบายดีไหมครับ"

    token = test_login() # This token is not strictly needed now due to mock_get_current_user for chat_client
                        # but test_login() also ensures the main app's /token endpoint works.

    response = chat_client.post(
        "/chat/chat",
        json={
            "text": "สวัสดีครับ ผมชื่อสมชาย",
            "model": "deeja-v1", # This model is not used by the mocked endpoint
            "temperature": 0.7,
            "max_tokens": 1000
        },
        headers={"Authorization": f"Bearer {token}"} # Header is still sent, mock_get_current_user handles it
    )
    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert data["text"] == "สวัสดีครับ สมชาย สบายดีไหมครับ"
    assert "cultural_context" in data
    assert data["cultural_context"]["politeness_level"] == 0.8
    assert "suggestions" in data
    assert "Maintain politeness" in data["suggestions"]

def test_authentication():
    """Test authentication"""
    # Test without token
    response = client.post(
        "/api/v1/cultural/analyze",
        json={"text": "สวัสดีครับ"}
    )
    assert response.status_code == 401

    # Test with invalid token
    response = client.post(
        "/api/v1/cultural/analyze",
        json={"text": "สวัสดีครับ"},
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401

def test_cultural_prompts():
    """Test cultural prompts endpoint"""
    token = test_login()
    response = client.get(
        "/api/v1/cultural/prompts",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_cultural_resources():
    """Test cultural resources endpoint"""
    token = test_login()
    response = client.get(
        "/api/v1/cultural/resources",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0 