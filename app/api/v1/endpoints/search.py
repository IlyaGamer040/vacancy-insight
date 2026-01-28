from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.api.deps import get_db
from app.crud.vacancy import vacancy_crud
from app.schemas.vacancy import VacancyWithCompany

router = APIRouter()

@router.get("/vacancies", response_model=List[VacancyWithCompany])
async def search_vacancies(
    q: Optional[str] = Query(None, description="Поисковый запрос"),
    location: Optional[str] = None,
    salary_min: Optional[float] = None,
    salary_max: Optional[float] = None,
    experience_ids: Optional[List[int]] = Query(None),
    skill_ids: Optional[List[int]] = Query(None),
    remote_only: bool = False,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Расширенный поиск вакансий"""
    from sqlalchemy import select, or_, and_
    from app.models.vacancy import Vacancy
    from app.models.company import Company
    from app.models.vacancy_skill import VacancySkill
    
    query = (
        select(Vacancy)
        .join(Company)
        .where(Vacancy.is_active == True)
        .options(selectinload(Vacancy.company))
    )
    
    conditions = []
    
    # Поиск по тексту
    if q:
        search_conditions = [
            Vacancy.title.ilike(f"%{q}%"),
            Vacancy.description.ilike(f"%{q}%"),
            Company.name.ilike(f"%{q}%"),
        ]
        conditions.append(or_(*search_conditions))
    
    # Локация
    if location:
        conditions.append(Vacancy.location.ilike(f"%{location}%"))
    
    # Зарплата
    if salary_min:
        conditions.append(
            or_(
                Vacancy.salary_from >= salary_min,
                Vacancy.salary_to >= salary_min
            )
        )
    if salary_max:
        conditions.append(
            or_(
                Vacancy.salary_from <= salary_max,
                Vacancy.salary_to <= salary_max
            )
        )
    
    # Опыт
    if experience_ids:
        conditions.append(Vacancy.experience_id.in_(experience_ids))
    
    # Удаленная работа
    if remote_only:
        conditions.append(Vacancy.work_format_id == 2)  # ID для "Удаленно"
    
    # Навыки (требуются все указанные навыки)
    if skill_ids:
        for skill_id in skill_ids:
            subquery = (
                select(VacancySkill.vacancy_id)
                .where(VacancySkill.skill_id == skill_id)
                .scalar_subquery()
            )
            conditions.append(Vacancy.vacancy_id.in_(subquery))
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(Vacancy.published_date.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    vacancies = result.scalars().all()
    return vacancies