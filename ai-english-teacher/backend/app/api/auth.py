from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.auth import (
    AuthUserResponse,
    LoginResponse,
    RegisterResponse,
    TokenRefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.core.dependencies import get_db
from app.services.auth_service import AuthService

router = APIRouter(tags=["auth"])


def _to_auth_user(user) -> AuthUserResponse:
    return AuthUserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        teacher_voice=user.teacher_voice,
        role=user.role,
    )


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(
    payload: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> RegisterResponse:
    user, tokens = await AuthService(db).register(
        name=payload.name,
        email=payload.email,
        password=payload.password,
        phone_number=payload.phone_number,
        teacher_voice=payload.teacher_voice,
    )
    return RegisterResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        user=_to_auth_user(user),
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    user, tokens = await AuthService(db).login(email=payload.email, password=payload.password)
    return LoginResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        user=_to_auth_user(user),
    )


@router.post("/logout")
async def logout() -> dict[str, str]:
    return {"message": "Logout successful. Please remove token on client side."}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    payload: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    tokens = await AuthService(db).refresh(refresh_token=payload.refresh_token)
    return TokenResponse(**tokens)
