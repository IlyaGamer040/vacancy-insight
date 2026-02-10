from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.models.work_format import WorkFormat as WorkFormatModel
from app.schemas.work_format import WorkFormat, WorkFormatCreate
from app.core.config import settings
from app.api.links import resource_links

router = APIRouter()


@router.post("/", response_model=WorkFormat)
async def create_work_format(
    work_format_in: WorkFormatCreate,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """Создать формат работы"""
    existing = await db.execute(
        select(WorkFormatModel).where(WorkFormatModel.name == work_format_in.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Work format already exists")

    db_obj = WorkFormatModel(**work_format_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    payload = WorkFormat.model_validate(db_obj).model_dump()
    payload["links"] = resource_links(
        request,
        f"{settings.API_V1_PREFIX}/work-formats/{db_obj.work_format_id}",
        f"{settings.API_V1_PREFIX}/work-formats",
    )
    return payload


@router.get("/{work_format_id}", response_model=WorkFormat)
async def read_work_format(
    work_format_id: int,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """Получить формат работы по ID"""
    result = await db.execute(
        select(WorkFormatModel).where(WorkFormatModel.work_format_id == work_format_id)
    )
    work_format = result.scalar_one_or_none()
    if not work_format:
        raise HTTPException(status_code=404, detail="Work format not found")
    payload = WorkFormat.model_validate(work_format).model_dump()
    payload["links"] = resource_links(
        request,
        f"{settings.API_V1_PREFIX}/work-formats/{work_format.work_format_id}",
        f"{settings.API_V1_PREFIX}/work-formats",
    )
    return payload


@router.get("/", response_model=List[WorkFormat])
async def read_work_formats(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = Query(None, description="Фильтр по названию"),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """Получить список форматов работы"""
    query = select(WorkFormatModel)
    if name:
        query = query.where(WorkFormatModel.name.ilike(f"%{name}%"))
    query = query.order_by(WorkFormatModel.name).offset(skip).limit(limit)
    result = await db.execute(query)
    work_formats = result.scalars().all()
    response: List[WorkFormat] = []
    for work_format in work_formats:
        payload = WorkFormat.model_validate(work_format).model_dump()
        payload["links"] = resource_links(
            request,
            f"{settings.API_V1_PREFIX}/work-formats/{work_format.work_format_id}",
            f"{settings.API_V1_PREFIX}/work-formats",
        )
        response.append(payload)
    return response
