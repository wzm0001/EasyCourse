from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, School, ApprovalRecord
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_school(self, school_id: str, page: int = 1, page_size: int = 20, role: Optional[str] = None) -> tuple[List[User], int]:
        from sqlalchemy import func
        from app.models.user import UserRole
        conditions = [User.school_id == school_id]
        if role:
            conditions.append(User.role == role)
        count_result = await self.session.execute(
            select(func.count()).select_from(User).where(*conditions)
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(User).where(*conditions).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total

    async def get_admin_users(self, page: int = 1, page_size: int = 20) -> tuple[List[User], int]:
        from sqlalchemy import func
        from app.models.user import UserRole
        count_result = await self.session.execute(
            select(func.count()).select_from(User).where(
                User.role == UserRole.SUPER_ADMIN,
            )
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(User).where(
                User.role == UserRole.SUPER_ADMIN,
            ).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total


class SchoolRepository(BaseRepository[School]):
    def __init__(self, session: AsyncSession):
        super().__init__(School, session)

    async def get_by_code(self, code: str) -> Optional[School]:
        result = await self.session.execute(
            select(School).where(School.code == code)
        )
        return result.scalar_one_or_none()


class ApprovalRepository(BaseRepository[ApprovalRecord]):
    def __init__(self, session: AsyncSession):
        super().__init__(ApprovalRecord, session)

    async def get_pending(self, page: int = 1, page_size: int = 20) -> tuple[List[ApprovalRecord], int]:
        from sqlalchemy import func
        count_result = await self.session.execute(
            select(func.count()).select_from(ApprovalRecord).where(ApprovalRecord.status == "pending")
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(ApprovalRecord).where(ApprovalRecord.status == "pending").offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total

    async def get_by_school(self, school_id: str, page: int = 1, page_size: int = 20) -> tuple[List[ApprovalRecord], int]:
        from sqlalchemy import func
        count_result = await self.session.execute(
            select(func.count()).select_from(ApprovalRecord).where(ApprovalRecord.school_id == school_id)
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(ApprovalRecord).where(ApprovalRecord.school_id == school_id).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total
