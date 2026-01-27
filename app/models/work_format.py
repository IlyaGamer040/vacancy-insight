from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..core.database import Base

class WorkFormat(Base):
    __tablename__ = "work_formats"

    work_format_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)

    # Формат работы связан с вакансиями
    vacancies = relationship("Vacancy", back_populates="work_format")