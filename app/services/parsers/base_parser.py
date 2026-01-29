import aiohttp
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from app.core.config import settings

class BaseParser:
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
    
    async def parse_vacancies(self, search_query: str, limit: int = 100) -> List[Dict]:
        raise NotImplementedError
    
    def normalize_salary(self, salary_data: Dict) -> Dict:
        """Нормализация зарплаты из разных источников"""
        if not salary_data:
            return {"from": None, "to": None, "currency": None}
        
        # hh.ru
        return {
            "from": salary_data.get("from"),
            "to": salary_data.get("to"),
            "currency": salary_data.get("currency", "RUB").upper()
        }
    
    def parse_skills(self, description: str) -> List[str]:
        """Извлечение навыков из описания"""
        skills = []
        common_skills = ["Python", "JavaScript", "Java", "SQL", "Docker", 
                        "Kubernetes", "React", "Vue", "AWS", "Git"]
        
        for skill in common_skills:
            if skill.lower() in description.lower():
                skills.append(skill)
        
        return skills