import httpx
import base64
from src.core.config import settings

async def get_spotify_token():
    auth_str = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://accounts.spotify.com/api/token", 
            headers={"Authorization": f"Basic {b64_auth}"}, 
            data={"grant_type": "client_credentials"}
        )
        return resp.json().get("access_token")

async def search_track(query: str):
    token = await get_spotify_token()
    if not token: 
        return None
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.spotify.com/v1/search",
            headers={"Authorization": f"Bearer {token}"}, 
            params={"q": query, "type": "track", "limit": 1, "market": "TW"}
        )
        items = resp.json().get("tracks", {}).get("items", [])
        return items[0] if items else None