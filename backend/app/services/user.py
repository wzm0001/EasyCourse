import json
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import School, User, ApprovalRecord, UserRole, AccountStatus
from app.repositories.user import UserRepository, SchoolRepository, ApprovalRepository
from app.services.auth import get_password_hash, verify_password


async def register_school(school_data: dict, db: AsyncSession) -> School:
    school_repo = SchoolRepository(db)
    school = School(
        name=school_data["name"],
        code=school_data["code"],
        address=school_data.get("address", ""),
        contact_person=school_data.get("contact_person", ""),
        contact_phone=school_data.get("contact_phone", ""),
        status=AccountStatus.PENDING,
        attachment=school_data.get("attachment", ""),
    )
    school = await school_repo.create(school)
    return school


async def approve_school(school_id: str, reviewer_id: str, db: AsyncSession) -> Optional[School]:
    school_repo = SchoolRepository(db)
    school = await school_repo.get_by_id(school_id)
    if school is None:
        return None
    await school_repo.update(school_id, {"status": AccountStatus.ACTIVE, "reject_reason": ""})
    user_repo = UserRepository(db)
    users, _ = await user_repo.get_by_school(school_id)
    for user in users:
        if user.role == UserRole.SCHOOL_ADMIN:
            await user_repo.update(user.id, {"is_active": True})
    return await school_repo.get_by_id(school_id)


async def reject_school(school_id: str, reviewer_id: str, reject_reason: str, db: AsyncSession) -> Optional[School]:
    school_repo = SchoolRepository(db)
    school = await school_repo.get_by_id(school_id)
    if school is None:
        return None
    await school_repo.update(school_id, {"status": AccountStatus.REJECTED, "reject_reason": reject_reason})
    return await school_repo.get_by_id(school_id)


async def create_teacher(teacher_data: dict, school_id: str, db: AsyncSession) -> User:
    user_repo = UserRepository(db)
    user = User(
        username=teacher_data["username"],
        password_hash=get_password_hash(teacher_data["password"]),
        real_name=teacher_data.get("real_name", ""),
        role=UserRole.TEACHER,
        school_id=school_id,
        phone=teacher_data.get("phone", ""),
        email=teacher_data.get("email", ""),
        is_active=True,
    )
    user = await user_repo.create(user)
    return user


async def update_user_profile(user_id: str, data: dict, db: AsyncSession) -> Optional[User]:
    user_repo = UserRepository(db)
    update_data = {}
    for key in ["real_name", "phone", "email"]:
        if key in data and data[key] is not None:
            update_data[key] = data[key]
    if "password" in data and data["password"] is not None:
        update_data["password_hash"] = get_password_hash(data["password"])
    if not update_data:
        return await user_repo.get_by_id(user_id)
    return await user_repo.update(user_id, update_data)


async def change_password(user_id: str, old_password: str, new_password: str, db: AsyncSession) -> bool:
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if user is None:
        return False
    if not verify_password(old_password, user.password_hash):
        return False
    await user_repo.update(user_id, {"password_hash": get_password_hash(new_password)})
    return True


async def request_data_change(school_id: str, change_data: dict, requester_id: str, db: AsyncSession) -> ApprovalRecord:
    approval_repo = ApprovalRepository(db)
    record = ApprovalRecord(
        type="school_data_change",
        requester_id=requester_id,
        school_id=school_id,
        status="pending",
        request_data=json.dumps(change_data, ensure_ascii=False),
    )
    record = await approval_repo.create(record)
    return record


async def approve_data_change(approval_id: str, reviewer_id: str, db: AsyncSession) -> Optional[ApprovalRecord]:
    approval_repo = ApprovalRepository(db)
    record = await approval_repo.get_by_id(approval_id)
    if record is None:
        return None
    change_data = json.loads(record.request_data) if record.request_data else {}
    school_repo = SchoolRepository(db)
    await school_repo.update(record.school_id, change_data)
    await approval_repo.update(approval_id, {"status": "approved", "reviewer_id": reviewer_id})
    return await approval_repo.get_by_id(approval_id)


async def reject_data_change(approval_id: str, reviewer_id: str, reject_reason: str, db: AsyncSession) -> Optional[ApprovalRecord]:
    approval_repo = ApprovalRepository(db)
    record = await approval_repo.get_by_id(approval_id)
    if record is None:
        return None
    await approval_repo.update(approval_id, {"status": "rejected", "reviewer_id": reviewer_id, "reject_reason": reject_reason})
    return await approval_repo.get_by_id(approval_id)
