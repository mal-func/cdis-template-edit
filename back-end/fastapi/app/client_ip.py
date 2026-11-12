from fastapi import Request
from app.config import settings
def client_ip(request: Request) -> str:
    direct = request.client.host if request.client else "unknown"
    if settings.trust_proxy_hops <= 0:
        return direct
    forwarded = [value.strip() for value in request.headers.get("x-forwarded-for", "").split(",") if value.strip()]
    if len(forwarded) >= settings.trust_proxy_hops:
        return forwarded[-settings.trust_proxy_hops]
    return direct
