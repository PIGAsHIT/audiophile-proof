import pytest
import json
from unittest.mock import MagicMock, patch
from src.services.ai_service import analyze_headphone

MOCK_AI_RESPONSE = {
    "specs": { "form_factor": "Over-ear", "connection": "Wired", "year": "2009", "price": "$1500", "driver": "Ring Radiator" },
    "sound_features": ["Soundstage", "Detail"],
    "detailed_analysis": {
        "bass": "Punchy", "mids": "Natural", "highs": "Crisp", "guide": "Use a good amp"
    },
    "song_query": "Hotel California - Eagles",
    "summary": "King of soundstage."
}

async def test_analyze_headphone_success(mocker):
    """Test 1: 成功獲取分析 (Happy Path)"""
    mock_client_class = mocker.patch("src.services.ai_service.genai.Client")
    mock_instance = mock_client_class.return_value

    mock_resp = MagicMock()
    mock_resp.text = json.dumps(MOCK_AI_RESPONSE)
    mock_instance.models.generate_content.return_value = mock_resp

    result = await analyze_headphone("Sennheiser", "HD800S")

    assert result["specs"]["year"] == "2009"
    assert result["song_query"] == "Hotel California - Eagles"
    assert mock_instance.models.generate_content.called

async def test_analyze_headphone_retry_and_fail(mocker):
    """Test 2: Mock API 連續失敗 3 次 (Negative Path)"""
    mock_client_class = mocker.patch("src.services.ai_service.genai.Client")
    mock_instance = mock_client_class.return_value

    mock_instance.models.generate_content.side_effect = Exception("Gemini is down")

    mocker.patch("src.services.ai_service.time.sleep", return_value=None)

    result = await analyze_headphone("Bad", "Brand")

    assert result is None
    assert mock_instance.models.generate_content.call_count == 3

async def test_analyze_headphone_no_api_key(mocker):
    """Test 3: Mock API Key 缺失"""
    mocker.patch("src.services.ai_service.settings.GEMINI_API_KEY", "")
    
    result = await analyze_headphone("Sennheiser", "HD800S")
    
    assert result is None
