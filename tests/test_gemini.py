import os
import pytest
from google import genai
from dotenv import load_dotenv

# 嘗試載入本地 .env (CI 環境可能沒有這檔案，這行不會報錯)
load_dotenv()

# 取得 API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ⚠️ 關鍵修正 1: 使用 pytest 的裝飾器
# 如果環境變數裡沒有 Key，這個測試函式會被直接「跳過 (Skipped)」，不會讓 CI 崩潰
@pytest.mark.skipif(not GEMINI_API_KEY, reason=" 未設定 GEMINI_API_KEY，跳過 Gemini 連線測試")
def test_gemini_connection():
    """
    測試與 Google Gemini 的連線是否正常，以及 API Key 是否有效。
    """
    
    # 1. 初始化 Client
    client = genai.Client(api_key=GEMINI_API_KEY)

    # 2. 準備測試資料
    headphone_model = "Sennheiser HD800S"
    prompt = f"請用一句話形容 {headphone_model} 的缺點。"

    print(f"\n🤖 [Test] 正在測試 Gemini API 連線...")

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )

        # 4. 驗證結果 (Assertions)
        # 確保有回傳文字
        assert response.text is not None
        # 確保回傳長度大於 0
        assert len(response.text) > 0
        
        print(f"✅ [Test] 測試成功! Gemini 回應: {response.text.strip()}")

    except Exception as e:
        # 如果 API 呼叫失敗，讓測試失敗並顯示原因
        pytest.fail(f"Gemini API 呼叫失敗: {str(e)}")