from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from typing import Optional, List, Dict, Any
from datetime import datetime
import re
from app.models.vacancy import Vacancy
from app.models.vacancy_skill import VacancySkill
from app.models.company import Company
from app.models.experience import Experience
from app.models.work_format import WorkFormat
from app.models.work_schedule import WorkSchedule
from app.models.skill import Skill
from app.schemas.vacancy import VacancyCreate, VacancyFilter

class CRUDVacancy:
    def _build_conditions(self, filter: VacancyFilter):
        conditions = []

        if filter.title:
            conditions.append(
                or_(
                    Vacancy.title.ilike(f"%{filter.title}%"),
                    Vacancy.description.ilike(f"%{filter.title}%"),
                )
            )
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
        if filter.since:
            parsed_since = self._safe_parse_datetime(filter.since)
            if parsed_since:
                conditions.append(
                    or_(
                        Vacancy.published_date >= parsed_since,
                        Vacancy.created_at >= parsed_since,
                    )
                )

        return conditions

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

    async def get_by_source_url(self, db: AsyncSession, source_url: str) -> Optional[Vacancy]:
        result = await db.execute(
            select(Vacancy).where(Vacancy.source_url == source_url)
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

    async def create_from_parsed(
        self,
        db: AsyncSession,
        data: Dict[str, Any],
        commit: bool = True,
    ) -> Vacancy:
        company_name = (data.get("company") or {}).get("name") or "Не указано"
        company_website = (data.get("company") or {}).get("website")

        company = await self._get_or_create_company(
            db, name=company_name, website=company_website
        )
        experience = await self._get_or_create_experience(db, data.get("experience"))
        work_format = await self._get_or_create_work_format(db, data.get("work_format"))
        work_schedule = await self._get_or_create_work_schedule(db, data.get("work_schedule"))

        salary = data.get("salary") or {}
        location = data.get("location") or "Не указано"
        raw_address = data.get("raw_address") or location

        title = data.get("title") or "Без названия"
        title = await self._ensure_unique_title(db, title, company_name)

        published_date = data.get("published_date")
        if isinstance(published_date, datetime):
            parsed_date = published_date
        elif isinstance(published_date, str):
            parsed_date = self._safe_parse_datetime(published_date)
        else:
            parsed_date = None

        vacancy = Vacancy(
            title=title,
            description=data.get("description") or "",
            salary_from=salary.get("from"),
            salary_to=salary.get("to"),
            currency=salary.get("currency"),
            location=location,
            raw_address=raw_address,
            parsed_address=data.get("parsed_address"),
            source_url=data.get("source_url"),
            published_date=parsed_date,
            is_active=True,
            company_id=company.company_id,
            experience_id=experience.experience_id,
            work_format_id=work_format.work_format_id,
            work_schedule_id=work_schedule.work_schedule_id,
        )

        db.add(vacancy)
        await db.flush()

        skill_names = data.get("skills") or []
        for skill_name in skill_names:
            if not skill_name:
                continue
            skill = await self._get_or_create_skill(db, skill_name)
            db.add(
                VacancySkill(
                    vacancy_id=vacancy.vacancy_id,
                    skill_id=skill.skill_id,
                    is_mandatory=True,
                )
            )

        if commit:
            await db.commit()
            await db.refresh(vacancy)

        return vacancy

    async def _get_or_create_company(
        self, db: AsyncSession, name: str, website: Optional[str]
    ) -> Company:
        result = await db.execute(select(Company).where(Company.name == name))
        company = result.scalar_one_or_none()
        if company:
            return company
        company = Company(
            name=name,
            website=website,
            description="Импортировано из hh.ru",
        )
        db.add(company)
        await db.flush()
        return company

    async def _get_or_create_experience(
        self, db: AsyncSession, name: Optional[str]
    ) -> Experience:
        normalized = self._normalize_experience_name(name)
        result = await db.execute(select(Experience).where(Experience.name == normalized))
        experience = result.scalar_one_or_none()
        if experience:
            return experience
        experience = Experience(name=normalized, order=0)
        db.add(experience)
        await db.flush()
        return experience

    async def _get_or_create_work_format(
        self, db: AsyncSession, name: Optional[str]
    ) -> WorkFormat:
        normalized = self._normalize_work_format_name(name)
        result = await db.execute(select(WorkFormat).where(WorkFormat.name == normalized))
        work_format = result.scalar_one_or_none()
        if work_format:
            return work_format
        work_format = WorkFormat(name=normalized)
        db.add(work_format)
        await db.flush()
        return work_format

    async def _get_or_create_work_schedule(
        self, db: AsyncSession, name: Optional[str]
    ) -> WorkSchedule:
        normalized = self._normalize_work_schedule_name(name)
        result = await db.execute(select(WorkSchedule).where(WorkSchedule.name == normalized))
        work_schedule = result.scalar_one_or_none()
        if work_schedule:
            return work_schedule
        work_schedule = WorkSchedule(name=normalized)
        db.add(work_schedule)
        await db.flush()
        return work_schedule

    async def _get_or_create_skill(self, db: AsyncSession, name: str) -> Skill:
        result = await db.execute(select(Skill).where(Skill.name == name))
        skill = result.scalar_one_or_none()
        if skill:
            return skill
        skill = Skill(name=name, category=None)
        db.add(skill)
        await db.flush()
        return skill

    async def _ensure_unique_title(
        self, db: AsyncSession, title: str, company_name: str
    ) -> str:
        result = await db.execute(select(Vacancy.vacancy_id).where(Vacancy.title == title))
        if not result.scalar_one_or_none():
            return title
        candidate = f"{title} ({company_name})"
        result = await db.execute(select(Vacancy.vacancy_id).where(Vacancy.title == candidate))
        if not result.scalar_one_or_none():
            return candidate
        return f"{title} ({company_name}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')})"

    def _normalize_work_format_name(self, name: Optional[str]) -> str:
        if not name:
            return "Любой"
        lowered = name.lower()
        if "удал" in lowered or "remote" in lowered:
            return "Удаленно"
        if "гибрид" in lowered:
            return "Гибрид"
        if "офис" in lowered or "office" in lowered:
            return "Офис"
        return "Любой"

    def _normalize_work_schedule_name(self, name: Optional[str]) -> str:
        if not name:
            return "Полный день"
        lowered = name.lower()
        if "смен" in lowered:
            return "Сменный график"
        if "гибк" in lowered:
            return "Гибкий график"
        if "вахт" in lowered:
            return "Вахта"
        if "частич" in lowered:
            return "Частичная занятость"
        return "Полный день"

    def _normalize_experience_name(self, name: Optional[str]) -> str:
        if not name:
            return "Нет опыта"
        lowered = name.lower()
        if "нет опыта" in lowered:
            return "Нет опыта"
        if "1" in lowered and "3" in lowered:
            return "1–3 года"
        if "3" in lowered and "6" in lowered:
            return "3–6 лет"
        if "6" in lowered or "более" in lowered:
            return "Более 6 лет"
        return name

    def _safe_parse_datetime(self, value: str) -> Optional[datetime]:
        if not value:
            return None
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        if re.match(r"^(.*[T ]\d{2}:\d{2}:\d{2})([+-]\d{2})(\d{2})$", value):
            value = f"{value[:-2]}:{value[-2:]}"
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    
    async def filter(self, db: AsyncSession, filter: VacancyFilter) -> List[Vacancy]:
        query = select(Vacancy).options(
            selectinload(Vacancy.company),
            selectinload(Vacancy.experience)
        )
        conditions = self._build_conditions(filter)

        if conditions:
            query = query.where(and_(*conditions))

        # Пагинация
        query = query.offset(filter.offset).limit(filter.limit)

        result = await db.execute(query)
        return result.scalars().all()
    
vacancy_crud = CRUDVacancy()