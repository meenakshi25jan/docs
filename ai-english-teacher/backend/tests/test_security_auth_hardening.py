"""JWT and authentication hardening tests."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core.security import create_access_token, get_current_user
from app.models import User


class TestGetCurrentUserHardening:
    @pytest.mark.asyncio
    async def test_rejects_missing_user(self):
        db = AsyncMock()
        db.get = AsyncMock(return_value=None)
        user_id = uuid4()
        tenant_id = uuid4()
        token = create_access_token(
            {
                "sub": str(user_id),
                "tenant_id": str(tenant_id),
                "role": "student",
                "email": "gone@example.com",
            }
        )
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with pytest.raises(HTTPException) as exc:
            await get_current_user(creds, db)
        assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_rejects_inactive_user(self):
        db = AsyncMock()
        user_id = uuid4()
        tenant_id = uuid4()
        db_user = User(
            id=user_id,
            tenant_id=tenant_id,
            email="inactive@example.com",
            role="student",
            is_active=False,
        )
        db.get = AsyncMock(return_value=db_user)
        token = create_access_token(
            {
                "sub": str(user_id),
                "tenant_id": str(tenant_id),
                "role": "student",
                "email": "inactive@example.com",
            }
        )

        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with pytest.raises(HTTPException) as exc:
            await get_current_user(creds, db)
        assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_rejects_tenant_mismatch(self):
        db = AsyncMock()
        user_id = uuid4()
        real_tenant = uuid4()
        wrong_tenant = uuid4()
        db_user = User(
            id=user_id,
            tenant_id=real_tenant,
            email="tenant@example.com",
            role="student",
            is_active=True,
        )
        db.get = AsyncMock(return_value=db_user)
        token = create_access_token(
            {
                "sub": str(user_id),
                "tenant_id": str(wrong_tenant),
                "role": "student",
                "email": "tenant@example.com",
            }
        )

        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with pytest.raises(HTTPException) as exc:
            await get_current_user(creds, db)
        assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_rejects_role_mismatch(self):
        db = AsyncMock()
        user_id = uuid4()
        tenant_id = uuid4()
        db_user = User(
            id=user_id,
            tenant_id=tenant_id,
            email="role@example.com",
            role="admin",
            is_active=True,
        )
        db.get = AsyncMock(return_value=db_user)
        token = create_access_token(
            {
                "sub": str(user_id),
                "tenant_id": str(tenant_id),
                "role": "student",
                "email": "role@example.com",
            }
        )

        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with pytest.raises(HTTPException) as exc:
            await get_current_user(creds, db)
        assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_accepts_valid_user(self):
        db = AsyncMock()
        user_id = uuid4()
        tenant_id = uuid4()
        db_user = User(
            id=user_id,
            tenant_id=tenant_id,
            email="valid@example.com",
            role="teacher",
            is_active=True,
        )
        db.get = AsyncMock(return_value=db_user)
        token = create_access_token(
            {
                "sub": str(user_id),
                "tenant_id": str(tenant_id),
                "role": "teacher",
                "email": "valid@example.com",
            }
        )

        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        payload = await get_current_user(creds, db)
        assert payload.role == "teacher"
        assert payload.user_id == user_id
