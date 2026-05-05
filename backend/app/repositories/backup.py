from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.backup import BackupRecord
from app.repositories.base import BaseRepository


class BackupRecordRepository(BaseRepository[BackupRecord]):
    def __init__(self, session: AsyncSession):
        super().__init__(BackupRecord, session)

    async def get_all_ordered(self, page: int = 1, page_size: int = 20) -> tuple[List[BackupRecord], int]:
        from sqlalchemy import func
        count_result = await self.session.execute(
            select(func.count()).select_from(BackupRecord)
        )
        total = count_result.scalar_one()
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(BackupRecord).order_by(BackupRecord.created_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total
