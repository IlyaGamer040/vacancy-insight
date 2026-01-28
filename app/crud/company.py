from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.models.company import Company
from app.schemas.company import CompanyCreate

class CRUDCompany:
    async def get(self, db: AsyncSession, company_id: int) -> Optional[Company]:
        result = await db.execute(
            select(Company).where(Company.company_id == company_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Company]:
        result = await db.execute(
            select(Company).where(Company.name.ilike(f"%{name}%"))
        )
        return result.scalar_one_or_none()
    
    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Company]:
        result = await db.execute(
            select(Company)
            .offset(skip)
            .limit(limit)
            .order_by(Company.name)
        )
        return result.scalars().all()
    
    async def create(self, db: AsyncSession, obj_in: CompanyCreate) -> Company:
        db_obj = Company(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
company_crud = CRUDCompany()