from fastapi.testclient import TestClient
from src.main import app

# 不需要再建立 SQLite engine 了
# 不需要再 override_get_db 了
# 測試程式會自動讀取我們在 GitHub Actions 設定的環境變數，去連那個真的 Postgres

client = TestClient(app)

def test_read_root():
    """測試首頁是否活著"""
    response = client.get("/")
    assert response.status_code == 200

def test_register_user():
    """測試註冊功能"""
    # 為了避免資料庫殘留導致測試失敗，我們用一個隨機或特殊的 Email
    user_data = {"email": "ci_test_user@example.com", "password": "password123"}
    
    # 先發送請求
    response = client.post("/register", json=user_data)
    
    # 這裡要處理兩種情況：
    # 1. 如果是乾淨的 DB (CI環境)，會是 200 Success
    # 2. 如果你在本機跑第二次，可能會是 400 Already registered
    # 為了讓測試穩健，我們允許這兩種情況都算通過，或者確保每次 CI 都是乾淨的
    
    if response.status_code == 200:
        assert response.json()["msg"] == "Created successfully"
    elif response.status_code == 400:
        assert response.json()["detail"] == "Email already registered"
    else:
        # 其他狀態碼就是真的出錯了
        assert False, f"Unexpected status code: {response.status_code}, detail: {response.text}"

def test_register_duplicate_user():
    """測試重複註冊 (應該失敗)"""
    user_data = {"email": "duplicate_user@example.com", "password": "password123"}
    
    # 1. 先註冊一次 (不管成功或已存在)
    client.post("/register", json=user_data)
    
    # 2. 再註冊一次 (一定要失敗)
    response = client.post("/register", json=user_data)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"