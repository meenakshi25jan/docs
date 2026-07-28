# Agent Governance Layer

Enterprise deployments require explicit governance over who can ship agents, what runs in production, and full auditability of every execution.

## Agent Registry

Central catalog of all agents (human- and machine-readable).

### Registry Entry Schema

```json
{
  "name": "TeacherAgent",
  "id": "05",
  "version": "2.1.0",
  "wave": 1,
  "owner": "ai-platform@school.edu",
  "environment": "production",
  "prompt_version": "2.1",
  "tools": ["RAG", "Memory", "openai_chat"],
  "models": {"primary": "gpt-4o", "fallback": "gpt-4o-mini"},
  "sla": {"p95_latency_ms": 3000, "availability": 0.995},
  "approved_at": "2026-07-15T10:00:00Z",
  "approved_by": "platform-lead@school.edu"
}
```

### Storage

- **Git** — Specs in `docs/agents/` (source of truth for design)
- **Database** — Runtime registry in PostgreSQL `agent_registry` table
- **Runtime** — `AGENT_REGISTRY` dict in `backend/app/agents/` (current V1)

## Agent Approval Pipeline

```
Development
    ↓
Validation (automated eval + unit tests)
    ↓
Human Review (security, pedagogy, compliance)
    ↓
Staging (shadow traffic or internal users)
    ↓
Production (tagged release)
```

### Gate Criteria

| Stage | Requirements |
|-------|----------------|
| Validation | Unit tests pass; offline eval thresholds met |
| Human Review | Spec updated; security sign-off for Wave 6 agents |
| Staging | 48h soak; no P0 incidents |
| Production | Registry entry approved; rollback plan documented |

### Roles

| Role | Can approve |
|------|-------------|
| Agent owner | Development → Validation |
| Platform lead | Staging → Production |
| Security / DPO | Wave 6 agents (32–38) |
| Pedagogy lead | Teaching agents (04, 05, 19–25) |

## Agent Audit Trail

Every agent execution records an immutable event (Privacy Agent redacts PII in stored payloads).

```json
{
  "trace_id": "tr_abc123",
  "timestamp": "2026-07-26T01:24:00Z",
  "tenant_id": "school-uuid",
  "session_id": "session-uuid",
  "student_id_hash": "sha256:...",
  "agent": "TeacherAgent",
  "agent_version": "2.1.0",
  "prompt_version": "2.1",
  "input_hash": "sha256:...",
  "output_hash": "sha256:...",
  "model": "gpt-4o",
  "tokens_in": 450,
  "tokens_out": 120,
  "cost_usd": 0.002,
  "latency_ms": 1200,
  "routing_path": ["Orchestrator", "ContextManager", "TeacherAgent", "HallucinationChecker"],
  "policy_checks": ["Moderation:pass", "Policy:pass", "Privacy:redacted"],
  "status": "success"
}
```

### Retention

| Data | Retention | Regulation |
|------|-----------|------------|
| Audit metadata | 7 years | SOC2, FERPA |
| Input/output hashes | 90 days | Operational |
| Full prompts (staging only) | 30 days | Debug |

## Change Management

### Versioning Rules

- **Patch** (2.1.0 → 2.1.1) — Bug fix, no prompt change
- **Minor** (2.1.0 → 2.2.0) — Prompt or tool change; re-run offline eval
- **Major** (2.x → 3.0) — Breaking I/O contract; human review required

### Rollback

1. Orchestrator reads `agent_version` from registry
2. On error rate spike, flip traffic to previous version tag (no redeploy)
3. Post-incident: Compliance Agent exports audit slice for review

## Security & Compliance Integration

| Agent | Governance role |
|-------|-----------------|
| 32 Moderation | Blocks unsafe I/O before/after orchestration |
| 35 Privacy | Redacts PII in audit logs and exports |
| 36 Policy | Enforces tenant rules per request |
| 37 Compliance | DSAR, delete propagation, compliance reports |
| 38 Cost Optimization | Budget caps per tenant; prevents runaway spend |

## Implementation Roadmap

1. **Now** — Structured logging in `openai_client.py` with `trace_id`
2. **Wave 1** — `agent_executions` table + Orchestrator emits events
3. **Wave 6** — Full approval API + admin UI for registry
4. **Enterprise** — SOC2 evidence exports from Compliance Agent

## Related Documents

- [00-MASTER-BLUEPRINT.md](./00-MASTER-BLUEPRINT.md)
- [40-mlops-layer.md](./40-mlops-layer.md)
- Individual agent specs: [README.md](./README.md)
