from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.services import schedule_export as export_service
from app.middleware.auth import get_current_user_dependency

router = APIRouter(prefix="/exports", tags=["课表导出"])


async def _get_school_id(current_user: User) -> str:
    if current_user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="超级管理员需指定学校")
    if not current_user.school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    return current_user.school_id


def _stream_response(data: bytes, filename: str, content_type: str) -> StreamingResponse:
    import io
    return StreamingResponse(
        io.BytesIO(data),
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/class/{class_id}/excel")
async def export_class_excel(
    class_id: str,
    semester_id: str = Query(...),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    data = await export_service.export_class_schedule_excel(class_id, semester_id, db)
    return _stream_response(data, f"class_{class_id}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@router.get("/class/{class_id}/pdf")
async def export_class_pdf(
    class_id: str,
    semester_id: str = Query(...),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    data = await export_service.export_class_schedule_pdf(class_id, semester_id, db)
    return _stream_response(data, f"class_{class_id}.pdf", "application/pdf")


@router.get("/teacher/{teacher_id}/excel")
async def export_teacher_excel(
    teacher_id: str,
    semester_id: str = Query(...),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    data = await export_service.export_teacher_schedule_excel(teacher_id, semester_id, db)
    return _stream_response(data, f"teacher_{teacher_id}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@router.get("/teacher/{teacher_id}/pdf")
async def export_teacher_pdf(
    teacher_id: str,
    semester_id: str = Query(...),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    data = await export_service.export_teacher_schedule_pdf(teacher_id, semester_id, db)
    return _stream_response(data, f"teacher_{teacher_id}.pdf", "application/pdf")


@router.get("/batch/teachers")
async def batch_export_teachers(
    semester_id: str = Query(...),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await _get_school_id(current_user)
    data = await export_service.batch_export_teacher_schedules(school_id, semester_id, db)
    return _stream_response(data, "teachers_schedules.zip", "application/zip")


@router.get("/batch/classes")
async def batch_export_classes(
    semester_id: str = Query(...),
    grade_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await _get_school_id(current_user)
    data = await export_service.batch_export_class_schedules(school_id, semester_id, grade_id, db)
    return _stream_response(data, "classes_schedules.zip", "application/zip")


class CustomExportRequest(BaseModel):
    format: str = "excel"
    scope: str = "class"
    ids: List[str] = []
    include_classroom: bool = False


@router.post("/custom")
async def custom_export(
    request: CustomExportRequest,
    semester_id: str = Query(...),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await _get_school_id(current_user)
    options = {
        "format": request.format,
        "scope": request.scope,
        "ids": request.ids,
        "include_classroom": request.include_classroom,
    }
    data = await export_service.custom_export(school_id, semester_id, options, db)

    if request.format == "pdf":
        if len(request.ids) <= 1:
            return _stream_response(data, "schedule.pdf", "application/pdf")
        return _stream_response(data, "schedules.zip", "application/zip")

    if len(request.ids) <= 1:
        return _stream_response(data, "schedule.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    return _stream_response(data, "schedules.zip", "application/zip")
