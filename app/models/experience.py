from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..core.database import Base

class Experience(Base):
    __tablename__ = "experiences"

    experience_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    order = Column(Integer, nullable=False, default=0)

    # Опыт связан с вакансиями
    vacancies = relationship("Vacancy", back_populates="experience")