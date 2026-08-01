from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.db.models.user import User


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email.lower()))
        return result.scalar_one_or_none()

    async def create_user(
        self,
        *,
        email: str,
        password: str,
        name: str,
        phone_number: str | None = None,
        teacher_voice: str = "female",
    ) -> User:
        user = User(
            name=name,
            email=email.lower(),
            phone_number=phone_number,
            hashed_password=hash_password(password),
            role="student",
            teacher_voice=teacher_voice,
            is_active=True,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
