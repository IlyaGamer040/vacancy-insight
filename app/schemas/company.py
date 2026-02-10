from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from .base import BaseSchema, TimestampMixin, Link


# Базовые схемы

class CompanyBase(BaseSchema):
    name: str
    website: Optional[HttpUrl] = None
    description: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    website: Optional[HttpUrl] = None
    description: Optional[str] = None


# Схемы ответа

class CompanySimple(CompanyBase, TimestampMixin):
    company_id: int


class Company(CompanySimple):
    links: Optional[List[Link]] = None


# Для вложенного отображения

class CompanyInVacancy(BaseSchema):
    company_id: int
    name: str
    