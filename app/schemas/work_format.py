from typing import Optional, List
from .base import BaseSchema, Link

class WorkFormatBase(BaseSchema):
    name: str


class WorkFormatCreate(WorkFormatBase):
    pass


class WorkFormat(WorkFormatBase):
    work_format_id: int
    links: Optional[List[Link]] = None


class WorkFormatInVacancy(BaseSchema):
    work_format_id: int
    name: str
    