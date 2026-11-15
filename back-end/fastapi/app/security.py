from datetime import datetime, timedelta, timezone
from hashlib import sha256
from secrets import token_hex
import bcrypt
import jwt
from app.config import settings
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=settings.bcrypt_salt_rounds)).decode("utf-8")
def verify_password(password: str, encoded: str) -> bool:
    try: return bcrypt.checkpw(password.encode("utf-8"), encoded.encode("utf-8"))
    except (ValueError, TypeError): return False
def sign_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": user_id, "iat": now, "exp": now + timedelta(seconds=settings.jwt_access_expires_in_seconds)}, settings.jwt_access_secret, algorithm="HS256")
def verify_access_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_access_secret, algorithms=["HS256"])
def new_refresh_token() -> str: return token_hex(32)
def hash_refresh_token(token: str) -> str: return sha256(token.encode()).hexdigest()
def refresh_expiry() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=settings.refresh_token_expires_in_days)
