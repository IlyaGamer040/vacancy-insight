from .base_parser import BaseParser
import logging
import aiohttp

logger = logging.getLogger(__name__)

class HHParser(BaseParser):
    BASE_URL = "https://api.hh.ru"
    
    async def parse_vacancies(self, search_query: str, limit: int = 100):
        vacancies = []
        page = 0
        per_page = 20
        
        async with aiohttp.ClientSession() as session:
            while len(vacancies) < limit:
                params = {
                    "text": search_query,
                    "page": page,
                    "per_page": per_page,
                    "area": 1,  # Москва
                    "only_with_salary": True,
                }
                
                async with session.get(f"{self.BASE_URL}/vacancies", params=params) as resp:
                    if resp.status != 200:
                        break
                    
                    data = await resp.json()
                    items = data.get("items", [])
                    
                    if not items:
                        break
                    
                    for item in items:
                        vacancy = await self.parse_vacancy_detail(session, item["id"])
                        if vacancy:
                            vacancies.append(vacancy)
                    
                    page += 1
        
        return vacancies[:limit]
    
    async def parse_vacancy_detail(self, session, vacancy_id: str):
        async with session.get(f"{self.BASE_URL}/vacancies/{vacancy_id}") as resp:
            if resp.status != 200:
                return None
            
            data = await resp.json()
            
            # Преобразование в нашу структуру
            vacancy = {
                "title": data.get("name", ""),
                "description": data.get("description", ""),
                "salary": self.normalize_salary(data.get("salary")),
                "company": {
                    "name": data.get("employer", {}).get("name", ""),
                    "website": data.get("employer", {}).get("site_url", ""),
                },
                "experience": data.get("experience", {}).get("name", ""),
                "work_format": self.parse_work_format(data),
                "location": data.get("area", {}).get("name", ""),
                "skills": [skill["name"] for skill in data.get("key_skills", [])],
                "source_url": data.get("alternate_url", ""),
                "published_date": data.get("published_at", ""),
            }
            
            return vacancy