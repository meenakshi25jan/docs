from app.services.grok_service import GrokService


class ConversationAgent:
    def __init__(self, llm: GrokService | None = None) -> None:
        self.llm = llm or GrokService()

    async def chat(self, student_text: str) -> str:
        system_prompt = """
You are an AI English speaking teacher.

Talk naturally with the student.
Correct major mistakes gently.
Ask one follow-up question.
Keep your answer short and conversational.
"""
        return await self.llm.chat(system_prompt, student_text)
