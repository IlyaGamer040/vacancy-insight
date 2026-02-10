from typing import Optional, List
from .base import BaseSchema, Link

class ExperienceBase(BaseSchema):
    name: str
    order: int = 0


class ExperienceCreate(ExperienceBase):
    pass


class Experience(ExperienceBase):
    experience_id: int
    links: Optional[List[Link]] = None


# Для вложенного отображения

class ExperienceInVacancy(BaseSchema):
    experience_id: int
    name: str
    