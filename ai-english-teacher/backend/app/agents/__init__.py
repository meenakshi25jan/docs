from app.agents.base import AgentInput, AgentOutput, BaseAgent
from app.scoring.engine import aggregate_scores, calculate_grammar_score, calculate_vocabulary_score


class GrammarAgent(BaseAgent):
    name = "grammar"
    system_prompt_template = """You are an expert English grammar analyst.
Analyze the text for grammar errors. Categories: tense, subject-verb agreement,
articles, prepositions, word order, conditionals, modals, punctuation.
Learner CEFR level: {cefr_level}
Return JSON: {{"score": float, "accuracy": float, "complexity": float, "error_density": float,
"errors": [{{"text": str, "correction": str, "category": str, "severity": str}}],
"cefr_estimate": str, "feedback": str}}"""

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        text = self.sanitize(input_data.context.get("text", ""))
        cefr = input_data.context.get("cefr_level", "B1")
        prompt = self.build_system_prompt(cefr_level=cefr)
        result = await self.call_llm(prompt, f"Analyze grammar:\n{text}")

        score = calculate_grammar_score(
            result.get("accuracy", result.get("score", 70)),
            result.get("complexity", 65),
            result.get("error_density", 20),
        )
        result["score"] = score
        return AgentOutput(data=result)


class VocabularyAgent(BaseAgent):
    name = "vocabulary"
    system_prompt_template = """You are an English vocabulary assessment specialist.
Evaluate vocabulary range, accuracy, and sophistication.
Learner level: {cefr_level}
Return JSON: {{"range_score": float, "accuracy": float, "sophistication": float,
"unique_words": int, "total_words": int, "recommended_words": [str],
"feedback": str}}"""

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        text = self.sanitize(input_data.context.get("text", ""))
        prompt = self.build_system_prompt(cefr_level=input_data.context.get("cefr_level", "B1"))
        result = await self.call_llm(prompt, f"Evaluate vocabulary:\n{text}")
        score = calculate_vocabulary_score(
            result.get("range_score", 70),
            result.get("accuracy", 70),
            result.get("sophistication", 65),
        )
        result["score"] = score
        return AgentOutput(data=result)


class AssessmentAgent(BaseAgent):
    name = "assessment"
    system_prompt_template = """You are an English proficiency assessment specialist.
Evaluate the learner's response for skill: {skill} at {difficulty} level.
Scoring: Accuracy(40%), Range(30%), Appropriateness(20%), Fluency(10%).
Return JSON: {{"score": float, "dimension_scores": {{}}, "cefr_estimate": str,
"errors": [], "feedback": str}}"""

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        skill = input_data.context.get("skill", "grammar")
        difficulty = input_data.context.get("difficulty", "B1")
        responses = input_data.context.get("responses", [])
        prompt = self.build_system_prompt(skill=skill, difficulty=difficulty)
        user_msg = f"Skill: {skill}\nResponses: {responses}"
        result = await self.call_llm(prompt, user_msg)

        skill_scores = {skill: result.get("score", 70)}
        estimate = aggregate_scores(skill_scores)
        result.update({
            "ielts_estimate": estimate.ielts,
            "pte_estimate": estimate.pte,
            "confidence": estimate.confidence,
        })
        return AgentOutput(data=result)


class TeacherAgent(BaseAgent):
    name = "teacher"
    system_prompt_template = """You are an expert English teacher conducting a {scenario} role-play.
Learner CEFR: {cefr_level}. Known weaknesses: {error_summary}.
Stay in character. Use language at {cefr_level} with slight challenge.
Gently correct errors inline. Ask follow-up questions.
Return JSON: {{"response": str, "grammar_corrections": [], "vocabulary_introduced": [],
"difficulty_adjustment": "maintain", "encouragement": str}}"""

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        scenario = input_data.context.get("scenario", "general_conversation")
        cefr = input_data.context.get("cefr_level", "B1")
        errors = input_data.context.get("recent_errors", [])
        history = input_data.context.get("message_history", [])
        user_message = self.sanitize(input_data.context.get("message", ""))

        prompt = self.build_system_prompt(
            scenario=scenario, cefr_level=cefr, error_summary=", ".join(errors[:5]) or "none"
        )
        chat_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in history[-10:]
            if m.get("role") in ("user", "assistant") and m.get("content")
        ]
        result = await self.call_llm(prompt, user_message, messages=chat_messages)
        return AgentOutput(data=result)


class WritingAgent(BaseAgent):
    name = "writing"
    system_prompt_template = """Score this IELTS Writing Task 2 essay.
Task Achievement(25%), Coherence(25%), Lexical Resource(25%), Grammar(25%).
Return JSON: {{"task_achievement": float, "coherence": float, "lexical_resource": float,
"grammatical_range": float, "overall_score": float, "strengths": [str],
"improvements": [str], "errors": [{{"text": str, "correction": str, "category": str}}]}}"""

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        from app.scoring.engine import calculate_writing_score, aggregate_scores

        prompt_text = input_data.context.get("prompt", "")
        content = self.sanitize(input_data.context.get("content", ""))
        result = await self.call_llm(
            self.system_prompt_template,
            f"Prompt: {prompt_text}\n\nEssay ({len(content.split())} words):\n{content}",
        )
        overall = calculate_writing_score(
            result.get("task_achievement", 70),
            result.get("coherence", 70),
            result.get("lexical_resource", 70),
            result.get("grammatical_range", 70),
        )
        result["overall_score"] = overall
        estimate = aggregate_scores({"writing": overall})
        result["estimates"] = {"cefr": estimate.cefr, "ielts": estimate.ielts, "pte": estimate.pte}
        return AgentOutput(data=result)


class SpeakingAgent(BaseAgent):
    name = "speaking"
    system_prompt_template = """Analyze spoken English transcript.
Score: pronunciation(30%), fluency(25%), grammar(25%), vocabulary(20%).
Return JSON: {{"pronunciation": float, "fluency": float, "grammar": float,
"vocabulary": float, "overall_score": float, "filler_words": [str], "feedback": str}}"""

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        from app.scoring.engine import calculate_speaking_score, aggregate_scores

        transcript = self.sanitize(input_data.context.get("transcript", ""))
        result = await self.call_llm(self.system_prompt_template, f"Transcript:\n{transcript}")
        overall = calculate_speaking_score(
            result.get("pronunciation", 70),
            result.get("fluency", 70),
            result.get("grammar", 70),
            result.get("vocabulary", 70),
        )
        result["overall_score"] = overall
        estimate = aggregate_scores({"speaking": overall})
        result["estimates"] = {"cefr": estimate.cefr, "ielts": estimate.ielts, "pte": estimate.pte}
        return AgentOutput(data=result)


class LearningPlannerAgent(BaseAgent):
    name = "planner"
    system_prompt_template = """Create a {duration_weeks}-week learning plan.
Learner: {cefr_level}, target: {target_exam} band {target_score}.
Scores: {skill_scores}. Errors: {error_patterns}. Hours/week: {hours_per_week}.
Return JSON: {{"goals": [str], "weeks": [{{"week": int, "focus": str, "items": [{{"skill": str, "type": str, "description": str, "priority": int}}]}}]}}"""

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        ctx = input_data.context
        prompt = self.build_system_prompt(
            duration_weeks=ctx.get("duration_weeks", 4),
            cefr_level=ctx.get("cefr_level", "B1"),
            target_exam=ctx.get("target_exam", "ielts"),
            target_score=ctx.get("target_score", 7.0),
            skill_scores=str(ctx.get("skill_scores", {})),
            error_patterns=str(ctx.get("error_patterns", [])),
            hours_per_week=ctx.get("hours_per_week", 5),
        )
        result = await self.call_llm(prompt, "Generate the learning plan.")
        return AgentOutput(data=result)


class ProgressTrackerAgent(BaseAgent):
    name = "progress"
    system_prompt_template = """Analyze learner progress over {period_days} days.
Return JSON: {{"improving_skills": [str], "declining_skills": [str], "plateau_areas": [str],
"recommended_focus": [str], "projected_30d": {{"cefr": str, "ielts": float}},
"projected_90d": {{"cefr": str, "ielts": float}}}}"""

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        ctx = input_data.context
        prompt = self.build_system_prompt(period_days=ctx.get("period_days", 30))
        result = await self.call_llm(
            prompt,
            f"Snapshots: {ctx.get('snapshots', [])}\nErrors: {ctx.get('errors', [])}",
        )
        return AgentOutput(data=result)


class ReportGeneratorAgent(BaseAgent):
    name = "report"
    system_prompt_template = """Generate a {report_type} report.
Return JSON: {{"executive_summary": str, "skill_breakdown": {{}}, "error_analysis": [str],
"recommendations": [str], "next_steps": [str]}}"""

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        ctx = input_data.context
        prompt = self.build_system_prompt(report_type=ctx.get("report_type", "progress_summary"))
        result = await self.call_llm(
            prompt,
            f"Learner data: {ctx.get('progress_data', {})}",
        )
        return AgentOutput(data=result)


class GrammarTeacherAgent(BaseAgent):
    """Voice-friendly grammar teacher for school students (grades 5–12)."""

    name = "grammar_teacher"
    system_prompt_template = """You are a kind, patient English grammar teacher for Grade {grade} students (ages 10–18).
Current lesson: {lesson_title}
Grammar rule: {lesson_rule}

Use simple, clear English appropriate for the grade. Be encouraging — never harsh.
When correcting, explain WHY the rule applies in one short sentence.

Return JSON:
{{
  "response": "what you say to the student (2-4 short sentences, speakable aloud)",
  "rule_explained": "one simple explanation of the grammar rule with an example",
  "corrections": [{{"wrong": str, "correct": str, "tip": str}}],
  "practice_prompt": "one sentence for the student to say next",
  "encouragement": "short positive message",
  "score_comment": "Great / Good try / Keep practicing"
}}"""

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        ctx = input_data.context
        grade = ctx.get("grade", 8)
        mode = ctx.get("mode", "practice")

        if mode == "intro":
            prompt = self.build_system_prompt(
                grade=grade,
                lesson_title=ctx.get("lesson_title", "Grammar"),
                lesson_rule=ctx.get("lesson_rule", ""),
            )
            user_msg = (
                f"Give a friendly spoken introduction to this grammar lesson for Grade {grade}. "
                "Explain the rule simply with one example. End with a practice_prompt asking "
                "the student to make one sentence using the rule."
            )
        else:
            errors = ctx.get("grammar_errors", [])
            prompt = self.build_system_prompt(
                grade=grade,
                lesson_title=ctx.get("lesson_title", "Grammar"),
                lesson_rule=ctx.get("lesson_rule", ""),
            )
            user_msg = (
                f"Student said: {ctx.get('student_text', '')}\n"
                f"Grammar score: {ctx.get('grammar_score', 0)}\n"
                f"Detected errors: {errors}\n"
                "Correct gently, teach the rule, and give one new practice sentence."
            )

        result = await self.call_llm(prompt, user_msg)
        return AgentOutput(data=result, metadata={"agent": self.name})


AGENT_REGISTRY: dict[str, BaseAgent] = {
    "teacher": TeacherAgent(),
    "assessment": AssessmentAgent(),
    "grammar": GrammarAgent(),
    "grammar_teacher": GrammarTeacherAgent(),
    "vocabulary": VocabularyAgent(),
    "writing": WritingAgent(),
    "speaking": SpeakingAgent(),
    "planner": LearningPlannerAgent(),
    "progress": ProgressTrackerAgent(),
    "report": ReportGeneratorAgent(),
}
