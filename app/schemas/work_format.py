from .base import BaseSchema

class WorkFormatBase(BaseSchema):
    name: str


class WorkFormatCreate(WorkFormatBase):
    pass


class WorkFormat(WorkFormatBase):
    work_format_id: int


class WorkFormatInVacancy(BaseSchema):
    work_format_id: int
    name: str
    