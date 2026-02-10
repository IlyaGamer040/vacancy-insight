from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class BaseSchema(BaseModel):
    """
    Docstring for BaseSchema
    """
    model_config = ConfigDict(from_attributes=True)

class Link(BaseSchema):
    rel: str
    href: str
    method: Optional[str] = "GET"

class TimestampMixin(BaseSchema):
    created_at: datetime
    updated_at: datetime | None = None