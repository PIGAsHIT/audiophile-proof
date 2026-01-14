import json
import time
from google import genai
from google.genai import types
from src.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

async def analyze_headphone(brand: str, model: str):
    try:
        if not settings.GEMINI_API_KEY:
            print("警告: 未設定 GEMINI_API_KEY")
            return None
            
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
    except Exception as e:
        print(f"Gemini Client 初始化失敗: {e}")
        return None
    
    prompt = f"""
    使用者正在查詢耳機：{brand} {model}。
    請扮演一位「想推別人入坑的耳機發燒友」，提供深度的聽感分析。
    請回傳 JSON (不要 Markdown):
    {{
        "specs": {{ "form_factor": "...", "connection": "...", "year": "...", "price": "...", "driver": "..." }},
        "sound_features": ["特色1", "特色2"],
        "detailed_analysis": {{
            "bass": "低頻描述...", "mids": "中頻描述...", "highs": "高頻描述...", "guide": "試聽指南..."
        }},
        "song_query": "Song Name - Artist",
        "summary": "一句話總評這支耳機的特點和不足"
    }}
    """
    
    for attempt in range(3):
        try:
            # print(f"AI 分析中... (Attempt {attempt+1})")
            resp = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return json.loads(resp.text)
        except Exception as e:
            print(f"Gemini Error: {e}")
            if attempt == 2: 
                return None 
            time.sleep(1)
    return None