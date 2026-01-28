from sqlalchemy import (Column, Integer, String, Text,
Numeric, Boolean, DateTime, ForeignKey)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class Vacancy(Base):
    __tablename__ = "vacancies"

    vacancy_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, nullable=False)

    company_id = Column(Integer, ForeignKey("companies.company_id", ondelete="CASCADE"))
    experience_id = Column(Integer, ForeignKey("experiences.experience_id"))
    work_format_id = Column(Integer, ForeignKey("work_formats.work_format_id"))
    work_schedule_id = Column(Integer, ForeignKey("work_schedules.work_schedule_id"))

    description = Column(Text, nullable=True)
    salary_from = Column(Numeric(10, 2), nullable=True)
    salary_to = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(10), nullable=True)
    location = Column(Text, nullable=False)
    raw_address = Column(Text, nullable=False)
    parsed_address = Column(String(500), nullable=True)
    source_url = Column(String(500), nullable=False, unique=True)
    published_date = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    company = relationship("Company", back_populates="vacancies")
    experience = relationship("Experience", back_populates="vacancies")
    work_format = relationship("WorkFormat", back_populates="vacancies")
    work_schedule = relationship("WorkSchedule", back_populates="vacancies")

    skills = relationship(
        "VacancySkill",
        back_populates="vacancy",
        cascade="all, delete-orphan",
        lazy="selectin"
    )