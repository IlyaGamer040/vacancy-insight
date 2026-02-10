from pydantic import BaseModel, Field
from typing import Optional


class PollingSettings(BaseModel):
    enabled: bool = True
    title: Optional[str] = None
    location: Optional[str] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    limit: int = Field(20, ge=1, le=200)
    area: int = 1
    only_with_salary: bool = False
