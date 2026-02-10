from typing import Optional, List
from .base import BaseSchema, Link

class WordScheduleBase(BaseSchema):
    name: str


class WorkScheduleCreate(WordScheduleBase):
    pass


class WorkSchedule(WordScheduleBase):
    work_schedule_id: int
    links: Optional[List[Link]] = None


class WorkScheduleInVacancy(BaseSchema):
    work_schedule_id: int
    name: str
    