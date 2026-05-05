from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.settings import SystemSetting
from app.repositories.base import BaseRepository


class SystemSettingRepository(BaseRepository[SystemSetting]):
    def __init__(self, session: AsyncSession):
        super().__init__(SystemSetting, session)

    async def get_by_key(self, key: str) -> Optional[SystemSetting]:
        result = await self.session.execute(
            select(SystemSetting).where(SystemSetting.key == key)
        )
        return result.scalar_one_or_none()

    async def get_public_settings(self) -> List[SystemSetting]:
        result = await self.session.execute(
            select(SystemSetting).where(SystemSetting.is_public == True)
        )
        return list(result.scalars().all())

    async def upsert(self, key: str, value: str, description: str = "", is_public: bool = False) -> SystemSetting:
        existing = await self.get_by_key(key)
        if existing:
            existing.value = value
            if description:
                existing.description = description
            existing.is_public = is_public
            await self.session.flush()
            return existing
        setting = SystemSetting(
            key=key,
            value=value,
            description=description,
            is_public=is_public,
        )
        self.session.add(setting)
        await self.session.flush()
        return setting
