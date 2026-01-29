from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime
from .base import BaseSchema, TimestampMixin
from .company import CompanyInVacancy
from .experience import ExperienceInVacancy
from .work_format import WorkFormatInVacancy
from .work_schedule import WorkScheduleInVacancy
from .skill import SkillInVacancy, VacancySkillCreate

# Базовые схемы
class VacancyBase(BaseSchema):
    title: str
    description: str
    salary_from: Optional[float] = None
    salary_to: Optional[float] = None
    currency: Optional[str] = None
    location: Optional[str] = None
    raw_address: Optional[str] = None
    parsed_address: Optional[str] = None
    source_url: HttpUrl
    published_date: Optional[datetime] = None
    is_active: bool = True

# Создание вакансии (с ID внешних ключей)
class VacancyCreate(VacancyBase):
    company_id: int
    experience_id: int
    work_format_id: int
    work_schedule_id: int
    skills: List[VacancySkillCreate] = Field(default_factory=list)  # Навыки при создании

class VacancyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    salary_from: Optional[float] = None
    salary_to: Optional[float] = None
    currency: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None
    experience_id: Optional[int] = None
    work_format_id: Optional[int] = None
    work_schedule_id: Optional[int] = None

# Схемы ответа
class VacancySimple(VacancyBase, TimestampMixin):
    vacancy_id: int
    company_id: int
    experience_id: int
    work_format_id: int
    work_schedule_id: int

# Полная вакансия со связанными объектами
class Vacancy(VacancySimple):
    company: Optional[CompanyInVacancy] = None
    experience: Optional[ExperienceInVacancy] = None
    work_format: Optional[WorkFormatInVacancy] = None
    work_schedule: Optional[WorkScheduleInVacancy] = None
    skills: List[SkillInVacancy] = []

# Вакансия с деталями компании (для списков)
class VacancyWithCompany(VacancySimple):
    company: Optional[CompanyInVacancy] = None
    experience: Optional[ExperienceInVacancy] = None

# Для фильтрации и поиска
class VacancyFilter(BaseModel):
    title: Optional[str] = None
    company_id: Optional[int] = None
    experience_id: Optional[int] = None
    work_format_id: Optional[int] = None
    work_schedule_id: Optional[int] = None
    location: Optional[str] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    currency: Optional[str] = None
    skill_ids: Optional[List[int]] = None
    is_active: Optional[bool] = True
    offset: int = 0
    limit: int = Field(100, le=1000)

# Статистика
class VacancyStats(BaseSchema):
    total: int
    active: int
    with_salary: int
    average_salary: Optional[float] = None