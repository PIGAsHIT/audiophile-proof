import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from src.main import app
from src.services.auth_service import get_current_user

client = TestClient(app)

MOCK_AI_DATA = {
    "specs": {"form_factor": "Over-Ear", "year": "2024", "price": "$500", "driver": "Dynamic"},
    "sound_features": ["Balanced"],
    "detailed_analysis": {"bass": "Good", "mids": "Clear", "highs": "Crisp", "guide": "Listen loud"},
    "song_query": "Hotel California",
    "summary": "Excellent"
}

MOCK_TRACK_DATA = {
    "name": "Hotel California",
    "artists": [{"name": "Eagles"}],
    "album": {"images": [{"url": "http://cover.jpg"}]},
    "external_urls": {"spotify": "http://spotify.com/track"},
    "id": "track_id_123"
}

@pytest.fixture
def mock_dependencies(mocker):
    app.dependency_overrides[get_current_user] = lambda: MagicMock(id=1, email="test@me.com")

    mocker.patch("src.routers.recommendation.get_cached_recommendation", return_value=None)
    mocker.patch("src.routers.recommendation.set_cached_recommendation")
    mocker.patch("src.routers.recommendation.log_request", new_callable=AsyncMock)
    
    yield
    app.dependency_overrides.clear()


async def test_get_recommendation_full_flow(mock_dependencies, mocker):
    """Test 1: 完整的推薦流程 (從 AI 到 Spotify)"""
    mocker.patch("src.routers.recommendation.analyze_headphone", new_callable=AsyncMock, return_value=MOCK_AI_DATA)
    mocker.patch("src.routers.recommendation.search_track", new_callable=AsyncMock, return_value=MOCK_TRACK_DATA)

    payload = {"brand": "Sennheiser", "model": "HD800S"}
    response = client.post("/recommend", json=payload) 

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Hotel California"
    assert data["form_factor"] == "Over-Ear"

async def test_get_recommendation_cache_hit(mock_dependencies, mocker):
    """Test 2: 快取命中情況"""
    mocker.patch("src.routers.recommendation.get_cached_recommendation", return_value={"title": "Cached Song", "artist": "Cached Artist"})
    
    payload = {"brand": "Sennheiser", "model": "HD800S"}
    response = client.post("/recommend", json=payload)

    assert response.status_code == 200
    assert response.json()["title"] == "Cached Song"

async def test_get_recommendation_mock_mode():
    """Test 3: mock=True 模式"""
    payload = {"brand": "Test", "model": "Mock"}
    response = client.post("/recommend?mock=true", json=payload)

    assert response.status_code == 200
    assert "(Mock)" in response.json()["form_factor"]

async def test_get_recommendation_ai_fails(mock_dependencies, mocker):
    """Test 4: AI 服務失敗時的降級邏輯"""
    mocker.patch("src.routers.recommendation.analyze_headphone", new_callable=AsyncMock, return_value=None)
    mocker.patch("src.routers.recommendation.search_track", new_callable=AsyncMock, return_value=MOCK_TRACK_DATA)

    payload = {"brand": "Broken", "model": "AI"}
    response = client.post("/recommend", json=payload)

    assert response.status_code == 200
    assert response.json()["comment"] == "AI not available"
