import logging
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from src.core.config import settings

logger = logging.getLogger("uvicorn")

class MongoDBManager:
    """
    MongoDB 管理類別 (Singleton 模式)
    負責連線、關閉以及寫入稽核日誌 (Audit Logs)
    """
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db = None

    async def connect(self):
        logger.info(f"🔗 正在連線 MongoDB: {settings.MONGO_HOST}:{settings.MONGO_PORT} ...")
        try:
            self.client = AsyncIOMotorClient(settings.MONGO_URI)
            self.db = self.client.audiophile_db
           
            await self.client.admin.command('ping')
            logger.info("✅ MongoDB 連線成功！")
        except Exception as e:
            logger.error(f"❌ MongoDB 連線失敗: {e}")
            raise e

    async def close(self):
        if self.client:
            self.client.close()
            logger.info("🔌 MongoDB 連線已關閉")

    async def log_request(self, event_type: str, data: dict, user_id: str = None):
        """
        記錄 API 請求或系統事件
        """
        if self.db is None:
            logger.warning("⚠️ MongoDB 尚未連線，無法寫入 Log")
            return

        try:
            log_entry = {
                "event": event_type,
                "timestamp": datetime.now(timezone.utc),
                "user_id": user_id,
                "data": data
            }
            await self.db.logs.insert_one(log_entry)
        except Exception as e:
            logger.error(f"❌ [MongoDB Log Error] {e}")

mongo_manager = MongoDBManager()


async def connect_to_mongo():
    await mongo_manager.connect()

async def close_mongo_connection():
    await mongo_manager.close()

async def log_request(event_type: str, data: dict, user_id: str = None):
    await mongo_manager.log_request(event_type, data, user_id)

def get_database():
    return mongo_manager.db
