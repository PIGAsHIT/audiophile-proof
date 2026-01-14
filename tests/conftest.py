import pytest
from src.db.postgres import engine, Base

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # 🚀 在 CI 測試開始前，自動建立所有資料表
    Base.metadata.create_all(bind=engine)
    yield
    