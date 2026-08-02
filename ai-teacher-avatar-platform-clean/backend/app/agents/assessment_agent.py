from app.guardrails import GuardrailError
from app.llm_client import llm_client
from app.schemas import AgentMessageResponse

SYSTEM_PROMPT = """You are an IELTS-style spoken English examiner.
Assess ONLY the following student response for fluency, grammar range/accuracy, vocabulary,
and coherence: "{text}"

Give a band score from 1.0 to 9.0 (IELTS speaking band scale, 0.5 increments allowed), plus
one strength and one improvement area, in encouraging spoken language.

Respond ONLY as JSON with exactly these keys:
{{"reply_text": "<2-3 spoken sentences giving the student feedback and their band score>",
  "band_score": <number between 1.0 and 9.0>,
  "strength": "<one short strength>",
  "improvement": "<one short improvement area>"}}
"""


class AssessmentAgent:
    async def handle(self, text: str) -> AgentMessageResponse:
        prompt = SYSTEM_PROMPT.format(text=text)
        try:
            data = await llm_client.chat_json(prompt, text)
        except Exception as e:
            raise GuardrailError(f"LLM call failed: {e}")

        return AgentMessageResponse(
            session_id="",
            reply_text=data.get("reply_text", "Thanks, let me think about that."),
            band_score=float(data.get("band_score", 0)) or None,
            details={
                "strength": data.get("strength", ""),
                "improvement": data.get("improvement", ""),
            },
        )


assessment_agent = AssessmentAgent()
