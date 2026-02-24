import asyncio 
import httpx  # 新增：用於發送非同步 HTTP 請求給 n8n
from datetime import datetime, timezone # 新增：用於產生 timestamp
from fastapi import APIRouter, Depends, Request, Query, BackgroundTasks # 新增 BackgroundTasks
from typing import Optional
from src.schema.schemas import HeadphoneRequest, TrackRecommendation
from src.services.ai_service import analyze_headphone
from src.services.music_service import search_track
from src.db.redis import get_cached_recommendation, set_cached_recommendation
from src.db.mongo import log_request, mongo_manager # 新增：匯入 mongo_manager 以使用知識庫功能
from src.models.user import User
from jose import jwt
from src.core.config import settings
from src.db.postgres import get_db
from sqlalchemy.orm import Session

router = APIRouter()

# ==========================================
# 🚀 新增：非同步背景任務 (通知 n8n)
# ==========================================
async def notify_n8n_report(email: str, model: str, result_summary: str, spotify_url: str):
    """
    透過 K8s 內部網路呼叫 n8n 的 Webhook，由 n8n 處理後續的 Email 寄發。
    """
    N8N_WEBHOOK_URL = "http://n8n-service.n8n.svc.cluster.local:5678/webhook/share-search"
    async with httpx.AsyncClient() as client:
        try:
            await client.post(N8N_WEBHOOK_URL, json={
                "email": email,
                "model": model,
                "summary": result_summary,
                "spotify_url": spotify_url,
                "sent_at": datetime.now(timezone.utc).isoformat()
            }, timeout=5.0)
        except Exception as e:
            print(f"⚠️ n8n 通知發送失敗: {e}")

# ==========================================

async def get_optional_user(request: Request, db: Session = Depends(get_db)):
    auth = request.headers.get('Authorization')
    if not auth: 
        return None
    try:
        token = auth.split(" ")[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return db.query(User).filter(User.email == payload.get("sub")).first()
    except Exception: 
        return None

@router.post("", response_model=TrackRecommendation) 
async def get_recommendation(
    request: HeadphoneRequest,
    background_tasks: BackgroundTasks, # 🌟 新增：注入背景任務管理員
    user: Optional[User] = Depends(get_optional_user),
    mock: bool = Query(False, description="開啟模擬模式 (不消耗 API 配額)") 
):
    # 提取使用者資訊 (供後續儲存與寄信用)
    user_id = str(user.id) if user else None
    user_email = user.email if user else None

    # 模擬非同步 I/O
    if mock:
        await asyncio.sleep(3)  
        return TrackRecommendation(
            form_factor="Over-Ear (Mock)",
            connection="Wired (Mock)",
            release_year="2024",
            price_range="High-End",
            driver_config="Dynamic Driver",
            sound_features=["Balanced", "Warm", "Detailed"],
            analysis_bass="Deep and punchy (Simulated)",
            analysis_mids="Clear and natural (Simulated)",
            analysis_highs="Smooth extension (Simulated)",
            listening_guide="This is a mock response for load testing.",
            title=f"Mock Song for {request.model}",
            artist="Test Artist",
            comment="This analysis generated without calling Gemini API.",
            cover_url="https://via.placeholder.com/300",
            spotify_url="https://open.spotify.com",
            track_id="mock_track_id_123",
            preview_url=None
        )
        
    # 1. Cache Check
    cached = get_cached_recommendation(request.brand, request.model)
    if cached:
        await log_request("search_cache_hit", {"brand": request.brand, "model": request.model}, user_id)
        
        # 🌟 新增：即使是快取中獎，只要使用者有登入，一樣觸發寄信任務
        if user_email:
            background_tasks.add_task(
                notify_n8n_report, 
                user_email, request.model, cached.get("comment", ""), cached.get("spotify_url", "")
            )
        return TrackRecommendation(**cached)

    # 2. AI Analysis
    ai_data = await analyze_headphone(request.brand, request.model)
    should_cache = True
    
    if not ai_data:
        should_cache = False
        ai_data = {"specs": {}, "sound_features": [], "song_query": "Hotel California - Eagles", "detailed_analysis": {}, "summary": "AI Busy"}
    else:
        # 🌟 新增：將成功的 AI 原始輸出存入 MongoDB 知識庫 (作為背景任務執行)
        background_tasks.add_task(
            mongo_manager.save_earphone_knowledge, 
            request.brand, request.model, ai_data, user_id
        )

    # 3. Spotify Search
    track = await search_track(ai_data["song_query"])
    if not track:
        should_cache = False
        track = {"name": ai_data["song_query"], "artists": [{"name": "Unknown"}], "album": {"images": [{"url": ""}]}, "external_urls": {"spotify": "#"}, "id": "unknown"}

    # 4. Assembly
    analysis = ai_data.get("detailed_analysis", {})
    result = {
        "form_factor": ai_data.get("specs", {}).get("form_factor", "N/A"),
        "connection": ai_data.get("specs", {}).get("connection", "N/A"),
        "release_year": ai_data.get("specs", {}).get("year", "N/A"),
        "price_range": ai_data.get("specs", {}).get("price", "N/A"),
        "driver_config": ai_data.get("specs", {}).get("driver", "N/A"),
        "sound_features": ai_data.get("sound_features", []),
        "analysis_bass": analysis.get("bass", "N/A"),
        "analysis_mids": analysis.get("mids", "N/A"),
        "analysis_highs": analysis.get("highs", "N/A"),
        "listening_guide": analysis.get("guide", "N/A"),
        "title": track["name"],
        "artist": track["artists"][0]["name"],
        "comment": ai_data.get("summary", ""),
        "cover_url": track["album"]["images"][0]["url"] if track["album"]["images"] else "",
        "spotify_url": track["external_urls"]["spotify"],
        "track_id": track["id"],
        "preview_url": track.get("preview_url")
    }

    if should_cache:
        set_cached_recommendation(request.brand, request.model, result)
    
    await log_request("search_headphone", {"brand": request.brand, "model": request.model, "result": result["title"]}, user_id)
    
    # 🌟 新增：搜尋完成後，觸發 n8n 寄信任務
    if user_email:
        background_tasks.add_task(
            notify_n8n_report, 
            user_email, request.model, result["comment"], result["spotify_url"]
        )
        
    return TrackRecommendation(**result)