"""Authentication: JWT HS256 (production) + API Key fallback (demo/MVP).

JWT payload schema:
  { "sub": "user@company.com", "role": "executive",
    "allowed_categories": ["all"], "exp": <unix> }

Role hierarchy: admin > executive > user
API Key fallback is active when JWT_SECRET env var is not set.
"""
from __future__ import annotations

import os
from typing import Literal, Optional

from fastapi import Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# ---------------------------------------------------------------------------
# Hardcoded API keys — demo / MVP only
# ---------------------------------------------------------------------------
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
ALLOWED_TOKENS: dict[str, str] = {
    "admin-token": "admin",
    "user-token": "user",
    "viewer-token": "viewer",
}

# ---------------------------------------------------------------------------
# JWT Bearer — production
# ---------------------------------------------------------------------------
_bearer = HTTPBearer(auto_error=False)
JWT_SECRET = os.getenv("JWT_SECRET", "")
JWT_ALGORITHM = "HS256"

RoleType = Literal["admin", "executive", "user", "viewer"]


def _decode_jwt(token: str) -> Optional[dict]:
    """Decode and validate a JWT. Returns payload dict or None on failure."""
    if not JWT_SECRET:
        return None
    try:
        import jwt  # PyJWT
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception:
        return None


def get_current_role(
    api_key: Optional[str] = Security(API_KEY_HEADER),
    bearer: Optional[HTTPAuthorizationCredentials] = Security(_bearer),
) -> RoleType:
    """Extract role from JWT Bearer token or API Key header.

    Precedence: JWT Bearer > X-API-Key
    Falls back to API Key when JWT_SECRET is not configured (demo mode).
    """
    # 1. Try JWT Bearer
    if bearer is not None:
        payload = _decode_jwt(bearer.credentials)
        if payload is not None:
            role = payload.get("role", "user")
            if role not in ("admin", "executive", "user", "viewer"):
                role = "user"
            return role  # type: ignore[return-value]

    # 2. Try API Key (demo fallback)
    if api_key is not None and api_key in ALLOWED_TOKENS:
        return ALLOWED_TOKENS[api_key]  # type: ignore[return-value]

    raise HTTPException(status_code=401, detail="Invalid or missing credentials")


def get_allowed_categories(
    api_key: Optional[str] = Security(API_KEY_HEADER),
    bearer: Optional[HTTPAuthorizationCredentials] = Security(_bearer),
) -> list[str]:
    """Return allowed_categories from JWT payload, or ['all'] for admin API key."""
    if bearer is not None:
        payload = _decode_jwt(bearer.credentials)
        if payload is not None:
            return payload.get("allowed_categories", ["all"])

    # API Key: admin sees everything, others see 'general' only
    if api_key in ("admin-token",):
        return ["all"]
    return ["general"]
