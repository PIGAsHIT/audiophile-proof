from fastapi import APIRouter, Depends, Request
from typing import Optional
from src.schema.schemas import HeadphoneRequest, TrackRecommendation
from src.services.ai_service import analyze_headphone
from src.services.music_service import search_track
from src.db.redis import get_cached_recommendation, set_cached_recommendation
from src.db.mongo import log_request
from src.models.user import User
from jose import jwt
from src.core.config import settings
from src.db.postgres import get_db
from sqlalchemy.orm import Session

router = APIRouter()

# 輔助：嘗試取得使用者但不強制
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
async def get_recommendation(request: HeadphoneRequest, user: Optional[User] = Depends(get_optional_user)):
    # 1. Cache Check
    cached = get_cached_recommendation(request.brand, request.model)
    user_id = str(user.id) if user else None
    
    if cached:
        await log_request("search_cache_hit", {"brand": request.brand, "model": request.model}, user_id)
        return TrackRecommendation(**cached)

    # 2. AI Analysis
    ai_data = await analyze_headphone(request.brand, request.model)
    should_cache = True
    
    if not ai_data:
        should_cache = False
        ai_data = {"specs": {}, "sound_features": [], "song_query": "Hotel California - Eagles", "detailed_analysis": {}, "summary": "AI Busy"}

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
    return TrackRecommendation(**result)