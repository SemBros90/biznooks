import os
from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import Header, HTTPException

JWT_SECRET = os.getenv('JWT_SECRET', 'dev-secret')
JWT_ALGO = os.getenv('JWT_ALGO', 'HS256')


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = {"sub": subject}
    if expires_delta:
        to_encode.update({"exp": datetime.utcnow() + expires_delta})
    else:
        to_encode.update({"exp": datetime.utcnow() + timedelta(hours=1)})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGO)


def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except Exception:
        raise HTTPException(status_code=401, detail='Invalid token')


def get_current_user_optional(authorization: Optional[str] = Header(default=None)):
    """Optional auth dependency for FastAPI endpoints.

    If `Authorization` header present as `Bearer <token>`, verifies and returns claims dict.
    Otherwise returns None.
    """
    if not authorization:
        return None
    if not authorization.lower().startswith('bearer '):
        raise HTTPException(status_code=401, detail='Invalid auth header')
    token = authorization.split(None, 1)[1]
    claims = verify_token(token)
    return claims


def get_current_user(authorization: Optional[str] = Header(default=None)):
    """Required auth dependency: returns claims dict or raises 401."""
    if not authorization or not authorization.lower().startswith('bearer '):
        raise HTTPException(status_code=401, detail='Missing Authorization header')
    token = authorization.split(None, 1)[1]
    claims = verify_token(token)
    return claims


def require_role(claims: dict, role: str) -> bool:
    """Simple RBAC check: expects `role` claim or `roles` list in token claims."""
    if not claims:
        return False
    if claims.get('role') == role:
        return True
    roles = claims.get('roles') or []
    return role in roles
