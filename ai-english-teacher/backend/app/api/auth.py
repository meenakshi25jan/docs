from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.auth import (
    TokenRefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.core.dependencies import get_db
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    payload: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    user = await AuthService(db).register(email=payload.email, password=payload.password)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    tokens = await AuthService(db).login(email=payload.email, password=payload.password)
    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    payload: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    tokens = await AuthService(db).refresh(refresh_token=payload.refresh_token)
    return TokenResponse(**tokens)
