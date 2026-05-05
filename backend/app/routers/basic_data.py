from io import BytesIO
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.common import APIResponse, PageResponse
from app.schemas.basic_data import (
    GradeCreate, GradeUpdate, GradeInfo,
    ClassCreate, ClassUpdate, ClassInfo,
    CourseCreate, CourseUpdate, CourseInfo,
    GradeCourseCreate, GradeCourseInfo,
    TeacherCreate, TeacherUpdate, TeacherInfo,
    TeacherCourseCreate, TeacherCourseInfo,
    ClassroomCreate, ClassroomUpdate, ClassroomInfo,
    ClassroomCourseCreate, ClassroomCourseInfo,
    TeachingArrangementCreate, TeachingArrangementUpdate, TeachingArrangementInfo,
)
from app.services.basic_data import (
    GradeService, ClassService, CourseService, GradeCourseService,
    TeacherService, TeacherCourseService, ClassroomService,
    ClassroomCourseService, TeachingArrangementService,
)
from app.services.excel_import_export import download_template, import_data, export_data
from app.middleware.auth import get_current_user_dependency
from app.repositories.semester import SemesterRepository
from app.repositories.basic_data import (
    GradeRepository, ClassRepository, CourseRepository,
    TeacherRepository, ClassroomRepository, TeachingArrangementRepository,
)

router = APIRouter(prefix="/basic-data", tags=["基础数据管理"])


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
    sid = await resolve_semester_id(db, school_id, semester_id)
    service = GradeService(db)
    grades, total = await service.get_list(school_id, sid, page, page_size)
    items = [GradeInfo(id=g.id, school_id=g.school_id, semester_id=g.semester_id, name=g.name, sort_order=g.sort_order, created_at=g.created_at) for g in grades]
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
    sid = await resolve_semester_id(db, school_id, semester_id)
    service = GradeService(db)
    grade = await service.create(school_id, sid, request.model_dump())
    return APIResponse.success(data=GradeInfo(id=grade.id, school_id=grade.school_id, semester_id=grade.semester_id, name=grade.name, sort_order=grade.sort_order, created_at=grade.created_at))


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
    updated = await service.update(grade_id, request.model_dump(exclude_unset=True))
    return APIResponse.success(data=GradeInfo(id=updated.id, school_id=updated.school_id, semester_id=updated.semester_id, name=updated.name, sort_order=updated.sort_order, created_at=updated.created_at))


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
    deleted = await service.delete(grade_id)
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
    sid = await resolve_semester_id(db, school_id, semester_id)
    service = ClassService(db)
    classes, total = await service.get_list(school_id, sid, grade_id, page, page_size)
    items = []
    for c in classes:
        teacher_name = None
        if c.teacher_id:
            from app.repositories.user import UserRepository
            user_repo = UserRepository(db)
            teacher_user = await user_repo.get_by_id(c.teacher_id)
            if teacher_user:
                teacher_name = teacher_user.real_name
        items.append(ClassInfo(
            id=c.id, school_id=c.school_id, semester_id=c.semester_id,
            grade_id=c.grade_id, name=c.name, teacher_id=c.teacher_id,
            teacher_name=teacher_name, is_teaching_class=c.is_teaching_class,
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
    sid = await resolve_semester_id(db, school_id, semester_id)
    service = ClassService(db)
    cls = await service.create(school_id, sid, request.model_dump())
    teacher_name = None
    if cls.teacher_id:
        from app.repositories.user import UserRepository
        user_repo = UserRepository(db)
        teacher_user = await user_repo.get_by_id(cls.teacher_id)
        if teacher_user:
            teacher_name = teacher_user.real_name
    return APIResponse.success(data=ClassInfo(
        id=cls.id, school_id=cls.school_id, semester_id=cls.semester_id,
        grade_id=cls.grade_id, name=cls.name, teacher_id=cls.teacher_id,
        teacher_name=teacher_name, is_teaching_class=cls.is_teaching_class,
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
    updated = await service.update(class_id, request.model_dump(exclude_unset=True))
    teacher_name = None
    if updated.teacher_id:
        from app.repositories.user import UserRepository
        user_repo = UserRepository(db)
        teacher_user = await user_repo.get_by_id(updated.teacher_id)
        if teacher_user:
            teacher_name = teacher_user.real_name
    return APIResponse.success(data=ClassInfo(
        id=updated.id, school_id=updated.school_id, semester_id=updated.semester_id,
        grade_id=updated.grade_id, name=updated.name, teacher_id=updated.teacher_id,
        teacher_name=teacher_name, is_teaching_class=updated.is_teaching_class,
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
    page: int = Query(1),
    page_size: int = Query(20),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    service = GradeCourseService(db)
    grade_courses = await service.get_grade_courses(grade_id)
    course_repo = CourseRepository(db)
    items = []
    for gc in grade_courses:
        course = await course_repo.get_by_id(gc.course_id)
        course_name = course.name if course else None
        items.append(GradeCourseInfo(id=gc.id, grade_id=gc.grade_id, course_id=gc.course_id, course_name=course_name))
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
    sid = await resolve_semester_id(db, school_id, semester_id)
    service = GradeCourseService(db)
    gc = await service.add_course_to_grade(school_id, sid, request.grade_id, request.course_id)
    course_repo = CourseRepository(db)
    course = await course_repo.get_by_id(gc.course_id)
    course_name = course.name if course else None
    return APIResponse.success(data=GradeCourseInfo(id=gc.id, grade_id=gc.grade_id, course_id=gc.course_id, course_name=course_name))


@router.delete("/grade-courses/{grade_course_id}", response_model=APIResponse)
async def delete_grade_course(
    grade_course_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    service = GradeCourseService(db)
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
    sid = await resolve_semester_id(db, school_id, semester_id)
    service = TeacherService(db)
    teachers, total = await service.get_list(school_id, sid, page, page_size)
    items = [TeacherInfo(
        id=t.id, school_id=t.school_id, semester_id=t.semester_id,
        user_id=t.user_id, name=t.name, employee_id=t.employee_id,
        gender=t.gender, phone=t.phone, teaching_group=t.teaching_group,
        created_at=t.created_at,
    ) for t in teachers]
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
    sid = await resolve_semester_id(db, school_id, semester_id)
    service = TeacherService(db)
    teacher = await service.create(school_id, sid, request.model_dump())
    return APIResponse.success(data=TeacherInfo(
        id=teacher.id, school_id=teacher.school_id, semester_id=teacher.semester_id,
        user_id=teacher.user_id, name=teacher.name, employee_id=teacher.employee_id,
        gender=teacher.gender, phone=teacher.phone, teaching_group=teacher.teaching_group,
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
    updated = await service.update(teacher_id, request.model_dump(exclude_unset=True))
    return APIResponse.success(data=TeacherInfo(
        id=updated.id, school_id=updated.school_id, semester_id=updated.semester_id,
        user_id=updated.user_id, name=updated.name, employee_id=updated.employee_id,
        gender=updated.gender, phone=updated.phone, teaching_group=updated.teaching_group,
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
    deleted = await service.delete(teacher_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="教师存在关联教学安排，无法删除")
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
    sid = await resolve_semester_id(db, school_id, semester_id)
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
    deleted = await service.remove_course_from_teacher(teacher_course_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="教师课程记录不存在")
    return APIResponse.success(message="删除成功")


@router.get("/classrooms", response_model=APIResponse[PageResponse[ClassroomInfo]])
async def get_classrooms(
    semester_id: Optional[str] = Query(None),
    page: int = Query(1),
    page_size: int = Query(20),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    school_id = await get_school_id(current_user) if current_user.role != UserRole.SUPER_ADMIN else current_user.school_id
    if not school_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前用户未关联学校")
    sid = await resolve_semester_id(db, school_id, semester_id)
    service = ClassroomService(db)
    classrooms, total = await service.get_list(school_id, sid, page, page_size)
    items = [ClassroomInfo(
        id=c.id, school_id=c.school_id, semester_id=c.semester_id,
        name=c.name, room_type=c.room_type, capacity=c.capacity,
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
    sid = await resolve_semester_id(db, school_id, semester_id)
    service = ClassroomService(db)
    classroom = await service.create(school_id, sid, request.model_dump())
    return APIResponse.success(data=ClassroomInfo(
        id=classroom.id, school_id=classroom.school_id, semester_id=classroom.semester_id,
        name=classroom.name, room_type=classroom.room_type, capacity=classroom.capacity,
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
    updated = await service.update(classroom_id, request.model_dump(exclude_unset=True))
    return APIResponse.success(data=ClassroomInfo(
        id=updated.id, school_id=updated.school_id, semester_id=updated.semester_id,
        name=updated.name, room_type=updated.room_type, capacity=updated.capacity,
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
        classroom_name = cr.name if cr else None
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
    sid = await resolve_semester_id(db, school_id, semester_id)
    service = ClassroomCourseService(db)
    cc = await service.add_course_to_classroom(school_id, sid, request.classroom_id, request.course_id)
    course_repo = CourseRepository(db)
    classroom_repo = ClassroomRepository(db)
    course = await course_repo.get_by_id(cc.course_id)
    course_name = course.name if course else None
    cr = await classroom_repo.get_by_id(cc.classroom_id)
    classroom_name = cr.name if cr else None
    return APIResponse.success(data=ClassroomCourseInfo(id=cc.id, classroom_id=cc.classroom_id, course_id=cc.course_id, course_name=course_name, classroom_name=classroom_name))


@router.delete("/classroom-courses/{classroom_course_id}", response_model=APIResponse)
async def delete_classroom_course(
    classroom_course_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    service = ClassroomCourseService(db)
    deleted = await service.remove_course_from_classroom(classroom_course_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="教室课程记录不存在")
    return APIResponse.success(message="删除成功")


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
    sid = await resolve_semester_id(db, school_id, semester_id)
    service = TeachingArrangementService(db)
    arrangements, total = await service.get_list(school_id, sid, page, page_size)
    teacher_repo = TeacherRepository(db)
    course_repo = CourseRepository(db)
    class_repo = ClassRepository(db)
    items = []
    for a in arrangements:
        teacher = await teacher_repo.get_by_id(a.teacher_id)
        teacher_name = teacher.name if teacher else None
        course = await course_repo.get_by_id(a.course_id)
        course_name = course.name if course else None
        cls = await class_repo.get_by_id(a.class_id)
        class_name = cls.name if cls else None
        items.append(TeachingArrangementInfo(
            id=a.id, teacher_id=a.teacher_id, course_id=a.course_id,
            class_id=a.class_id, weekly_hours=a.weekly_hours,
            teacher_name=teacher_name, course_name=course_name, class_name=class_name,
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
    sid = await resolve_semester_id(db, school_id, semester_id)
    service = TeachingArrangementService(db)
    arrangement = await service.create(school_id, sid, request.model_dump())
    teacher_repo = TeacherRepository(db)
    course_repo = CourseRepository(db)
    class_repo = ClassRepository(db)
    teacher = await teacher_repo.get_by_id(arrangement.teacher_id)
    teacher_name = teacher.name if teacher else None
    course = await course_repo.get_by_id(arrangement.course_id)
    course_name = course.name if course else None
    cls = await class_repo.get_by_id(arrangement.class_id)
    class_name = cls.name if cls else None
    return APIResponse.success(data=TeachingArrangementInfo(
        id=arrangement.id, teacher_id=arrangement.teacher_id, course_id=arrangement.course_id,
        class_id=arrangement.class_id, weekly_hours=arrangement.weekly_hours,
        teacher_name=teacher_name, course_name=course_name, class_name=class_name,
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
    updated = await service.update(arrangement_id, request.model_dump(exclude_unset=True))
    teacher_repo = TeacherRepository(db)
    course_repo = CourseRepository(db)
    class_repo = ClassRepository(db)
    teacher = await teacher_repo.get_by_id(updated.teacher_id)
    teacher_name = teacher.name if teacher else None
    course = await course_repo.get_by_id(updated.course_id)
    course_name = course.name if course else None
    cls = await class_repo.get_by_id(updated.class_id)
    class_name = cls.name if cls else None
    return APIResponse.success(data=TeachingArrangementInfo(
        id=updated.id, teacher_id=updated.teacher_id, course_id=updated.course_id,
        class_id=updated.class_id, weekly_hours=updated.weekly_hours,
        teacher_name=teacher_name, course_name=course_name, class_name=class_name,
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
    sid = await resolve_semester_id(db, school_id, semester_id)
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
