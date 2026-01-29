from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.vacancy import Vacancy
from app.models.company import Company
from app.models.skill import Skill
from app.models.vacancy_skill import VacancySkill


router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(func.count(Vacancy.vacancy_id)))
    total_vacancies = result.scalar()

    result = await db.execute(select(func.count(Company.company_id)))
    total_companies = result.scalar()

    result = await db.execute(select(func.count(Skill.skill_id)))
    total_skills = result.scalar()

    # Активные вакансии
    result = await db.execute(
        select(func.count(Vacancy.vacancy_id))
        .where(Vacancy.is_active == True)
    )
    active_vacancies = result.scalar()

    # Вакансии с ЗП
    result = await db.execute(
        select(func.count(Vacancy.vacancy_id))
        .where(Vacancy.salary_from.isnot(None))
    )
    vacancies_with_salary = result.scalar()

    # Средняя ЗП
    result = await db.execute(
        select(func.avg((Vacancy.salary_from + Vacancy.salary_to) / 2))
        .where(Vacancy.salary_from.isnot(None))
    )
    avg_salary = result.scalar()

    # Топ навыков
    result = await db.execute(
        select(Skill.name, func.count(VacancySkill.skill_id).label("count"))
        .join(VacancySkill, Skill.skill_id == VacancySkill.skill_id)
        .group_by(Skill.skill_id)
        .order_by(func.count(VacancySkill.skill_id).desc())
        .limit(10)
    )
    top_skills = result.all()

    # Распределение по опыту
    from app.models.experience import Experience
    result = await db.execute(
        select(Experience.name, func.count(Vacancy.vacancy_id))
        .join(Vacancy, Vacancy.experience_id == Experience.experience_id)
        .group_by(Experience.experience_id)
        .order_by(Experience.order)
    )
    experience_distribution = result.all()


    return {
        "overview": {
            "total_vacancies": total_vacancies,
            "active_vacancies": active_vacancies,
            "total_companies": total_companies,
            "total_skills": total_skills,
        },
        "salary": {
            "with_salary": vacancies_with_salary,
            "average_salary": float(avg_salary) if avg_salary else None,
        },
        "top_skills": [
            {"skill": skill, "count": count} for skill, count in top_skills
        ],
        "experience_distribution": [
            {"experience": exp, "count": count} for exp, count in experience_distribution
        ]
    }