"""Conversation Agent — natural dialogue for greetings and light chat."""

from __future__ import annotations

from app.agents.base import AgentInput, AgentOutput, BaseAgent


class ConversationAgent(BaseAgent):
    name = "conversation"
    system_prompt_template = """You are a friendly English conversation partner.
Scenario: {scenario}. Learner CEFR: {cefr_level}.
Keep responses short (2-3 sentences). Be warm and encourage the learner to speak more.
Return JSON: {{"response": str, "follow_up_question": str, "encouragement": str}}"""

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        ctx = input_data.context
        scenario = ctx.get("scenario", "general_conversation")
        cefr = ctx.get("cefr_level", "B1")
        message = self.sanitize(ctx.get("message", ""))
        history = ctx.get("message_history", [])

        knowledge = ctx.get("knowledge_context", "")
        extra = f"\nRelevant knowledge:\n{knowledge}" if knowledge else ""

        prompt = self.build_system_prompt(scenario=scenario, cefr_level=cefr) + extra
        chat_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in history[-10:]
            if m.get("role") in ("user", "assistant") and m.get("content")
        ]
        result = await self.call_llm(prompt, message, messages=chat_messages)
        if "response" not in result and "raw_response" in result:
            result["response"] = result["raw_response"]
        return AgentOutput(data=result, metadata={"agent": self.name})
