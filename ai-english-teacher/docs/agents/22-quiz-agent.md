# 22. Quiz Agent

| Field | Value |
|-------|-------|
| **Wave** | 4 |
| **Priority** | P1 |
| **Status** | `planned` |
| **LangGraph Node** | Learning Node |
| **Primary Model** | GPT-4o |
| **Owner** | AI Platform Team |

---

## Purpose

Generate MCQs, adaptive questions, and case studies tailored to student level.

## Responsibilities

- MCQ and open-ended generation
- Adaptive difficulty
- Distractor quality
- Anti-repeat from recent quizzes

## Inputs

```json
{"topic":"conditionals","level":"B1","count":5,"weak_topics":["type 2"]}
```

## Outputs

```json
{"questions":[{"type":"mcq","stem":"...","options":[],"answer":1,"bloom":"apply"}]}
```

## Tools

RAG Agent, question bank, randomization

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | GPT-4o | GPT-4o-mini |

## Memory

PostgreSQL (question history)

## Prompt (Summary)

```
Generate valid MCQs with one clear answer and plausible distractors.
```

## Workflows

Weak Topic Agent → Quiz Agent → student UI

## KPIs

- Teacher approval rate > 90%
- Duplicate rate < 5%

## Failure Handling

Invalid JSON → regenerate once; still fail → use bank fallback

## Observability

Question difficulty calibration

## Security

No leaked answers in prompts/logs

## Test Cases

- 5 questions returned
- Difficulty adapts after correct streak

## Implementation Notes

Not implemented.
