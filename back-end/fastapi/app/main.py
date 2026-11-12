from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.database import engine
from app.limiting import limiter
from app.routers import auth, demo, health, roles, users
@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    await engine.dispose()
app = FastAPI(title="CDIS API", version="1.0.0", lifespan=lifespan)
app.state.limiter = limiter
@app.exception_handler(RateLimitExceeded)
async def rate_limit_error(_request: Request, _exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"success": False, "error": {"code": "RATE_LIMITED", "message": "Too many requests. Please try again later."}})
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(CORSMiddleware, allow_origins=[settings.cors_origin], allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"])
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
    response.headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")
    response.headers.setdefault("Origin-Agent-Cluster", "?1")
    response.headers.setdefault("X-DNS-Prefetch-Control", "off")
    response.headers.setdefault("X-Download-Options", "noopen")
    response.headers.setdefault("X-Permitted-Cross-Domain-Policies", "none")
    response.headers.setdefault("X-XSS-Protection", "0")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    if settings.secure_cookies:
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response
@app.exception_handler(StarletteHTTPException)
async def http_error(_request: Request, exc: StarletteHTTPException):
    if isinstance(exc.detail, tuple) and len(exc.detail) == 2:
        code, message = exc.detail
    else:
        code, message = ("ROUTE_NOT_FOUND", f"No route found for {_request.method} {_request.url.path}") if exc.status_code == 404 else ("HTTP_ERROR", str(exc.detail))
    return JSONResponse(status_code=exc.status_code, content={"success": False, "error": {"code": code, "message": message}}, headers=exc.headers)
@app.exception_handler(RequestValidationError)
async def validation_error(_request: Request, exc: RequestValidationError):
    first = exc.errors()[0] if exc.errors() else {}
    message = str(first.get("msg", "Invalid request."))
    return JSONResponse(status_code=400, content={"success": False, "error": {"code": "VALIDATION_ERROR", "message": message}})
@app.exception_handler(Exception)
async def unhandled_error(_request: Request, _exc: Exception):
    return JSONResponse(status_code=500, content={"success": False, "error": {"code": "INTERNAL_ERROR", "message": "Something went wrong. Please try again later."}})
app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(roles.router, prefix="/api/v1")
app.include_router(demo.router, prefix="/api/v1")
