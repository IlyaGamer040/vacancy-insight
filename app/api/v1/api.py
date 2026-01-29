from fastapi import APIRouter
from app.api.v1.endpoints import (
    vacancies,
    search,
    stats,
    companies,
    experiences,
    work_formats,
    work_schedules,
    skills,
)

api_router = APIRouter()

api_router.include_router(vacancies.router, prefix="/vacancies", tags=["vacancies"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(experiences.router, prefix="/experiences", tags=["experiences"])
api_router.include_router(work_formats.router, prefix="/work-formats", tags=["work-formats"])
api_router.include_router(work_schedules.router, prefix="/work-schedules", tags=["work-schedules"])
api_router.include_router(skills.router, prefix="/skills", tags=["skills"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])