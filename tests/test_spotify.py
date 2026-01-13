import os
import pytest
import httpx
import base64
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# 判斷是否要跳過測試 (如果沒有 Key)
skip_spotify = (not CLIENT_ID or not CLIENT_SECRET)

@pytest.mark.skipif(skip_spotify, reason="未設定 SPOTIFY_CLIENT_ID 或 SECRET，跳過測試")
@pytest.mark.asyncio  # ⚠️ 告訴 pytest這是一個非同步測試
async def test_spotify_search_flow():
    """
    整合測試：取得 Token -> 搜尋歌曲 -> 驗證資料
    """
    
    print("\n🎵 [Test] 開始測試 Spotify API...")

    # --- 步驟 1: 取得 Access Token (Client Credentials Flow) ---
    auth_url = "https://accounts.spotify.com/api/token"  
    
    # Base64 編碼 ID:Secret
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth_str}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    async with httpx.AsyncClient() as client:
        resp = await client.post(auth_url, headers=headers, data=data)
        
        # 斷言 1: 認證必須成功 (200 OK)
        assert resp.status_code == 200, f"認證失敗: {resp.text}"
        
        token_data = resp.json()
        access_token = token_data.get("access_token")
        
        # 斷言 2: 必須拿到 Token 字串
        assert access_token is not None, "回應中沒有 access_token"
        print("✅ [Auth] 成功取得 Access Token")


    # --- 步驟 2: 搜尋歌曲 ---
    search_query = "Hotel California - Live"
    search_url = "https://api.spotify.com/v1/search" 
    
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "q": search_query,
        "type": "track",
        "limit": 1,
        "market": "TW"
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(search_url, headers=headers, params=params)
        
        # 斷言 3: 搜尋請求必須成功
        assert resp.status_code == 200, f"搜尋失敗: {resp.text}"
        
        data = resp.json()
        tracks = data.get("tracks", {}).get("items", [])

        # 斷言 4: 必須搜到至少一首歌
        assert len(tracks) > 0, "搜尋結果為空，找不到歌曲"
        
        # 驗證資料結構 (Evidence)
        track = tracks[0]
        assert "name" in track
        assert "external_urls" in track
        assert "spotify" in track["external_urls"]
        
        print(f"✅ [Search] 成功找到: {track['name']} by {track['artists'][0]['name']}")
        print(f"🔗 連結: {track['external_urls']['spotify']}")
