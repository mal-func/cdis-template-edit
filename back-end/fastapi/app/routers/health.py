from datetime import datetime, timezone
from time import monotonic
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.responses import success

router = APIRouter()
_STARTED_AT = monotonic()

@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    # Match Express liveness + readiness: don't report healthy if MySQL is down.
    await db.execute(text("SELECT 1"))
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return success({
        "status": "ok",
        "uptimeSeconds": round(monotonic() - _STARTED_AT),
        "timestamp": timestamp,
    })
