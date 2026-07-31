"""Structured logging configuration using loguru."""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

from config import get_settings

_configured = False


def setup_logger(log_file: Path | None = None) -> None:
    """Configure loguru for console and file output."""
    global _configured
    if _configured:
        return

    settings = get_settings()
    settings.logs_dir.mkdir(parents=True, exist_ok=True)

    logger.remove()
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    logger.add(
        sys.stderr,
        format=log_format,
        level="DEBUG" if settings.debug else "INFO",
        colorize=True,
    )

    file_path = log_file or settings.logs_dir / "research_agent.log"
    logger.add(
        file_path,
        format=log_format,
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        enqueue=True,
    )
    _configured = True


def get_logger():
    """Return configured logger instance."""
    setup_logger()
    return logger
