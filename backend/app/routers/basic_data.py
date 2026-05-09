from io import BytesIO
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User, UserRole
from app.models.basic_data import TeacherCourse, TeachingArrangement, Class_, Course, Teacher, Grade, Classroom
from app.models.schedule import ScheduleCell
from app.schemas.common import APIResponse, PageResponse
from app.schemas.basic_data import (
    GradeCreate, GradeUpdate, GradeInfo,
    ClassCreate, ClassUpdate, ClassInfo,
    CourseCreate, CourseUpdate, CourseInfo,
    GradeCourseCreate, GradeCourseUpdate, GradeCourseInfo,
    BatchGradeCourseCreate,
    TeacherCreate, TeacherUpdate, TeacherInfo,
    TeacherCourseCreate, TeacherCourseInfo, TeacherCourseBatchSet,
    ClassroomCreate, ClassroomUpdate, ClassroomInfo,
    ClassroomCourseCreate, ClassroomCourseInfo, ClassroomCourseBatchSet,
    TeachingArrangementCreate, TeachingArrangementUpdate, TeachingArrangementInfo,
    QuickSetupRequest, QuickSetupResult, BatchTeachingArrangementCreate,
    TeachingArrangementSummary,
)
from app.services.basic_data import (
    GradeService, ClassService, CourseService, GradeCourseService,
    TeacherService, TeacherCourseService, ClassroomService,
    ClassroomCourseService, TeachingArrangementService, QuickSetupService,
)
from app.services.excel_import_export import download_template, import_data, export_data
from app.middleware.auth import get_current_user_dependency
from app.repositories.semester import SemesterRepository
from app.repositories.user import UserRepository
from app.repositories.basic_data import (
    GradeRepository, ClassRepository, CourseRepository,
    GradeCourseRepository,
    TeacherRepository, ClassroomRepository, TeachingArrangementRepository,
)
from app.utils.semester_guard import check_semester_writable, resolve_semester_id_with_archive_check

router = APIRouter(prefix="/basic-data", tags=["基础数据管理"])


async def get_school_id(current_user: User) -> str:
    if current_user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="超级管理员需指定学校")
    if not current_user.school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    return current_user.school_id


async def resolve_semester_id(db: AsyncSession, school_id: str, semester_id: Optional[str], raise_if_missing: bool = True, check_archive: bool = False) -> Optional[str]:
    if check_archive:
        return await resolve_semester_id_with_archive_check(db, school_id, semester_id, raise_if_missing)
    if semester_id:
        return semester_id
    semester_repo = SemesterRepository(db)
    active = await semester_repo.get_active(school_id)
    if not active:
        if raise_if_missing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="没有活跃学期，请指定学期")
        return None
    return active.id


async def build_grade_info(g: Grade, db: AsyncSession, course_count: int = 0) -> GradeInfo:
    grade_leader_name = None
    if g.grade_leader_id:
        result = await db.execute(select(Teacher).where(Teacher.id == g.grade_leader_id))
        leader = result.scalar_one_or_none()
        if leader:
            grade_leader_name = leader.name
    return GradeInfo(
        id=g.id, school_id=g.school_id, semester_id=g.semester_id, name=g.name,
        sort_order=g.sort_order, morning_reading_count=g.morning_reading_count,
        regular_class_count=g.regular_class_count, evening_study_count=g.evening_study_count,
        grade_leader_id=g.grade_leader_id, grade_leader_name=grade_leader_name,
        course_count=course_count, created_at=g.created_at,
    )


@router.get("/grades", response_model=APIResponse[PageResponse[GradeInfo]])
async def get_grades(
    semester_id: Optional[str] = Query(None),
    page: int = Query(1),
    page_size: int = Query(20),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    sid = await resolve_semester_id(db, school_id, semester_id, raise_if_missing=False)
    if not sid:
        return APIResponse.success(data=PageResponse(items=[], total=0, page=page, page_size=page_size))
    service = GradeService(db)
    grades, total = await service.get_list(school_id, sid, page, page_size)
    grade_course_repo = GradeCourseRepository(db)
    items = []
    for g in grades:
        grade_courses = await grade_course_repo.get_by_grade(g.id)
        course_count = len(grade_courses)
        items.append(await build_grade_info(g, db, course_count))
    return APIResponse.success(data=PageResponse(items=items, total=total, page=page, page_size=page_size))


@router.post("/grades", response_model=APIResponse[GradeInfo])
async def create_grade(
    request: GradeCreate,
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    sid = await resolve_semester_id(db, school_id, semester_id, check_archive=True)
    service = GradeService(db)
    grade = await service.create(school_id, sid, request.model_dump())
    return APIResponse.success(data=await build_grade_info(grade, db))


@router.put("/grades/{grade_id}", response_model=APIResponse[GradeInfo])
async def update_grade(
    grade_id: str,
    request: GradeUpdate,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    service = GradeService(db)
    grade = await service.get_by_id(grade_id)
    if not grade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="年级不存在")
    if current_user.role != UserRole.SUPER_ADMIN and current_user.school_id != grade.school_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    await check_semester_writable(db, grade.semester_id)
    updated = await service.update(grade_id, request.model_dump(exclude_unset=True))
    grade_course_repo = GradeCourseRepository(db)
    grade_courses = await grade_course_repo.get_by_grade(updated.id)
    course_count = len(grade_courses)
    return APIResponse.success(data=await build_grade_info(updated, db, course_count))


@router.delete("/grades/{grade_id}", response_model=APIResponse)
async def delete_grade(
    grade_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    service = GradeService(db)
    grade = await service.get_by_id(grade_id)
    if not grade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="年级不存在")
    if current_user.role != UserRole.SUPER_ADMIN and current_user.school_id != grade.school_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    await check_semester_writable(db, grade.semester_id)
    try:
        deleted = await service.delete(grade_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not deleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="年级下存在关联班级或课程，无法删除")
    return APIResponse.success(message="删除成功")


@router.get("/classes", response_model=APIResponse[PageResponse[ClassInfo]])
async def get_classes(
    grade_id: Optional[str] = Query(None),
    semester_id: Optional[str] = Query(None),
    page: int = Query(1),
    page_size: int = Query(20),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    sid = await resolve_semester_id(db, school_id, semester_id, raise_if_missing=False)
    if not sid:
        return APIResponse.success(data=PageResponse(items=[], total=0, page=page, page_size=page_size))
    service = ClassService(db)
    classes, total = await service.get_list(school_id, sid, grade_id, page, page_size)
    items = []
    for c in classes:
        head_teacher_name = None
        if c.head_teacher_id:
            teacher_repo = TeacherRepository(db)
            ht = await teacher_repo.get_by_id(c.head_teacher_id)
            if ht:
                head_teacher_name = ht.name
        classroom_name = None
        if c.classroom_id:
            classroom_repo = ClassroomRepository(db)
            classroom = await classroom_repo.get_by_id(c.classroom_id)
            if classroom:
                classroom_name = f"{classroom.building_name} {classroom.room_number}"
        grade_name = None
        if c.grade_id:
            grade_repo = GradeRepository(db)
            grade = await grade_repo.get_by_id(c.grade_id)
            if grade:
                grade_name = grade.name
        items.append(ClassInfo(
            id=c.id, school_id=c.school_id, semester_id=c.semester_id,
            grade_id=c.grade_id, name=c.name, head_teacher_id=c.head_teacher_id,
            head_teacher_name=head_teacher_name, classroom_id=c.classroom_id,
            classroom_name=classroom_name, grade_name=grade_name,
            is_teaching_class=c.is_teaching_class,
            created_at=c.created_at,
        ))
    return APIResponse.success(data=PageResponse(items=items, total=total, page=page, page_size=page_size))


@router.post("/classes", response_model=APIResponse[ClassInfo])
async def create_class(
    request: ClassCreate,
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    sid = await resolve_semester_id(db, school_id, semester_id, check_archive=True)
    service = ClassService(db)
    cls = await service.create(school_id, sid, request.model_dump())
    head_teacher_name = None
    if cls.head_teacher_id:
        teacher_repo = TeacherRepository(db)
        ht = await teacher_repo.get_by_id(cls.head_teacher_id)
        if ht:
            head_teacher_name = ht.name
    classroom_name = None
    if cls.classroom_id:
        classroom_repo = ClassroomRepository(db)
        classroom = await classroom_repo.get_by_id(cls.classroom_id)
        if classroom:
            classroom_name = f"{classroom.building_name} {classroom.room_number}"
    grade_name = None
    if cls.grade_id:
        grade_repo = GradeRepository(db)
        grade = await grade_repo.get_by_id(cls.grade_id)
        if grade:
            grade_name = grade.name
    return APIResponse.success(data=ClassInfo(
        id=cls.id, school_id=cls.school_id, semester_id=cls.semester_id,
        grade_id=cls.grade_id, name=cls.name, head_teacher_id=cls.head_teacher_id,
        head_teacher_name=head_teacher_name, classroom_id=cls.classroom_id,
        classroom_name=classroom_name, grade_name=grade_name,
        is_teaching_class=cls.is_teaching_class,
        created_at=cls.created_at,
    ))


@router.put("/classes/{class_id}", response_model=APIResponse[ClassInfo])
async def update_class(
    class_id: str,
    request: ClassUpdate,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    service = ClassService(db)
    cls = await service.get_by_id(class_id)
    if not cls:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="班级不存在")
    if current_user.role != UserRole.SUPER_ADMIN and current_user.school_id != cls.school_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    await check_semester_writable(db, cls.semester_id)
    updated = await service.update(class_id, request.model_dump(exclude_unset=True))
    head_teacher_name = None
    if updated.head_teacher_id:
        teacher_repo = TeacherRepository(db)
        ht = await teacher_repo.get_by_id(updated.head_teacher_id)
        if ht:
            head_teacher_name = ht.name
    classroom_name = None
    if updated.classroom_id:
        classroom_repo = ClassroomRepository(db)
        classroom = await classroom_repo.get_by_id(updated.classroom_id)
        if classroom:
            classroom_name = f"{classroom.building_name} {classroom.room_number}"
    grade_name = None
    if updated.grade_id:
        grade_repo = GradeRepository(db)
        grade = await grade_repo.get_by_id(updated.grade_id)
        if grade:
            grade_name = grade.name
    return APIResponse.success(data=ClassInfo(
        id=updated.id, school_id=updated.school_id, semester_id=updated.semester_id,
        grade_id=updated.grade_id, name=updated.name, head_teacher_id=updated.head_teacher_id,
        head_teacher_name=head_teacher_name, classroom_id=updated.classroom_id,
        classroom_name=classroom_name, grade_name=grade_name,
        is_teaching_class=updated.is_teaching_class,
        created_at=updated.created_at,
    ))


@router.delete("/classes/{class_id}", response_model=APIResponse)
async def delete_class(
    class_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    service = ClassService(db)
    cls = await service.get_by_id(class_id)
    if not cls:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="班级不存在")
    if current_user.role != UserRole.SUPER_ADMIN and current_user.school_id != cls.school_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    await check_semester_writable(db, cls.semester_id)
    deleted = await service.delete(class_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="班级下存在关联教学安排，无法删除")
    return APIResponse.success(message="删除成功")


@router.get("/courses", response_model=APIResponse[PageResponse[CourseInfo]])
async def get_courses(
    page: int = Query(1),
    page_size: int = Query(20),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    service = CourseService(db)
    courses, total = await service.get_list(school_id, page, page_size)
    items = [CourseInfo(id=c.id, school_id=c.school_id, code=c.code, name=c.name, course_type=c.course_type, weekly_hours=c.weekly_hours, created_at=c.created_at) for c in courses]
    return APIResponse.success(data=PageResponse(items=items, total=total, page=page, page_size=page_size))


@router.post("/courses", response_model=APIResponse[CourseInfo])
async def create_course(
    request: CourseCreate,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    service = CourseService(db)
    course = await service.create(school_id, request.model_dump())
    return APIResponse.success(data=CourseInfo(id=course.id, school_id=course.school_id, code=course.code, name=course.name, course_type=course.course_type, weekly_hours=course.weekly_hours, created_at=course.created_at))


@router.put("/courses/{course_id}", response_model=APIResponse[CourseInfo])
async def update_course(
    course_id: str,
    request: CourseUpdate,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    service = CourseService(db)
    course = await service.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")
    if current_user.role != UserRole.SUPER_ADMIN and current_user.school_id != course.school_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    updated = await service.update(course_id, request.model_dump(exclude_unset=True))
    return APIResponse.success(data=CourseInfo(id=updated.id, school_id=updated.school_id, code=updated.code, name=updated.name, course_type=updated.course_type, weekly_hours=updated.weekly_hours, created_at=updated.created_at))


@router.delete("/courses/{course_id}", response_model=APIResponse)
async def delete_course(
    course_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    service = CourseService(db)
    course = await service.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")
    if current_user.role != UserRole.SUPER_ADMIN and current_user.school_id != course.school_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    deleted = await service.delete(course_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="课程存在关联教学安排，无法删除")
    return APIResponse.success(message="删除成功")


@router.get("/grade-courses", response_model=APIResponse[PageResponse[GradeCourseInfo]])
async def get_grade_courses(
    grade_id: str = Query(...),
    period_type: Optional[str] = Query(None),
    page: int = Query(1),
    page_size: int = Query(20),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    service = GradeCourseService(db)
    grade_courses = await service.get_grade_courses(grade_id, period_type)
    course_repo = CourseRepository(db)
    items = []
    for gc in grade_courses:
        course = await course_repo.get_by_id(gc.course_id)
        course_name = course.name if course else None
        course_code = course.code if course else None
        items.append(GradeCourseInfo(id=gc.id, grade_id=gc.grade_id, course_id=gc.course_id, course_name=course_name, course_code=course_code, weekly_hours=gc.weekly_hours, period_type=gc.period_type))
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    paged = items[start:end]
    return APIResponse.success(data=PageResponse(items=paged, total=total, page=page, page_size=page_size))


@router.post("/grade-courses", response_model=APIResponse[GradeCourseInfo])
async def add_grade_course(
    request: GradeCourseCreate,
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    sid = await resolve_semester_id(db, school_id, semester_id, check_archive=True)
    service = GradeCourseService(db)
    gc = await service.add_course_to_grade(school_id, sid, request.grade_id, request.course_id, request.weekly_hours, request.period_type)
    course_repo = CourseRepository(db)
    course = await course_repo.get_by_id(gc.course_id)
    course_name = course.name if course else None
    course_code = course.code if course else None
    return APIResponse.success(data=GradeCourseInfo(id=gc.id, grade_id=gc.grade_id, course_id=gc.course_id, course_name=course_name, course_code=course_code, weekly_hours=gc.weekly_hours, period_type=gc.period_type))


@router.post("/grade-courses/batch", response_model=APIResponse)
async def batch_add_grade_courses(
    request: BatchGradeCourseCreate,
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    sid = await resolve_semester_id(db, school_id, semester_id, check_archive=True)
    service = GradeCourseService(db)
    results = await service.batch_add_courses_to_grade(school_id, sid, request.grade_id, [c.model_dump() for c in request.courses], request.period_type)
    return APIResponse.success(data={"count": len(results)})


@router.put("/grade-courses/{grade_course_id}", response_model=APIResponse[GradeCourseInfo])
async def update_grade_course(
    grade_course_id: str,
    request: GradeCourseUpdate,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    service = GradeCourseService(db)
    gc = await service.repo.get_by_id(grade_course_id)
    if not gc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="年级课程记录不存在")
    await check_semester_writable(db, gc.semester_id)
    if request.weekly_hours is not None or request.period_type is not None:
        gc = await service.update_grade_course(grade_course_id, request.weekly_hours, request.period_type)
    course_repo = CourseRepository(db)
    course = await course_repo.get_by_id(gc.course_id)
    course_name = course.name if course else None
    course_code = course.code if course else None
    return APIResponse.success(data=GradeCourseInfo(id=gc.id, grade_id=gc.grade_id, course_id=gc.course_id, course_name=course_name, course_code=course_code, weekly_hours=gc.weekly_hours, period_type=gc.period_type))


@router.delete("/grade-courses/{grade_course_id}", response_model=APIResponse)
async def delete_grade_course(
    grade_course_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    service = GradeCourseService(db)
    gc = await service.repo.get_by_id(grade_course_id)
    if not gc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="年级课程记录不存在")
    await check_semester_writable(db, gc.semester_id)
    deleted = await service.remove_course_from_grade(grade_course_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="年级课程记录不存在")
    return APIResponse.success(message="删除成功")


@router.get("/teachers", response_model=APIResponse[PageResponse[TeacherInfo]])
async def get_teachers(
    semester_id: Optional[str] = Query(None),
    page: int = Query(1),
    page_size: int = Query(20),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    sid = await resolve_semester_id(db, school_id, semester_id, raise_if_missing=False)
    if not sid:
        return APIResponse.success(data=PageResponse(items=[], total=0, page=page, page_size=page_size))
    service = TeacherService(db)
    teachers, total = await service.get_list(school_id, sid, page, page_size)
    items = []
    for t in teachers:
        tc_result = await db.execute(
            select(TeacherCourse, Course).join(Course, TeacherCourse.course_id == Course.id).where(
                TeacherCourse.teacher_id == t.id,
            )
        )
        tc_rows = tc_result.all()
        course_names = [c.name for _, c in tc_rows]

        arr_result = await db.execute(
            select(TeachingArrangement, Class_, Course).join(
                Class_, TeachingArrangement.class_id == Class_.id
            ).join(
                Course, TeachingArrangement.course_id == Course.id
            ).where(
                TeachingArrangement.teacher_id == t.id,
                TeachingArrangement.semester_id == sid,
            )
        )
        arr_rows = arr_result.all()
        arrangements = [
            {"class_id": cls.id, "class_name": cls.name, "course_id": c.id, "course_name": c.name, "weekly_hours": a.weekly_hours}
            for a, cls, c in arr_rows
        ]

        items.append(TeacherInfo(
            id=t.id, school_id=t.school_id, semester_id=t.semester_id,
            user_id=t.user_id, name=t.name, employee_id=t.employee_id,
            gender=t.gender, phone=t.phone, teaching_group=t.teaching_group,
            specialization=t.specialization,
            course_names=course_names, arrangements=arrangements,
            created_at=t.created_at,
        ))
    return APIResponse.success(data=PageResponse(items=items, total=total, page=page, page_size=page_size))


@router.post("/teachers", response_model=APIResponse[TeacherInfo])
async def create_teacher(
    request: TeacherCreate,
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    sid = await resolve_semester_id(db, school_id, semester_id, check_archive=True)
    service = TeacherService(db)
    try:
        teacher = await service.create(school_id, sid, request.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return APIResponse.success(data=TeacherInfo(
        id=teacher.id, school_id=teacher.school_id, semester_id=teacher.semester_id,
        user_id=teacher.user_id, name=teacher.name, employee_id=teacher.employee_id,
        gender=teacher.gender, phone=teacher.phone, teaching_group=teacher.teaching_group,
        specialization=teacher.specialization,
        created_at=teacher.created_at,
    ))


@router.put("/teachers/{teacher_id}", response_model=APIResponse[TeacherInfo])
async def update_teacher(
    teacher_id: str,
    request: TeacherUpdate,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    service = TeacherService(db)
    teacher = await service.get_by_id(teacher_id)
    if not teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="教师不存在")
    if current_user.role != UserRole.SUPER_ADMIN and current_user.school_id != teacher.school_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    await check_semester_writable(db, teacher.semester_id)
    updated = await service.update(teacher_id, request.model_dump(exclude_unset=True))
    return APIResponse.success(data=TeacherInfo(
        id=updated.id, school_id=updated.school_id, semester_id=updated.semester_id,
        user_id=updated.user_id, name=updated.name, employee_id=updated.employee_id,
        gender=updated.gender, phone=updated.phone, teaching_group=updated.teaching_group,
        specialization=updated.specialization,
        created_at=updated.created_at,
    ))


@router.delete("/teachers/{teacher_id}", response_model=APIResponse)
async def delete_teacher(
    teacher_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    service = TeacherService(db)
    teacher = await service.get_by_id(teacher_id)
    if not teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="教师不存在")
    if current_user.role != UserRole.SUPER_ADMIN and current_user.school_id != teacher.school_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    await check_semester_writable(db, teacher.semester_id)
    deleted = await service.delete(teacher_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="删除失败")
    return APIResponse.success(message="删除成功")


@router.get("/teacher-courses", response_model=APIResponse[PageResponse[TeacherCourseInfo]])
async def get_teacher_courses(
    teacher_id: str = Query(...),
    page: int = Query(1),
    page_size: int = Query(20),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    service = TeacherCourseService(db)
    teacher_courses = await service.get_teacher_courses(teacher_id)
    course_repo = CourseRepository(db)
    teacher_repo = TeacherRepository(db)
    items = []
    for tc in teacher_courses:
        course = await course_repo.get_by_id(tc.course_id)
        course_name = course.name if course else None
        t = await teacher_repo.get_by_id(tc.teacher_id)
        teacher_name = t.name if t else None
        items.append(TeacherCourseInfo(id=tc.id, teacher_id=tc.teacher_id, course_id=tc.course_id, course_name=course_name, teacher_name=teacher_name))
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    paged = items[start:end]
    return APIResponse.success(data=PageResponse(items=paged, total=total, page=page, page_size=page_size))


@router.post("/teacher-courses", response_model=APIResponse[TeacherCourseInfo])
async def add_teacher_course(
    request: TeacherCourseCreate,
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    sid = await resolve_semester_id(db, school_id, semester_id, check_archive=True)
    service = TeacherCourseService(db)
    tc = await service.add_course_to_teacher(school_id, sid, request.teacher_id, request.course_id)
    course_repo = CourseRepository(db)
    teacher_repo = TeacherRepository(db)
    course = await course_repo.get_by_id(tc.course_id)
    course_name = course.name if course else None
    t = await teacher_repo.get_by_id(tc.teacher_id)
    teacher_name = t.name if t else None
    return APIResponse.success(data=TeacherCourseInfo(id=tc.id, teacher_id=tc.teacher_id, course_id=tc.course_id, course_name=course_name, teacher_name=teacher_name))


@router.delete("/teacher-courses/{teacher_course_id}", response_model=APIResponse)
async def delete_teacher_course(
    teacher_course_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    service = TeacherCourseService(db)
    tc = await service.repo.get_by_id(teacher_course_id)
    if not tc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="教师课程记录不存在")
    await check_semester_writable(db, tc.semester_id)
    deleted = await service.remove_course_from_teacher(teacher_course_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="教师课程记录不存在")
    return APIResponse.success(message="删除成功")


@router.get("/teachers/{teacher_id}/courses", response_model=APIResponse)
async def get_teacher_courses_by_id(
    teacher_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    service = TeacherCourseService(db)
    teacher_courses = await service.get_teacher_courses(teacher_id)
    course_repo = CourseRepository(db)
    items = []
    for tc in teacher_courses:
        course = await course_repo.get_by_id(tc.course_id)
        course_name = course.name if course else None
        items.append({"id": tc.id, "teacher_id": tc.teacher_id, "course_id": tc.course_id, "course_name": course_name})
    return APIResponse.success(data=items)


@router.put("/teachers/{teacher_id}/courses", response_model=APIResponse)
async def set_teacher_courses(
    teacher_id: str,
    request: TeacherCourseBatchSet,
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    sid = await resolve_semester_id(db, school_id, semester_id, check_archive=True)
    service = TeacherCourseService(db)
    existing = await service.get_teacher_courses(teacher_id)
    existing_course_ids = {tc.course_id for tc in existing}
    new_course_ids = set(request.course_ids)
    for course_id in existing_course_ids - new_course_ids:
        for tc in existing:
            if tc.course_id == course_id:
                await service.remove_course_from_teacher(tc.id)
                break
    for course_id in new_course_ids - existing_course_ids:
        await service.add_course_to_teacher(school_id, sid, teacher_id, course_id)
    return APIResponse.success(message="设置成功")


@router.get("/classrooms", response_model=APIResponse[PageResponse[ClassroomInfo]])
async def get_classrooms(
    semester_id: Optional[str] = Query(None),
    building_name: Optional[str] = Query(None),
    room_type: Optional[str] = Query(None),
    page: int = Query(1),
    page_size: int = Query(20),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    sid = await resolve_semester_id(db, school_id, semester_id, raise_if_missing=False)
    if not sid:
        return APIResponse.success(data=PageResponse(items=[], total=0, page=page, page_size=page_size))
    service = ClassroomService(db)
    classrooms, total = await service.get_list(school_id, sid, page, page_size, building_name, room_type)
    items = [ClassroomInfo(
        id=c.id, school_id=c.school_id, semester_id=c.semester_id,
        building_name=c.building_name, room_number=c.room_number,
        code=c.code, room_type=c.room_type, capacity=c.capacity,
        created_at=c.created_at,
    ) for c in classrooms]
    return APIResponse.success(data=PageResponse(items=items, total=total, page=page, page_size=page_size))


@router.post("/classrooms", response_model=APIResponse[ClassroomInfo])
async def create_classroom(
    request: ClassroomCreate,
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    sid = await resolve_semester_id(db, school_id, semester_id, check_archive=True)
    service = ClassroomService(db)
    classroom = await service.create(school_id, sid, request.model_dump())
    return APIResponse.success(data=ClassroomInfo(
        id=classroom.id, school_id=classroom.school_id, semester_id=classroom.semester_id,
        building_name=classroom.building_name, room_number=classroom.room_number,
        code=classroom.code, room_type=classroom.room_type, capacity=classroom.capacity,
        created_at=classroom.created_at,
    ))


@router.put("/classrooms/{classroom_id}", response_model=APIResponse[ClassroomInfo])
async def update_classroom(
    classroom_id: str,
    request: ClassroomUpdate,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    service = ClassroomService(db)
    classroom = await service.get_by_id(classroom_id)
    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="教室不存在")
    if current_user.role != UserRole.SUPER_ADMIN and current_user.school_id != classroom.school_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    await check_semester_writable(db, classroom.semester_id)
    updated = await service.update(classroom_id, request.model_dump(exclude_unset=True))
    return APIResponse.success(data=ClassroomInfo(
        id=updated.id, school_id=updated.school_id, semester_id=updated.semester_id,
        building_name=updated.building_name, room_number=updated.room_number,
        code=updated.code, room_type=updated.room_type, capacity=updated.capacity,
        created_at=updated.created_at,
    ))


@router.delete("/classrooms/{classroom_id}", response_model=APIResponse)
async def delete_classroom(
    classroom_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    service = ClassroomService(db)
    classroom = await service.get_by_id(classroom_id)
    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="教室不存在")
    if current_user.role != UserRole.SUPER_ADMIN and current_user.school_id != classroom.school_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    await check_semester_writable(db, classroom.semester_id)
    deleted = await service.delete(classroom_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="教室不存在")
    return APIResponse.success(message="删除成功")


@router.get("/classroom-courses", response_model=APIResponse[PageResponse[ClassroomCourseInfo]])
async def get_classroom_courses(
    classroom_id: str = Query(...),
    page: int = Query(1),
    page_size: int = Query(20),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    service = ClassroomCourseService(db)
    classroom_courses = await service.get_classroom_courses(classroom_id)
    course_repo = CourseRepository(db)
    classroom_repo = ClassroomRepository(db)
    items = []
    for cc in classroom_courses:
        course = await course_repo.get_by_id(cc.course_id)
        course_name = course.name if course else None
        cr = await classroom_repo.get_by_id(cc.classroom_id)
        classroom_name = f"{cr.building_name} {cr.room_number}" if cr else None
        items.append(ClassroomCourseInfo(id=cc.id, classroom_id=cc.classroom_id, course_id=cc.course_id, course_name=course_name, classroom_name=classroom_name))
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    paged = items[start:end]
    return APIResponse.success(data=PageResponse(items=paged, total=total, page=page, page_size=page_size))


@router.post("/classroom-courses", response_model=APIResponse[ClassroomCourseInfo])
async def add_classroom_course(
    request: ClassroomCourseCreate,
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    sid = await resolve_semester_id(db, school_id, semester_id, check_archive=True)
    service = ClassroomCourseService(db)
    cc = await service.add_course_to_classroom(school_id, sid, request.classroom_id, request.course_id)
    course_repo = CourseRepository(db)
    classroom_repo = ClassroomRepository(db)
    course = await course_repo.get_by_id(cc.course_id)
    course_name = course.name if course else None
    cr = await classroom_repo.get_by_id(cc.classroom_id)
    classroom_name = f"{cr.building_name} {cr.room_number}" if cr else None
    return APIResponse.success(data=ClassroomCourseInfo(id=cc.id, classroom_id=cc.classroom_id, course_id=cc.course_id, course_name=course_name, classroom_name=classroom_name))


@router.delete("/classroom-courses/{classroom_course_id}", response_model=APIResponse)
async def delete_classroom_course(
    classroom_course_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    service = ClassroomCourseService(db)
    cc = await service.repo.get_by_id(classroom_course_id)
    if not cc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="教室课程记录不存在")
    await check_semester_writable(db, cc.semester_id)
    deleted = await service.remove_course_from_classroom(classroom_course_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="教室课程记录不存在")
    return APIResponse.success(message="删除成功")


@router.get("/classrooms/{classroom_id}/courses", response_model=APIResponse)
async def get_classroom_courses_by_id(
    classroom_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    service = ClassroomCourseService(db)
    classroom_courses = await service.get_classroom_courses(classroom_id)
    course_repo = CourseRepository(db)
    items = []
    for cc in classroom_courses:
        course = await course_repo.get_by_id(cc.course_id)
        course_name = course.name if course else None
        items.append({"id": cc.id, "classroom_id": cc.classroom_id, "course_id": cc.course_id, "course_name": course_name})
    return APIResponse.success(data=items)


@router.put("/classrooms/{classroom_id}/courses", response_model=APIResponse)
async def set_classroom_courses(
    classroom_id: str,
    request: ClassroomCourseBatchSet,
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    sid = await resolve_semester_id(db, school_id, semester_id, check_archive=True)
    service = ClassroomCourseService(db)
    existing = await service.get_classroom_courses(classroom_id)
    existing_course_ids = {cc.course_id for cc in existing}
    new_course_ids = set(request.course_ids)
    for course_id in existing_course_ids - new_course_ids:
        for cc in existing:
            if cc.course_id == course_id:
                await service.remove_course_from_classroom(cc.id)
                break
    for course_id in new_course_ids - existing_course_ids:
        await service.add_course_to_classroom(school_id, sid, classroom_id, course_id)
    return APIResponse.success(message="设置成功")


@router.get("/teaching-arrangements/summary", response_model=APIResponse[List[TeachingArrangementSummary]])
async def get_teaching_arrangement_summary(
    grade_id: Optional[str] = Query(None),
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    sid = await resolve_semester_id(db, school_id, semester_id, raise_if_missing=False)
    if not sid:
        return APIResponse.success(data=[])

    class_repo = ClassRepository(db)
    grade_repo = GradeRepository(db)
    grade_course_repo = GradeCourseRepository(db)
    course_repo = CourseRepository(db)
    arrangement_repo = TeachingArrangementRepository(db)
    teacher_repo = TeacherRepository(db)
    classroom_repo = ClassroomRepository(db)

    components: tuple[List[Class_], int]
    if grade_id:
        components = await class_repo.get_by_grade(grade_id, page=1, page_size=10000)
    else:
        components = await class_repo.get_by_semester(school_id, sid, page=1, page_size=10000)
    all_classes = components[0]

    results = []
    for cls in all_classes:
        if cls.is_teaching_class:
            continue
        grade = await grade_repo.get_by_id(cls.grade_id)
        grade_name = grade.name if grade else ""
        grade_courses = await grade_course_repo.get_by_grade(cls.grade_id)
        grade_course_infos = []
        for gc in grade_courses:
            course = await course_repo.get_by_id(gc.course_id)
            course_name = course.name if course else None
            course_code = course.code if course else None
            grade_course_infos.append(GradeCourseInfo(
                id=gc.id, grade_id=gc.grade_id, course_id=gc.course_id,
                course_name=course_name, course_code=course_code,
                weekly_hours=gc.weekly_hours, period_type=gc.period_type,
            ))

        arrangements = await arrangement_repo.get_by_class(cls.id)
        teacher_infos = []
        for a in arrangements:
            teacher = await teacher_repo.get_by_id(a.teacher_id)
            course = await course_repo.get_by_id(a.course_id)
            teacher_infos.append(TeachingArrangementInfo(
                id=a.id, teacher_id=a.teacher_id, course_id=a.course_id,
                class_id=a.class_id, weekly_hours=a.weekly_hours,
                continuous_hours=a.continuous_hours,
                teacher_name=teacher.name if teacher else None,
                course_name=course.name if course else None,
                class_name=cls.name, grade_name=grade_name,
            ))

        classroom_name = None
        if cls.classroom_id:
            cr = await classroom_repo.get_by_id(cls.classroom_id)
            if cr:
                classroom_name = f"{cr.building_name} {cr.room_number}"

        results.append(TeachingArrangementSummary(
            class_id=cls.id, class_name=cls.name,
            grade_id=cls.grade_id, grade_name=grade_name,
            classroom_name=classroom_name,
            total_courses=len(grade_course_infos),
            assigned_count=len(teacher_infos),
            courses=grade_course_infos,
            teacher_assignments=teacher_infos,
        ))

    return APIResponse.success(data=results)


@router.get("/teaching-arrangements", response_model=APIResponse[PageResponse[TeachingArrangementInfo]])
async def get_teaching_arrangements(
    semester_id: Optional[str] = Query(None),
    page: int = Query(1),
    page_size: int = Query(20),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    sid = await resolve_semester_id(db, school_id, semester_id, raise_if_missing=False)
    if not sid:
        return APIResponse.success(data=PageResponse(items=[], total=0, page=page, page_size=page_size))
    service = TeachingArrangementService(db)
    arrangements, total = await service.get_list(school_id, sid, page, page_size)
    teacher_repo = TeacherRepository(db)
    course_repo = CourseRepository(db)
    class_repo = ClassRepository(db)
    grade_repo = GradeRepository(db)
    items = []
    for a in arrangements:
        teacher = await teacher_repo.get_by_id(a.teacher_id)
        teacher_name = teacher.name if teacher else None
        course = await course_repo.get_by_id(a.course_id)
        course_name = course.name if course else None
        cls = await class_repo.get_by_id(a.class_id)
        class_name = cls.name if cls else None
        grade_name = None
        if cls and cls.grade_id:
            grade = await grade_repo.get_by_id(cls.grade_id)
            grade_name = grade.name if grade else None
        items.append(TeachingArrangementInfo(
            id=a.id, teacher_id=a.teacher_id, course_id=a.course_id,
            class_id=a.class_id, weekly_hours=a.weekly_hours, continuous_hours=a.continuous_hours,
            teacher_name=teacher_name, course_name=course_name, class_name=class_name, grade_name=grade_name,
        ))
    return APIResponse.success(data=PageResponse(items=items, total=total, page=page, page_size=page_size))


@router.post("/teaching-arrangements", response_model=APIResponse[TeachingArrangementInfo])
async def create_teaching_arrangement(
    request: TeachingArrangementCreate,
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    sid = await resolve_semester_id(db, school_id, semester_id, check_archive=True)
    service = TeachingArrangementService(db)
    arrangement = await service.create(school_id, sid, request.model_dump())
    teacher_repo = TeacherRepository(db)
    course_repo = CourseRepository(db)
    class_repo = ClassRepository(db)
    grade_repo = GradeRepository(db)
    teacher = await teacher_repo.get_by_id(arrangement.teacher_id)
    teacher_name = teacher.name if teacher else None
    course = await course_repo.get_by_id(arrangement.course_id)
    course_name = course.name if course else None
    cls = await class_repo.get_by_id(arrangement.class_id)
    class_name = cls.name if cls else None
    grade_name = None
    if cls and cls.grade_id:
        grade = await grade_repo.get_by_id(cls.grade_id)
        grade_name = grade.name if grade else None
    return APIResponse.success(data=TeachingArrangementInfo(
        id=arrangement.id, teacher_id=arrangement.teacher_id, course_id=arrangement.course_id,
        class_id=arrangement.class_id, weekly_hours=arrangement.weekly_hours, continuous_hours=arrangement.continuous_hours,
        teacher_name=teacher_name, course_name=course_name, class_name=class_name, grade_name=grade_name,
    ))


@router.put("/teaching-arrangements/{arrangement_id}", response_model=APIResponse[TeachingArrangementInfo])
async def update_teaching_arrangement(
    arrangement_id: str,
    request: TeachingArrangementUpdate,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    service = TeachingArrangementService(db)
    arrangement = await service.get_by_id(arrangement_id)
    if not arrangement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="教学安排不存在")
    if current_user.role != UserRole.SUPER_ADMIN and current_user.school_id != arrangement.school_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    await check_semester_writable(db, arrangement.semester_id)
    updated = await service.update(arrangement_id, request.model_dump(exclude_unset=True))
    teacher_repo = TeacherRepository(db)
    course_repo = CourseRepository(db)
    class_repo = ClassRepository(db)
    grade_repo = GradeRepository(db)
    teacher = await teacher_repo.get_by_id(updated.teacher_id)
    teacher_name = teacher.name if teacher else None
    course = await course_repo.get_by_id(updated.course_id)
    course_name = course.name if course else None
    cls = await class_repo.get_by_id(updated.class_id)
    class_name = cls.name if cls else None
    grade_name = None
    if cls and cls.grade_id:
        grade = await grade_repo.get_by_id(cls.grade_id)
        grade_name = grade.name if grade else None
    return APIResponse.success(data=TeachingArrangementInfo(
        id=updated.id, teacher_id=updated.teacher_id, course_id=updated.course_id,
        class_id=updated.class_id, weekly_hours=updated.weekly_hours, continuous_hours=updated.continuous_hours,
        teacher_name=teacher_name, course_name=course_name, class_name=class_name, grade_name=grade_name,
    ))


@router.delete("/teaching-arrangements/{arrangement_id}", response_model=APIResponse)
async def delete_teaching_arrangement(
    arrangement_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    service = TeachingArrangementService(db)
    arrangement = await service.get_by_id(arrangement_id)
    if not arrangement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="教学安排不存在")
    if current_user.role != UserRole.SUPER_ADMIN and current_user.school_id != arrangement.school_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    await check_semester_writable(db, arrangement.semester_id)
    deleted = await service.delete(arrangement_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="教学安排不存在")
    return APIResponse.success(message="删除成功")


@router.get("/excel/template/{data_type}")
async def get_excel_template(
    data_type: str,
    current_user: User = Depends(get_current_user_dependency),
):
    try:
        content = await download_template(data_type)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return StreamingResponse(
        BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=template_{data_type}.xlsx"},
    )


@router.post("/excel/import/{data_type}", response_model=APIResponse)
async def import_excel_data(
    data_type: str,
    file: UploadFile = File(...),
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    sid = await resolve_semester_id(db, school_id, semester_id, check_archive=True)
    try:
        result = await import_data(data_type, file, school_id, sid, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return APIResponse.success(data=result)


@router.get("/excel/export/{data_type}")
async def export_excel_data(
    data_type: str,
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    sid = await resolve_semester_id(db, school_id, semester_id)
    try:
        content = await export_data(data_type, school_id, sid, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return StreamingResponse(
        BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={data_type}.xlsx"},
    )


@router.post("/quick-setup", response_model=APIResponse[QuickSetupResult])
async def quick_setup(
    request: QuickSetupRequest,
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    sid = await resolve_semester_id(db, school_id, semester_id, check_archive=True)
    service = QuickSetupService(db)
    result = await service.quick_setup(school_id, sid, request.model_dump())
    return APIResponse.success(data=QuickSetupResult(**result))


@router.post("/teaching-arrangements/batch", response_model=APIResponse)
async def batch_create_teaching_arrangements(
    request: BatchTeachingArrangementCreate,
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    sid = await resolve_semester_id(db, school_id, semester_id, check_archive=True)
    service = QuickSetupService(db)
    results = await service.batch_create_arrangements(school_id, sid, [a.model_dump() for a in request.arrangements])
    return APIResponse.success(data={"count": len(results)})


@router.get("/my-teaching-info", response_model=APIResponse)
async def get_my_teaching_info(
    semester_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != UserRole.TEACHER:
        return APIResponse.success(data={"teacher_id": None, "class_ids": [], "grade_ids": [], "classroom_ids": []})

    teacher_repo = TeacherRepository(db)
    result = await db.execute(
        select(Teacher).where(Teacher.user_id == current_user.id)
    )
    teacher = result.scalar_one_or_none()
    if not teacher:
        return APIResponse.success(data={"teacher_id": None, "class_ids": [], "grade_ids": [], "classroom_ids": []})

    school_id = current_user.school_id
    if not school_id:
        return APIResponse.success(data={"teacher_id": None, "class_ids": [], "grade_ids": [], "classroom_ids": []})

    sid = await resolve_semester_id(db, school_id, semester_id, raise_if_missing=False)
    if not sid:
        return APIResponse.success(data={"teacher_id": teacher.id, "class_ids": [], "grade_ids": [], "classroom_ids": []})

    arr_repo = TeachingArrangementRepository(db)
    arrangements = await arr_repo.get_by_teacher_and_semester(teacher.id, sid)

    class_ids = list(set(a.class_id for a in arrangements if a.class_id))

    grade_ids = []
    classroom_ids = []
    if class_ids:
        class_repo = ClassRepository(db)
        for cid in class_ids:
            cls = await class_repo.get_by_id(cid)
            if cls and cls.grade_id and cls.grade_id not in grade_ids:
                grade_ids.append(cls.grade_id)
            if cls and cls.classroom_id and cls.classroom_id not in classroom_ids:
                classroom_ids.append(cls.classroom_id)

    schedule_cell_result = await db.execute(
        select(ScheduleCell).where(
            ScheduleCell.teacher_id == teacher.id,
            ScheduleCell.semester_id == sid,
        )
    )
    schedule_cells = list(schedule_cell_result.scalars().all())
    for cell in schedule_cells:
        if cell.classroom_id and cell.classroom_id not in classroom_ids:
            classroom_ids.append(cell.classroom_id)

    head_teacher_class_result = await db.execute(
        select(Class_).where(
            Class_.head_teacher_id == teacher.id,
            Class_.semester_id == sid,
        )
    )
    head_teacher_classes = list(head_teacher_class_result.scalars().all())
    head_teacher_class_ids = [c.id for c in head_teacher_classes]

    grade_leader_result = await db.execute(
        select(Grade).where(
            Grade.grade_leader_id == teacher.id,
            Grade.semester_id == sid,
        )
    )
    grade_leader_grades = list(grade_leader_result.scalars().all())
    grade_leader_grade_ids = [g.id for g in grade_leader_grades]

    return APIResponse.success(data={
        "teacher_id": teacher.id,
        "class_ids": class_ids,
        "grade_ids": grade_ids,
        "classroom_ids": classroom_ids,
        "head_teacher_class_ids": head_teacher_class_ids,
        "grade_leader_grade_ids": grade_leader_grade_ids,
    })
