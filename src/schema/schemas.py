from pydantic import BaseModel
from typing import List, Optional

# --- 既有的耳機推薦 Schema ---
class HeadphoneRequest(BaseModel):
    brand: str
    model: str

class TrackRecommendation(BaseModel):
    # 硬體規格
    form_factor: str
    connection: str
    release_year: str
    price_range: str
    driver_config: str
    
    # 聲音特色
    sound_features: List[str]
    
    # 詳細分析
    analysis_bass: str
    analysis_mids: str
    analysis_highs: str
    listening_guide: str

    # 歌曲資訊
    title: str
    artist: str
    comment: str
    cover_url: str
    spotify_url: str
    track_id: str
    preview_url: Optional[str] = None

# --- 使用者驗證相關 Schema ---

# 註冊與登入用的 
class UserCreate(BaseModel):
    email: str
    password: str

# 回傳給前端的使用者資訊
class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool

    class Config:
        from_attributes = True  # Pydantic 讀取 SQLAlchemy 物件

# Token 回傳格式
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
