import pytest
from sqlalchemy.orm import sessionmaker
from src.db.postgres import engine, Base

SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
   
    Base.metadata.create_all(bind=engine)
    
    yield
    
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
  
    connection = engine.connect()
    
    transaction = connection.begin()

    session = SessionTesting(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
