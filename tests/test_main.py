import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.db.postgres import get_db  

client = TestClient(app)

@pytest.fixture(autouse=True)
def override_get_db(db_session):
   
    app.dependency_overrides[get_db] = lambda: db_session
    yield
    
    app.dependency_overrides.clear()


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200

def test_user_registration_lifecycle():
    user_data = {"email": "tester@example.com", "password": "password123"}

    res_create = client.post("/auth/register", json=user_data)
    assert res_create.status_code == 200
    
    assert "successfully" in res_create.json().get("msg", "")

    res_duplicate = client.post("/auth/register", json=user_data)
    assert res_duplicate.status_code == 400
    assert res_duplicate.json()["detail"] == "Email already registered"

    login_data = {"username": "tester@example.com", "password": "password123"}
    res_login = client.post("/auth/token", data=login_data)
    assert res_login.status_code == 200
    assert "access_token" in res_login.json()

def test_invalid_registration():

    invalid_data = {"email": "not-an-email"}
    response = client.post("/auth/register", json=invalid_data)
    assert response.status_code == 422
