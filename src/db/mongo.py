import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv
from src.core.config import settings

load_dotenv()

MONGO_USER = os.getenv("MONGO_USER", "admin")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "secret_mongo")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_URL = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"


client: AsyncIOMotorClient = None
db = None


async def connect_to_mongo():
    global client, db
    print(f"🔗 正在連線 MongoDB: {MONGO_HOST}:{MONGO_PORT} ...")
    try:
        client = AsyncIOMotorClient(settings.MONGO_URI)
        db = client.audiophile_db
        
        await client.admin.command('ping')
        print("✅ MongoDB 連線成功！")
    except Exception as e:
        print(f"❌ MongoDB 連線失敗: {e}")

async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("🔌 MongoDB 連線已關閉")

async def log_request(event_type: str, data: dict, user_id: str = None):
    
    if db is None:
        print("⚠️ Warning: MongoDB 尚未連線，無法寫入 Log")
        return

    try:
        log_entry = {
            "event": event_type,
            "timestamp": datetime.utcnow(),
            "user_id": user_id,
            "data": data
        }
       
        await db.logs.insert_one(log_entry)
        
    except Exception as e:
        print(f"❌ [Log Error] {e}")

def get_database():
    return db
