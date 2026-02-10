import os
import base64
import pytest
import httpx
from dotenv import load_dotenv

load_dotenv()

AUTH_URL = "https://accounts.spotify.com/api/token"
SEARCH_URL = "https://api.spotify.com/v1/search"

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

@pytest.mark.skipif(not CLIENT_ID or not CLIENT_SECRET, reason="Spotify Credentials missing")
@pytest.mark.asyncio
async def test_spotify_search_flow():
    # 建立 Basic Auth 字串
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    headers_auth = {
        "Authorization": f"Basic {b64_auth_str}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data_auth = {"grant_type": "client_credentials"}

    async with httpx.AsyncClient() as client:
        # 1. 取得 Access Token
        
        token_resp = await client.post(AUTH_URL, headers=headers_auth, data=data_auth, timeout=10.0)
        
        if token_resp.status_code != 200:
            pytest.fail(f"Auth Failed: {token_resp.text}")
            
        access_token = token_resp.json().get("access_token")
        assert access_token is not None

        # 2. 執行歌曲搜尋 (以 Hotel California 作為經典燒友測試)
        headers_search = {"Authorization": f"Bearer {access_token}"}
        params_search = {
            "q": "Hotel California - Live",
            "type": "track",
            "limit": 1,
            "market": "TW" # 指定市場確保能拿到正確的 Spotify 連結
        }

        search_resp = await client.get(SEARCH_URL, headers=headers_search, params=params_search)
        
        if search_resp.status_code != 200:
             pytest.fail(f"Search Failed: {search_resp.text}")

        results = search_resp.json().get("tracks", {}).get("items", [])
        assert len(results) > 0, "No tracks found for the query"
        
        track = results[0]
        assert "name" in track
        assert track["artists"][0]["name"] is not None
        
        print(f"\n[Spotify Test Success] Found: {track['name']} by {track['artists'][0]['name']}")
        print(f"URL: {track['external_urls']['spotify']}")
