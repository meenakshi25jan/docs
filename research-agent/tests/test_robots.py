"""Tests for robots.txt handling."""

import pytest

from app.crawler.robots import RobotsCache, is_allowed_by_robots
from urllib.robotparser import RobotFileParser


def test_is_allowed_when_no_parser():
    assert is_allowed_by_robots(None, "https://example.com", "TestBot") is True


def test_robots_parser_blocks_disallowed():
    parser = RobotFileParser()
    parser.parse(
        [
            "User-agent: *",
            "Disallow: /private/",
        ]
    )
    assert is_allowed_by_robots(parser, "https://example.com/private/secret", "*") is False
    assert is_allowed_by_robots(parser, "https://example.com/public", "*") is True


@pytest.mark.asyncio
async def test_robots_cache_can_fetch_without_network():
    cache = RobotsCache()
    # Unknown domain returns None parser, which allows fetch
    allowed = await cache.can_fetch("https://nonexistent-test-domain-12345.invalid/page")
    assert allowed is True
