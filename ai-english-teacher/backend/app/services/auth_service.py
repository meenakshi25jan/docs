from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.db.models.user import User
from app.services.user_service import UserService


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.users = UserService(db)

    async def register(
        self,
        *,
        name: str,
        email: str,
        password: str,
        phone_number: str | None = None,
        teacher_voice: str = "female",
    ) -> tuple[User, dict[str, str]]:
        existing = await self.users.get_by_email(email)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        user = await self.users.create_user(
            name=name,
            email=email,
            password=password,
            phone_number=phone_number,
            teacher_voice=teacher_voice,
        )
        tokens = self._build_tokens(user)
        return user, tokens

    async def login(self, email: str, password: str) -> tuple[User, dict[str, str]]:
        user = await self.users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
            )
        return user, self._build_tokens(user)

    async def refresh(self, refresh_token: str) -> dict[str, str]:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                )
            user_id = payload["sub"]
        except (JWTError, KeyError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            ) from exc

        from uuid import UUID

        user = await self.users.get_by_id(UUID(user_id))
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        return self._build_tokens(user)

    def _build_tokens(self, user: User) -> dict[str, str]:
        return {
            "access_token": create_access_token(user.id),
            "refresh_token": create_refresh_token(user.id),
            "token_type": "bearer",
        }
