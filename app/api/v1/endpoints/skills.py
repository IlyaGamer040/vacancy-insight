from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.models.skill import Skill as SkillModel
from app.schemas.skill import Skill, SkillCreate
from app.core.config import settings
from app.api.links import resource_links

router = APIRouter()


@router.post("/", response_model=Skill)
async def create_skill(
    skill_in: SkillCreate,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """Создать навык"""
    db_obj = SkillModel(**skill_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    payload = Skill.model_validate(db_obj).model_dump()
    payload["links"] = resource_links(
        request,
        f"{settings.API_V1_PREFIX}/skills/{db_obj.skill_id}",
        f"{settings.API_V1_PREFIX}/skills",
    )
    return payload


@router.get("/{skill_id}", response_model=Skill)
async def read_skill(
    skill_id: int,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """Получить навык по ID"""
    result = await db.execute(
        select(SkillModel).where(SkillModel.skill_id == skill_id)
    )
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    payload = Skill.model_validate(skill).model_dump()
    payload["links"] = resource_links(
        request,
        f"{settings.API_V1_PREFIX}/skills/{skill.skill_id}",
        f"{settings.API_V1_PREFIX}/skills",
    )
    return payload


@router.get("/", response_model=List[Skill])
async def read_skills(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = Query(None, description="Фильтр по названию"),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """Получить список навыков"""
    query = select(SkillModel)
    if name:
        query = query.where(SkillModel.name.ilike(f"%{name}%"))
    if category:
        query = query.where(SkillModel.category.ilike(f"%{category}%"))
    query = query.order_by(SkillModel.name).offset(skip).limit(limit)
    result = await db.execute(query)
    skills = result.scalars().all()
    response: List[Skill] = []
    for skill in skills:
        payload = Skill.model_validate(skill).model_dump()
        payload["links"] = resource_links(
            request,
            f"{settings.API_V1_PREFIX}/skills/{skill.skill_id}",
            f"{settings.API_V1_PREFIX}/skills",
        )
        response.append(payload)
    return response
