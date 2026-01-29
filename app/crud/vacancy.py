from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from typing import Optional, List
from app.models.vacancy import Vacancy
from app.models.vacancy_skill import VacancySkill
from app.schemas.vacancy import VacancyCreate, VacancyFilter

class CRUDVacancy:
    async def get(self, db: AsyncSession, vacancy_id: int) -> Optional[Vacancy]:
        result = await db.execute(
            select(Vacancy)
            .options(
                selectinload(Vacancy.company),
                selectinload(Vacancy.experience),
                selectinload(Vacancy.work_format),
                selectinload(Vacancy.work_schedule),
                selectinload(Vacancy.skills).selectinload(VacancySkill.skill)
            )
            .where(Vacancy.vacancy_id == vacancy_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, db: AsyncSession, obj_in: VacancyCreate) -> Vacancy:
        vacancy_data = obj_in.model_dump(exclude={"skills"})
        if vacancy_data.get("source_url") is not None:
            vacancy_data["source_url"] = str(vacancy_data["source_url"])
        db_obj = Vacancy(**vacancy_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        if obj_in.skills:
            for skill_data in obj_in.skills:
                vacancy_skill = VacancySkill(
                    vacancy_id=db_obj.vacancy_id,
                    skill_id=skill_data.skill_id,
                    is_mandatory=skill_data.in_mandatory
                )
                db.add(vacancy_skill)
            await db.commit()

        # Возвращаем объект с подгруженными связями для корректного ответа API
        return await self.get(db, vacancy_id=db_obj.vacancy_id)
    
    async def filter(self, db: AsyncSession, filter: VacancyFilter) -> List[Vacancy]:
        query = select(Vacancy).options(
            selectinload(Vacancy.company),
            selectinload(Vacancy.experience)
        )

        conditions = []

        if filter.title:
            conditions.append(Vacancy.title.ilike(f"%{filter.title}%"))
        if filter.company_id:
            conditions.append(Vacancy.company_id == filter.company_id)
        if filter.experience_id:
            conditions.append(Vacancy.experience_id == filter.experience_id)
        if filter.work_format_id:
            conditions.append(Vacancy.work_format_id == filter.work_format_id)
        if filter.work_schedule_id:
            conditions.append(Vacancy.work_schedule_id == filter.work_schedule_id)
        if filter.location:
            conditions.append(Vacancy.location.ilike(f"%{filter.location}%"))
        if filter.min_salary:
            conditions.append(
                or_(
                    Vacancy.salary_from >= filter.min_salary,
                    Vacancy.salary_to >= filter.min_salary
                )
            )
        if filter.max_salary:
            conditions.append(
                or_(
                    Vacancy.salary_from <= filter.max_salary,
                    Vacancy.salary_to <= filter.max_salary
                )
            )
        if filter.currency:
            conditions.append(Vacancy.currency == filter.currency)
        if filter.is_active is not None:
            conditions.append(Vacancy.is_active == filter.is_active)

        if conditions:
            query = query.where(and_(*conditions))

        # Пагинация
        query = query.offset(filter.offset).limit(filter.limit)

        result = await db.execute(query)
        return result.scalars().all()
    
vacancy_crud = CRUDVacancy()