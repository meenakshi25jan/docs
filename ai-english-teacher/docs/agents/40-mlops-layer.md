# MLOps Layer — Enterprise Requirement

Most multi-agent education platforms fail at scale without explicit MLOps. This layer sits alongside the 38 agents and governs models, prompts, evaluations, and experiments.

## Components

### Model Registry

Store and version:

- LLM deployments (Azure OpenAI, Groq, OpenAI)
- Embedding models
- Speech models (Whisper variants)
- Custom classifiers (accent, emotion)

**Recommended tools:** MLflow, Weights & Biases, or Azure ML Registry.

| Artifact | Example |
|----------|---------|
| Model name | `teacher-gpt-4o-prod` |
| Version | `2.1.0` |
| Prompt hash | `sha256:abc...` |
| Eval score | `teaching_quality: 4.2/5` |

### Prompt Registry

Version prompts per agent independently of code deploys.

```
agents/teacher/prompts/
  v1.0.txt
  v2.0.txt   ← A/B candidate
```

Link prompt version to audit trail (see [41-agent-governance.md](./41-agent-governance.md)).

## Offline Evaluation

Run before promoting agent or prompt versions to production.

| Metric | Agents | Target |
|--------|--------|--------|
| Teaching quality | 05 Teacher | Human rating > 4/5 |
| Pronunciation accuracy | 08 Pronunciation | r > 0.8 vs human |
| Quiz quality | 22 Quiz | Teacher approval > 90% |
| Hallucination rate | 33 Hallucination Checker | < 2% on gold set |
| Routing accuracy | 01 Orchestrator | > 95% |
| Grammar precision | 10 Grammar | > 90% |

### Eval Datasets

- `eval/teaching/` — lesson Q&A pairs with expert answers
- `eval/pronunciation/` — labeled audio clips
- `eval/safety/` — moderation edge cases
- `eval/rag/` — query → expected chunk IDs

### CI Integration

```yaml
# Example GitHub Actions step
- name: Offline agent eval
  run: python -m mlops.eval --agents teacher,moderation --fail-under 0.85
```

## Online Evaluation

Track production behavior continuously.

| Signal | Source | Action |
|--------|--------|--------|
| Student satisfaction | thumbs up/down | Alert if < 3.5 avg |
| Learning improvement | pre/post assessment delta | Weekly report |
| Completion rate | session funnel | Dashboard |
| Retention | D7/D30 return | Cohort analysis |
| Cost per session | Cost Optimization Agent | Budget alerts |

## A/B Testing Agent

Compare variants (prompts, models, routing) with statistical rigor.

### Example Experiment

| Arm | Teacher Prompt | Traffic |
|-----|----------------|---------|
| A (control) | `teacher/v1.0` | 50% |
| B (treatment) | `teacher/v2.0` | 50% |

**Primary metric:** Learning outcome (assessment delta after 7 days)  
**Guardrails:** Hallucination rate, moderation blocks, P95 latency

### Experiment Record

```json
{
  "experiment_id": "exp-teacher-prompt-2026-07",
  "agent": "TeacherAgent",
  "variants": ["v1.0", "v2.0"],
  "status": "running",
  "min_sample_size": 500,
  "started_at": "2026-07-01T00:00:00Z"
}
```

## Observability Stack

| Concern | Tool |
|---------|------|
| Traces | OpenTelemetry → Jaeger / Azure App Insights |
| Logs | Structured JSON; Privacy Agent scrubs PII |
| Metrics | Prometheus / Grafana |
| LLM calls | LangSmith or custom span per agent |

### Standard Span Attributes

```
agent.name=TeacherAgent
agent.prompt_version=2.1
llm.model=gpt-4o
llm.tokens_in=450
llm.tokens_out=120
llm.cost_usd=0.002
latency_ms=1200
```

## Deployment Environments

| Environment | Purpose | Agent approval |
|-------------|---------|----------------|
| development | Engineer local | None |
| validation | Automated eval | CI pass |
| staging | Human review | Required |
| production | Live students | Approved + tagged version |

## Implementation Roadmap

1. **Phase 1** — Log all LLM calls with agent name, model, cost (extend `openai_client.py`)
2. **Phase 2** — Prompt files on disk + version in audit trail
3. **Phase 3** — MLflow for eval runs on merge to `main`
4. **Phase 4** — A/B framework hooked to Orchestrator traffic split
