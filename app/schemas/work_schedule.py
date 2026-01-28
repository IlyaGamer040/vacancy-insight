from .base import BaseSchema

class WordScheduleBase(BaseSchema):
    name: str


class WorkScheduleCreate(WordScheduleBase):
    pass


class WorkSchedule(WordScheduleBase):
    work_schedule_id: int


class WorkScheduleInVacancy(BaseSchema):
    work_schedule_id: int
    name: str
    