from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.dependencies import require_permission, safe_user, require_csrf
from app.models import Role, User
from app.responses import success
from app.schemas import SetUserRolesRequest
router = APIRouter(prefix="/users", tags=["users"])
@router.get("")
async def list_users(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0),
    _actor: User = Depends(require_permission("users:read")), db: AsyncSession = Depends(get_db)):
    base = select(User).where(User.deleted_at.is_(None))
    total = await db.scalar(select(func.count()).select_from(base.subquery()))
    rows = await db.scalars(base.options(selectinload(User.roles).selectinload(Role.permissions)).order_by(User.created_at.desc()).limit(limit).offset(offset))
    return success({"users": [safe_user(user) for user in rows], "pagination": {"limit": limit, "offset": offset, "total": total or 0}})
@router.put("/{user_id}/roles")
async def set_roles(user_id: str, payload: SetUserRolesRequest, actor: User = Depends(require_permission("roles:manage")),
    _csrf: None = Depends(require_csrf), db: AsyncSession = Depends(get_db)):
    if actor.id == user_id: raise HTTPException(403, detail=("FORBIDDEN", "You can't change your own roles. Ask another administrator."))
    target = await db.scalar(select(User).where(User.id == user_id, User.deleted_at.is_(None)).options(selectinload(User.roles).selectinload(Role.permissions)))
    if target is None: raise HTTPException(404, detail=("NOT_FOUND", "User not found."))
    roles = list((await db.scalars(select(Role).where(Role.name.in_(payload.roles), Role.deleted_at.is_(None)))).all())
    known = {role.name for role in roles}
    unknown = [name for name in payload.roles if name not in known]
    if unknown: raise HTTPException(400, detail=("VALIDATION_ERROR", f"Unknown role(s): {', '.join(unknown)}."))
    target.roles = roles
    await db.commit()
    target = await db.scalar(select(User).where(User.id == user_id).options(selectinload(User.roles).selectinload(Role.permissions)))
    return success({"user": safe_user(target)})
