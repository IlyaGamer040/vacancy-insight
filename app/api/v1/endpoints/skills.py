from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.models.skill import Skill as SkillModel
from app.schemas.skill import Skill, SkillCreate

router = APIRouter()


@router.post("/", response_model=Skill)
async def create_skill(
    skill_in: SkillCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать навык"""
    db_obj = SkillModel(**skill_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


@router.get("/{skill_id}", response_model=Skill)
async def read_skill(
    skill_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить навык по ID"""
    result = await db.execute(
        select(SkillModel).where(SkillModel.skill_id == skill_id)
    )
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.get("/", response_model=List[Skill])
async def read_skills(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = Query(None, description="Фильтр по названию"),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    db: AsyncSession = Depends(get_db)
):
    """Получить список навыков"""
    query = select(SkillModel)
    if name:
        query = query.where(SkillModel.name.ilike(f"%{name}%"))
    if category:
        query = query.where(SkillModel.category.ilike(f"%{category}%"))
    query = query.order_by(SkillModel.name).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
