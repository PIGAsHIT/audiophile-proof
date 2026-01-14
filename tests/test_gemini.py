import os
import pytest
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

TEST_MODEL = "gemini-2.5-flash" 

@pytest.mark.skipif(not GEMINI_API_KEY, reason="Skipping: GEMINI_API_KEY not found")
@pytest.mark.asyncio
async def test_gemini_connection(): # 💡 修正：加上 async
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # 使用 Sennheiser HD800S 測試 AI 描述能力
    headphone_model = "Sennheiser HD800S"
    test_prompt = f"Explain the soundstage of {headphone_model} in one short sentence."

    try:
        
        response = client.models.generate_content(
            model=TEST_MODEL, 
            contents=test_prompt
        )

        assert response is not None, "API returned None"
        res_text = response.text if hasattr(response, 'text') else response.candidates[0].content.parts[0].text
        assert len(res_text.strip()) > 0, "Response text is empty"
        print(f"\n[Gemini Test Success] Response: {res_text.strip()}")

    except Exception as e:
        pytest.fail(f"Gemini API connection failed: {e}")