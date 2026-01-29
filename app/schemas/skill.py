from pydantic import BaseModel
from typing import Optional
from .base import BaseSchema

class SkillBase(BaseSchema):
    name: str
    category: Optional[str] = None


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None


class Skill(SkillBase):
    skill_id: int


class VacancySkillBase(BaseSchema):
    skill_id: int
    in_mandatory: bool = True


class VacancySkillCreate(VacancySkillBase):
    pass


class SkillInVacancy(BaseSchema):
    skill_id: int
    name: Optional[str] = None
    category: Optional[str] = None
    is_mandatory: bool
    