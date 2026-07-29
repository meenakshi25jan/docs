# AI English Teacher — Complete Architecture

> **C4 model**, agent orchestration flows, data architecture, and deployment plans for all environments ($0 hobby → enterprise).

| Live URLs | |
|-----------|---|
| Web | https://ai-english-teacher-web.onrender.com |
| API | https://ai-english-teacher-api.onrender.com |
| API Docs | https://ai-english-teacher-api.onrender.com/docs |

**Related docs:** [RUNBOOK.md](../RUNBOOK.md) · [Master Blueprint](agents/00-MASTER-BLUEPRINT.md) · [System Architecture](02-SYSTEM_ARCHITECTURE.md)

---

## Table of Contents

1. [C4 Level 1 — System Context](#1-c4-level-1--system-context)
2. [C4 Level 2 — Containers](#2-c4-level-2--containers)
3. [C4 Level 3 — Backend Components](#3-c4-level-3--backend-components)
4. [Agent Registry (38-Agent Roadmap)](#4-agent-registry-38-agent-roadmap)
5. [Conversation Agent Flow (LangGraph)](#5-conversation-agent-flow-langgraph)
6. [Voice Analysis Pipeline](#6-voice-analysis-pipeline)
7. [Grammar Class Flow](#7-grammar-class-flow)
8. [Assessment & Writing Flows](#8-assessment--writing-flows)
9. [Multi-Tenancy & Security](#9-multi-tenancy--security)
10. [Data Architecture](#10-data-architecture)
11. [LLM Provider Resolution](#11-llm-provider-resolution)
12. [Deployment Plans](#12-deployment-plans)
13. [Environment Variable Matrix](#13-environment-variable-matrix)
14. [Ports & Network Reference](#14-ports--network-reference)

---

## 1. C4 Level 1 — System Context

Who uses the system and what external systems it connects to.

```mermaid
C4Context
    title System Context — AI English Teacher

    Person(student, "Student", "Practices English via chat, voice, grammar lessons, assessments")
    Person(teacher, "Teacher", "Views class progress and learner analytics")
    Person(admin, "Admin", "Manages tenant/school configuration")

    System(aet, "AI English Teacher Platform", "Multi-tenant AI English teaching: role-play, voice analysis, grammar class, CEFR/IELTS scoring")

    System_Ext(groq, "Groq / OpenAI API", "LLM chat + Whisper STT")
    System_Ext(azure, "Azure OpenAI", "Optional Copilot / enterprise LLM")
    System_Ext(ollama, "Ollama", "Self-hosted LLM on Oracle VM")
    System_Ext(neon, "Neon PostgreSQL", "Database + pgvector RAG")
    System_Ext(redis, "Redis", "Session cache (Oracle VM / optional)")
    System_Ext(render, "Render.com", "Hosts web + API (free tier)")
    System_Ext(play, "Google Play", "Android app distribution")

    Rel(student, aet, "HTTPS — web browser or mobile app")
    Rel(teacher, aet, "HTTPS — dashboard")
    Rel(admin, aet, "HTTPS — admin dashboard")
    Rel(aet, groq, "HTTPS — chat + transcription")
    Rel(aet, azure, "HTTPS — optional LLM")
    Rel(aet, ollama, "HTTP — VM only")
    Rel(aet, neon, "SSL PostgreSQL")
    Rel(aet, redis, "TCP — sessions")
    Rel(aet, render, "Deployed on")
    Rel(student, play, "Installs mobile app")
```

### Actors

| Actor | Channels | Primary features |
|-------|----------|------------------|
| **Student** | Web, Android (Expo) | Role-play chat, voice practice, grammar class (grades 5–12), placement test |
| **Teacher** | Web dashboard | Class overview, learner progress |
| **Admin** | Web dashboard | Tenant management, usage stats |

---

## 2. C4 Level 2 — Containers

Major deployable units and how they communicate.

### 2A. Production — Render + Neon ($0)

```mermaid
flowchart TB
    subgraph Clients
        BR[Browser<br/>Chrome / Edge]
        MOB[Android App<br/>Expo React Native]
    end

    subgraph Render["Render.com (Oregon)"]
        WEB["ai-english-teacher-web<br/>Next.js 15 :3000<br/>Static pages + API proxy"]
        API["ai-english-teacher-api<br/>FastAPI + Uvicorn :$PORT<br/>LangGraph orchestration"]
    end

    subgraph External["External Services"]
        NEON[(Neon PostgreSQL<br/>pgvector + RLS)]
        GROQ[Groq API<br/>llama-3.1-8b + Whisper]
    end

    BR -->|HTTPS| WEB
    BR -->|Web Speech API<br/>STT/TTS local| BR
    MOB -->|HTTPS /api/v1| API
    WEB -->|rewrite /api/v1/*| API
    API -->|SSL :5432| NEON
    API -->|HTTPS| GROQ
```

### 2B. Self-Hosted — Oracle Cloud VM ($0)

```mermaid
flowchart TB
    subgraph Clients
        BR[Browser]
        MOB[Android App]
    end

    subgraph OCI["Oracle VM (Always Free A1)"]
        NGX[nginx :80/443]
        FE[Next.js :3000]
        BE[FastAPI :8000]
        RD[(Redis :6379)]
        OL[Ollama :11434]
        NGX --> FE
        NGX -->|/api/v1| BE
        BE --> RD
        BE --> OL
    end

    NEON[(Neon PostgreSQL)]

    BR --> NGX
    MOB --> NGX
    BE --> NEON
```

### Container Summary

| Container | Technology | Responsibility |
|-----------|------------|----------------|
| **Web Frontend** | Next.js 15, React, Tailwind | UI pages, same-origin API proxy (`/api/v1` → API) |
| **Mobile App** | Expo React Native | Direct API calls, JWT in SecureStore |
| **Backend API** | FastAPI, SQLAlchemy async, LangGraph | Auth, orchestration, agents, scoring |
| **PostgreSQL** | Neon (managed) | Tenants, users, conversations, pgvector RAG, voice analyses |
| **Redis** | Optional (OCI) | Session state for LangGraph Session Manager |
| **LLM** | Groq / Azure / Ollama / Mock | Chat completions + Whisper transcription |

---

## 3. C4 Level 3 — Backend Components

Internal structure of the FastAPI backend (`backend/app/`).

```mermaid
flowchart TB
    subgraph API["API Layer (api/v1/)"]
        AUTH[auth.py]
        CONV[conversations.py]
        ASSESS[assessments.py]
        VOICE[voice.py]
        GRAMMAR[grammar_lessons.py]
        EXT[extended.py<br/>writing, plans, reports, dashboard]
    end

    subgraph ORCH["Orchestration (orchestration/)"]
        GRAPH[graph.py<br/>LangGraph 8-node pipeline]
        RUNNER[runner.py]
        ORC[orchestrator.py]
        SESS[session_manager.py]
        CTX[context_manager.py]
        MEM_A[memory_agent.py]
        RAG_A[rag_agent.py]
        MOD[moderation.py]
        COST[cost_router.py]
        VP[voice/pipeline.py]
    end

    subgraph AGENTS["Agent Registry (agents/)"]
        REG[AGENT_REGISTRY<br/>10 LLM agents]
        BASE[base.py<br/>BaseAgent]
    end

    subgraph SVC["Services"]
        AI[ai/openai_client.py]
        EMB[embeddings.py]
        MEM_S[memory_store.py]
        KNOW[knowledge_store.py]
        TRANS[transcription.py]
        SCORE[scoring/engine.py]
        GCUR[grammar_curriculum.py]
    end

    subgraph CORE["Core"]
        DB[database.py<br/>async PG + RLS]
        SEC[security.py<br/>JWT]
        CFG[config.py]
    end

    CONV --> RUNNER --> GRAPH
    VOICE --> VP
    GRAMMAR --> VP
    GRAMMAR --> REG
    ASSESS --> REG
    EXT --> REG

    GRAPH --> ORC & SESS & CTX & MEM_A & RAG_A & MOD & COST
    GRAPH --> REG
    VP --> REG & TRANS & MEM_S

    REG --> BASE --> AI
    MEM_A --> MEM_S & SESS
    RAG_A --> KNOW --> EMB
    AUTH & CONV & ASSESS --> DB
    DB --> SEC
```

### API → Orchestration Mapping

| Endpoint | Orchestration path |
|----------|-------------------|
| `POST /conversations` | Full LangGraph pipeline |
| `POST /conversations/{id}/messages` | Full LangGraph pipeline |
| `POST /voice/analyze` | Voice pipeline (Wave 2) |
| `POST /grammar/practice` | Voice pipeline → GrammarTeacherAgent |
| `GET /grammar/intro` | GrammarTeacherAgent (direct) |
| `POST /assessments/{id}/submit` | AGENT_REGISTRY per skill (direct) |
| `POST /writing/submit` | WritingAgent (direct) |
| `POST /learning-plans` | LearningPlannerAgent (direct) |
| `POST /reports/generate` | ReportGeneratorAgent (direct) |

---

## 4. Agent Registry (38-Agent Roadmap)

The platform is designed for **38 agents in 6 waves**. Waves 1–2 are implemented; 3–6 are specified in `docs/agents/`.

```mermaid
flowchart LR
    subgraph W1["Wave 1 — Foundation ✅"]
        A01[01 Orchestrator]
        A02[02 Session Manager]
        A03[03 Context Manager]
        A04[04 Conversation]
        A05[05 Teacher]
        A06[06 Memory]
        A07[07 RAG]
    end

    subgraph W2["Wave 2 — Voice ✅"]
        A08[08 Pronunciation]
        A09[09 Fluency]
        A10[10 Grammar]
        A11[11 Vocabulary]
        A12[12 Accent]
        A13[13 Speech Quality]
    end

    subgraph W3["Wave 3 — Emotional 🔜"]
        A14[14 Emotion]
        A15[15 Confidence]
        A16[16 Engagement]
        A17[17 Stress]
        A18[18 Motivation]
    end

    subgraph W4["Wave 4 — Learning 🔜"]
        A19[19 Assessment]
        A20[20 Bloom Taxonomy]
        A21[21 Weak Topic]
        A22[22 Quiz]
        A23[23 Homework]
        A24[24 Recommendation]
        A25[25 Curriculum]
    end

    subgraph W5["Wave 5 — Educational 🔜"]
        A26[26 Student Profile]
        A27[27 Goal Tracker]
        A28[28 Progress]
        A29[29 Parent Report]
        A30[30 Teacher Dashboard]
        A31[31 Analytics]
    end

    subgraph W6["Wave 6 — Governance ⚡"]
        A32[32 Moderation ✅]
        A33[33 Hallucination]
        A34[34 Citation]
        A35[35 Privacy]
        A36[36 Policy]
        A37[37 Compliance]
        A38[38 Cost Optimization ✅]
    end

    A01 --> W1
    W1 --> W2
```

### Implemented LLM Agents (`AGENT_REGISTRY`)

| Key | Class | Role | Triggered by |
|-----|-------|------|--------------|
| `teacher` | `TeacherAgent` | Role-play English teacher with inline corrections | LangGraph, conversations |
| `grammar_teacher` | `GrammarTeacherAgent` | Grade 5–12 grammar lessons with voice | `/grammar/intro`, `/grammar/practice` |
| `grammar` | `GrammarAgent` | Grammar error detection + scoring | Voice pipeline, assessments |
| `vocabulary` | `VocabularyAgent` | Vocabulary range scoring | Voice pipeline, assessments |
| `writing` | `WritingAgent` | IELTS Writing Task 2 scoring | `/writing/submit` |
| `speaking` | `SpeakingAgent` | Transcript-based speaking analysis | Assessments |
| `assessment` | `AssessmentAgent` | General proficiency scoring | Assessments (fallback) |
| `planner` | `LearningPlannerAgent` | Multi-week learning plans | `/learning-plans` |
| `progress` | `ProgressTrackerAgent` | Progress trend analysis | *(registry only)* |
| `report` | `ReportGeneratorAgent` | Executive summaries | `/reports/generate` |

---

## 5. Conversation Agent Flow (LangGraph)

Primary path for role-play chat (`/conversation`).

### 5A. Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Student
    participant Web as Next.js Web
    participant API as FastAPI
    participant LG as LangGraph Pipeline
    participant Mod as ModerationAgent
    participant Orch as OrchestratorAgent
    participant Mem as MemoryAgent
    participant RAG as RAGAgent
    participant Ctx as ContextManager
    participant Agent as Conversation/Teacher Agent
    participant LLM as Groq / Azure / Ollama
    participant PG as Neon PostgreSQL
    participant Redis as Redis (optional)

    Student->>Web: Type message / Start conversation
    Web->>API: POST /api/v1/conversations/{id}/messages
    API->>API: JWT → SET LOCAL app.tenant_id (RLS)
    API->>LG: run_conversation_turn()

    LG->>Mod: moderate_text(input)
    alt unsafe input
        Mod-->>LG: blocked
        LG-->>API: safe refusal message
    end

    LG->>Orch: classify_intent(message, scenario)
    Orch-->>LG: intent + next_agent (Conversation or Teacher)

    LG->>Mem: recall_memories(learner_id, query)
    Mem->>PG: vector search error_tracking + learner_memories
    Mem->>Redis: load session state
    Mem-->>LG: memories + recent_errors

    LG->>RAG: retrieve(message, scenario, top_k=3)
    RAG->>PG: pgvector cosine search on knowledge_chunks
    RAG-->>LG: curriculum snippets

    LG->>Ctx: build_enriched_context(history, errors, RAG, CEFR)
    Ctx-->>LG: enriched prompt context

    LG->>Agent: execute(enriched_context)
    Agent->>LLM: chat_completion_json(system + user prompt)
    LLM-->>Agent: JSON response + corrections
    Agent-->>LG: AgentOutput

    LG->>Mem: store_from_teacher_output(corrections, vocab)
    Mem->>PG: persist_mistake / persist_preference
    Mem->>Redis: merge_session(turn_count++)

    LG->>Mod: moderate_text(output)
    Mod-->>LG: safe response

    LG-->>API: final state + agent_path + trace_id
    API->>PG: save ConversationMessage
    API-->>Web: { response, corrections, metadata }
    Web-->>Student: Display AI reply
```

### 5B. LangGraph Node Pipeline

```mermaid
flowchart TD
    START([Student Message]) --> N1

    N1[moderate_input<br/>ModerationAgent #32]
    N1 -->|blocked| END1([Safe refusal])
    N1 -->|safe| N2

    N2[orchestrate<br/>OrchestratorAgent #01<br/>+ CostRouter #38]
    N2 --> N3

    N3[recall_memory<br/>MemoryAgent #06]
    N3 --> N4

    N4[rag<br/>RAGAgent #07]
    N4 --> N5

    N5[build_context<br/>ContextManager #03]
    N5 --> N6

    N6[execute_agent<br/>ConversationAgent #04<br/>OR TeacherAgent #05]
    N6 --> N7

    N7[store_memory<br/>MemoryAgent #06<br/>+ SessionManager #02]
    N7 --> N8

    N8[moderate_output<br/>ModerationAgent #32]
    N8 --> END2([Response to Student])

    style N1 fill:#fef3c7
    style N8 fill:#fef3c7
    style N6 fill:#dbeafe
```

### 5C. Intent Routing Rules

`orchestrator.py:classify_intent()` decides which agent runs:

| Condition | Intent | Agent |
|-----------|--------|-------|
| Empty, greeting, or "Start the conversation." | `greeting` | `ConversationAgent` |
| Contains teaching keywords (explain, grammar, practice…) | `teaching` | `TeacherAgent` |
| Question with >4 words | `teaching` | `TeacherAgent` |
| Non-general scenario (job_interview, travel…) | `teaching` | `TeacherAgent` |
| Default | `conversation` | `ConversationAgent` |

---

## 6. Voice Analysis Pipeline

Triggered by `POST /api/v1/voice/analyze` and optionally by grammar practice with audio.

```mermaid
flowchart TD
    IN([Audio base64 OR transcript]) --> STT{Audio provided?}

    STT -->|Yes| WHISPER[transcription.py<br/>Groq Whisper large-v3-turbo]
    STT -->|No| TX[Use transcript]
    WHISPER --> TX

    TX --> SQ[13 Speech Quality Agent<br/>SNR, clipping heuristics]
    TX --> FL[09 Fluency Agent<br/>fillers, WPM]
    TX --> PR[08 Pronunciation Agent<br/>pattern heuristics]
    TX --> AC[12 Accent Agent<br/>intelligibility proxy]

    TX --> GR[10 Grammar Agent<br/>LLM JSON scoring]
    TX --> VO[11 Vocabulary Agent<br/>LLM JSON scoring]

    GR --> MEM[persist_mistake → error_tracking]
    SQ & FL & PR & AC & GR & VO --> SCORE[Weighted overall score<br/>25% each: fluency, pronunciation, grammar, vocab]
    SCORE --> SAVE[(voice_analyses table)]
    SAVE --> OUT([JSON report to client])
```

### Voice on Web vs Mobile

| Platform | STT (speech-to-text) | TTS (text-to-speech) | Server analysis |
|----------|---------------------|---------------------|-----------------|
| **Web** | Browser Web Speech API (`useVoice.ts`) | Browser `speechSynthesis` | Optional `POST /voice/analyze` |
| **Mobile** | Expo / device STT | Expo TTS | `POST /voice/analyze` with audio |
| **API** | Groq Whisper (`transcription.py`) | — | Full Wave 2 pipeline |

---

## 7. Grammar Class Flow

Grades 5–12 structured grammar lessons (`/grammar-class`).

```mermaid
sequenceDiagram
    actor Student
    participant Web as Grammar Class Page
    participant API as FastAPI
    participant GC as grammar_curriculum.py
    participant GT as GrammarTeacherAgent
    participant VP as Voice Pipeline
    participant LLM as Groq LLM

    Student->>Web: Select Grade 7
    Web->>API: GET /grammar/grades
    API->>GC: get_grade_info()
    GC-->>Web: grades list

    Student->>Web: Select lesson "Subject-Verb Agreement"
    Web->>API: GET /grammar/lessons?grade=7
    Web->>API: GET /grammar/intro?grade=7&lesson_id=sv_agreement
    API->>GT: execute(mode=intro)
    GT->>LLM: age-appropriate lesson intro
    LLM-->>Web: teacher intro + TTS

    Student->>Web: Speak/type practice sentence
    Web->>API: POST /grammar/practice {grade, lesson_id, transcript/audio}
    API->>VP: run_voice_analysis (if audio)
    VP-->>API: grammar + vocab scores
    API->>GT: execute(mode=practice, errors)
    GT->>LLM: friendly correction for grade level
    LLM-->>Web: correction + tip + score
```

**Curriculum source:** `backend/app/services/grammar_curriculum.py` — 24 lessons across grades 5–12, mapped to CEFR levels.

---

## 8. Assessment & Writing Flows

### Assessment Submit

```mermaid
flowchart LR
    A[POST /assessments/id/submit] --> B{skill type}
    B -->|grammar| G[GrammarAgent]
    B -->|vocabulary| V[VocabularyAgent]
    B -->|writing| W[WritingAgent]
    B -->|speaking| S[SpeakingAgent]
    B -->|other| F[AssessmentAgent]
    G & V & W & S & F --> SC[scoring/engine.py<br/>aggregate_scores + CEFR]
    SC --> DB[(assessment_results)]
```

### Writing & Reports (Direct Agent Calls)

| Flow | Path | Agent |
|------|------|-------|
| Essay scoring | `POST /writing/submit` | `WritingAgent` → IELTS band estimate |
| Learning plan | `POST /learning-plans` | `LearningPlannerAgent` → multi-week plan |
| Progress report | `POST /reports/generate` | `ReportGeneratorAgent` → PDF-ready summary |

---

## 9. Multi-Tenancy & Security

```mermaid
flowchart TD
    REQ[HTTP Request + JWT Bearer] --> JWT[security.py<br/>decode_token]
    JWT --> TID[Extract tenant_id from claims]
    TID --> DB[get_db dependency]
    DB --> SET["SET LOCAL app.tenant_id = '{uuid}'"]
    SET --> RLS[PostgreSQL Row Level Security]
    RLS --> Q[Query only tenant rows]

    LOGIN[POST /auth/login] --> LOOKUP[SET LOCAL app.auth_lookup = 'on']
    LOOKUP --> EMAIL[Cross-tenant email lookup policy]
    EMAIL --> TOKEN[Issue JWT with tenant_id]
```

| Layer | Mechanism | File |
|-------|-----------|------|
| **Authentication** | JWT access + refresh tokens (24h / 7d) | `core/security.py` |
| **Tenant isolation** | `SET LOCAL app.tenant_id` per request | `core/database.py` |
| **Database RLS** | `tenant_isolation` policies on all tenant tables | `database/migrations/001_initial_schema.sql` |
| **Login exception** | `auth_email_lookup` policy when `app.auth_lookup=on` | `003_auth_rls.sql` |
| **Input safety** | `prompt_guard.py` + ModerationAgent regex blocklist | `core/prompt_guard.py`, `orchestration/moderation.py` |
| **CORS** | `CORS_ORIGINS` env var | `main.py` |

---

## 10. Data Architecture

```mermaid
erDiagram
    tenants ||--o{ users : has
    tenants ||--o{ conversations : has
    tenants ||--o{ learner_profiles : has
    tenants ||--o{ assessments : has
    tenants ||--o{ knowledge_chunks : "optional scope"

    users ||--o| learner_profiles : has
    users ||--o{ conversations : owns
    users ||--o{ error_tracking : mistakes
    users ||--o{ learner_memories : preferences
    users ||--o{ voice_analyses : voice

    conversations ||--o{ conversation_messages : contains
    assessments ||--o{ assessment_results : produces
    learning_plans ||--o{ learning_plan_items : contains

    knowledge_chunks {
        uuid id
        vector embedding
        text content
        uuid tenant_id "nullable = global"
    }

    error_tracking {
        uuid id
        vector embedding
        text error_text
        text correction
    }
```

### Storage Responsibilities

| Store | Technology | Data | TTL |
|-------|------------|------|-----|
| **PostgreSQL** | Neon + pgvector | Users, conversations, assessments, RAG chunks, voice analyses, long-term memory | Persistent |
| **Redis** | Optional (OCI) | Session state (`session:{id}`) | 24 hours |
| **In-memory fallback** | Python dict | Sessions when Redis unavailable | Process lifetime |
| **Browser** | localStorage / SecureStore | JWT tokens | Until logout |

---

## 11. LLM Provider Resolution

`ai/openai_client.py` selects provider based on `AI_PROVIDER` env var:

```mermaid
flowchart TD
    START([AI_PROVIDER setting]) --> AUTO{auto?}

    AUTO -->|yes| AZ{AZURE_OPENAI_KEY<br/>configured?}
    AZ -->|yes| COPILOT[Azure OpenAI<br/>gpt-4o-mini]
    AZ -->|no| OAI{OPENAI_API_KEY<br/>configured?}
    OAI -->|yes| GROQ[OpenAI-compatible<br/>Groq / OpenAI]
    OAI -->|no| OLL{OLLAMA_BASE_URL?}
    OLL -->|yes| OLLAMA[Ollama local]
    OLL -->|no| MOCK[Mock responses]

    AUTO -->|openai| GROQ
    AUTO -->|copilot/azure| COPILOT
    AUTO -->|ollama| OLLAMA
    AUTO -->|mock| MOCK
```

### Recommended Production Config (Render + Groq)

```env
AI_PROVIDER=openai
OPENAI_API_KEY=gsk_...
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama-3.1-8b-instant
WHISPER_MODEL=whisper-large-v3-turbo
```

Verify: `GET /health/ai` → `"configured": true`

---

## 12. Deployment Plans

### Plan A — Hobby / $0 (Current Production) ⭐

**Best for:** Demos, ≤50 users, personal projects

| Component | Service | Cost |
|-----------|---------|------|
| Database | Neon free (0.5 GB, scale-to-zero) | $0 |
| API | Render free web (Oregon, cold start ~30s) | $0 |
| Web | Render free web (Oregon) | $0 |
| LLM | Groq free tier | $0 |
| **Total** | | **$0/month** |

**Deploy steps:**

1. **Neon** — https://neon.tech
   - Create project → run `CREATE EXTENSION IF NOT EXISTS vector;`
   - Copy **pooler** URL: `postgresql://...@ep-xxx-pooler.neon.tech/neondb?sslmode=require`

2. **Render Blueprint** — https://dashboard.render.com/blueprints
   - Connect repo → uses `render.yaml`
   - Set `DATABASE_URL`, `OPENAI_API_KEY` (Groq key)
   - Set branch to **`main`** on both services

3. **Migrations** (one time):
   ```bash
   cd ai-english-teacher/backend
   DATABASE_URL='your-neon-url' python3 scripts/migrate.py
   ```

4. **Smoke test:**
   - https://ai-english-teacher-api.onrender.com/health
   - https://ai-english-teacher-api.onrender.com/health/ai
   - Register → Login → Start conversation → Grammar class

```mermaid
flowchart LR
    subgraph Internet
        U[Users]
    end
    subgraph Render Free
        W[Web :3000]
        A[API :10000]
    end
    subgraph External
        N[(Neon)]
        G[Groq]
    end
    U --> W --> A --> N
    A --> G
```

**Limitations:** Cold starts, 512 MB RAM, spins down after 15 min idle, Neon scale-to-zero.

---

### Plan B — Starter / ~$14/month

**Best for:** Small classroom, no cold starts

| Component | Change |
|-----------|--------|
| Render API | Starter plan ($7) — always on |
| Render Web | Starter plan ($7) — always on |
| Neon | Free tier still OK |
| Groq | Free tier |

---

### Plan C — Oracle Cloud VM / $0 Always-On ⭐

**Best for:** India/low-latency, 50+ users, voice-heavy, no cold starts

| Component | Service |
|-----------|---------|
| Compute | Oracle Always Free A1 (1 OCPU / 6 GB) |
| Database | Neon (external, free) |
| LLM | Groq (cloud) OR Ollama (on VM) |
| Cache | Redis (Docker on VM) |
| Proxy | nginx :80 |

**Deploy (one command on VM):**
```bash
curl -fsSL https://raw.githubusercontent.com/meenakshi25jan/docs/main/ai-english-teacher/deploy/oracle-cloud/deploy-now.sh | bash
```

```mermaid
flowchart TB
    U[Users] --> VM[Oracle VM<br/>nginx :80]
    VM --> FE[Next.js :3000]
    VM --> BE[FastAPI :8000]
    BE --> RD[Redis]
    BE --> OL[Ollama optional]
    BE --> N[(Neon)]
    BE --> G[Groq optional]
```

**Note:** Mumbai AD-1 Ampere capacity is often unavailable — retry or use a different region.

---

### Plan D — Enterprise / Azure AKS (~$8,100/month)

**Best for:** Schools, districts, compliance requirements

See `docs/08-DEPLOYMENT_ARCHITECTURE.md` and `docs/11-COST_ESTIMATION.md` for:
- Azure Kubernetes Service
- Azure OpenAI (Copilot)
- Azure PostgreSQL Flexible Server
- Azure Redis, Key Vault, Application Gateway
- Multi-region DR

---

### Deployment Comparison

| Plan | Monthly cost | Cold start | Always-on | Best for |
|------|-------------|------------|-----------|----------|
| **A — Render + Neon** | $0 | Yes (~30s) | No | Demos, hobby |
| **B — Render Starter** | ~$14 | No | Yes | Small classes |
| **C — Oracle VM** | $0 | No | Yes | 50+ users, India |
| **D — Azure AKS** | ~$8,100 | No | Yes | Enterprise schools |

---

## 13. Environment Variable Matrix

### Backend API

| Variable | Required | Default (Render) | Purpose |
|----------|----------|-------------------|---------|
| `DATABASE_URL` | ✅ | manual | Neon PostgreSQL URL with `?sslmode=require` |
| `JWT_SECRET_KEY` | ✅ | auto-generated | Auth token signing |
| `CORS_ORIGINS` | ✅ | web URL JSON array | Cross-origin allowlist |
| `AI_PROVIDER` | | `openai` | LLM provider selection |
| `OPENAI_API_KEY` | ✅ | manual | Groq or OpenAI key |
| `OPENAI_BASE_URL` | | `https://api.groq.com/openai/v1` | Groq endpoint |
| `OPENAI_MODEL` | | `llama-3.1-8b-instant` | Chat model |
| `WHISPER_MODEL` | | `whisper-large-v3-turbo` | STT model |
| `DATABASE_POOL_SIZE` | | `5` | Connection pool (Neon) |
| `DATABASE_POOL_RECYCLE` | | `280` | Recycle stale connections |
| `DATABASE_POOL_PRE_PING` | | `true` | Health-check pool connections |
| `SKIP_MIGRATIONS` | | `true` | Skip auto-migrate on boot |
| `REDIS_URL` | | `redis://localhost:6379/0` | Session cache (OCI) |
| `AZURE_OPENAI_*` | | empty | Azure Copilot (optional) |
| `OLLAMA_BASE_URL` | | empty | Self-hosted LLM (OCI) |

### Frontend Web

| Variable | Render value | Purpose |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | `/api/v1` | Same-origin API path |
| `API_PROXY_URL` | `https://ai-english-teacher-api.onrender.com` | Rewrite target |
| `NODE_VERSION` | `20` | Node.js version |

### Mobile

| Variable | Example | Purpose |
|----------|---------|---------|
| `EXPO_PUBLIC_API_URL` | `https://ai-english-teacher-api.onrender.com/api/v1` | Direct API base URL |

---

## 14. Ports & Network Reference

| Environment | Service | Port | Protocol |
|-------------|---------|------|----------|
| Render API | FastAPI | `$PORT` (~10000) | HTTPS |
| Render Web | Next.js | 3000 | HTTPS |
| Neon | PostgreSQL | 5432 | SSL/TLS |
| Neon Pooler | PgBouncer | 5432 | SSL/TLS |
| Oracle VM | nginx | 80, 443 | HTTP/S |
| Oracle VM | FastAPI | 8000 | internal |
| Oracle VM | Next.js | 3000 | internal |
| Oracle VM | Redis | 6379 | internal |
| Oracle VM | Ollama | 11434 | internal |
| Local dev | Frontend | 3000 | HTTP |
| Local dev | Backend | 8000 | HTTP |
| Local dev | PostgreSQL | 5432 | TCP |
| Fly.io | FastAPI | 8000 | HTTPS |

---

## Quick Reference — Request Paths

```
Browser
  └─ /conversation          → POST /api/v1/conversations → LangGraph → TeacherAgent → Groq
  └─ /grammar-class         → GET  /api/v1/grammar/*    → GrammarTeacherAgent → Groq
  └─ /assessment            → POST /api/v1/assessments  → AssessmentAgents → Groq
  └─ /dashboard/student     → GET  /api/v1/dashboard/*  → PostgreSQL reads
  └─ /login, /register      → POST /api/v1/auth/*         → PostgreSQL + JWT

Android App
  └─ (tabs)/practice        → POST /api/v1/conversations → LangGraph
  └─ (tabs)/grammar         → POST /api/v1/grammar/practice → Voice + GrammarTeacher
  └─ (tabs)/assessment      → POST /api/v1/assessments
```

---

*Last updated: branch `main` — Waves 1–2 implemented, Plans A–D documented.*
