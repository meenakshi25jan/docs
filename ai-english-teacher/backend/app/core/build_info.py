import os
from datetime import UTC, datetime


def get_build_commit() -> str:
    return (
        os.getenv("BUILD_COMMIT_SHA")
        or os.getenv("RENDER_GIT_COMMIT")
        or os.getenv("GITHUB_SHA")
        or "unknown"
    )


def get_build_timestamp() -> str:
    return os.getenv("BUILD_TIMESTAMP") or datetime.now(UTC).isoformat()


def get_build_info() -> dict[str, str]:
    return {
        "commit": get_build_commit(),
        "builtAt": get_build_timestamp(),
        "service": "ai-english-teacher-api",
    }
