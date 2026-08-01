#!/usr/bin/env python3
"""Idempotent database seed for local/dev environments.

Safe to run multiple times — uses natural keys (email, lesson title) for upserts.
Does NOT seed knowledge_embedding rows (vectors require a real embedding pipeline).
"""

from __future__ import annotations

import asyncio
import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.models.lesson_knowledge import LessonKnowledge
from app.db.models.user import User
from app.db.models.user_profile import UserProfile

SEED_USERS = [
    {
        "id": uuid.UUID("11111111-1111-4111-8111-111111111101"),
        "name": "Seed Alice",
        "email": "alice@seed.local",
        "password": "SeedTest1!",
        "role": "student",
        "teacher_voice": "female",
        "profile": {
            "display_name": "Alice (seed)",
            "native_language": "es",
            "target_level": "B1",
            "learning_goals": "Improve conversational fluency for travel.",
            "timezone": "America/New_York",
        },
    },
    {
        "id": uuid.UUID("11111111-1111-4111-8111-111111111102"),
        "name": "Seed Bob",
        "email": "bob@seed.local",
        "password": "SeedTest1!",
        "role": "student",
        "teacher_voice": "male",
        "profile": {
            "display_name": "Bob (seed)",
            "native_language": "hi",
            "target_level": "A2",
            "learning_goals": "Build grammar foundations for IELTS prep.",
            "timezone": "Asia/Kolkata",
        },
    },
    {
        "id": uuid.UUID("11111111-1111-4111-8111-111111111103"),
        "name": "Seed Carol",
        "email": "carol@seed.local",
        "password": "SeedTest1!",
        "role": "teacher",
        "teacher_voice": "female",
        "profile": {
            "display_name": "Carol (seed)",
            "native_language": "en",
            "target_level": "C1",
            "learning_goals": "Demo teacher account for platform testing.",
            "timezone": "Europe/London",
        },
    },
]

SEED_LESSONS = [
    {
        "id": uuid.UUID("22222222-2222-4222-8222-222222222201"),
        "title": "Present Simple vs Present Continuous",
        "content": (
            "Use the present simple for habits and facts. "
            "Use the present continuous for actions happening now or temporary situations."
        ),
        "skill": "grammar",
        "level": "A2",
        "topic": "tenses",
        "tags": ["present-simple", "present-continuous"],
        "source": "seed",
    },
    {
        "id": uuid.UUID("22222222-2222-4222-8222-222222222202"),
        "title": "Ordering Food Politely",
        "content": (
            "Practice phrases: 'Could I have...', 'I'd like...', and 'May I get...' "
            "to sound natural when ordering in a restaurant."
        ),
        "skill": "speaking",
        "level": "B1",
        "topic": "daily-life",
        "tags": ["restaurant", "politeness"],
        "source": "seed",
    },
    {
        "id": uuid.UUID("22222222-2222-4222-8222-222222222203"),
        "title": "Academic Essay Linking Words",
        "content": (
            "Link ideas with 'Furthermore', 'However', 'In contrast', and 'Consequently' "
            "to improve coherence in IELTS Writing Task 2."
        ),
        "skill": "writing",
        "level": "B2",
        "topic": "ielts",
        "tags": ["linking-words", "essay"],
        "source": "seed",
    },
    {
        "id": uuid.UUID("22222222-2222-4222-8222-222222222204"),
        "title": "Listening for Main Idea",
        "content": (
            "Focus on the first and last sentences of each section. "
            "Note repeated keywords and speaker tone shifts."
        ),
        "skill": "listening",
        "level": "B1",
        "topic": "comprehension",
        "tags": ["listening", "main-idea"],
        "source": "seed",
    },
    {
        "id": uuid.UUID("22222222-2222-4222-8222-222222222205"),
        "title": "Pronunciation: TH Sounds",
        "content": (
            "Place the tongue lightly between teeth for /θ/ (think) and /ð/ (this). "
            "Avoid substituting /t/ or /d/ in connected speech drills."
        ),
        "skill": "pronunciation",
        "level": "A2",
        "topic": "phonetics",
        "tags": ["th-sound", "pronunciation"],
        "source": "seed",
    },
]


async def _upsert_user(session: AsyncSession, seed: dict) -> None:
    profile_data = seed.pop("profile")
    password = seed.pop("password")
    user_values = {
        **seed,
        "hashed_password": hash_password(password),
        "is_active": True,
    }

    bind = session.get_bind()
    if bind is not None and bind.dialect.name == "postgresql":
        stmt = pg_insert(User).values(**user_values)
        stmt = stmt.on_conflict_do_update(
            index_elements=[User.email],
            set_={
                "name": stmt.excluded.name,
                "role": stmt.excluded.role,
                "teacher_voice": stmt.excluded.teacher_voice,
                "is_active": stmt.excluded.is_active,
            },
        )
        await session.execute(stmt)
    else:
        existing = await session.scalar(select(User).where(User.email == user_values["email"]))
        if existing is None:
            session.add(User(**user_values))
        else:
            existing.name = user_values["name"]
            existing.role = user_values["role"]
            existing.teacher_voice = user_values["teacher_voice"]
            existing.is_active = True

    await session.flush()
    user = await session.scalar(select(User).where(User.email == user_values["email"]))
    if user is None:
        raise RuntimeError(f"Failed to upsert seed user {user_values['email']}")

    profile_values = {"user_id": user.id, **profile_data}
    existing_profile = await session.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
    if existing_profile is None:
        session.add(UserProfile(**profile_values))
    else:
        for key, value in profile_data.items():
            setattr(existing_profile, key, value)


async def _upsert_lesson(session: AsyncSession, lesson: dict) -> None:
    bind = session.get_bind()
    if bind is not None and bind.dialect.name == "postgresql":
        stmt = pg_insert(LessonKnowledge).values(**lesson)
        stmt = stmt.on_conflict_do_update(
            index_elements=[LessonKnowledge.id],
            set_={
                "title": stmt.excluded.title,
                "content": stmt.excluded.content,
                "skill": stmt.excluded.skill,
                "level": stmt.excluded.level,
                "topic": stmt.excluded.topic,
                "tags": stmt.excluded.tags,
                "source": stmt.excluded.source,
            },
        )
        await session.execute(stmt)
    else:
        existing = await session.scalar(
            select(LessonKnowledge).where(LessonKnowledge.id == lesson["id"])
        )
        if existing is None:
            session.add(LessonKnowledge(**lesson))
        else:
            for key, value in lesson.items():
                setattr(existing, key, value)


async def seed_database() -> None:
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        for user_seed in SEED_USERS:
            await _upsert_user(session, dict(user_seed))
        for lesson in SEED_LESSONS:
            await _upsert_lesson(session, dict(lesson))
        await session.commit()

    await engine.dispose()
    print("Seed complete: users, profiles, and lesson_knowledge upserted.")


def main() -> None:
    asyncio.run(seed_database())


if __name__ == "__main__":
    main()
