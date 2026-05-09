from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.teaching_class import TeachingClass, TeachingClassMember
from app.repositories.teaching_class import TeachingClassRepository, TeachingClassMemberRepository
from app.repositories.basic_data import CourseRepository, TeacherRepository, ClassroomRepository, ClassRepository
from app.schemas.teaching_class import (
    TeachingClassCreate, TeachingClassUpdate, TeachingClassInfo, TeachingClassMemberInfo,
)
from app.schemas.common import PageResponse


async def _build_teaching_class_info(tc: TeachingClass, db: AsyncSession) -> TeachingClassInfo:
    course_repo = CourseRepository(db)
    teacher_repo = TeacherRepository(db)
    classroom_repo = ClassroomRepository(db)
    class_repo = ClassRepository(db)
    member_repo = TeachingClassMemberRepository(db)

    course = await course_repo.get_by_id(tc.course_id)
    teacher = await teacher_repo.get_by_id(tc.teacher_id)
    classroom = await classroom_repo.get_by_id(tc.classroom_id) if tc.classroom_id else None

    members = await member_repo.get_by_teaching_class(tc.id)
    member_infos = []
    for m in members:
        cls = await class_repo.get_by_id(m.class_id)
        member_infos.append(TeachingClassMemberInfo(
            id=m.id,
            teaching_class_id=m.teaching_class_id,
            class_id=m.class_id,
            class_name=cls.name if cls else None,
        ))

    return TeachingClassInfo(
        id=tc.id,
        school_id=tc.school_id,
        semester_id=tc.semester_id,
        grade_id=tc.grade_id,
        name=tc.name,
        course_id=tc.course_id,
        course_name=course.name if course else None,
        teacher_id=tc.teacher_id,
        teacher_name=teacher.name if teacher else None,
        classroom_id=tc.classroom_id,
        classroom_name=f"{classroom.building_name} {classroom.room_number}" if classroom else None,
        description=tc.description,
        members=member_infos,
        created_at=tc.created_at,
    )


async def create_teaching_class(data: TeachingClassCreate, school_id: str, semester_id: str, db: AsyncSession) -> TeachingClassInfo:
    tc_repo = TeachingClassRepository(db)
    member_repo = TeachingClassMemberRepository(db)

    tc = TeachingClass(
        school_id=school_id,
        semester_id=semester_id,
        grade_id=data.grade_id,
        name=data.name,
        course_id=data.course_id,
        teacher_id=data.teacher_id,
        classroom_id=data.classroom_id,
        description=data.description or "",
    )
    tc = await tc_repo.create(tc)

    for class_id in data.member_class_ids:
        member = TeachingClassMember(
            teaching_class_id=tc.id,
            class_id=class_id,
        )
        await member_repo.create(member)

    return await _build_teaching_class_info(tc, db)


async def update_teaching_class(id: str, data: TeachingClassUpdate, db: AsyncSession) -> Optional[TeachingClassInfo]:
    tc_repo = TeachingClassRepository(db)
    member_repo = TeachingClassMemberRepository(db)

    tc = await tc_repo.get_by_id(id)
    if not tc:
        return None

    update_data = {}
    if data.name is not None:
        update_data["name"] = data.name
    if data.teacher_id is not None:
        update_data["teacher_id"] = data.teacher_id
    if data.classroom_id is not None:
        update_data["classroom_id"] = data.classroom_id
    if data.description is not None:
        update_data["description"] = data.description

    if update_data:
        tc = await tc_repo.update(id, update_data)

    if data.member_class_ids is not None:
        await member_repo.delete_by_teaching_class(id)
        for class_id in data.member_class_ids:
            member = TeachingClassMember(
                teaching_class_id=id,
                class_id=class_id,
            )
            await member_repo.create(member)

    tc = await tc_repo.get_by_id(id)
    return await _build_teaching_class_info(tc, db)


async def delete_teaching_class(id: str, db: AsyncSession) -> bool:
    tc_repo = TeachingClassRepository(db)
    member_repo = TeachingClassMemberRepository(db)

    tc = await tc_repo.get_by_id(id)
    if not tc:
        return False

    await member_repo.delete_by_teaching_class(id)
    return await tc_repo.delete(id)


async def get_teaching_classes(
    school_id: str, semester_id: str, grade_id: Optional[str],
    page: int, page_size: int, db: AsyncSession,
) -> PageResponse[TeachingClassInfo]:
    tc_repo = TeachingClassRepository(db)

    if grade_id:
        items, total = await tc_repo.get_by_grade(grade_id, semester_id, page, page_size)
    else:
        items, total = await tc_repo.get_by_semester(school_id, semester_id, page, page_size)

    infos = []
    for tc in items:
        info = await _build_teaching_class_info(tc, db)
        infos.append(info)

    return PageResponse(items=infos, total=total, page=page, page_size=page_size)


async def get_teaching_class(id: str, db: AsyncSession) -> Optional[TeachingClassInfo]:
    tc_repo = TeachingClassRepository(db)
    tc = await tc_repo.get_by_id(id)
    if not tc:
        return None
    return await _build_teaching_class_info(tc, db)


async def get_class_teaching_classes(class_id: str, semester_id: str, db: AsyncSession) -> List[TeachingClassInfo]:
    member_repo = TeachingClassMemberRepository(db)
    tc_repo = TeachingClassRepository(db)

    members = await member_repo.get_by_class(class_id)
    infos = []
    seen = set()
    for m in members:
        if m.teaching_class_id in seen:
            continue
        seen.add(m.teaching_class_id)
        tc = await tc_repo.get_by_id(m.teaching_class_id)
        if tc and tc.semester_id == semester_id:
            info = await _build_teaching_class_info(tc, db)
            infos.append(info)
    return infos
