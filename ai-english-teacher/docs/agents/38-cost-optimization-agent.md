# 38. Cost Optimization Agent

| Field | Value |
|-------|-------|
| **Wave** | 6 |
| **Priority** | P1 |
| **Status** | `planned` |
| **LangGraph Node** | Governance Node |
| **Primary Model** | Routing rules + usage analytics |
| **Owner** | AI Platform Team |

---

## Purpose

Dynamically route requests to the cheapest capable model per task type.

## Responsibilities

- Model routing by intent and complexity
- Token budget enforcement
- Cost attribution per tenant/session
- A/B cost vs quality tradeoffs

## Inputs

```json
{"intent":"greeting","complexity":"low","tenant_budget_remaining":10.0}
```

## Outputs

```json
{"model":"gpt-4o-mini","reason":"simple greeting","estimated_cost":0.0001}
```

## Tools

Usage DB, model price table, Orchestrator hook

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | Routing rules | GPT-4o-mini default |

## Memory

PostgreSQL (usage and budgets)

## Prompt (Summary)

```
N/A — routing agent
```

## Workflows

Orchestrator → Cost Optimization → LLM provider

## KPIs

- 30–60% LLM cost reduction
- Quality regression < 5% on eval

## Failure Handling

Budget exceeded → downgrade or queue

## Observability

Cost per agent, per tenant dashboards

## Security

Prevent cost-based denial of service across tenants

## Test Cases

- Greeting → mini model
- Complex essay → full model

## Implementation Notes

Not implemented. Current: single model per AI_PROVIDER in config.
