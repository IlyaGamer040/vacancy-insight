from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.models.experience import Experience as ExperienceModel
from app.schemas.experience import Experience, ExperienceCreate
from app.core.config import settings
from app.api.links import resource_links

router = APIRouter()


@router.post("/", response_model=Experience)
async def create_experience(
    experience_in: ExperienceCreate,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """Создать запись опыта"""
    existing = await db.execute(
        select(ExperienceModel).where(ExperienceModel.name == experience_in.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Experience already exists")

    db_obj = ExperienceModel(**experience_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    payload = Experience.model_validate(db_obj).model_dump()
    payload["links"] = resource_links(
        request,
        f"{settings.API_V1_PREFIX}/experiences/{db_obj.experience_id}",
        f"{settings.API_V1_PREFIX}/experiences",
    )
    return payload


@router.get("/{experience_id}", response_model=Experience)
async def read_experience(
    experience_id: int,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """Получить опыт по ID"""
    result = await db.execute(
        select(ExperienceModel).where(ExperienceModel.experience_id == experience_id)
    )
    experience = result.scalar_one_or_none()
    if not experience:
        raise HTTPException(status_code=404, detail="Experience not found")
    payload = Experience.model_validate(experience).model_dump()
    payload["links"] = resource_links(
        request,
        f"{settings.API_V1_PREFIX}/experiences/{experience.experience_id}",
        f"{settings.API_V1_PREFIX}/experiences",
    )
    return payload


@router.get("/", response_model=List[Experience])
async def read_experiences(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = Query(None, description="Фильтр по названию"),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """Получить список опыта"""
    query = select(ExperienceModel)
    if name:
        query = query.where(ExperienceModel.name.ilike(f"%{name}%"))
    query = query.order_by(ExperienceModel.order).offset(skip).limit(limit)
    result = await db.execute(query)
    experiences = result.scalars().all()
    response: List[Experience] = []
    for experience in experiences:
        payload = Experience.model_validate(experience).model_dump()
        payload["links"] = resource_links(
            request,
            f"{settings.API_V1_PREFIX}/experiences/{experience.experience_id}",
            f"{settings.API_V1_PREFIX}/experiences",
        )
        response.append(payload)
    return response
