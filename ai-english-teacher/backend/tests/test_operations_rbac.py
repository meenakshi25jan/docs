"""Operations RBAC tests."""

import pytest
from httpx import AsyncClient

from app.schemas.operations import AdminSummaryResponse, TeacherRosterResponse


class TestOperationsRBAC:
    @pytest.mark.asyncio
    async def test_student_forbidden_teacher_roster(self, client: AsyncClient):
        res = await client.get("/api/v1/operations/teacher/roster")
        assert res.status_code == 403

    @pytest.mark.asyncio
    async def test_teacher_allowed_roster(self, teacher_client: AsyncClient):
        from unittest.mock import AsyncMock, patch

        with patch(
            "app.api.v1.operations._service.get_teacher_roster",
            new_callable=AsyncMock,
            return_value=TeacherRosterResponse(total=0),
        ):
            res = await teacher_client.get("/api/v1/operations/teacher/roster")
        assert res.status_code == 200

    @pytest.mark.asyncio
    async def test_student_forbidden_admin_summary(self, client: AsyncClient):
        res = await client.get("/api/v1/operations/admin/summary")
        assert res.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_allowed_summary(self, admin_client: AsyncClient):
        from unittest.mock import AsyncMock, patch
        from uuid import uuid4

        with patch(
            "app.api.v1.operations._service.get_admin_summary",
            new_callable=AsyncMock,
            return_value=AdminSummaryResponse(tenant_id=uuid4()),
        ):
            res = await admin_client.get("/api/v1/operations/admin/summary")
        assert res.status_code == 200

    @pytest.mark.asyncio
    async def test_student_forbidden_users(self, client: AsyncClient):
        res = await client.get("/api/v1/operations/users")
        assert res.status_code == 403

    @pytest.mark.asyncio
    async def test_auth_required(self, public_client: AsyncClient):
        res = await public_client.get("/api/v1/operations/teacher/roster")
        assert res.status_code in (401, 403)
