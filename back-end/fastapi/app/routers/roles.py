from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.dependencies import require_permission
from app.models import Role, User
from app.responses import success
router = APIRouter(prefix="/roles", tags=["roles"])
@router.get("")
async def list_roles(_actor: User = Depends(require_permission("roles:manage")), db: AsyncSession = Depends(get_db)):
    roles = await db.scalars(select(Role).where(Role.deleted_at.is_(None)).options(selectinload(Role.permissions)).order_by(Role.name.asc()))
    return success({"roles": [{"name": role.name, "description": role.description, "permissions": sorted({p.key for p in role.permissions})} for role in roles]})
