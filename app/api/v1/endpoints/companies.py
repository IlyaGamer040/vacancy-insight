from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.schemas.company import Company, CompanyCreate
from app.crud.company import company_crud
from app.core.database import get_db

router = APIRouter()


@router.post("/", response_model=Company)
async def create_company(
    company_in: CompanyCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать компанию"""
    existing = await company_crud.get_by_name(db, name=company_in.name)
    if existing:
        raise HTTPException(status_code=409, detail="Company already exists")
    return await company_crud.create(db, obj_in=company_in)


@router.get("/{company_id}", response_model=Company)
async def read_company(
    company_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить компанию по ID"""
    company = await company_crud.get(db, company_id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.get("/", response_model=List[Company])
async def read_companies(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = Query(None, description="Фильтр по названию"),
    db: AsyncSession = Depends(get_db)
):
    """Получить список компаний"""
    if name:
        company = await company_crud.get_by_name(db, name=name)
        return [company] if company else []
    return await company_crud.get_multi(db, skip=skip, limit=limit)
