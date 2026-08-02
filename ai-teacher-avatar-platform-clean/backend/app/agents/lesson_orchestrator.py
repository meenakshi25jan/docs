"""
LessonOrchestrator — owns the "today's class" state machine.

This is what turns a stateless chatbot into something that behaves like a
teacher across a whole session and across days:
- Knows what day of the course this is, and whether today is a fresh day
  (new topic, stage resets to warmup, streak updates) or a continuation of
  a lesson already in progress.
- Picks today's topic (rotates through a fixed syllabus; easy to swap for
  a real curriculum table later).
- Walks the student through STAGE_ORDER, calling TeacherAgent for each turn
  and advancing the stage only when the agent says the student completed it.
- Persists everything in LessonProgress so the "teacher" remembers the
  student across logins — this is the memory a real chatbot lacks.
"""

import uuid
from datetime import date, datetime

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.teacher_agent import teacher_agent
from app.guardrails import GuardrailError, check_input
from app.models import Attempt, ChatSession, LessonProgress, Message, StudentProfile, User
from app.schemas import (
    STAGE_LABELS,
    STAGE_ORDER,
    LessonMessageResponse,
    LessonTodayResponse,
)

TOPIC_SYLLABUS = [
    "Daily Routine",
    "Family & Friends",
    "Food & Restaurants",
    "Travel & Directions",
    "Work & Study",
    "Hobbies & Free Time",
    "Shopping",
    "Health & Body",
    "Weather & Seasons",
    "Future Plans",
]

GOAL_CHECKLIST_TEMPLATE = [
    "Speak for a few minutes",
    "Learn 1 new word",
    "Practice a grammar point",
    "Complete a short speaking test",
    "Get today's homework",
]


class LessonOrchestrator:
    async def get_today(self, db: AsyncSession, user: User) -> LessonTodayResponse:
        progress = await self._get_or_create_progress(db, user)
        today_str = date.today().isoformat()
        is_new_day = progress.last_session_date != today_str

        if is_new_day:
            # Advance the syllabus, reset to the first stage, and update the streak.
            if progress.last_session_date:
                yesterday = date.fromordinal(date.today().toordinal() - 1).isoformat()
                progress.streak_days = (
                    progress.streak_days + 1 if progress.last_session_date == yesterday else 1
                )
            else:
                progress.streak_days = 1

            if progress.stage_index >= len(STAGE_ORDER):
                progress.day_number += 1
            progress.stage_index = 0
            progress.lesson_topic = TOPIC_SYLLABUS[(progress.day_number - 1) % len(TOPIC_SYLLABUS)]
            progress.last_session_date = today_str

            session = ChatSession(id=str(uuid.uuid4()), user_id=user.id, mode="lesson")
            db.add(session)
            await db.flush()
            progress.lesson_session_id = session.id
        else:
            session = await self._get_session(db, progress.lesson_session_id, user)
            if session is None:
                session = ChatSession(id=str(uuid.uuid4()), user_id=user.id, mode="lesson")
                db.add(session)
                await db.flush()
                progress.lesson_session_id = session.id

        stage = STAGE_ORDER[min(progress.stage_index, len(STAGE_ORDER) - 1)]
        homework = progress.homework_text if progress.homework_text and not progress.homework_done else None
        profile = await self._get_or_create_profile(db, user)
        focus_weakness = self._pick_focus_weakness(profile, progress.day_number)

        result = await teacher_agent.handle(
            student_name=user.display_name or "there",
            day_number=progress.day_number,
            lesson_topic=progress.lesson_topic,
            stage=stage,
            stage_index=progress.stage_index,
            total_stages=len(STAGE_ORDER),
            student_text="",
            homework_from_last_time=homework,
            level=profile.level,
            target_band=profile.target_band,
            focus_weakness=focus_weakness,
        )

        db.add(
            Message(
                session_id=session.id,
                role="assistant",
                content=result["reply_text"],
                correction="",
            )
        )
        await db.commit()

        latest_band_score = await self._get_latest_band_score(db, user)

        return LessonTodayResponse(
            session_id=session.id,
            student_name=user.display_name or "Student",
            day_number=progress.day_number,
            lesson_topic=progress.lesson_topic,
            stage=stage,
            stage_index=progress.stage_index,
            total_stages=len(STAGE_ORDER),
            stage_label=STAGE_LABELS[stage],
            goal_checklist=GOAL_CHECKLIST_TEMPLATE,
            prompt_text=result["reply_text"],
            homework_from_last_time=homework,
            streak_days=progress.streak_days,
            words_learned=progress.words_learned,
            level=profile.level,
            target_band=profile.target_band,
            latest_band_score=latest_band_score,
            weaknesses=profile.weaknesses or [],
            focus_weakness=focus_weakness,
        )

    async def handle_message(
        self, db: AsyncSession, user: User, session_id: str, text: str
    ) -> LessonMessageResponse:
        clean_text = check_input(text)
        progress = await self._get_or_create_progress(db, user)
        session = await self._get_session(db, session_id, user)
        if session is None:
            raise GuardrailError("Lesson session not found. Start a new lesson first.")

        stage = STAGE_ORDER[min(progress.stage_index, len(STAGE_ORDER) - 1)]
        homework = progress.homework_text if progress.homework_text and not progress.homework_done else None
        profile = await self._get_or_create_profile(db, user)
        focus_weakness = self._pick_focus_weakness(profile, progress.day_number)

        result = await teacher_agent.handle(
            student_name=user.display_name or "there",
            day_number=progress.day_number,
            lesson_topic=progress.lesson_topic,
            stage=stage,
            stage_index=progress.stage_index,
            total_stages=len(STAGE_ORDER),
            student_text=clean_text,
            homework_from_last_time=homework,
            level=profile.level,
            target_band=profile.target_band,
            focus_weakness=focus_weakness,
        )

        db.add(Message(session_id=session.id, role="user", content=clean_text))
        db.add(
            Message(
                session_id=session.id,
                role="assistant",
                content=result["reply_text"],
                correction=result["correction"],
            )
        )

        if result["new_word_taught"]:
            progress.words_learned += 1

        lesson_complete = False
        if result["stage_complete"]:
            if stage == "homework":
                if result["homework_text"]:
                    progress.homework_text = result["homework_text"]
                    progress.homework_done = False
                progress.stage_index = len(STAGE_ORDER)  # mark today's class finished
                lesson_complete = True
            else:
                progress.stage_index = min(progress.stage_index + 1, len(STAGE_ORDER) - 1)

        progress.updated_at = datetime.utcnow()
        await db.commit()

        new_stage = STAGE_ORDER[min(progress.stage_index, len(STAGE_ORDER) - 1)]
        return LessonMessageResponse(
            session_id=session.id,
            reply_text=result["reply_text"],
            correction=result["correction"],
            stage=new_stage,
            stage_index=progress.stage_index,
            total_stages=len(STAGE_ORDER),
            stage_label=STAGE_LABELS[new_stage],
            stage_complete=result["stage_complete"],
            lesson_complete=lesson_complete,
            words_learned=progress.words_learned,
            homework_text=progress.homework_text if lesson_complete else None,
        )

    async def _get_or_create_progress(self, db: AsyncSession, user: User) -> LessonProgress:
        result = await db.execute(select(LessonProgress).where(LessonProgress.user_id == user.id))
        progress = result.scalar_one_or_none()
        if progress:
            return progress
        progress = LessonProgress(user_id=user.id, lesson_topic=TOPIC_SYLLABUS[0])
        db.add(progress)
        await db.flush()
        return progress

    async def _get_or_create_profile(self, db: AsyncSession, user: User) -> StudentProfile:
        result = await db.execute(select(StudentProfile).where(StudentProfile.user_id == user.id))
        profile = result.scalar_one_or_none()
        if profile:
            return profile
        profile = StudentProfile(user_id=user.id)
        db.add(profile)
        await db.flush()
        return profile

    def _pick_focus_weakness(self, profile: StudentProfile, day_number: int) -> str | None:
        """Rotate through the student's known weak areas day by day, so the
        teacher keeps circling back to old trouble spots instead of only
        ever moving forward — this is what makes 'last time you struggled
        with X' possible.
        """
        weaknesses = profile.weaknesses or []
        if not weaknesses:
            return None
        return weaknesses[(day_number - 1) % len(weaknesses)]

    async def _get_latest_band_score(self, db: AsyncSession, user: User) -> float | None:
        result = await db.execute(
            select(Attempt)
            .where(Attempt.user_id == user.id, Attempt.mode == "assessment")
            .order_by(desc(Attempt.created_at))
            .limit(1)
        )
        attempt = result.scalar_one_or_none()
        if not attempt:
            return None
        return attempt.score_json.get("band_score")

    async def _get_session(self, db: AsyncSession, session_id: str | None, user: User):
        if not session_id:
            return None
        result = await db.execute(
            select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user.id)
        )
        return result.scalar_one_or_none()


lesson_orchestrator = LessonOrchestrator()
