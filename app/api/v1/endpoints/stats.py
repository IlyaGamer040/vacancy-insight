from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.vacancy import Vacancy
from app.models.company import Company
from app.models.skill import Skill
from app.models.vacancy_skill import VacancySkill


router = APIRouter()

