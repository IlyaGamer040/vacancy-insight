from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.models.work_format import WorkFormat as WorkFormatModel
from app.schemas.work_format import WorkFormat, WorkFormatCreate

router = APIRouter()


@router.post("/", response_model=WorkFormat)
async def create_work_format(
    work_format_in: WorkFormatCreate,
    db: AsyncSession = Depends(get_db)
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
    return db_obj


@router.get("/{work_format_id}", response_model=WorkFormat)
async def read_work_format(
    work_format_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить формат работы по ID"""
    result = await db.execute(
        select(WorkFormatModel).where(WorkFormatModel.work_format_id == work_format_id)
    )
    work_format = result.scalar_one_or_none()
    if not work_format:
        raise HTTPException(status_code=404, detail="Work format not found")
    return work_format


@router.get("/", response_model=List[WorkFormat])
async def read_work_formats(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = Query(None, description="Фильтр по названию"),
    db: AsyncSession = Depends(get_db)
):
    """Получить список форматов работы"""
    query = select(WorkFormatModel)
    if name:
        query = query.where(WorkFormatModel.name.ilike(f"%{name}%"))
    query = query.order_by(WorkFormatModel.name).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
