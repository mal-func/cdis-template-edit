from fastapi import Depends, HTTPException, Request
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import Role, User
from app.security import verify_access_token
def safe_user(user: User) -> dict:
    roles = [role.name for role in user.roles if role.deleted_at is None]
    permissions = sorted({permission.key for role in user.roles if role.deleted_at is None for permission in role.permissions})
    return {"id": user.id, "email": user.email, "name": user.name, "roles": roles, "permissions": permissions}
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    if not token: raise HTTPException(401, detail=("UNAUTHORIZED", "Authentication is required."))
    try: subject = verify_access_token(token).get("sub")
    except InvalidTokenError: raise HTTPException(401, detail=("UNAUTHORIZED", "Your session is invalid or has expired.")) from None
    result = await db.execute(select(User).where(User.id == subject, User.deleted_at.is_(None)).options(selectinload(User.roles).selectinload(Role.permissions)))
    user = result.scalar_one_or_none()
    if user is None: raise HTTPException(401, detail=("UNAUTHORIZED", "Your session is invalid or has expired."))
    return user
def require_permission(*required: str):
    async def guard(user: User = Depends(get_current_user)) -> User:
        if not set(safe_user(user)["permissions"]).intersection(required):
            raise HTTPException(403, detail=("FORBIDDEN", "You do not have permission to perform this action."))
        return user
    return guard
async def require_csrf(request: Request) -> None:
    cookie, header = request.cookies.get("csrf_token"), request.headers.get("x-csrf-token")
    if not cookie or not header or cookie != header:
        raise HTTPException(403, detail=("FORBIDDEN", "Missing or invalid CSRF token."))
