from sqlalchemy import Column, Integer, ForeignKey, DateTime, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class FavoriteVacancy(Base):
    __tablename__ = "favorite_vacancies"

    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    vacancy_id = Column(Integer, ForeignKey("vacancies.vacancy_id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (PrimaryKeyConstraint('user_id', 'vacancy_id'),)

    user = relationship("User", back_populates="favorite_vacancies")
    vacancy = relationship("Vacancy")