import pytest
from fastapi.testclient import TestClient
from zynx_agi.ai_platforms.thai_cultural_mcp import app
from zynx_agi.api.chat import router as chat_router
from fastapi import FastAPI

# Create test app
test_app = FastAPI()
test_app.include_router(chat_router)

client = TestClient(app)
chat_client = TestClient(test_app)

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

def test_chat_endpoint():
    """Test chat endpoint"""
    token = test_login()
    response = chat_client.post(
        "/chat",
        json={
            "text": "สวัสดีครับ ผมชื่อสมชาย",
            "model": "deeja-v1",
            "temperature": 0.7,
            "max_tokens": 1000
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert "cultural_context" in data
    assert "suggestions" in data

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