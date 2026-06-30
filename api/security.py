from __future__ import annotations

from fastapi import Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from typing import Literal

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
ALLOWED_TOKENS = {
    "admin-token": "admin",
    "user-token": "user",
    "viewer-token": "viewer",
}


def get_current_role(api_key: str = Security(API_KEY_HEADER)) -> Literal["admin", "user", "viewer"]:
    if api_key is None or api_key not in ALLOWED_TOKENS:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return ALLOWED_TOKENS[api_key]
