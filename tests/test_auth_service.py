import pytest
from jose import jwt
from fastapi import HTTPException
from unittest.mock import MagicMock
from src.services.auth_service import (
    verify_password, get_password_hash, create_access_token, get_current_user
)
from src.core.config import settings

def test_password_logic():
    pw = "secret123"
    hashed = get_password_hash(pw)
    assert verify_password(pw, hashed) is True
    assert verify_password("wrong", hashed) is False

def test_create_access_token():
    data = {"sub": "tester@example.com"}
    token = create_access_token(data)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "tester@example.com"

async def test_get_current_user_invalid_token():
    """Mock JWT 格式錯誤"""
    with pytest.raises(HTTPException) as exc:
        await get_current_user(token="not-a-token", db=MagicMock())
    assert exc.value.status_code == 401

async def test_get_current_user_user_not_found():
    """Mock Token 正常但 User 已不存在"""
    token = create_access_token({"sub": "ghost@example.com"})

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    with pytest.raises(HTTPException) as exc:
        await get_current_user(token=token, db=mock_db)
    assert exc.value.status_code == 401
