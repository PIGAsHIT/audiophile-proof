import logging
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from src.core.config import settings

logger = logging.getLogger("uvicorn")

class MongoDBManager:
    """
    MongoDB 管理類別 (Singleton 模式)
    負責連線、關閉、寫入稽核日誌 (Audit Logs) 以及管理 AI 知識庫
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
            logger.info("✅ MongoDB 連線成功！知識庫準備就緒。")
        except Exception as e:
            logger.error(f"❌ MongoDB 連線失敗: {e}")
            raise e

    async def close(self):
        if self.client:
            self.client.close()
            logger.info("🔌 MongoDB 連線已關閉")

    async def log_request(self, event_type: str, data: dict, user_id: str = None):
        """
        記錄 API 請求或系統事件 (Log)
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

   
    async def save_earphone_knowledge(self, brand: str, model: str, raw_data: dict, user_id: str = None):
        """
        將 Gemini 的原始 JSON 輸出存入 'earphone_knowledge' 集合。
        使用 upsert=True，如果該型號已存在則更新，不存在則建立。
        """
        if self.db is None:
            logger.warning("⚠️ MongoDB 尚未連線，無法寫入知識庫")
            return

        try:
            await self.db.earphone_knowledge.update_one(
                {"brand": brand, "model": model}, # 查詢條件：品牌 + 型號
                {
                    "$set": {
                        "raw_data": raw_data,          # 儲存完整的 AI 原始回應
                        "updated_at": datetime.now(timezone.utc), # 更新最後修改時間
                        "latest_user": user_id         # 記錄最後查詢的使用者
                    },
                    "$inc": {"search_count": 1}        # 自動計數：這支耳機被搜了幾次 (熱度分析)
                },
                upsert=True # 有就改，沒有就新增
            )
        except Exception as e:
            logger.error(f"❌ [Mongo Knowledge Error] {e}")

# 建立實例
mongo_manager = MongoDBManager()


async def connect_to_mongo():
    await mongo_manager.connect()

async def close_mongo_connection():
    await mongo_manager.close()

async def log_request(event_type: str, data: dict, user_id: str = None):
    await mongo_manager.log_request(event_type, data, user_id)

def get_database():
    return mongo_manager.db