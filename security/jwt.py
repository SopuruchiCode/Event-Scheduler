from datetime import datetime, timedelta, timezone
from jose import jwt
from config import settings
from hashlib import sha256
from db import REFRESH_TOKEN_DATABASE
from bson import ObjectId
from typing import Literal

async def create_token(user_id: str, *, scopes: list[str], ttl: timedelta, token_type: Literal["refresh", "access"]):
    now = datetime.now(timezone.utc)
    iat = int(now.timestamp())
    exp = int((now + ttl).timestamp())
    payload = {
        "sub": user_id,
        "iat": iat,
        "exp": exp,
        "type": token_type,
        "scopes": scopes,
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    if token_type == "refresh":
        hashed_token = sha256(token.encode()).hexdigest()
        db = REFRESH_TOKEN_DATABASE
        await db.insert_one(
            {
                "hashed_token": hashed_token,
                "exp_date": exp,
                "valid": True,
            }
        )

    return token

async def decode_token(token: str):
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])

async def create_access_token(user_id: str, scopes: list[str]):
    return await create_token(
        user_id,
        scopes=scopes,
        ttl=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access",
    )

async def create_refresh_token(user_id: str):
    token = await create_token(
        user_id,
        scopes=[],
        ttl=timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS),
        token_type="refresh",
    )
    return token