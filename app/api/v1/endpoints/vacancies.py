from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.vacancy import Vacancy, VacancyCreate, VacancyWithCompany, VacancyFilter
from app.crud.vacancy import vacancy_crud
from app.core.database import get_db
from app.models.company import Company
from app.models.experience import Experience
from app.models.work_format import WorkFormat
from app.models.work_schedule import WorkSchedule
from app.models.skill import Skill

router = APIRouter()

@router.post("/", response_model=Vacancy)
async def create_vacancy(
    vacancy_in: VacancyCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Создать новую вакансию

    Docstring for create_vacancy
    
    :param vacancy_in: Description
    :type vacancy_in: VacancyCreate
    :param db: Description
    :type db: AsyncSession
    """
    company = await db.execute(
        select(Company).where(Company.company_id == vacancy_in.company_id)
    )
    if not company.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Company not found")

    experience = await db.execute(
        select(Experience).where(Experience.experience_id == vacancy_in.experience_id)
    )
    if not experience.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Experience not found")

    work_format = await db.execute(
        select(WorkFormat).where(WorkFormat.work_format_id == vacancy_in.work_format_id)
    )
    if not work_format.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Work format not found")

    work_schedule = await db.execute(
        select(WorkSchedule).where(WorkSchedule.work_schedule_id == vacancy_in.work_schedule_id)
    )
    if not work_schedule.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Work schedule not found")

    if vacancy_in.skills:
        skill_ids = [skill.skill_id for skill in vacancy_in.skills]
        result = await db.execute(
            select(Skill.skill_id).where(Skill.skill_id.in_(skill_ids))
        )
        found_skill_ids = {row[0] for row in result.all()}
        missing_skill_ids = sorted(set(skill_ids) - found_skill_ids)
        if missing_skill_ids:
            raise HTTPException(
                status_code=404,
                detail=f"Skills not found: {missing_skill_ids}",
            )

    vacancy = await vacancy_crud.create(db, obj_in=vacancy_in)
    return vacancy


@router.get("/{vacancy_id}", response_model=Vacancy)
async def read_vacancy(
    vacancy_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить вакансию по ID

    Docstring for read_vacancy
    
    :param vacancy_id: Description
    :type vacancy_id: int
    :param db: Description
    :type db: AsyncSession
    """
    vacancy = await vacancy_crud.get(db, vacancy_id=vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    return vacancy


@router.get("/", response_model=List[VacancyWithCompany])
async def read_vacancies(
    filter: VacancyFilter = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список вакансий с фильтрацией

    Docstring for read_vacancies
    
    :param filter: Description
    :type filter: VacancyFilter
    :param db: Description
    :type db: AsyncSession
    """
    vacancies = await vacancy_crud.filter(db, filter=filter)
    return vacancies


@router.get("/company/{company_id}", response_model=List[VacancyWithCompany])
async def read_company_vacancies(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить вакансии компании

    Docstring for read_company_vacancies
    
    :param company_id: Description
    :type company_id: int
    :param skip: Description
    :type skip: int
    :param limit: Description
    :type limit: int
    :param db: Description
    :type db: AsyncSession
    """
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.models.vacancy import Vacancy

    result = await db.execute(
        select(Vacancy)
        .options(selectinload(Vacancy.company))
        .where(Vacancy.company_id == company_id, Vacancy.is_active == True)
        .offset(skip)
        .limit(limit)
        .order_by(Vacancy.published_date.desc())
    )
    vacancies = result.scalars().all()
    return vacancies