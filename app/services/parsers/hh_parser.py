from .base_parser import BaseParser
from app.core.config import settings
from bs4 import BeautifulSoup
import logging
import aiohttp
from datetime import datetime
from typing import Optional, Dict, Any, List
import re

logger = logging.getLogger(__name__)

class HHParser(BaseParser):
    BASE_URL = settings.HH_API_URL

    async def parse_vacancies(
        self,
        search_query: str,
        limit: int = 100,
        area: Optional[int] = None,
        only_with_salary: bool = False,
    ) -> List[Dict[str, Any]]:
        vacancies: List[Dict[str, Any]] = []
        page = 0
        per_page = min(20, max(1, limit))
        headers = {"User-Agent": "vacancy-insight/1.0"}

        session = self.session or aiohttp.ClientSession(headers=headers)
        close_session = self.session is None

        try:
            while len(vacancies) < limit:
                params = {
                    "text": search_query,
                    "page": page,
                    "per_page": per_page,
                }
                if area is not None:
                    params["area"] = area
                if only_with_salary:
                    params["only_with_salary"] = True

                async with session.get(f"{self.BASE_URL}/vacancies", params=params) as resp:
                    if resp.status != 200:
                        logger.warning("HH API returned status %s", resp.status)
                        break

                    data = await resp.json()
                    items = data.get("items", [])
                    if not items:
                        break

                    for item in items:
                        vacancy = await self.parse_vacancy_detail(session, item["id"])
                        if vacancy:
                            vacancies.append(vacancy)
                        if len(vacancies) >= limit:
                            break

                    page += 1
        finally:
            if close_session:
                await session.close()

        return vacancies[:limit]

    async def parse_vacancy_detail(self, session: aiohttp.ClientSession, vacancy_id: str) -> Optional[Dict[str, Any]]:
        async with session.get(f"{self.BASE_URL}/vacancies/{vacancy_id}") as resp:
            if resp.status != 200:
                return None

            data = await resp.json()

            description_html = data.get("description", "") or ""
            description_text = self._html_to_text(description_html)

            skills = [skill.get("name") for skill in data.get("key_skills", []) if skill.get("name")]
            parsed_skills = self.parse_skills(description_text)
            skills = list(dict.fromkeys(skills + parsed_skills))

            address_raw = None
            address_data = data.get("address") or {}
            if isinstance(address_data, dict):
                address_raw = address_data.get("raw")

            # Преобразование в нашу структуру
            vacancy = {
                "title": data.get("name", ""),
                "description": description_text,
                "salary": self.normalize_salary(data.get("salary")),
                "company": {
                    "name": data.get("employer", {}).get("name", ""),
                    "website": data.get("employer", {}).get("site_url", ""),
                },
                "experience": data.get("experience", {}).get("name", ""),
                "work_format": self.parse_work_format(data),
                "work_schedule": self.parse_work_schedule(data),
                "location": data.get("area", {}).get("name", ""),
                "raw_address": address_raw,
                "skills": skills,
                "source_url": data.get("alternate_url", ""),
                "published_date": self.parse_published_date(data.get("published_at")),
            }

            return vacancy

    def _html_to_text(self, html: str) -> str:
        if not html:
            return ""
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator=" ", strip=True)

    def parse_work_format(self, data: Dict[str, Any]) -> str:
        # Пытаемся извлечь формат работы из разных полей
        work_format = None

        modes = data.get("working_time_modes")
        if isinstance(modes, list) and modes:
            work_format = modes[0].get("name")

        if not work_format:
            work_format_field = data.get("work_format")
            if isinstance(work_format_field, dict):
                work_format = work_format_field.get("name")
            elif isinstance(work_format_field, list) and work_format_field:
                first = work_format_field[0]
                if isinstance(first, dict):
                    work_format = first.get("name")

        if not work_format:
            schedule = (data.get("schedule") or {}).get("name")
            if schedule and "удал" in schedule.lower():
                work_format = "Удаленно"

        return work_format or "Любой"

    def parse_work_schedule(self, data: Dict[str, Any]) -> str:
        schedule = (data.get("schedule") or {}).get("name")
        return schedule or "Полный день"

    def parse_published_date(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        # Приводим к ISO 8601 с двоеточием в таймзоне
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        match = re.match(r"^(.*[T ]\d{2}:\d{2}:\d{2})([+-]\d{2})(\d{2})$", value)
        if match:
            value = f"{match.group(1)}{match.group(2)}:{match.group(3)}"
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None