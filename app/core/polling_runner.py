import asyncio
import time
import logging

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.polling import load_polling_state
from app.crud.vacancy import vacancy_crud
from app.services.parsers.hh_parser import HHParser

logger = logging.getLogger(__name__)


async def polling_loop() -> None:
    logger.info(
        "Polling loop initialized, interval=%ss", settings.POLLING_INTERVAL_SECONDS
    )
    # Первый цикл: небольшая задержка, чтобы сервер успел подняться
    await asyncio.sleep(5)

    while True:
        state = load_polling_state()
        enabled = state.get("enabled", True)
        query = state.get("title")

        if not enabled or not query:
            logger.info("Polling skipped: enabled=%s query=%s", enabled, query)
            await asyncio.sleep(settings.POLLING_INTERVAL_SECONDS)
            continue

        limit = min(state.get("limit", 20), 20)
        area = state.get("area", 1)

        logger.info(
            "Polling cycle START: query='%s' limit=%s area=%s", query, limit, area
        )
        t0 = time.monotonic()

        try:
            # --- Шаг 1: получить список вакансий (только ID/url, без деталей) ---
            parser = HHParser()
            async with parser:
                vacancies = await parser.parse_vacancies(
                    search_query=query,
                    limit=limit,
                    area=area,
                    only_with_salary=state.get("only_with_salary", False),
                    light=True,
                )
            t1 = time.monotonic()
            logger.info(
                "Polling hh.ru done: fetched=%s time=%.1fs", len(vacancies), t1 - t0
            )

            # --- Шаг 2: сохранить в БД ---
            async with AsyncSessionLocal() as db:
                added = 0
                skipped = 0
                for vacancy_data in vacancies:
                    source_url = vacancy_data.get("source_url")
                    if not source_url:
                        continue
                    existing = await vacancy_crud.get_by_source_url(db, source_url)
                    if not existing:
                        await vacancy_crud.create_from_parsed(
                            db, vacancy_data, commit=False
                        )
                        added += 1
                    else:
                        skipped += 1
                await db.commit()

            t2 = time.monotonic()
            logger.info(
                "Polling cycle END: added=%s skipped=%s db_time=%.1fs total=%.1fs",
                added,
                skipped,
                t2 - t1,
                t2 - t0,
            )

        except Exception:
            logger.exception("Polling cycle FAILED after %.1fs", time.monotonic() - t0)

        logger.info("Polling sleeping %ss...", settings.POLLING_INTERVAL_SECONDS)
        await asyncio.sleep(settings.POLLING_INTERVAL_SECONDS)
