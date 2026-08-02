from app.guardrails import GuardrailError, check_output
from app.llm_client import llm_client
from app.schemas import AgentMessageResponse

SYSTEM_PROMPT = """You are a warm, encouraging spoken English grammar tutor.
The student is at grammar Level {level} (1 = beginner basics, higher = more advanced).
The student just said (via speech-to-text, so expect minor transcription noise): "{text}"

Your job, in this order:
1. Gently and briefly correct any grammar mistake in what they said, in plain spoken language
   (as if you're speaking out loud to them, not writing a report).
2. Give ONE short next grammar exercise or question appropriate for Level {level}, so the
   lesson keeps moving.
3. Decide if they should move up a level: return "advance": true only if their answer was
   clearly correct and shows mastery of the current level; otherwise false.

Respond ONLY as JSON with exactly these keys:
{{"reply_text": "<what you'd say out loud, correction + next exercise, 2-4 sentences>",
  "correction": "<short written form of the correction, or empty string if nothing to correct>",
  "advance": <true or false>}}
"""


class GrammarAgent:
    async def handle(self, text: str, level: int) -> tuple[AgentMessageResponse, bool]:
        prompt = SYSTEM_PROMPT.format(level=level, text=text)
        try:
            data = await llm_client.chat_json(prompt, text)
        except Exception as e:
            raise GuardrailError(f"LLM call failed: {e}")

        advance = bool(data.get("advance", False))
        response = AgentMessageResponse(
            session_id="",  # filled by orchestrator
            reply_text=data.get("reply_text", "Let's try that again."),
            correction=data.get("correction", ""),
            level=level + 1 if advance else level,
        )
        return response, advance


grammar_agent = GrammarAgent()
