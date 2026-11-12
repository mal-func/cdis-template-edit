from datetime import datetime, timezone, timedelta
from secrets import token_hex
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user, require_csrf, safe_user
from app.models import RefreshToken, Role, User
from app.limiting import limiter, login_rate_key
from app.client_ip import client_ip
from app.responses import success
from app.schemas import LoginRequest, RegisterRequest
from app.security import hash_password, hash_refresh_token, new_refresh_token, refresh_expiry, sign_access_token, verify_password
router = APIRouter(prefix="/auth", tags=["authentication"])
REFRESH_PATH = "/api/v1/auth"
def request_meta(request: Request):
    return (client_ip(request), request.headers.get("user-agent", "")[:255])
def set_cookies(response: Response, access: str, refresh: str):
    secure = settings.secure_cookies
    response.set_cookie("access_token", access, httponly=True, secure=secure, samesite="lax", path="/", max_age=settings.jwt_access_expires_in_seconds)
    response.set_cookie("refresh_token", refresh, httponly=True, secure=secure, samesite="lax", path=REFRESH_PATH, max_age=settings.refresh_token_expires_in_days * 86400)
    response.set_cookie("csrf_token", token_hex(24), httponly=False, secure=secure, samesite="lax", path="/", max_age=settings.refresh_token_expires_in_days * 86400)
def clear_cookies(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path=REFRESH_PATH)
    response.delete_cookie("csrf_token", path="/")
@router.get("/options")
async def options():
    return success({"selfRegistration": settings.allow_self_registration})
@router.post("/register")
async def register(payload: RegisterRequest, request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    if not settings.allow_self_registration:
        raise HTTPException(403, detail=("FORBIDDEN", "Self-registration is turned off. Ask an administrator for an account."))
    if await db.scalar(select(User.id).where(User.email == payload.email, User.deleted_at.is_(None))):
        raise HTTPException(409, detail=("CONFLICT", "An account with this email already exists."))
    role = await db.scalar(select(Role).where(Role.name == "user", Role.deleted_at.is_(None)))
    if role is None:
        raise HTTPException(500, detail=("INTERNAL_ERROR", "Default role 'user' is missing. Run the seed command."))
    user = User(id=str(uuid4()), email=payload.email, name=payload.name, password_hash=hash_password(payload.password))
    user.roles.append(role)
    db.add(user)
    await db.flush()
    access, refresh = sign_access_token(user.id), new_refresh_token()
    ip, agent = request_meta(request)
    db.add(RefreshToken(id=str(uuid4()), user_id=user.id, token_hash=hash_refresh_token(refresh), expires_at=refresh_expiry(), created_by_ip=ip, user_agent=agent))
    await db.commit()
    set_cookies(response, access, refresh)
    return success({"user": safe_user(user)}, 201, response=response)
@router.post("/login")
@limiter.limit("10/15minutes", key_func=login_rate_key)
async def login(payload: LoginRequest, request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == payload.email, User.deleted_at.is_(None)).options(selectinload(User.roles).selectinload(Role.permissions)))
    if user is None:
        raise HTTPException(401, detail=("UNAUTHORIZED", "Invalid email or password."))
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if user.locked_until and user.locked_until > now:
        raise HTTPException(403, detail=("FORBIDDEN", "This account is temporarily locked due to repeated failed sign-in attempts. Please try again later."))
    if not verify_password(payload.password, user.password_hash):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= settings.account_lockout_max_attempts:
            user.locked_until = now + timedelta(minutes=settings.account_lockout_duration_minutes)
        await db.commit()
        raise HTTPException(401, detail=("UNAUTHORIZED", "Invalid email or password."))
    user.failed_login_attempts, user.locked_until = 0, None
    ip, agent = request_meta(request)
    access, refresh = sign_access_token(user.id), new_refresh_token()
    db.add(RefreshToken(id=str(uuid4()), user_id=user.id, token_hash=hash_refresh_token(refresh), expires_at=refresh_expiry(), created_by_ip=ip, user_agent=agent))
    await db.commit()
    set_cookies(response, access, refresh)
    return success({"user": safe_user(user)}, response=response)
@router.post("/refresh")
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db), _csrf: None = Depends(require_csrf)):
    raw = request.cookies.get("refresh_token")
    if not raw: raise HTTPException(401, detail=("UNAUTHORIZED", "No session found."))
    token = await db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(raw)).with_for_update())
    if token is None: raise HTTPException(401, detail=("UNAUTHORIZED", "Invalid session. Please sign in again."))
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if token.revoked_at:
        await db.execute(update(RefreshToken).where(RefreshToken.user_id == token.user_id, RefreshToken.revoked_at.is_(None)).values(revoked_at=now))
        await db.commit()
        raise HTTPException(401, detail=("UNAUTHORIZED", "This session is no longer valid. Please sign in again."))
    if token.expires_at < now: raise HTTPException(401, detail=("UNAUTHORIZED", "Your session has expired. Please sign in again."))
    user = await db.scalar(select(User).where(User.id == token.user_id, User.deleted_at.is_(None)).options(selectinload(User.roles).selectinload(Role.permissions)))
    if user is None: raise HTTPException(401, detail=("UNAUTHORIZED", "Invalid session. Please sign in again."))
    ip, agent = request_meta(request)
    access, new_raw = sign_access_token(user.id), new_refresh_token()
    replacement = RefreshToken(id=str(uuid4()), user_id=user.id, token_hash=hash_refresh_token(new_raw), expires_at=refresh_expiry(), created_by_ip=ip, user_agent=agent)
    db.add(replacement)
    await db.flush()
    token.revoked_at, token.replaced_by_token_id = now, replacement.id
    await db.commit()
    set_cookies(response, access, new_raw)
    return success({"user": safe_user(user)}, response=response)
@router.post("/logout")
async def logout(request: Request, response: Response, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user), _csrf: None = Depends(require_csrf)):
    raw = request.cookies.get("refresh_token")
    if raw:
        token = await db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(raw)))
        if token and token.revoked_at is None:
            token.revoked_at = datetime.now(timezone.utc).replace(tzinfo=None)
            await db.commit()
    clear_cookies(response)
    return success({"message": "Logged out successfully."}, response=response)
@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return success({"user": safe_user(user)})
