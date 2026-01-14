from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from pydantic import BaseModel
from src.models.user import User
from src.services.auth_service import get_current_user
from src.db.mongo import get_database

router = APIRouter()

class FavoriteRequest(BaseModel):
    track_id: str
    title: str
    artist: str
    cover_url: str
    spotify_url: str

@router.post("/favorites")
async def add_favorite(fav: FavoriteRequest, user: User = Depends(get_current_user), db = Depends(get_database)):
    fav_col = db["favorites"]
    
    if await fav_col.find_one({"user_id": str(user.id), "track_id": fav.track_id}):
        return {"status": "exists"}
    
    data = fav.model_dump()
    data.update({"user_id": str(user.id), "added_at": datetime.utcnow()})
    
    await fav_col.insert_one(data)
    return {"status": "added"}

@router.get("/favorites")
async def get_favorites(user: User = Depends(get_current_user), db = Depends(get_database)):
    fav_col = db["favorites"]
    cursor = fav_col.find({"user_id": str(user.id)})
    favorites = await cursor.to_list(length=100)

    for fav in favorites:
        if "_id" in fav:
            fav["_id"] = str(fav["_id"])
    return favorites

@router.delete("/favorites/{track_id}")
async def remove_favorite(track_id: str, user: User = Depends(get_current_user), db = Depends(get_database)):
    fav_col = db["favorites"]
    res = await fav_col.delete_one({"user_id": str(user.id), "track_id": track_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return {"status": "removed"}

@router.get("/favorites/check/{track_id}")
async def check_fav(track_id: str, user: User = Depends(get_current_user), db = Depends(get_database)):
    fav_col = db["favorites"]
    exists = await fav_col.find_one({"user_id": str(user.id), "track_id": track_id})
    return {"is_favorited": bool(exists)}

@router.get("/history")
async def get_history(user: User = Depends(get_current_user), db = Depends(get_database)):
    log_col = db["logs"]
    cursor = log_col.find({"user_id": str(user.id), "event": "search_headphone"}).sort("timestamp", -1).limit(20)
    results = []
    async for doc in cursor:
        results.append({
            "brand": doc["data"].get("brand"),
            "model": doc["data"].get("model"),
            "result_song": doc["data"].get("result"),
            "timestamp": doc.get("timestamp", datetime.utcnow()).strftime("%Y-%m-%d %H:%M")
        })
    return results