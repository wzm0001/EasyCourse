from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.common import APIResponse
from app.schemas.schedule import (
    ScheduleCellCreate, ScheduleCellUpdate, ScheduleCellInfo,
    ScheduleGrid, AutoScheduleRequest, AutoScheduleResult,
    SwapRequest, ScheduleLockInfo, ClearScheduleRequest,
)
from app.services import schedule as schedule_service
from app.middleware.auth import get_current_user_dependency
from app.repositories.semester import SemesterRepository

router = APIRouter(prefix="/schedules", tags=["排课管理"])


async def get_school_id(current_user: User) -> str:
    if current_user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="超级管理员需指定学校")
    if not current_user.school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    return current_user.school_id


async def resolve_semester_id(db: AsyncSession, school_id: str, semester_id: Optional[str]) -> str:
    if semester_id:
        return semester_id
    semester_repo = SemesterRepository(db)
    active = await semester_repo.get_active(school_id)
    if not active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="没有活跃学期，请指定学期")
    return active.id


@router.get("/class/{class_id}", response_model=APIResponse[ScheduleGrid])
async def get_class_schedule(
    class_id: str,
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = current_user.school_id
    if current_user.role == UserRole.SUPER_ADMIN:
        if not school_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="超级管理员需指定学校")
    sid = await resolve_semester_id(db, school_id, semester_id) if school_id else semester_id
    if not sid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请指定学期")
    grid = await schedule_service.get_class_schedule(class_id, sid, db)
    return APIResponse.success(data=grid)


@router.get("/teacher/{teacher_id}", response_model=APIResponse[ScheduleGrid])
async def get_teacher_schedule(
    teacher_id: str,
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = current_user.school_id
    if current_user.role == UserRole.SUPER_ADMIN:
        if not school_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="超级管理员需指定学校")
    sid = await resolve_semester_id(db, school_id, semester_id) if school_id else semester_id
    if not sid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请指定学期")
    grid = await schedule_service.get_teacher_schedule(teacher_id, sid, db)
    return APIResponse.success(data=grid)


@router.get("/classroom/{classroom_id}", response_model=APIResponse[ScheduleGrid])
async def get_classroom_schedule(
    classroom_id: str,
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = current_user.school_id
    if current_user.role == UserRole.SUPER_ADMIN:
        if not school_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="超级管理员需指定学校")
    sid = await resolve_semester_id(db, school_id, semester_id) if school_id else semester_id
    if not sid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请指定学期")
    grid = await schedule_service.get_classroom_schedule(classroom_id, sid, db)
    return APIResponse.success(data=grid)


@router.get("/grade/{grade_id}", response_model=APIResponse[List[ScheduleGrid]])
async def get_grade_schedule(
    grade_id: str,
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = current_user.school_id
    if current_user.role == UserRole.SUPER_ADMIN:
        if not school_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="超级管理员需指定学校")
    sid = await resolve_semester_id(db, school_id, semester_id) if school_id else semester_id
    if not sid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请指定学期")
    grids = await schedule_service.get_grade_schedule(grade_id, sid, db)
    return APIResponse.success(data=grids)


@router.get("/school", response_model=APIResponse[List[ScheduleGrid]])
async def get_school_schedule(
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    sid = await resolve_semester_id(db, school_id, semester_id)
    grids = await schedule_service.get_school_schedule(school_id, sid, db)
    return APIResponse.success(data=grids)


@router.post("/place", response_model=APIResponse[ScheduleCellInfo])
async def place_schedule_cell(
    request: ScheduleCellCreate,
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    sid = await resolve_semester_id(db, school_id, semester_id)
    try:
        cell, conflicts = await schedule_service.place_cell(request.model_dump(), school_id, sid, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    from app.repositories.basic_data import CourseRepository, TeacherRepository, ClassroomRepository
    course_repo = CourseRepository(db)
    teacher_repo = TeacherRepository(db)
    classroom_repo = ClassroomRepository(db)
    course_name = None
    teacher_name = None
    classroom_name = None
    if cell.course_id:
        course = await course_repo.get_by_id(cell.course_id)
        course_name = course.name if course else None
    if cell.teacher_id:
        teacher = await teacher_repo.get_by_id(cell.teacher_id)
        teacher_name = teacher.name if teacher else None
    if cell.classroom_id:
        classroom = await classroom_repo.get_by_id(cell.classroom_id)
        classroom_name = classroom.name if classroom else None

    info = schedule_service._cell_to_info(cell, course_name, teacher_name, classroom_name)
    if conflicts:
        return APIResponse(data=info, message=f"放置成功，但存在{len(conflicts)}个冲突", code=0)
    return APIResponse.success(data=info)


@router.delete("/cells/{cell_id}", response_model=APIResponse)
async def remove_schedule_cell(
    cell_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    try:
        removed = await schedule_service.remove_cell(cell_id, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="单元格不存在")
    return APIResponse.success(message="移除成功")


@router.post("/cells/{cell_id}/fix", response_model=APIResponse[ScheduleCellInfo])
async def fix_schedule_cell(
    cell_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    cell = await schedule_service.fix_cell(cell_id, db)
    if not cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="单元格不存在")
    from app.repositories.basic_data import CourseRepository, TeacherRepository, ClassroomRepository
    course_repo = CourseRepository(db)
    teacher_repo = TeacherRepository(db)
    classroom_repo = ClassroomRepository(db)
    course_name = None
    teacher_name = None
    classroom_name = None
    if cell.course_id:
        course = await course_repo.get_by_id(cell.course_id)
        course_name = course.name if course else None
    if cell.teacher_id:
        teacher = await teacher_repo.get_by_id(cell.teacher_id)
        teacher_name = teacher.name if teacher else None
    if cell.classroom_id:
        classroom = await classroom_repo.get_by_id(cell.classroom_id)
        classroom_name = classroom.name if classroom else None
    info = schedule_service._cell_to_info(cell, course_name, teacher_name, classroom_name)
    return APIResponse.success(data=info)


@router.post("/cells/{cell_id}/unfix", response_model=APIResponse[ScheduleCellInfo])
async def unfix_schedule_cell(
    cell_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    cell = await schedule_service.unfix_cell(cell_id, db)
    if not cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="单元格不存在")
    from app.repositories.basic_data import CourseRepository, TeacherRepository, ClassroomRepository
    course_repo = CourseRepository(db)
    teacher_repo = TeacherRepository(db)
    classroom_repo = ClassroomRepository(db)
    course_name = None
    teacher_name = None
    classroom_name = None
    if cell.course_id:
        course = await course_repo.get_by_id(cell.course_id)
        course_name = course.name if course else None
    if cell.teacher_id:
        teacher = await teacher_repo.get_by_id(cell.teacher_id)
        teacher_name = teacher.name if teacher else None
    if cell.classroom_id:
        classroom = await classroom_repo.get_by_id(cell.classroom_id)
        classroom_name = classroom.name if classroom else None
    info = schedule_service._cell_to_info(cell, course_name, teacher_name, classroom_name)
    return APIResponse.success(data=info)


@router.post("/swap", response_model=APIResponse)
async def swap_schedule_cells(
    request: SwapRequest,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    try:
        success, conflicts = await schedule_service.swap_cells(request.cell_id_1, request.cell_id_2, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if conflicts:
        return APIResponse(data={"conflicts": [c.model_dump() for c in conflicts]}, message=f"互换成功，但存在{len(conflicts)}个冲突", code=0)
    return APIResponse.success(message="互换成功")


@router.post("/auto", response_model=APIResponse[AutoScheduleResult])
async def auto_schedule(
    request: AutoScheduleRequest,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    result = await schedule_service.auto_schedule(school_id, request.semester_id, request.grade_id, db)
    return APIResponse.success(data=result)


@router.post("/clear", response_model=APIResponse)
async def clear_schedule(
    request: ClearScheduleRequest,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    count = await schedule_service.clear_schedule(school_id, request.semester_id, request.grade_id, db)
    return APIResponse.success(message=f"已清除{count}条非固定排课记录")


@router.get("/lock", response_model=APIResponse[ScheduleLockInfo])
async def check_schedule_lock(
    semester_id: str = Query(...),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    lock_info = await schedule_service.check_lock(semester_id, db)
    return APIResponse.success(data=lock_info)


@router.post("/lock/acquire", response_model=APIResponse)
async def acquire_schedule_lock(
    semester_id: str = Query(...),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    acquired = await schedule_service.acquire_lock(semester_id, school_id, current_user.id, db)
    if not acquired:
        lock_info = await schedule_service.check_lock(semester_id, db)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"排课锁已被其他用户持有: {lock_info.user_name if lock_info else '未知'}")
    return APIResponse.success(message="获取排课锁成功")


@router.post("/lock/release", response_model=APIResponse)
async def release_schedule_lock(
    semester_id: str = Query(...),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    released = await schedule_service.release_lock(semester_id, current_user.id, db)
    if not released:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有锁持有者才能释放排课锁")
    return APIResponse.success(message="释放排课锁成功")
