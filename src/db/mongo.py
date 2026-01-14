import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv
from src.core.config import settings

load_dotenv()

# --- 1. 環境變數設定 (保留你的設定) ---
MONGO_USER = os.getenv("MONGO_USER", "admin")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "secret_mongo")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_URL = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"

# --- 2. 定義全域變數 (重點！) ---
# 先設為 None，不要一開始就連線
client: AsyncIOMotorClient = None
db = None

# --- 3. 連線函式 (main.py 要呼叫這個！) ---
async def connect_to_mongo():
    global client, db
    print(f"🔗 正在連線 MongoDB: {MONGO_HOST}:{MONGO_PORT} ...")
    try:
        client = AsyncIOMotorClient(settings.MONGO_URI)
        db = client.audiophile_db
        # 測試連線是否成功
        await client.admin.command('ping')
        print("✅ MongoDB 連線成功！")
    except Exception as e:
        print(f"❌ MongoDB 連線失敗: {e}")

# --- 4. 斷線函式 (main.py 也要呼叫這個！) ---
async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("🔌 MongoDB 連線已關閉")

# --- 5. Log 功能 (保留你的功能，但稍微改一下) ---
async def log_request(event_type: str, data: dict, user_id: str = None):
    # 確保 db 已經連線才寫入，不然會噴錯
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
        # 直接使用 db.logs，不需要在最上面先定義 logs_collection
        await db.logs.insert_one(log_entry)
        # print(f"📝 Log saved: {event_type}") # debug 用，嫌吵可以註解掉
    except Exception as e:
        print(f"❌ [Log Error] {e}")

# 讓其他檔案可以取得 db 的 helper
def get_database():
    return db