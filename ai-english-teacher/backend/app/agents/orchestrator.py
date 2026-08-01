from typing import Any

from app.agents.conversation_agent import ConversationAgent
from app.agents.grammar_agent import GrammarAgent
from app.services.grok_service import GrokService


class OrchestratorAgent:
    def __init__(self, llm: GrokService | None = None) -> None:
        self.grammar_agent = GrammarAgent(llm=llm)
        self.conversation_agent = ConversationAgent(llm=llm)

    async def handle(self, mode: str, text: str) -> dict[str, Any]:
        if mode == "conversation":
            response = await self.conversation_agent.chat(text)
            return {
                "original_text": text,
                "corrected_text": "",
                "explanation": "",
                "mistakes": [],
                "score": 0,
                "teacher_response": response,
            }

        return await self.grammar_agent.correct(text)
