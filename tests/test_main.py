import uuid
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200

def test_user_registration_lifecycle():
    unique_email = f"test_{uuid.uuid4()}@example.com"
    user_data = {"email": unique_email, "password": "password123"}

    res_create = client.post("/auth/register", json=user_data)
    assert res_create.status_code == 200
    assert "success" in res_create.json().get("detail", "").lower() or res_create.status_code == 200

    res_duplicate = client.post("/auth/register", json=user_data)
    assert res_duplicate.status_code == 400
    assert res_duplicate.json()["detail"] == "Email already registered"

    login_data = {"username": unique_email, "password": "password123"}
    res_login = client.post("/auth/token", data=login_data)
    assert res_login.status_code == 200
    assert "access_token" in res_login.json()

def test_invalid_registration():
    # 測試格式錯誤的請求
    invalid_data = {"email": "not-an-email"}
    response = client.post("/auth/register", json=invalid_data)
    assert response.status_code == 422 # FastAPI 預設的驗證錯誤碼