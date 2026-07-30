"""Environment validation tests."""

from unittest.mock import MagicMock, patch

from app.services.production_readiness_service import verify_environment


class TestEnvironmentValidation:
    def test_skip_migrations_warning(self):
        with patch.dict("os.environ", {"SKIP_MIGRATIONS": "true"}, clear=False):
            with patch("app.services.production_readiness_service.database_url_configured", return_value=True):
                with patch("app.services.production_readiness_service.jwt_secret_is_safe", return_value=True):
                    result = verify_environment()
        assert any(c.name == "skip_migrations" for c in result.checks)
        assert any(w.code == "skip_migrations" for w in result.warnings)

    def test_ai_provider_check(self):
        with patch("app.services.production_readiness_service.database_url_configured", return_value=True):
            with patch("app.services.production_readiness_service.jwt_secret_is_safe", return_value=True):
                with patch("app.services.production_readiness_service.ai_client", MagicMock(provider="mock", is_configured=False)):
                    with patch("app.services.production_readiness_service.get_settings") as mock_settings:
                        mock_settings.return_value.AI_PROVIDER = "mock"
                        mock_settings.return_value.CORS_ORIGINS = ["http://localhost:3000"]
                        mock_settings.return_value.DEBUG = False
                        mock_settings.return_value.APP_VERSION = "1.0.0"
                        result = verify_environment()
        assert any(c.name == "ai_provider" for c in result.checks)
