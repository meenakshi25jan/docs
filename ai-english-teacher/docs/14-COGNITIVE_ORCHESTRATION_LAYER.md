# Layer 1 — Cognitive Orchestration Layer

The **Cognitive Orchestrator** is the executive controller of the platform. It does not teach, analyze grammar, or generate pedagogy directly. It coordinates events, tools, memory, agents, workflows, and LLM routing before invoking the **Teacher Brain**.

## Architecture

```text
Voice / Text Input
      │
      ▼
Cognitive Orchestrator (`app/cognitive/orchestrator.py`)
      │
      ├── Intent Classifier
      ├── Event Router
      ├── Workflow Manager
      ├── Tool Router
      ├── Memory Router
      ├── Agent Planner
      ├── Web Intelligence Gateway
      ├── Policy Engine
      ├── LLM Router
      ├── Context Builder
      ├── State Manager (session)
      └── Observability
              │
              ▼
        Teacher Brain (TeacherAgent / ConversationAgent)
```

## Module map

| Module | Responsibility |
|--------|----------------|
| `events.py` | Event types (`USER_SPOKE`, `LESSON_FINISHED`, …) |
| `intent_classifier.py` | Route request class (grammar explain, web, scenario, …) |
| `tool_router.py` | Select deterministic tools vs LLM |
| `memory_router.py` | Query conversation, learning, profile memories |
| `agent_planner.py` | Invoke only required specialists |
| `workflow_manager.py` | Predefined step sequences per intent |
| `context_builder.py` | Unified context for Teacher Brain |
| `policy_engine.py` | Token/latency/tool policy |
| `llm_router.py` | Model tier selection |
| `web_gateway.py` | External knowledge classification + search stub |
| `tool_executor.py` | Run coaches, tools, Teacher Brain |
| `session_lifecycle.py` | Lesson pause/resume/end |
| `failure_recovery.py` | Fallbacks when tools fail |
| `observability.py` | Trace latency, tools, agents |
| `state.py` | Shared cognitive state slices |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `COGNITIVE_ORCHESTRATION_ENABLED` | `true` | Use Layer 1 vs legacy LangGraph |

## Integration points

- `orchestration/runner.py` — text turns route through `process_cognitive_turn` when enabled
- `orchestration/voice/voice_turn.py` — voice analysis → cognitive turn with precomputed coaches

## Event examples

```python
from app.cognitive.events import CognitiveEvent, EventType

event = CognitiveEvent(
    type=EventType.USER_SPOKE,
    session_id="...",
    learner_id="...",
    payload={"message": "Explain present perfect", "scenario": "everyday"},
)
```

## Web search policy

Web search is invoked only when intent is `web_knowledge` or message matches current-affairs patterns. Grammar correction, pronunciation, lesson memory, and vocabulary review **never** call web search.

## Related

- `docs/13-VOICE_FIRST_PRD_V2.md` — product vision
- `RUNBOOK.md` — deploy and smoke tests
