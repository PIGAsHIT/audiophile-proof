import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

# 匯入你定義的資料庫與路由組件
from src.db.postgres import engine, Base
from src.db.mongo import connect_to_mongo, close_mongo_connection
from src.routers import auth, recommendation, user

# 設定 Logging，方便在 K8s Log 中追蹤啟動狀況
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

# --- 應用程式生命週期管理 (Lifespan) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🟢 【Startup】啟動時執行
    logger.info("🚀 Starting up FastAPI Application...")

    # 1. 初始化 PostgreSQL 資料表
    # 解決你遇到的 "relation 'users' does not exist" 報錯
    try:
        logger.info("💾 Initializing PostgreSQL tables...")
        # 注意：Base.metadata.create_all 是同步操作
        Base.metadata.create_all(bind=engine)
        logger.info("✅ PostgreSQL tables initialized successfully.")
    except Exception as e:
        logger.error(f"❌ PostgreSQL initialization failed: {e}")
        # 在 DevOps 實踐中，若基礎設施未就緒，通常讓它噴錯以觸發 K8s 重啟機制

    # 2. 連線 MongoDB
    try:
        logger.info("🔗 Connecting to MongoDB...")
        await connect_to_mongo()
        logger.info("✅ MongoDB Connected!")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")

    yield  # --- 應用程式運行中 ---

    # 🔴 【Shutdown】關閉時執行
    logger.info("🛑 Shutting down Application...")
    await close_mongo_connection()
    logger.info("💤 MongoDB Connection Closed.")

# --- 初始化 FastAPI App ---
app = FastAPI(
    title="Audiophile Proof API (DevOps Optimized)",
    description="具備 PostgreSQL, MongoDB, Redis 與監控功能的後端架構",
    lifespan=lifespan 
)

# --- Middleware 設定 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 監控與維運 (Prometheus) ---
# 這是你提到的 DevOps 技術棧中重要的監控環節
Instrumentator().instrument(app).expose(app)

# --- 靜態檔案與目錄處理 ---
# 確保靜態目錄存在，避免啟動時報錯
os.makedirs("src/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# --- 註冊 Routers ---
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(recommendation.router, prefix="/recommend", tags=["Recommendation"])
app.include_router(user.router, prefix="/user", tags=["User Data"])

@app.get("/")
async def read_root():
    """入口首頁"""
    index_path = 'src/static/index.html'
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Welcome to Audiophile Proof API. Please visit /docs for API documentation."}

@app.get("/health")
async def health_check():
    """K8s Liveness/Readiness Probe 專用路徑"""
    return {"status": "ok", "version": "1.0.0"}