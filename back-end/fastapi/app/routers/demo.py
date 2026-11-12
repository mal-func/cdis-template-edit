from datetime import timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.dependencies import get_current_user
from app.models import DemoChartDataset, DemoStateMetric, DemoTableDataset, User
from app.responses import success
router = APIRouter(prefix="/demo", tags=["demo"])

def iso_utc(value):
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
@router.get("/map/states")
async def state_metrics(_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    rows = await db.scalars(select(DemoStateMetric).order_by(DemoStateMetric.state_name.asc()))
    return success({"states": [{"id": r.id, "stateCode": r.state_code, "stateName": r.state_name, "projectCount": r.project_count, "activityIntensity": r.activity_intensity, "createdAt": iso_utc(r.created_at), "updatedAt": iso_utc(r.updated_at)} for r in rows]})
@router.get("/charts")
async def chart_datasets(type: str | None = Query(default=None), _user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    query = select(DemoChartDataset).options(selectinload(DemoChartDataset.points)).order_by(DemoChartDataset.title.asc())
    if type: query = query.where(DemoChartDataset.chart_type == type)
    datasets = await db.scalars(query)
    return success({"datasets": [{"id": d.id, "slug": d.slug, "title": d.title, "chartType": d.chart_type, "description": d.description, "points": [{"label": p.label, "series": p.series, "value": p.value} for p in d.points]} for d in datasets]})
@router.get("/tables")
async def table_datasets(_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    datasets = await db.scalars(select(DemoTableDataset).options(selectinload(DemoTableDataset.rows)).order_by(DemoTableDataset.title.asc()))
    return success({"datasets": [{"id": d.id, "slug": d.slug, "title": d.title, "description": d.description, "rows": [r.data for r in d.rows]} for d in datasets]})
