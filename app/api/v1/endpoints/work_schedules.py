from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.models.work_schedule import WorkSchedule as WorkScheduleModel
from app.schemas.work_schedule import WorkSchedule, WorkScheduleCreate
from app.core.config import settings
from app.api.links import resource_links

router = APIRouter()


@router.post("/", response_model=WorkSchedule)
async def create_work_schedule(
    work_schedule_in: WorkScheduleCreate,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """Создать график работы"""
    existing = await db.execute(
        select(WorkScheduleModel).where(WorkScheduleModel.name == work_schedule_in.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Work schedule already exists")

    db_obj = WorkScheduleModel(**work_schedule_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    payload = WorkSchedule.model_validate(db_obj).model_dump()
    payload["links"] = resource_links(
        request,
        f"{settings.API_V1_PREFIX}/work-schedules/{db_obj.work_schedule_id}",
        f"{settings.API_V1_PREFIX}/work-schedules",
    )
    return payload


@router.get("/{work_schedule_id}", response_model=WorkSchedule)
async def read_work_schedule(
    work_schedule_id: int,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """Получить график работы по ID"""
    result = await db.execute(
        select(WorkScheduleModel).where(WorkScheduleModel.work_schedule_id == work_schedule_id)
    )
    work_schedule = result.scalar_one_or_none()
    if not work_schedule:
        raise HTTPException(status_code=404, detail="Work schedule not found")
    payload = WorkSchedule.model_validate(work_schedule).model_dump()
    payload["links"] = resource_links(
        request,
        f"{settings.API_V1_PREFIX}/work-schedules/{work_schedule.work_schedule_id}",
        f"{settings.API_V1_PREFIX}/work-schedules",
    )
    return payload


@router.get("/", response_model=List[WorkSchedule])
async def read_work_schedules(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = Query(None, description="Фильтр по названию"),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """Получить список графиков работы"""
    query = select(WorkScheduleModel)
    if name:
        query = query.where(WorkScheduleModel.name.ilike(f"%{name}%"))
    query = query.order_by(WorkScheduleModel.name).offset(skip).limit(limit)
    result = await db.execute(query)
    work_schedules = result.scalars().all()
    response: List[WorkSchedule] = []
    for work_schedule in work_schedules:
        payload = WorkSchedule.model_validate(work_schedule).model_dump()
        payload["links"] = resource_links(
            request,
            f"{settings.API_V1_PREFIX}/work-schedules/{work_schedule.work_schedule_id}",
            f"{settings.API_V1_PREFIX}/work-schedules",
        )
        response.append(payload)
    return response
