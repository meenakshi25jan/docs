from app.guardrails import GuardrailError
from app.llm_client import llm_client
from app.schemas import AgentMessageResponse

SYSTEM_PROMPT = """You are a friendly, patient spoken-English conversation partner and teacher.
The student just said (via speech-to-text, expect minor transcription noise): "{text}"

Keep the conversation going naturally, like a real spoken chat — ask a follow-up question or
respond to what they said. If they made a grammar or word-choice mistake, weave a brief, kind
correction into your spoken reply (don't lecture; model the correct form naturally, the way a
patient native speaker would). Keep your reply to 2-4 sentences, spoken style.

Respond ONLY as JSON with exactly these keys:
{{"reply_text": "<your natural spoken reply, 2-4 sentences>",
  "correction": "<short written form of the correction, or empty string if nothing to correct>"}}
"""


class ConversationAgent:
    async def handle(self, text: str) -> AgentMessageResponse:
        prompt = SYSTEM_PROMPT.format(text=text)
        try:
            data = await llm_client.chat_json(prompt, text)
        except Exception as e:
            raise GuardrailError(f"LLM call failed: {e}")

        return AgentMessageResponse(
            session_id="",
            reply_text=data.get("reply_text", "Tell me more about that."),
            correction=data.get("correction", ""),
        )


conversation_agent = ConversationAgent()
