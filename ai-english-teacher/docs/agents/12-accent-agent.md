# 12. Accent Agent

| Field | Value |
|-------|-------|
| **Wave** | 2 |
| **Priority** | P2 |
| **Status** | `planned` |
| **LangGraph Node** | Voice Analysis Node |
| **Primary Model** | Acoustic classifier + GPT-4o-mini |
| **Owner** | AI Platform Team |

---

## Purpose

Assess accent quality, regional influence, and recommend targeted practice.

## Responsibilities

- Accent classification
- Intelligibility scoring
- Regional pattern identification
- Practice drill recommendations

## Inputs

```json
{"audio_features":{},"transcript":"...","target_accent":"en-US"}
```

## Outputs

```json
{"accent_profile":"South Asian English","intelligibility":88,"drills":["th sound","r-coloring"]}
```

## Tools

Acoustic model, drill library

## Models

| Task | Model | Fallback |
|------|-------|----------|
| Primary | Custom classifier | GPT-4o-mini |

## Memory

PostgreSQL (accent progress)

## Prompt (Summary)

```
Describe accent traits neutrally; focus on intelligibility not judgment.
```

## Workflows

Pronunciation Agent → Accent Agent → practice plan

## KPIs

- Intelligibility inter-rater agreement > 0.75

## Failure Handling

Insufficient audio → request longer sample

## Observability

Accent distribution analytics (aggregated)

## Security

Avoid stereotyping language in outputs

## Test Cases

- Non-native patterns identified
- Encouraging tone in feedback

## Implementation Notes

Not implemented.
