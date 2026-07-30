"""Operations health tests."""

import pytest

from app.core.security import TokenPayload
from app.services.operations_service import OperationsService


class TestOperationsHealth:
    @pytest.mark.asyncio
    async def test_composite_health_checks(self):
        user = TokenPayload(
            sub="00000000-0000-0000-0000-000000000001",
            tenant_id="00000000-0000-0000-0000-000000000002",
            role="admin",
            email="admin@example.com",
        )
        service = OperationsService()
        result = await service.get_operations_health(user)
        assert result.status in ("healthy", "degraded")
        assert result.database in ("reachable", "not_configured", "unreachable")
        assert len(result.checks) >= 3
        assert result.auth_hashing in ("ok", "failed", "error")
