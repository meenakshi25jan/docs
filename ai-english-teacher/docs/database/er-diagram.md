# Database ER Diagram — AI English Teacher MVP (Phase 1 + Phase 2)

This diagram covers the Phase 1 `users` table, the existing `grammar_feedback` table
(from the conversation MVP), and all eleven Phase 2 MVP tables. Deferred tables
(vocabulary_mastery, achievements, grammar_rule, vocabulary_knowledge, enterprise
multi-tenant tables) are intentionally omitted.

**Embeddings note:** `knowledge_embedding` stores vectors from a **separate** embedding
provider (default: `sentence-transformers/all-MiniLM-L6-v2`, 384-dim). Grok (xAI) does
not generate these vectors. The `knowledge_type` + `knowledge_id` pair is polymorphic and
validated in application code — there is no database foreign key to `lesson_knowledge`.

```mermaid
erDiagram
    users ||--o| user_profile : "has (1:1, CASCADE)"
    users ||--o{ conversation_session : "owns (CASCADE)"
    users ||--o{ grammar_feedback : "receives (RESTRICT)"
    users ||--o{ band_score : "assessed (RESTRICT)"
    users ||--o{ learning_plan : "has (CASCADE)"
    users ||--o{ user_progress : "tracks (CASCADE)"
    users ||--o{ user_mistake_memory : "remembers (CASCADE)"
    users ||--o| voice_settings : "prefers (1:1, CASCADE)"

    conversation_session ||--o{ conversation_message : "contains (CASCADE)"

    lesson_knowledge ||..o{ knowledge_embedding : "polymorphic ref (app-level)"

    users {
        uuid id PK
        string email UK
        string name
        string hashed_password
        string role
        string teacher_voice
        timestamptz created_at
        boolean is_active
    }

    user_profile {
        uuid id PK
        uuid user_id FK UK
        string display_name
        string native_language
        string target_level
        text learning_goals
        string avatar_url
        string timezone
        timestamptz created_at
        timestamptz updated_at
    }

    conversation_session {
        uuid id PK
        uuid user_id FK
        string title
        string mode
        string status
        timestamptz created_at
        timestamptz updated_at
    }

    conversation_message {
        uuid id PK
        uuid session_id FK
        string role
        text content
        string audio_url
        timestamptz created_at
        timestamptz updated_at
    }

    grammar_feedback {
        uuid id PK
        uuid user_id FK
        text original_text
        text corrected_text
        text explanation
        text teacher_response
        string mistake_type
        int score
        string mode
        timestamptz created_at
        timestamptz updated_at
    }

    band_score {
        uuid id PK
        uuid user_id FK
        string assessment_type
        int overall_score
        int grammar_score
        int vocabulary_score
        int fluency_score
        int pronunciation_score
        string cefr_level
        numeric ielts_band
        text notes
        timestamptz created_at
        timestamptz updated_at
    }

    learning_plan {
        uuid id PK
        uuid user_id FK
        string title
        text description
        string target_level
        string status
        jsonb plan_data
        timestamptz created_at
        timestamptz updated_at
    }

    user_progress {
        uuid id PK
        uuid user_id FK
        string skill_area
        string level
        int progress_percent
        int streak_days
        timestamptz last_activity_at
        timestamptz created_at
        timestamptz updated_at
    }

    user_mistake_memory {
        uuid id PK
        uuid user_id FK
        string mistake_pattern
        text example_text
        text correction
        int occurrence_count
        timestamptz last_seen_at
        timestamptz created_at
        timestamptz updated_at
    }

    lesson_knowledge {
        uuid id PK
        string title
        text content
        string skill
        string level
        string topic
        string_array tags
        string source
        timestamptz created_at
        timestamptz updated_at
    }

    knowledge_embedding {
        uuid id PK
        string knowledge_type
        uuid knowledge_id
        int chunk_index
        string embedding_model
        vector embedding
        timestamptz created_at
        timestamptz updated_at
    }

    voice_settings {
        uuid id PK
        uuid user_id FK UK
        string preferred_voice
        numeric speed
        numeric pitch
        timestamptz created_at
        timestamptz updated_at
    }
```

## ON DELETE behavior summary

| Child table | Parent | ON DELETE | Rationale |
|-------------|--------|-----------|-----------|
| user_profile | users | CASCADE | Profile is meaningless without the user |
| conversation_session | users | CASCADE | Sessions are owned learner data |
| conversation_message | conversation_session | CASCADE | Messages cannot exist without a session |
| grammar_feedback | users | RESTRICT | Preserve feedback history for analytics |
| band_score | users | RESTRICT | Preserve assessment history for analytics |
| learning_plan | users | CASCADE | Personalized plans are user-owned working data |
| user_progress | users | CASCADE | Per-user progress is ephemeral working state |
| user_mistake_memory | users | CASCADE | Learner-specific mistake memory |
| voice_settings | users | CASCADE | Per-user TTS preferences |

## Indexes of note

- All foreign key columns are indexed.
- `knowledge_embedding`: composite index on `(knowledge_type, knowledge_id)` plus HNSW
  approximate nearest-neighbor index on `embedding` using cosine distance.
