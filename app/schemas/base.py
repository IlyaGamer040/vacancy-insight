from pydantic import BaseModel, ConfigDict
from datetime import datetime

class BaseSchema(BaseModel):
    """
    Docstring for BaseSchema
    """
    model_config = ConfigDict(from_attributes=True)

class TimestampMixin(BaseSchema):
    created_at: datetime
    updated_at: datetime | None = None