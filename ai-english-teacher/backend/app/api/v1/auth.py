from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentInput
from app.agents import AGENT_REGISTRY
from app.core.database import disable_auth_lookup, enable_auth_lookup, get_db, set_tenant_context
from app.core.security import (
    TokenPayload,
    create_access_token,
    create_refresh_token,
    get_current_user,
    hash_password,
    require_role,
    verify_password,
)
from app.models import (
    Assessment,
    AssessmentResult,
    Conversation,
    ConversationMessage,
    LearnerProfile,
    Tenant,
    User,
    WritingSubmission,
)
from app.schemas import (
    AssessmentCreate,
    AssessmentResponse,
    AssessmentResultResponse,
    AssessmentSubmit,
    AuthResponse,
    ConversationCreate,
    ConversationResponse,
    LoginRequest,
    MessageCreate,
    MessageResponse,
    RegisterRequest,
    SkillResult,
    TokenResponse,
    UserResponse,
    WritingResponse,
    WritingSubmit,
)
from app.scoring.engine import aggregate_scores

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    tenant = await db.scalar(select(Tenant).where(Tenant.slug == req.tenant_slug))
    if not tenant:
        tenant = Tenant(name=req.tenant_slug.title(), slug=req.tenant_slug)
        db.add(tenant)
        await db.flush()

    await set_tenant_context(db, str(tenant.id))

    existing = await db.scalar(
        select(User).where(User.tenant_id == tenant.id, User.email == req.email)
    )
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        tenant_id=tenant.id,
        email=req.email,
        password_hash=hash_password(req.password),
        first_name=req.first_name,
        last_name=req.last_name,
        role="student",
    )
    db.add(user)
    await db.flush()

    profile = LearnerProfile(tenant_id=tenant.id, user_id=user.id)
    db.add(profile)
    await db.flush()

    tokens = TokenResponse(
        access_token=create_access_token({"sub": str(user.id), "tenant_id": str(tenant.id), "role": user.role, "email": user.email}),
        refresh_token=create_refresh_token({"sub": str(user.id)}),
        expires_in=900,
    )
    return AuthResponse(user=UserResponse.model_validate(user), tokens=tokens)


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    await enable_auth_lookup(db)
    user = await db.scalar(select(User).where(User.email == req.email))
    await disable_auth_lookup(db)
    if not user or not user.password_hash or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    await set_tenant_context(db, str(user.tenant_id))

    user.last_login_at = datetime.now(timezone.utc)
    tokens = TokenResponse(
        access_token=create_access_token({"sub": str(user.id), "tenant_id": str(user.tenant_id), "role": user.role, "email": user.email}),
        refresh_token=create_refresh_token({"sub": str(user.id)}),
        expires_in=900,
    )
    return AuthResponse(user=UserResponse.model_validate(user), tokens=tokens)


@router.get("/me", response_model=UserResponse)
async def get_me(user: TokenPayload = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    db_user = await db.get(User, user.user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(db_user)
