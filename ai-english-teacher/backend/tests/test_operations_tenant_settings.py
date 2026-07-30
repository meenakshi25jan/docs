"""Tenant settings operations tests."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.schemas.operations import TenantSettingsUpdateRequest
from app.services.operations_service import OperationsService


class TestTenantSettings:
    @pytest.mark.asyncio
    async def test_patch_validates_feature_keys(self):
        tenant_id = uuid4()
        tenant = MagicMock()
        tenant.id = tenant_id
        tenant.name = "Test"
        tenant.slug = "test"
        tenant.plan_tier = "free"
        tenant.is_active = True
        tenant.settings = {}

        from app.core.security import TokenPayload

        token = TokenPayload(
            sub=str(uuid4()),
            tenant_id=str(tenant_id),
            role="admin",
            email="admin@example.com",
        )

        with patch(
            "app.services.operations_service.get_tenant",
            new_callable=AsyncMock,
            return_value=tenant,
        ), patch(
            "app.services.operations_service.count_learners_in_tenant",
            new_callable=AsyncMock,
            return_value=1,
        ):
            service = OperationsService()
            with pytest.raises(HTTPException) as exc:
                await service.update_tenant_settings(
                    AsyncMock(),
                    token,
                    TenantSettingsUpdateRequest(settings={"features": {"invalid_key": True}}),
                )
            assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_feature_flags_from_settings(self):
        tenant_id = uuid4()
        tenant = MagicMock()
        tenant.id = tenant_id
        tenant.name = "Test"
        tenant.slug = "test"
        tenant.plan_tier = "free"
        tenant.is_active = True
        tenant.settings = {"features": {"voice_enabled": False}}

        from app.core.security import TokenPayload

        token = TokenPayload(
            sub=str(uuid4()),
            tenant_id=str(tenant_id),
            role="teacher",
            email="t@example.com",
        )

        with patch(
            "app.services.operations_service.get_tenant",
            new_callable=AsyncMock,
            return_value=tenant,
        ), patch(
            "app.services.operations_service.count_learners_in_tenant",
            new_callable=AsyncMock,
            return_value=0,
        ):
            service = OperationsService()
            result = await service.get_feature_flags(AsyncMock(), token)
        assert result.feature_flags.get("voice_enabled") is False
        assert result.feature_flags.get("analytics_dashboard") is True
