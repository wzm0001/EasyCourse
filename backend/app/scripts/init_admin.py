"""
初始化超级管理员账号
运行方式: python -m app.scripts.init_admin
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal, init_db
from app.models.user import User, UserRole
from app.repositories.user import UserRepository
from app.services.auth import get_password_hash


async def create_super_admin(
    username: str = "admin",
    password: str = "Admin@123",
    real_name: str = "超级管理员",
):
    async with AsyncSessionLocal() as db:
        user_repo = UserRepository(db)
        existing = await user_repo.get_by_username(username)
        if existing:
            print(f"用户 '{username}' 已存在，跳过创建")
            return existing

        admin = User(
            username=username,
            password_hash=get_password_hash(password),
            real_name=real_name,
            role=UserRole.SUPER_ADMIN,
            is_active=True,
        )
        admin = await user_repo.create(admin)
        await db.commit()
        print(f"超级管理员创建成功！")
        print(f"  用户名: {username}")
        print(f"  密码: {password}")
        return admin


async def main():
    print("=" * 40)
    print("初始化超级管理员账号")
    print("=" * 40)
    await init_db()
    await create_super_admin()
    print("=" * 40)
    print("完成！请使用上述账号登录系统。")


if __name__ == "__main__":
    asyncio.run(main())
