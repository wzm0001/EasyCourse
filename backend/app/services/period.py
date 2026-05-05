import json
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.period import GradePeriodConfig, DayPeriodConfig, PeriodTemplate, PeriodType
from app.repositories.period import (
    GradePeriodConfigRepository,
    DayPeriodConfigRepository,
    PeriodTemplateRepository,
)
from app.schemas.period import (
    PeriodConfigItem,
    GradePeriodSetup,
    DayPeriodSetup,
    DayPeriodBatch,
    PeriodTemplateCreate,
    GradePeriodInfo,
    DayPeriodInfo,
)


async def setup_grade_periods(
    data: GradePeriodSetup, school_id: str, semester_id: str, db: AsyncSession
) -> GradePeriodInfo:
    repo = GradePeriodConfigRepository(db)
    await repo.delete_by_grade_semester(data.grade_id, semester_id)
    for item in data.periods:
        config = GradePeriodConfig(
            school_id=school_id,
            semester_id=semester_id,
            grade_id=data.grade_id,
            period_type=item.period_type,
            period_index=item.period_index,
            start_time=item.start_time,
            end_time=item.end_time,
        )
        await repo.create(config)
    return GradePeriodInfo(grade_id=data.grade_id, periods=data.periods)


async def get_grade_periods(
    grade_id: str, semester_id: str, db: AsyncSession
) -> GradePeriodInfo:
    repo = GradePeriodConfigRepository(db)
    configs = await repo.get_by_grade_semester(grade_id, semester_id)
    periods = [
        PeriodConfigItem(
            period_type=c.period_type,
            period_index=c.period_index,
            start_time=c.start_time,
            end_time=c.end_time,
        )
        for c in configs
    ]
    return GradePeriodInfo(grade_id=grade_id, periods=periods)


async def setup_day_periods(
    data: DayPeriodBatch, school_id: str, semester_id: str, db: AsyncSession
) -> DayPeriodInfo:
    repo = DayPeriodConfigRepository(db)
    await repo.delete_by_grade_semester(data.grade_id, semester_id)
    for item in data.configs:
        config = DayPeriodConfig(
            school_id=school_id,
            semester_id=semester_id,
            grade_id=data.grade_id,
            day_of_week=item.day_of_week,
            period_type=item.period_type,
            period_index=item.period_index,
            is_available=item.is_available,
        )
        await repo.create(config)
    return DayPeriodInfo(grade_id=data.grade_id, configs=data.configs)


async def get_day_periods(
    grade_id: str, semester_id: str, db: AsyncSession
) -> DayPeriodInfo:
    repo = DayPeriodConfigRepository(db)
    configs = await repo.get_by_grade_semester(grade_id, semester_id)
    day_configs = [
        DayPeriodSetup(
            day_of_week=c.day_of_week,
            period_type=c.period_type,
            period_index=c.period_index,
            is_available=c.is_available,
        )
        for c in configs
    ]
    return DayPeriodInfo(grade_id=grade_id, configs=day_configs)


async def get_available_periods(
    grade_id: str, semester_id: str, day_of_week: int, db: AsyncSession
) -> List[PeriodConfigItem]:
    grade_repo = GradePeriodConfigRepository(db)
    day_repo = DayPeriodConfigRepository(db)
    grade_configs = await grade_repo.get_by_grade_semester(grade_id, semester_id)
    day_configs = await day_repo.get_by_grade_semester(grade_id, semester_id)
    unavailable_set = set()
    for dc in day_configs:
        if dc.day_of_week == day_of_week and not dc.is_available:
            unavailable_set.add((dc.period_type, dc.period_index))
    available = []
    for gc in grade_configs:
        if (gc.period_type, gc.period_index) not in unavailable_set:
            available.append(
                PeriodConfigItem(
                    period_type=gc.period_type,
                    period_index=gc.period_index,
                    start_time=gc.start_time,
                    end_time=gc.end_time,
                )
            )
    return available


async def create_template(
    data: PeriodTemplateCreate, school_id: str, db: AsyncSession
) -> PeriodTemplate:
    repo = PeriodTemplateRepository(db)
    template = PeriodTemplate(
        name=data.name,
        description=data.description,
        config_data=data.config_data,
        is_system=False,
    )
    return await repo.create(template)


async def get_templates(school_id: str, db: AsyncSession) -> List[PeriodTemplate]:
    repo = PeriodTemplateRepository(db)
    system_templates = await repo.get_system_templates()
    custom_templates = await repo.get_custom_templates(school_id)
    return system_templates + custom_templates


async def apply_template(
    template_id: str, grade_id: str, semester_id: str, school_id: str, db: AsyncSession
) -> GradePeriodInfo:
    template_repo = PeriodTemplateRepository(db)
    template = await template_repo.get_by_id(template_id)
    if template is None:
        return None
    config = json.loads(template.config_data)
    periods_data = config.get("periods", [])
    periods = [
        PeriodConfigItem(
            period_type=p["period_type"],
            period_index=p["period_index"],
            start_time=p["start_time"],
            end_time=p["end_time"],
        )
        for p in periods_data
    ]
    setup = GradePeriodSetup(grade_id=grade_id, periods=periods)
    result = await setup_grade_periods(setup, school_id, semester_id, db)
    available_days = config.get("available_days", [1, 2, 3, 4, 5])
    day_repo = DayPeriodConfigRepository(db)
    await day_repo.delete_by_grade_semester(grade_id, semester_id)
    for day in range(1, 8):
        is_available = day in available_days
        for p in periods_data:
            day_config = DayPeriodConfig(
                school_id=school_id,
                semester_id=semester_id,
                grade_id=grade_id,
                day_of_week=day,
                period_type=p["period_type"],
                period_index=p["period_index"],
                is_available=is_available,
            )
            await day_repo.create(day_config)
    return result


async def init_system_templates(db: AsyncSession) -> None:
    repo = PeriodTemplateRepository(db)
    existing = await repo.get_system_templates()
    if existing:
        return

    five_day_periods = [
        {"period_type": "morning_reading", "period_index": 1, "start_time": "07:00", "end_time": "07:30"},
        {"period_type": "regular", "period_index": 1, "start_time": "08:00", "end_time": "08:45"},
        {"period_type": "regular", "period_index": 2, "start_time": "08:55", "end_time": "09:40"},
        {"period_type": "regular", "period_index": 3, "start_time": "10:00", "end_time": "10:45"},
        {"period_type": "regular", "period_index": 4, "start_time": "10:55", "end_time": "11:40"},
        {"period_type": "regular", "period_index": 5, "start_time": "14:00", "end_time": "14:45"},
        {"period_type": "regular", "period_index": 6, "start_time": "14:55", "end_time": "15:40"},
        {"period_type": "regular", "period_index": 7, "start_time": "16:00", "end_time": "16:45"},
        {"period_type": "regular", "period_index": 8, "start_time": "16:55", "end_time": "17:40"},
    ]

    five_day_config = json.dumps(
        {"periods": five_day_periods, "available_days": [1, 2, 3, 4, 5]},
        ensure_ascii=False,
    )
    five_day_template = PeriodTemplate(
        name="标准五天制",
        description="周一至周五，早读1节+正课8节",
        config_data=five_day_config,
        is_system=True,
    )
    await repo.create(five_day_template)

    six_day_config = json.dumps(
        {"periods": five_day_periods, "available_days": [1, 2, 3, 4, 5, 6]},
        ensure_ascii=False,
    )
    six_day_template = PeriodTemplate(
        name="六天制",
        description="周一至周六，早读1节+正课8节",
        config_data=six_day_config,
        is_system=True,
    )
    await repo.create(six_day_template)
