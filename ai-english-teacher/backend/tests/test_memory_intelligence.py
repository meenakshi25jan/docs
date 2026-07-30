"""Tests for Memory Intelligence v1."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.models import ConversationMessage, LearnerProfile, ProgressSnapshot
from app.models.memory import ErrorTracking, LearnerMemory
from app.models.reports import Report
from app.schemas.memory_intelligence import MemoryBundle, RecurringMistake
from app.services.memory_intelligence_service import (
    MemoryIntelligenceService,
    _build_memory_summary,
    _empty_bundle,
)
from app.services.memory_store import persist_mistake


class TestMemoryBundleDefaults:
    def test_empty_bundle_safe_defaults(self):
        bundle = _empty_bundle()
        assert bundle.recent_turns == []
        assert bundle.recurring_mistakes == []
        assert bundle.memory_summary == ""
        assert bundle.metadata.used_fallback is True

    def test_router_dict_shape(self):
        bundle = MemoryBundle(
            recurring_mistakes=[RecurringMistake(error="I go", correction="I went", count=2)],
            memory_summary="Recurring mistakes: I go",
        )
        d = bundle.to_router_dict()
        assert "recurring_mistakes" in d
        assert "learning_mistakes" in d
        assert d["memory_summary"]

    def test_api_metadata(self):
        bundle = MemoryBundle(
            lesson_reflections=[],
            memory_summary="focus grammar",
        )
        meta = bundle.to_api_metadata()
        assert meta["memory_summary_available"] is True


class TestMemorySummary:
    def test_summary_bounded(self):
        long_mistakes = [
            RecurringMistake(error="x" * 200, correction="y" * 200, count=5)
            for _ in range(10)
        ]
        summary = _build_memory_summary(
            recurring=long_mistakes,
            reflections=[],
            preferences={},
            weaknesses=["grammar"],
        )
        assert len(summary) <= 1500


class TestRetrievalPolicyLimits:
    @pytest.mark.asyncio
    async def test_recent_turns_limit_12(self):
        service = MemoryIntelligenceService()
        mock_db = AsyncMock()
        lid = uuid4()
        messages = [
            ConversationMessage(
                conversation_id=uuid4(),
                role="user",
                content=f"msg {i}",
                created_at=datetime.now(timezone.utc),
            )
            for i in range(20)
        ]

        with patch(
            "app.services.memory_intelligence_service.get_recent_conversation_messages",
            new_callable=AsyncMock,
            return_value=messages[-12:],
        ):
            with patch(
                "app.services.memory_intelligence_service.get_recurring_mistakes_rows",
                new_callable=AsyncMock,
                return_value=[],
            ):
                with patch(
                    "app.services.memory_intelligence_service.get_learner_memories_by_type",
                    new_callable=AsyncMock,
                    return_value=[],
                ):
                    with patch(
                        "app.services.memory_intelligence_service.get_learner_profile",
                        new_callable=AsyncMock,
                        return_value=None,
                    ):
                        with patch(
                            "app.services.memory_intelligence_service.get_latest_progress_snapshots",
                            new_callable=AsyncMock,
                            return_value=[],
                        ):
                            bundle = await service._build_bundle_with_session(
                                mock_db,
                                learner_id=str(lid),
                                tenant_id=str(uuid4()),
                                conversation_id=str(uuid4()),
                                message_history=None,
                                session_recent_errors=None,
                                same_turn_errors=None,
                            )
        assert len(bundle.recent_turns) <= 12

    @pytest.mark.asyncio
    async def test_recurring_mistakes_limit_8(self):
        service = MemoryIntelligenceService()
        mock_db = AsyncMock()
        lid = uuid4()
        rows = [
            ErrorTracking(
                tenant_id=uuid4(),
                learner_id=lid,
                error_category="grammar",
                error_type="grammar",
                error_text=f"err {i}",
                occurrence_count=i + 1,
            )
            for i in range(15)
        ]

        with patch(
            "app.services.memory_intelligence_service.get_recurring_mistakes_rows",
            new_callable=AsyncMock,
            return_value=rows[:8],
        ):
            with patch(
                "app.services.memory_intelligence_service.get_learner_memories_by_type",
                new_callable=AsyncMock,
                return_value=[],
            ):
                with patch(
                    "app.services.memory_intelligence_service.get_learner_profile",
                    new_callable=AsyncMock,
                    return_value=None,
                ):
                    with patch(
                        "app.services.memory_intelligence_service.get_latest_progress_snapshots",
                        new_callable=AsyncMock,
                        return_value=[],
                    ):
                        bundle = await service._build_bundle_with_session(
                            mock_db,
                            learner_id=str(lid),
                            tenant_id=str(uuid4()),
                            conversation_id=None,
                            message_history=None,
                            session_recent_errors=None,
                            same_turn_errors=None,
                        )
        assert len(bundle.recurring_mistakes) <= 8

    @pytest.mark.asyncio
    async def test_reflections_limit_3(self):
        service = MemoryIntelligenceService()
        mock_db = AsyncMock()
        lid = uuid4()
        rows = [
            LearnerMemory(
                tenant_id=uuid4(),
                learner_id=lid,
                memory_type="lesson_reflection",
                content=json.dumps({"executive_summary": f"r{i}"}),
            )
            for i in range(5)
        ]

        async def fake_get_memories(db, learner_id, memory_type, limit=5):
            if memory_type == "lesson_reflection":
                return rows[:limit]
            return []

        with patch(
            "app.services.memory_intelligence_service.get_learner_memories_by_type",
            side_effect=fake_get_memories,
        ):
            with patch(
                "app.services.memory_intelligence_service.get_recurring_mistakes_rows",
                new_callable=AsyncMock,
                return_value=[],
            ):
                with patch(
                    "app.services.memory_intelligence_service.get_learner_profile",
                    new_callable=AsyncMock,
                    return_value=None,
                ):
                    with patch(
                        "app.services.memory_intelligence_service.get_latest_progress_snapshots",
                        new_callable=AsyncMock,
                        return_value=[],
                    ):
                        bundle = await service._build_bundle_with_session(
                            mock_db,
                            learner_id=str(lid),
                            tenant_id=str(uuid4()),
                            conversation_id=None,
                            message_history=None,
                            session_recent_errors=None,
                            same_turn_errors=None,
                        )
        assert len(bundle.lesson_reflections) <= 3


class TestPersistMistakeLastSeen:
    @pytest.mark.asyncio
    async def test_last_seen_at_updated_on_increment(self):
        lid = uuid4()
        tid = uuid4()
        existing = ErrorTracking(
            id=uuid4(),
            tenant_id=tid,
            learner_id=lid,
            error_category="grammar",
            error_type="grammar",
            error_text="I am go",
            correction="I went",
            occurrence_count=1,
            last_seen_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
        )
        mock_session = AsyncMock()
        mock_session.scalar = AsyncMock(return_value=existing)
        mock_session.commit = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.execute = AsyncMock()

        mock_factory = MagicMock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch("app.services.memory_store.get_session_factory", return_value=mock_factory):
            with patch("app.services.memory_store.embed_text", return_value=None):
                await persist_mistake(
                    learner_id=str(lid),
                    tenant_id=str(tid),
                    error_text="I am go",
                    correction="I went",
                )
        assert existing.occurrence_count == 2
        assert existing.last_seen_at.year >= 2020


class TestMemoryWrites:
    @pytest.mark.asyncio
    async def test_write_teacher_brain_decision(self):
        service = MemoryIntelligenceService()
        mock_db = AsyncMock()
        tid = uuid4()
        lid = uuid4()
        with patch(
            "app.services.memory_intelligence_service.insert_learner_memory",
            new_callable=AsyncMock,
        ) as insert_mock:
            await service.write_teacher_brain_decision(
                learner_id=str(lid),
                tenant_id=str(tid),
                decision={
                    "intent": "grammar_question",
                    "teaching_strategy": "explanation_first",
                    "skill_focus": "grammar",
                },
                conversation_id=str(uuid4()),
                db=mock_db,
            )
            insert_mock.assert_awaited_once()
            assert insert_mock.await_args.kwargs["memory_type"] == "teacher_brain_decision"

    @pytest.mark.asyncio
    async def test_write_lesson_reflection(self):
        service = MemoryIntelligenceService()
        mock_db = AsyncMock()
        tid = uuid4()
        lid = uuid4()
        with patch(
            "app.services.memory_intelligence_service.has_recent_reflection_for_conversation",
            new_callable=AsyncMock,
            return_value=False,
        ):
            with patch(
                "app.services.memory_intelligence_service.insert_learner_memory",
                new_callable=AsyncMock,
            ) as insert_mock:
                await service.write_lesson_reflection(
                    learner_id=str(lid),
                    tenant_id=str(tid),
                    executive_summary="Good progress on fluency.",
                    recurring_mistakes=[{"error": "I go", "correction": "I went"}],
                    recommended_next_focus="grammar",
                    conversation_id=str(uuid4()),
                    db=mock_db,
                )
                insert_mock.assert_awaited_once()
                assert insert_mock.await_args.kwargs["memory_type"] == "lesson_reflection"

    @pytest.mark.asyncio
    async def test_persist_lesson_report(self):
        service = MemoryIntelligenceService()
        mock_db = AsyncMock()
        tid = uuid4()
        lid = uuid4()
        report_row = Report(
            id=uuid4(),
            tenant_id=tid,
            learner_id=lid,
            report_type="lesson_completion",
            content={"scores": {}},
        )
        with patch(
            "app.services.memory_intelligence_service.insert_report",
            new_callable=AsyncMock,
            return_value=report_row,
        ):
            rid = await service.persist_lesson_report(
                learner_id=str(lid),
                tenant_id=str(tid),
                report_content={"executive_summary": "done"},
                db=mock_db,
            )
            assert rid == str(report_row.id)


class TestBuildBundleMerging:
    @pytest.mark.asyncio
    async def test_preferences_from_profile(self):
        service = MemoryIntelligenceService()
        mock_db = AsyncMock()
        lid = uuid4()
        profile = LearnerProfile(
            id=lid,
            tenant_id=uuid4(),
            user_id=uuid4(),
            preferences={"correction_style": "immediate", "daily_goal_minutes": 15},
        )
        with patch(
            "app.services.memory_intelligence_service.get_recurring_mistakes_rows",
            new_callable=AsyncMock,
            return_value=[],
        ):
            with patch(
                "app.services.memory_intelligence_service.get_learner_memories_by_type",
                new_callable=AsyncMock,
                return_value=[],
            ):
                with patch(
                    "app.services.memory_intelligence_service.get_learner_profile",
                    new_callable=AsyncMock,
                    return_value=profile,
                ):
                    with patch(
                        "app.services.memory_intelligence_service.get_latest_progress_snapshots",
                        new_callable=AsyncMock,
                        return_value=[],
                    ):
                        bundle = await service._build_bundle_with_session(
                            mock_db,
                            learner_id=str(lid),
                            tenant_id=str(profile.tenant_id),
                            conversation_id=None,
                            message_history=None,
                            session_recent_errors=None,
                            same_turn_errors=None,
                        )
        assert bundle.preferences.get("correction_style") == "immediate"

    @pytest.mark.asyncio
    async def test_skill_weaknesses_from_snapshot(self):
        service = MemoryIntelligenceService()
        mock_db = AsyncMock()
        lid = uuid4()
        snap = ProgressSnapshot(
            tenant_id=uuid4(),
            learner_id=lid,
            grammar_score=40,
            vocabulary_score=80,
            speaking_score=70,
            writing_score=75,
            reading_score=72,
            listening_score=68,
            confidence_score=65,
        )
        with patch(
            "app.services.memory_intelligence_service.get_recurring_mistakes_rows",
            new_callable=AsyncMock,
            return_value=[],
        ):
            with patch(
                "app.services.memory_intelligence_service.get_learner_memories_by_type",
                new_callable=AsyncMock,
                return_value=[],
            ):
                with patch(
                    "app.services.memory_intelligence_service.get_learner_profile",
                    new_callable=AsyncMock,
                    return_value=None,
                ):
                    with patch(
                        "app.services.memory_intelligence_service.get_latest_progress_snapshots",
                        new_callable=AsyncMock,
                        return_value=[snap],
                    ):
                        bundle = await service._build_bundle_with_session(
                            mock_db,
                            learner_id=str(lid),
                            tenant_id=str(snap.tenant_id),
                            conversation_id=None,
                            message_history=None,
                            session_recent_errors=None,
                            same_turn_errors=None,
                        )
        assert len(bundle.skill_weaknesses) <= 2
        assert bundle.skill_weaknesses[0] == "grammar"


class TestMemoryFailureSafe:
    @pytest.mark.asyncio
    async def test_build_bundle_failure_returns_empty(self):
        service = MemoryIntelligenceService()
        with patch.object(service, "_build_bundle_with_session", side_effect=RuntimeError("db down")):
            with patch("app.services.memory_intelligence_service.get_session_factory", side_effect=RuntimeError("db")):
                bundle = await service.build_bundle(
                    learner_id=str(uuid4()),
                    tenant_id=str(uuid4()),
                )
        assert bundle.metadata.used_fallback is True


class TestCognitiveMemoryWrite:
    @pytest.mark.asyncio
    async def test_orchestrator_writes_teacher_brain_decision(self):
        from app.cognitive.orchestrator import CognitiveOrchestrator

        orch = CognitiveOrchestrator()
        with patch("app.cognitive.orchestrator.moderate_text", return_value={"safe": True}):
            with patch("app.cognitive.orchestrator.classify_intent", return_value=MagicMock(value="conversation")):
                with patch("app.cognitive.orchestrator.select_tools", return_value=[]):
                    with patch("app.cognitive.orchestrator.tools_to_skip", return_value=[]):
                        with patch("app.cognitive.orchestrator.evaluate_policy", return_value=MagicMock(web_search_allowed=False, model_tier="mini")):
                            with patch("app.cognitive.orchestrator.route_memories", new_callable=AsyncMock, return_value={"recurring_mistakes": []}):
                                with patch("app.cognitive.orchestrator.plan_agents", return_value=MagicMock(agents=[], skipped=[])):
                                    with patch("app.cognitive.orchestrator.get_workflow", return_value=MagicMock(steps=[], name="test")):
                                        with patch("app.cognitive.orchestrator.build_teacher_context", new_callable=AsyncMock, return_value={}):
                                            with patch("app.cognitive.orchestrator.select_model_tier", return_value="mini"):
                                                with patch(
                                                    "app.cognitive.orchestrator.execute_teacher_brain",
                                                    new_callable=AsyncMock,
                                                    return_value={
                                                        "response": "Hello!",
                                                        "teacher_brain": {
                                                            "intent": "greeting",
                                                            "teaching_strategy": "practice_prompt",
                                                            "skill_focus": "speaking",
                                                        },
                                                    },
                                                ):
                                                    with patch(
                                                        "app.services.memory_intelligence_service.MemoryIntelligenceService.write_after_teacher_turn",
                                                        new_callable=AsyncMock,
                                                    ) as write_mock:
                                                        with patch("app.cognitive.orchestrator.persist_cognitive_state", new_callable=AsyncMock):
                                                            with patch("app.cognitive.orchestrator.load_session", new_callable=AsyncMock, return_value={}):
                                                                result = await orch.process_turn(
                                                                    session_id=str(uuid4()),
                                                                    learner_id=str(uuid4()),
                                                                    tenant_id=str(uuid4()),
                                                                    message="Hi",
                                                                    message_history=[],
                                                                    scenario="everyday",
                                                                    cefr_level="B1",
                                                                )
                                                                write_mock.assert_awaited_once()
                                                                assert result.get("memory") is not None


class TestLangGraphRecall:
    @pytest.mark.asyncio
    async def test_recall_memory_includes_recurring_mistakes(self):
        from app.orchestration.graph import node_recall_memory

        state = {
            "session_id": str(uuid4()),
            "learner_id": str(uuid4()),
            "tenant_id": str(uuid4()),
            "message": "test",
            "message_history": [],
            "agent_path": [],
        }
        mock_bundle = MemoryBundle(
            recurring_mistakes=[RecurringMistake(error="I go", correction="I went")],
            memory_summary="Recurring mistakes: I go",
        )
        with patch(
            "app.services.memory_intelligence_service.MemoryIntelligenceService.build_bundle_with_session_recall",
            new_callable=AsyncMock,
            return_value=mock_bundle,
        ):
            result = await node_recall_memory(state)
        assert len(result.get("recurring_mistakes", [])) >= 1
        assert result.get("memory_summary")


class TestLessonReportPersistence:
    @pytest.mark.asyncio
    async def test_generate_lesson_report_writes_reflection(self):
        from app.orchestration.voice.lesson_report import generate_lesson_report

        lid = uuid4()
        tid = uuid4()
        cid = uuid4()
        mock_db = AsyncMock()
        mock_analysis = MagicMock()
        mock_analysis.overall_score = 75
        mock_analysis.fluency_score = 70
        mock_analysis.pronunciation_score = 72
        mock_analysis.grammar_score = 68
        mock_analysis.vocabulary_score = 74
        mock_analysis.details = {}
        mock_db.scalars = AsyncMock(return_value=[mock_analysis])

        with patch("app.orchestration.voice.lesson_report.get_recurring_mistakes", new_callable=AsyncMock, return_value=[]):
            with patch("app.orchestration.voice.lesson_report.AGENT_REGISTRY") as registry:
                registry["report"].execute = AsyncMock(
                    return_value=MagicMock(data={
                        "executive_summary": "Nice work today.",
                        "recommendations": ["practice past tense"],
                        "next_steps": ["Try more sentences"],
                        "skill_breakdown": {"focus": "grammar"},
                    }),
                )
                with patch(
                    "app.orchestration.voice.lesson_report.record_from_lesson_scores",
                    new_callable=AsyncMock,
                ):
                    with patch(
                        "app.services.memory_intelligence_service.MemoryIntelligenceService.persist_lesson_report",
                        new_callable=AsyncMock,
                        return_value=str(uuid4()),
                    ):
                        with patch(
                            "app.services.memory_intelligence_service.MemoryIntelligenceService.write_lesson_reflection",
                            new_callable=AsyncMock,
                        ) as reflect_mock:
                            with patch(
                                "app.services.memory_intelligence_service.MemoryIntelligenceService.write_learning_event",
                                new_callable=AsyncMock,
                            ):
                                report = await generate_lesson_report(
                                    db=mock_db,
                                    learner_id=lid,
                                    tenant_id=tid,
                                    conversation_id=cid,
                                )
                                assert report.get("executive_summary") == "Nice work today."
                                reflect_mock.assert_awaited_once()


class TestMemoryAPI:
    @pytest.mark.asyncio
    async def test_memory_summary_endpoint(self, client: AsyncClient, learner_id):
        mock_bundle = MemoryBundle(
            memory_summary="Weakest skills: grammar.",
            recurring_mistakes=[RecurringMistake(error="I go", correction="I went")],
        )
        with patch(
            "app.services.memory_intelligence_service.MemoryIntelligenceService.build_bundle",
            new_callable=AsyncMock,
            return_value=mock_bundle,
        ):
            client.mock_db.scalar = AsyncMock(return_value=client.mock_learner)
            res = await client.get("/api/v1/memory/summary")
            assert res.status_code == 200
            data = res.json()
            assert data["recurring_mistakes_count"] == 1
            assert "grammar" in data["memory_summary"]

    @pytest.mark.asyncio
    async def test_memory_reflections_endpoint(self, client: AsyncClient, learner_id):
        from app.schemas.memory_intelligence import LessonReflection

        mock_bundle = MemoryBundle(
            lesson_reflections=[
                LessonReflection(content="Focus on past tense", recommended_focus="grammar"),
            ],
        )
        with patch(
            "app.services.memory_intelligence_service.MemoryIntelligenceService.build_bundle",
            new_callable=AsyncMock,
            return_value=mock_bundle,
        ):
            client.mock_db.scalar = AsyncMock(return_value=client.mock_learner)
            res = await client.get("/api/v1/memory/reflections")
            assert res.status_code == 200
            assert len(res.json()["reflections"]) == 1


class TestVoiceTurnMemoryMetadata:
    @pytest.mark.asyncio
    async def test_voice_turn_core_fields_and_memory(self, client: AsyncClient, learner_id):
        mock_result = {
            "transcript": "Hello",
            "response": "Welcome!",
            "teaching_mode": "none",
            "corrections": [],
            "voice_scores": {"overall": 80},
            "estimates": {"cefr": "B1"},
            "teacher_brain": {"intent": "greeting"},
            "memory": {
                "recurring_mistakes_count": 2,
                "reflections_available": True,
                "memory_summary_available": True,
            },
            "agent_output": {},
            "metadata": {},
        }
        with patch("app.api.v1.voice.run_voice_turn", return_value=mock_result):
            client.mock_db.scalar = AsyncMock(return_value=client.mock_learner)
            res = await client.post(
                "/api/v1/voice/turn",
                json={"transcript": "Hello"},
            )
            assert res.status_code == 200
            data = res.json()
            assert data["response"] == "Welcome!"
            assert data["teaching_mode"] == "none"
            assert data["memory"]["recurring_mistakes_count"] == 2
