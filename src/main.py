import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from src.db.postgres import engine, Base
from src.db.mongo import connect_to_mongo, close_mongo_connection
from contextlib import asynccontextmanager
from src.routers import auth, recommendation, user

# --- MongoDB 的生命週期管理 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🟢 這裡寫「啟動」時要做的事 (Startup)
    await connect_to_mongo()
    print("✅ MongoDB Connected! (Lifespan)")
    
    yield  
    
    await close_mongo_connection()
    print("💤 MongoDB Connection Closed. (Lifespan)")
# ---------------------------------------------

# 初始化 Postgres Table
Base.metadata.create_all(bind=engine)

# --- 初始化 App 時掛載 lifespan ---
app = FastAPI(
    title="Audiophile Proof API (Refactored)",
    lifespan=lifespan 
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus 監控
Instrumentator().instrument(app).expose(app)

# 掛載靜態檔案
os.makedirs("src/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# 註冊 Routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(recommendation.router, tags=["Recommendation"])
app.include_router(user.router, tags=["User Data"])

@app.get("/")
def read_root():
    return FileResponse('src/static/index.html')

@app.get("/health")
def health_check():
    return {"status": "ok"}