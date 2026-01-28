from sqlalchemy.ext.asyncio import AsyncSession
from app.models.experience import Experience
from app.models.work_format import WorkFormat
from app.models.work_schedule import WorkSchedule

async def init_reference_data(db: AsyncSession):
    # Опыт работы
    experiences = [
        Experience(name="Нет опыта", order=1),
        Experience(name="1–3 года", order=2),
        Experience(name="3–6 лет", order=3),
        Experience(name="Более 6 лет", order=4),
    ]
    
    # Форматы работы
    work_formats = [
        WorkFormat(name="Офис"),
        WorkFormat(name="Удаленно"),
        WorkFormat(name="Гибрид"),
        WorkFormat(name="Любой"),
    ]
    
    # Графики работы
    work_schedules = [
        WorkSchedule(name="Полный день"),
        WorkSchedule(name="Сменный график"),
        WorkSchedule(name="Гибкий график"),
        WorkSchedule(name="Вахта"),
        WorkSchedule(name="Частичная занятость"),
    ]
    
    # Добавляем все в базу
    for exp in experiences:
        db.add(exp)
    for wf in work_formats:
        db.add(wf)
    for ws in work_schedules:
        db.add(ws)
    
    await db.commit()