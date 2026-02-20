import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from src.main import app
from src.services.auth_service import get_current_user
from src.db.mongo import get_database

client = TestClient(app)

mock_user = MagicMock()
mock_user.id = 123
mock_user.email = "test@example.com"

@pytest.fixture(autouse=True)
def setup_mocks(mocker):
    app.dependency_overrides[get_current_user] = lambda: mock_user

    mock_db = MagicMock()
    app.dependency_overrides[get_database] = lambda: mock_db
    
    yield mock_db
    app.dependency_overrides.clear()


async def test_add_favorite_success(setup_mocks):
    """Test 1: 成功新增最愛 (Happy Path)"""
    mock_db = setup_mocks
    mock_col = mock_db["favorites"]

    mock_col.find_one = AsyncMock(return_value=None)
    mock_col.insert_one = AsyncMock()

    fav_data = {
        "track_id": "track_123",
        "title": "Hotel California",
        "artist": "Eagles",
        "cover_url": "http://image.com",
        "spotify_url": "http://spotify.com"
    }

    res = client.post("/user/favorites", json=fav_data)
    
    assert res.status_code == 200
    assert res.json()["status"] == "added"
    assert mock_col.insert_one.called

async def test_add_favorite_exists(setup_mocks):
    """Test 2: 重複新增最愛 (Negative Path)"""
    mock_db = setup_mocks
    mock_col = mock_db["favorites"]

    mock_col.find_one = AsyncMock(return_value={"id": "some_id"})

    fav_data = {"track_id": "track_123", "title": "...", "artist": "...", "cover_url": "...", "spotify_url": "..."}

    res = client.post("/user/favorites", json=fav_data)

    assert res.status_code == 200
    assert res.json()["status"] == "exists"

async def test_remove_favorite_not_found(setup_mocks):
    """Test 3: 刪除不存在的最愛 (404)"""
    mock_db = setup_mocks
    mock_col = mock_db["favorites"]

    mock_res = MagicMock()
    mock_res.deleted_count = 0
    mock_col.delete_one = AsyncMock(return_value=mock_res)

    res = client.delete("/user/favorites/track_123")

    assert res.status_code == 404
    assert res.json()["detail"] == "Favorite not found"
