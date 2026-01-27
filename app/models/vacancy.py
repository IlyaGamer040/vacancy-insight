from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from ..core.database import Base

class Vacancy(Base):
    __tablename__ = "vacancies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, nullable=False)
    company_id = relationship("Company", back_populates="")