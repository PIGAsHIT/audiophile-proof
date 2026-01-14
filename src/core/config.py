from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- 1. 專案基本資訊 ---
    PROJECT_NAME: str = "Audiophile Proof"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # --- 2. 安全性設定 (Security) ---
    # 這裡沒給預設值，強迫 .env 一定要設定，否則啟動會報錯 (Fail Fast)
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- 3. 資料庫設定 (Database) ---
    # Postgres
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "audiophile_db"

    # MongoDB
    MONGO_HOST: str = "localhost"
    MONGO_PORT: int = 27017
    MONGO_USER: str = "admin"
    MONGO_PASSWORD: str = "secret_mongo"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    

    # --- 4. 外部 API 設定 ---
    GEMINI_API_KEY: Optional[str] = None
    SPOTIFY_CLIENT_ID: Optional[str] = None
    SPOTIFY_CLIENT_SECRET: Optional[str] = None
    SPOTIFY_REDIRECT_URI: str = "http://127.0.0.1:8000/callback"

    # --- 5. Pydantic 設定 (V2 新寫法) ---
    model_config = SettingsConfigDict(
        # 指定讀取的檔案名稱
        env_file=".env",
        # 檔案編碼
        env_file_encoding="utf-8",
        # 關鍵！設為 'ignore' 可以忽略 .env 裡多餘的變數，解決你的報錯
        extra="ignore",
        # 讓變數不分大小寫 (db_host 和 DB_HOST 都可以通)
        case_sensitive=False
    )

    # --- helper property: 自動組裝連線字串 ---
    # 這樣你在 db/postgres.py 只要呼叫 settings.SQLALCHEMY_DATABASE_URI 即可
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def MONGO_URI(self) -> str:
        return f"mongodb://{self.MONGO_USER}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}/?authSource=admin"

# 初始化設定
settings = Settings()