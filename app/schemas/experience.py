from .base import BaseSchema

class ExperienceBase(BaseSchema):
    name: str
    order: int = 0


class ExperienceCreate(ExperienceBase):
    pass


class Experience(ExperienceBase):
    experience_id: int


# Для вложенного отображения

class ExperienceInVacancy(BaseSchema):
    experience_id: int
    name: str
    