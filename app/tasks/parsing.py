from celery import shared_task
from app.services.parsers.hh_parser import HHParser
from app.core.database import AsyncSessionLocal
from app.crud.vacancy import vacancy_crud

@shared_task
def parse_hh_vacancies(search_query: str):
    """Фоновая задача парсинга вакансий"""
    parser = HHParser()
    
    async def parse():
        async with parser:
            vacancies_data = await parser.parse_vacancies(search_query, limit=50)
            
            async with AsyncSessionLocal() as db:
                for vacancy_data in vacancies_data:
                    source_url = vacancy_data.get("source_url")
                    if not source_url:
                        continue
                    existing = await vacancy_crud.get_by_source_url(db, source_url)
                    if not existing:
                        await vacancy_crud.create_from_parsed(db, vacancy_data, commit=False)
                await db.commit()
    
    # Запускаем асинхронную функцию
    import asyncio
    asyncio.run(parse())