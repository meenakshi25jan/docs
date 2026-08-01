import json
import re
from typing import Any

from app.services.grok_service import GrokService


class GrammarAgent:
    def __init__(self, llm: GrokService | None = None) -> None:
        self.llm = llm or GrokService()

    def _extract_json(self, text: str) -> dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if not match:
                raise ValueError("No valid JSON found in LLM response") from None
            return json.loads(match.group())

    async def correct(self, student_text: str) -> dict[str, Any]:
        system_prompt = """
You are a friendly English grammar teacher.

Your job:
1. Correct the student's English.
2. Explain the mistake simply.
3. Identify mistake categories.
4. Give a grammar score from 0 to 100.
5. Speak in a warm teacher-like tone.

Return ONLY valid JSON.

JSON format:
{
  "original_text": "",
  "corrected_text": "",
  "explanation": "",
  "mistakes": [],
  "score": 0,
  "teacher_response": ""
}

Rules:
- Do not shame the student.
- Keep explanation simple.
- If the sentence is already correct, say it is correct.
- teacher_response should sound like a real teacher talking to the student.
"""
        user_prompt = f"Student sentence:\n{student_text}"
        response = await self.llm.chat(system_prompt, user_prompt)
        data = self._extract_json(response)

        required_keys = [
            "original_text",
            "corrected_text",
            "explanation",
            "mistakes",
            "score",
            "teacher_response",
        ]
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing key from LLM response: {key}")

        data["original_text"] = data.get("original_text") or student_text
        data["mistakes"] = data.get("mistakes") or []
        data["score"] = int(data.get("score", 0))
        return data
