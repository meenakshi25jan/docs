"""Structured logging configuration tests."""

import json
import logging
import os

import pytest

from app.core.logging_config import JsonLogFormatter, RequestIdFilter, setup_logging
from app.core.request_context import request_id_ctx


class TestLoggingConfig:
    def test_setup_logging_text_format(self, monkeypatch):
        monkeypatch.setenv("LOG_JSON_FORMAT", "false")
        # Reset module state for test isolation
        import app.core.logging_config as lc

        lc._configured = False
        setup_logging()
        root = logging.getLogger()
        assert root.handlers
        formatter = root.handlers[0].formatter
        assert formatter is not None

    def test_request_id_filter(self):
        token = request_id_ctx.set("log-test-rid")
        try:
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="hello",
                args=(),
                exc_info=None,
            )
            filt = RequestIdFilter()
            assert filt.filter(record)
            assert record.request_id == "log-test-rid"
        finally:
            request_id_ctx.reset(token)

    def test_json_formatter(self, monkeypatch):
        monkeypatch.setenv("LOG_JSON_FORMAT", "true")
        token = request_id_ctx.set("json-rid")
        try:
            record = logging.LogRecord(
                name="test.logger",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="structured",
                args=(),
                exc_info=None,
            )
            record.request_id = "json-rid"
            payload = json.loads(JsonLogFormatter().format(record))
            assert payload["level"] == "INFO"
            assert payload["request_id"] == "json-rid"
            assert payload["message"] == "structured"
        finally:
            request_id_ctx.reset(token)

    def test_logging_is_json_env(self, monkeypatch):
        from app.core.logging_config import logging_is_json_enabled

        monkeypatch.setenv("LOG_JSON_FORMAT", "true")
        assert logging_is_json_enabled()
        monkeypatch.setenv("LOG_JSON_FORMAT", "false")
        assert not logging_is_json_enabled()
