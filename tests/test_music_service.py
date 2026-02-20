import pytest
from unittest.mock import AsyncMock, MagicMock
from src.services.music_service import get_spotify_token, search_track

async def test_get_spotify_token_success(mocker):
    """Test 1: 成功取得 Spotify Token"""
    # Mock 整個 context manager
    mock_client = mocker.patch("httpx.AsyncClient.post", new_callable=AsyncMock)

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"access_token": "fake_spotify_token_999"}
    mock_client.return_value = mock_resp

    token = await get_spotify_token()

    assert token == "fake_spotify_token_999"
    assert mock_client.called

async def test_search_track_success(mocker):
    """Test 2: 成功搜尋到歌曲 (Happy Path)"""
    mocker.patch("src.services.music_service.get_spotify_token", return_value="fake_token")

    mock_get = mocker.patch("httpx.AsyncClient.get", new_callable=AsyncMock)

    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "tracks": {
            "items": [{"name": "Hotel California", "id": "123"}]
        }
    }
    mock_get.return_value = mock_resp

    result = await search_track("Hotel California")

    assert result["name"] == "Hotel California"
    assert result["id"] == "123"

async def test_search_track_no_result(mocker):
    """Test 3: 搜尋不到歌曲的情況 (edge)"""
    mocker.patch("src.services.music_service.get_spotify_token", return_value="fake_token")
    
    mock_get = mocker.patch("httpx.AsyncClient.get", new_callable=AsyncMock)
    mock_resp = MagicMock()

    mock_resp.json.return_value = {"tracks": {"items": []}}
    mock_get.return_value = mock_resp

    result = await search_track("A Song That Does Not Exist")

    assert result is None

async def test_search_track_no_token(mocker):
    """Test 4: Token 取得失敗的情況"""
    mocker.patch("src.services.music_service.get_spotify_token", return_value=None)
    
    result = await search_track("Any Query")
    
    assert result is None
