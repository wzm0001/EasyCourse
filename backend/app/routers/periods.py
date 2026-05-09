from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.common import APIResponse
from app.schemas.period import (
    GradePeriodSetup,
    GradePeriodInfo,
    DayPeriodBatch,
    DayPeriodInfo,
    PeriodConfigItem,
    PeriodTemplateCreate,
    PeriodTemplateInfo,
)
from app.services.period import (
    setup_grade_periods,
    get_grade_periods,
    setup_day_periods,
    get_day_periods,
    get_available_periods,
    create_template,
    get_templates,
    apply_template,
)
from app.middleware.auth import get_current_user_dependency
from app.utils.semester_guard import check_semester_writable

router = APIRouter(prefix="/periods", tags=["时间段管理"])


def _ensure_school_access(current_user: User, target_school_id: str = None) -> str:
    if current_user.role == UserRole.SUPER_ADMIN:
        if target_school_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="超管需指定学校"
            )
        return target_school_id
    if current_user.school_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无关联学校"
        )
    if target_school_id is not None and current_user.school_id != target_school_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="权限不足"
        )
    return current_user.school_id


@router.get("/grades/{grade_id}", response_model=APIResponse[GradePeriodInfo])
async def get_grade_periods_endpoint(
    grade_id: str,
    semester_id: str = Query(...),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = _ensure_school_access(current_user)
    result = await get_grade_periods(grade_id, semester_id, db)
    return APIResponse.success(data=result)


@router.post("/grades/{grade_id}", response_model=APIResponse[GradePeriodInfo])
async def setup_grade_periods_endpoint(
    grade_id: str,
    data: GradePeriodSetup,
    semester_id: str = Query(...),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = _ensure_school_access(current_user)
    await check_semester_writable(db, semester_id)
    data.grade_id = grade_id
    result = await setup_grade_periods(data, school_id, semester_id, db)
    return APIResponse.success(data=result)


@router.get("/grades/{grade_id}/days", response_model=APIResponse[DayPeriodInfo])
async def get_day_periods_endpoint(
    grade_id: str,
    semester_id: str = Query(...),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = _ensure_school_access(current_user)
    result = await get_day_periods(grade_id, semester_id, db)
    return APIResponse.success(data=result)


@router.post("/grades/{grade_id}/days", response_model=APIResponse[DayPeriodInfo])
async def setup_day_periods_endpoint(
    grade_id: str,
    data: DayPeriodBatch,
    semester_id: str = Query(...),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = _ensure_school_access(current_user)
    await check_semester_writable(db, semester_id)
    data.grade_id = grade_id
    result = await setup_day_periods(data, school_id, semester_id, db)
    return APIResponse.success(data=result)


@router.get("/grades/{grade_id}/available", response_model=APIResponse[List[PeriodConfigItem]])
async def get_available_periods_endpoint(
    grade_id: str,
    semester_id: str = Query(...),
    day_of_week: int = Query(..., ge=1, le=7),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = _ensure_school_access(current_user)
    result = await get_available_periods(grade_id, semester_id, day_of_week, db)
    return APIResponse.success(data=result)


@router.get("/templates", response_model=APIResponse[List[PeriodTemplateInfo]])
async def get_templates_endpoint(
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = _ensure_school_access(current_user)
    templates = await get_templates(school_id, db)
    items = [
        PeriodTemplateInfo(
            id=t.id,
            name=t.name,
            description=t.description,
            config_data=t.config_data,
            is_system=t.is_system,
        )
        for t in templates
    ]
    return APIResponse.success(data=items)


@router.post("/templates", response_model=APIResponse[PeriodTemplateInfo])
async def create_template_endpoint(
    data: PeriodTemplateCreate,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = _ensure_school_access(current_user)
    template = await create_template(data, school_id, db)
    return APIResponse.success(
        data=PeriodTemplateInfo(
            id=template.id,
            name=template.name,
            description=template.description,
            config_data=template.config_data,
            is_system=template.is_system,
        )
    )


@router.post("/templates/{template_id}/apply", response_model=APIResponse[GradePeriodInfo])
async def apply_template_endpoint(
    template_id: str,
    grade_id: str = Query(...),
    semester_id: str = Query(...),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = _ensure_school_access(current_user)
    await check_semester_writable(db, semester_id)
    result = await apply_template(template_id, grade_id, semester_id, school_id, db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="模板不存在"
        )
    return APIResponse.success(data=result)
