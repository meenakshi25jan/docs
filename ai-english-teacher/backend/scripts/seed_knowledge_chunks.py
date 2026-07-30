#!/usr/bin/env python3
"""Seed knowledge_chunks from grammar curriculum, registry, and scenarios (safe re-run)."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from app.core.database import get_session_factory
from app.services.curriculum_registry import get_lessons
from app.services.grammar_curriculum import GRAMMAR_LESSONS, GRADE_LEVELS


def _grammar_chunks() -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for grade, items in GRAMMAR_LESSONS.items():
        cefr = GRADE_LEVELS.get(grade, {}).get("cefr", "B1")
        for item in items:
            topic = item["id"].replace("-", " ")
            source = f"Grammar Grade {grade}: {item['title']}"
            content = f"{item['title']} ({cefr}). {item['rule']}"
            rows.append((topic, source, content))
    return rows


def _registry_chunks() -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for lesson in get_lessons():
        if lesson.lesson_id.startswith("grammar-"):
            continue
        topic = lesson.skill_focus or lesson.topic_id
        source = f"Curriculum: {lesson.title}"
        content = lesson.description or lesson.title
        if lesson.exam_tag:
            content = f"{content} Exam focus: {lesson.exam_tag}."
        rows.append((topic.replace("_", " "), source, content))
    return rows


async def main() -> None:
    all_rows = _grammar_chunks() + _registry_chunks()
    factory = get_session_factory()
    inserted = 0
    async with factory() as session:
        for topic, source, content in all_rows:
            exists = await session.execute(
                text(
                    "SELECT 1 FROM knowledge_chunks WHERE topic = :topic AND source = :source LIMIT 1"
                ),
                {"topic": topic, "source": source},
            )
            if exists.fetchone():
                continue
            await session.execute(
                text(
                    "INSERT INTO knowledge_chunks (tenant_id, topic, source, content) "
                    "VALUES (NULL, :topic, :source, :content)"
                ),
                {"topic": topic, "source": source, "content": content},
            )
            inserted += 1
        await session.commit()
    print(f"Inserted {inserted} new knowledge chunks ({len(all_rows)} candidates).")
    print("Run seed_knowledge_embeddings.py to generate vectors when AI is configured.")


if __name__ == "__main__":
    asyncio.run(main())
