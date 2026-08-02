"""
TeacherAgent — the persona layer that makes this feel like a real teacher
instead of a Q&A chatbot.

Unlike the other agents (which handle one isolated turn), this agent is
STAGE-AWARE: it knows which part of today's class it's in (warmup ->
vocabulary -> grammar -> speaking_test -> homework) and is told explicitly
whether it's opening a stage (deliver content + one question) or reacting
to the student's answer (correct gently, then decide whether to move on).

The actual state machine (which stage we're on, when to advance, persisting
progress) lives in lesson_orchestrator.py — this file is only responsible
for one LLM call with the right prompt for the current moment.
"""

from app.guardrails import GuardrailError
from app.llm_client import llm_client
from app.schemas import STAGE_LABELS

STAGE_GUIDE = {
    "warmup": (
        "Greet the student warmly by name (only if this is the first message of the "
        "lesson — student_text will be empty in that case). If they have unfinished "
        "homework from last time, gently ask about it first. Then ask ONE easy, "
        "friendly warm-up question related to today's topic to get them speaking."
    ),
    "vocabulary": (
        "Teach exactly ONE new useful word or short phrase related to today's topic. "
        "Give a simple one-line example sentence using it. Then ask the student to "
        "make their own sentence with that word."
    ),
    "grammar": (
        "Give ONE short, clear grammar point relevant to today's topic (e.g. a verb "
        "tense or sentence pattern), with one example. Then ask the student to produce "
        "a sentence using that grammar point."
    ),
    "speaking_test": (
        "Ask the student to speak 2-3 connected sentences about today's topic. Don't "
        "teach new content here — just listen, encourage, and gently note any mistakes."
    ),
    "homework": (
        "Warmly wrap up today's class. Praise something specific they did well today. "
        "Assign ONE short, concrete homework task connected to today's topic that they "
        "can do before the next lesson (e.g. 'write 3 sentences about...', 'practice "
        "saying...'). Put that task in homework_text."
    ),
}

SYSTEM_PROMPT = """You are "Mr. David", a warm, encouraging, patient AI English teacher.
You are teaching {student_name}, a {level}-level English learner{target_note}.

Today is Day {day_number}. Today's lesson topic is: "{lesson_topic}".
You are currently in the "{stage}" stage of class ({stage_num} of {total_stages}): {stage_label}.
{homework_note}{weakness_note}
Stage instructions for what to do right now:
{stage_guide}

The student's most recent spoken answer (via speech-to-text, expect minor transcription
noise; it may be empty if you are opening this stage): "{student_text}"

Rules:
- Sound like a real teacher speaking out loud, not a written report. Warm, natural, concise.
- Never lecture at length. 2-4 spoken sentences maximum per reply.
- If they made a grammar or word-choice mistake, correct it briefly and kindly, then keep
  going — don't dwell on it.
- Only mark "stage_complete": true once the student has actually responded to this stage's
  core question/task in this exchange (not on your very first opening message of a stage,
  since student_text is empty then).
- Only set "new_word_taught": true in the "vocabulary" stage, on the message where you
  actually introduce the new word.
- Only fill "homework_text" when you are in the "homework" stage and are assigning it.

Respond ONLY as JSON with exactly these keys:
{{"reply_text": "<what you say out loud, 2-4 sentences>",
  "correction": "<short written correction, or empty string if nothing to correct>",
  "stage_complete": <true or false>,
  "new_word_taught": <true or false>,
  "homework_text": "<homework assignment text, or empty string>"}}
"""


class TeacherAgent:
    async def handle(
        self,
        *,
        student_name: str,
        day_number: int,
        lesson_topic: str,
        stage: str,
        stage_index: int,
        total_stages: int,
        student_text: str,
        homework_from_last_time: str | None,
        level: str = "Intermediate",
        target_band: float | None = None,
        focus_weakness: str | None = None,
    ) -> dict:
        homework_note = (
            f'They still owe homework from last time: "{homework_from_last_time}". '
            "Briefly ask about it if this is your opening line of the lesson, otherwise ignore it.\n"
            if homework_from_last_time and stage == "warmup"
            else ""
        )

        target_note = f", aiming for a target score of {target_band}" if target_band else ""

        weakness_note = ""
        if focus_weakness:
            if stage == "warmup":
                weakness_note = (
                    f'You know this student has been struggling with "{focus_weakness}". If this is '
                    f"your opening line of the lesson, mention it warmly (e.g. \"last time you found "
                    f'{focus_weakness} tricky, let\'s work on that today\") before your warm-up question.\n'
                )
            elif stage == "grammar":
                weakness_note = (
                    f'This student\'s known weak area is "{focus_weakness}" — steer today\'s grammar '
                    "point toward that weak area if it fits naturally with the lesson topic; otherwise "
                    "teach the topic's own grammar point.\n"
                )

        prompt = SYSTEM_PROMPT.format(
            student_name=student_name,
            level=level,
            target_note=target_note,
            day_number=day_number,
            lesson_topic=lesson_topic,
            stage=stage,
            stage_num=stage_index + 1,
            total_stages=total_stages,
            stage_label=STAGE_LABELS.get(stage, stage),
            homework_note=homework_note,
            weakness_note=weakness_note,
            stage_guide=STAGE_GUIDE.get(stage, ""),
            student_text=student_text or "(no answer yet — this is the opening of the stage)",
        )

        try:
            data = await llm_client.chat_json(prompt, student_text or "(begin stage)")
        except Exception as e:
            raise GuardrailError(f"LLM call failed: {e}")

        return {
            "reply_text": data.get("reply_text", "Let's continue — tell me more."),
            "correction": data.get("correction", ""),
            "stage_complete": bool(data.get("stage_complete", False)),
            "new_word_taught": bool(data.get("new_word_taught", False)),
            "homework_text": data.get("homework_text", "") or "",
        }


teacher_agent = TeacherAgent()
