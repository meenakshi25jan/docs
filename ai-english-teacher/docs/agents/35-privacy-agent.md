# 35. Privacy Agent

| Field | Value |
|-------|-------|
| **Wave** | 6 |
| **Priority** | P0 |
| **Status** | `planned` |
| **LangGraph Node** | Safety Gate Node |
| **Primary Model** | NER + regex + GPT-4o-mini |
| **Owner** | AI Platform Team |

---

## Purpose

Detect PII and sensitive information in logs, prompts, and exports.

## Responsibilities

- PII detection and redaction
- Sensitive data classification
- Log scrubbing
- DSAR delete orchestration

## Inputs

```json
{"text":"...","context":"log|prompt|export","student_id":"uuid"}
```

## Outputs

```json
{"redacted_text":"...","pii_found":["email"],"action":"redact"}
```

## Tools

Presidio or similar NER, regex patterns

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | NER model | regex |

## Memory

Audit log only (redacted)

## Prompt (Summary)

```
Identify PII types; never echo raw PII in output.
```

## Workflows

Pre-log → Privacy Agent → observability backend

## KPIs

- PII recall > 98%
- False redaction < 1%

## Failure Handling

Uncertain → redact aggressively

## Observability

PII detection counts (no raw values)

## Security

Core compliance component; pairs with Compliance Agent

## Test Cases

- Email redacted in logs
- Name in lesson example preserved if fictional

## Implementation Notes

Not implemented.
