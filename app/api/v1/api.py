from fastapi import APIRouter
from app.api.v1.endpoints import (vacancies, search)

api_router = APIRouter()

api_router.include_router(vacancies.router, prefix="/vacancies", tags=["vacancies"])
api_router.include_router(vacancies.router, prefix="/search", tags=["search"])