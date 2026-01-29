from celery import shared_task
from app.services.parsers.hh_parser import HHParser
from app.db import SessionLocal
from app.crud.vacancy import vacancy_crud

@shared_task
def parse_hh_vacancies(search_query: str):
    """Фоновая задача парсинга вакансий"""
    parser = HHParser()
    
    async def parse():
        async with parser:
            vacancies_data = await parser.parse_vacancies(search_query, limit=50)
            
            db = SessionLocal()
            try:
                for vacancy_data in vacancies_data:
                    # Проверяем, нет ли уже такой вакансии
                    existing = await vacancy_crud.get_by_source_url(
                        db, vacancy_data["source_url"]
                    )
                    if not existing:
                        await vacancy_crud.create_from_parsed(db, vacancy_data)
                
                await db.commit()
            finally:
                await db.close()
    
    # Запускаем асинхронную функцию
    import asyncio
    asyncio.run(parse())