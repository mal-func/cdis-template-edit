import json
from slowapi import Limiter
from app.client_ip import client_ip

def login_rate_key(request) -> str:
    email = "unknown"
    body = getattr(request, "_body", b"")
    if body:
        try:
            payload = json.loads(body.decode("utf-8"))
            if isinstance(payload, dict) and isinstance(payload.get("email"), str):
                email = payload["email"].strip().lower()
        except (UnicodeDecodeError, json.JSONDecodeError):
            pass
    return f"{client_ip(request)}:{email}"

limiter = Limiter(key_func=client_ip, default_limits=["100/15minutes"])
