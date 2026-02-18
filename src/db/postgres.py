from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings  # <--- 1. 引入唯一的真理

DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  
    pool_size=10,
    max_overflow=20
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
