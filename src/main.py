import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from src.db.postgres import engine, Base
from src.db.mongo import connect_to_mongo, close_mongo_connection
from src.routers import auth, recommendation, user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    logger.info("🚀 Starting up FastAPI Application...")

    
    try:
        logger.info("💾 Initializing PostgreSQL tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ PostgreSQL tables initialized successfully.")
    except Exception as e:
        logger.error(f"❌ PostgreSQL initialization failed: {e}")
        

    
    try:
        logger.info("🔗 Connecting to MongoDB...")
        await connect_to_mongo()
        logger.info("✅ MongoDB Connected!")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")

    yield  

    
    logger.info("🛑 Shutting down Application...")
    await close_mongo_connection()
    logger.info("💤 MongoDB Connection Closed.")

app = FastAPI(
    title="Audiophile Proof API",
    description="具備 PostgreSQL, MongoDB, Redis 與監控功能的後端架構",
    lifespan=lifespan 
)

'''app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)'''

Instrumentator().instrument(app).expose(app)

os.makedirs("src/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

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
