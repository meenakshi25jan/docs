# Enterprise AI Teaching Platform — Agent Specifications

V2.0 domain-driven agent architecture for the AI English Teacher platform. Each agent has a dedicated specification document following a common template.

## Quick Links

| Document | Description |
|----------|-------------|
| [00-MASTER-BLUEPRINT.md](./00-MASTER-BLUEPRINT.md) | Full V2.0 architecture, waves, and release plan |
| [40-mlops-layer.md](./40-mlops-layer.md) | Model registry, offline/online evaluation, A/B testing |
| [41-agent-governance.md](./41-agent-governance.md) | Agent registry, approval pipeline, audit trail |
| [_TEMPLATE.md](./_TEMPLATE.md) | Template for new agent specs |

## Implementation Waves

| Wave | Focus | Agents | Duration |
|------|-------|--------|----------|
| 1 | Foundation Platform | 01–07 | 6 weeks |
| 2 | Voice Intelligence | 08–13 | 8 weeks |
| 3 | Emotional Intelligence | 14–18 | 6 weeks |
| 4 | Learning Intelligence | 19–25 | 8 weeks |
| 5 | Educational Intelligence | 26–31 | 8 weeks |
| 6 | Enterprise Governance | 32–38 | 10 weeks |

## Agent Index

### Wave 1 — Foundation

| # | Agent | Status |
|---|-------|--------|
| 01 | [Orchestrator](./01-orchestrator-agent.md) | planned |
| 02 | [Session Manager](./02-session-manager-agent.md) | planned |
| 03 | [Context Manager](./03-context-manager-agent.md) | planned |
| 04 | [Conversation](./04-conversation-agent.md) | planned |
| 05 | [Teacher](./05-teacher-agent.md) | partial |
| 06 | [Memory](./06-memory-agent.md) | planned |
| 07 | [RAG](./07-rag-agent.md) | planned |

### Wave 2 — Voice Intelligence

| # | Agent | Status |
|---|-------|--------|
| 08 | [Pronunciation](./08-pronunciation-agent.md) | planned |
| 09 | [Fluency](./09-fluency-agent.md) | planned |
| 10 | [Grammar](./10-grammar-agent.md) | partial |
| 11 | [Vocabulary](./11-vocabulary-agent.md) | partial |
| 12 | [Accent](./12-accent-agent.md) | planned |
| 13 | [Speech Quality](./13-speech-quality-agent.md) | planned |

### Wave 3 — Emotional Intelligence

| # | Agent | Status |
|---|-------|--------|
| 14 | [Emotion Detection](./14-emotion-detection-agent.md) | planned |
| 15 | [Confidence](./15-confidence-agent.md) | planned |
| 16 | [Engagement](./16-engagement-agent.md) | planned |
| 17 | [Stress Detection](./17-stress-detection-agent.md) | planned |
| 18 | [Motivation](./18-motivation-agent.md) | planned |

### Wave 4 — Learning Intelligence

| # | Agent | Status |
|---|-------|--------|
| 19 | [Assessment](./19-assessment-agent.md) | partial |
| 20 | [Bloom Taxonomy](./20-bloom-taxonomy-agent.md) | planned |
| 21 | [Weak Topic](./21-weak-topic-agent.md) | planned |
| 22 | [Quiz](./22-quiz-agent.md) | planned |
| 23 | [Homework](./23-homework-agent.md) | planned |
| 24 | [Recommendation](./24-recommendation-agent.md) | partial |
| 25 | [Curriculum](./25-curriculum-agent.md) | planned |

### Wave 5 — Educational Intelligence

| # | Agent | Status |
|---|-------|--------|
| 26 | [Student Profile](./26-student-profile-agent.md) | planned |
| 27 | [Goal Tracker](./27-goal-tracker-agent.md) | planned |
| 28 | [Progress](./28-progress-agent.md) | partial |
| 29 | [Parent Report](./29-parent-report-agent.md) | planned |
| 30 | [Teacher Dashboard](./30-teacher-dashboard-agent.md) | planned |
| 31 | [Analytics](./31-analytics-agent.md) | planned |

### Wave 6 — Enterprise Governance

| # | Agent | Status |
|---|-------|--------|
| 32 | [Moderation](./32-moderation-agent.md) | planned |
| 33 | [Hallucination Checker](./33-hallucination-checker-agent.md) | planned |
| 34 | [Citation](./34-citation-agent.md) | planned |
| 35 | [Privacy](./35-privacy-agent.md) | planned |
| 36 | [Policy](./36-policy-agent.md) | planned |
| 37 | [Compliance](./37-compliance-agent.md) | planned |
| 38 | [Cost Optimization](./38-cost-optimization-agent.md) | planned |

## Current V1 Implementation

The live app (`backend/app/agents/`) has 9 agent stubs in `AGENT_REGISTRY`:

`teacher`, `assessment`, `grammar`, `vocabulary`, `writing`, `speaking`, `planner`, `progress`, `report`

Wave 1 (Orchestrator, Session Manager, Context Manager, Memory, RAG) and LangGraph orchestration are the next implementation priority.

**Wave 1 status (implemented):** LangGraph pipeline in `backend/app/orchestration/` — Orchestrator, Session Manager (Redis + memory fallback), Context Manager, Conversation Agent, Memory Agent, RAG Agent (keyword MVP), Moderation gate, Cost router. Conversations API uses `run_conversation_turn()`.

## Spec Document Structure

Every agent spec (`NN-name-agent.md`) includes:

- Purpose, Responsibilities
- Inputs, Outputs (JSON)
- Tools, Models, Memory
- Prompt summary, Workflows
- KPIs, Failure Handling, Observability, Security
- Test Cases, Implementation Notes

## Regenerating Specs

```bash
cd ai-english-teacher/docs/agents
python3 generate_agents.py   # writes 07–38; skips existing 01–06
```
