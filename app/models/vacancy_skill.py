from sqlalchemy import Column, Integer, Boolean, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from ..core.database import Base

class VacancySkill(Base):
    __tablename__ = "vacancy_skills"

    vacancy_id = Column(Integer, ForeignKey("vacancies.vacancy_id", ondelete="CASCADE"))
    skill_id = Column(Integer, ForeignKey("skills.skill_id", ondelete="CASCADE"))
    is_mandatory = Column(Boolean, default=True)

    __table_args__ = (PrimaryKeyConstraint('vacancy_id', 'skill_id'),)

    vacancy = relationship("Vacancy", back_populates="skills")
    skill = relationship("Skill", back_populates="vacancies")