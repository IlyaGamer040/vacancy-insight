from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..core.database import Base

class WorkSchedule(Base):
    __tablename__ = "work_schedules"
    work_schedule_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)

    # График работы связан с вакансиями
    vacancies = relationship("Vacancy", back_populates="work_schedule")