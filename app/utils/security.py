import hashlib
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt(user_id: int, is_admin: bool) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_expire_minutes
    )
    payload = {"user_id": user_id, "is_admin": is_admin, "exp": expire}
    token = jwt.encode(payload, settings.secret_key, algorithm="HS256")
    return token


def decode_jwt(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        return None


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def compute_signature(data: dict, secret_key: str) -> str:
    sorted_keys = sorted(data.keys())
    raw = "".join(str(data[k]) for k in sorted_keys) + secret_key
    return hashlib.sha256(raw.encode()).hexdigest()
