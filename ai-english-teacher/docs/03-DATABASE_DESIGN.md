# Database Design

## 1. Entity-Relationship Diagram

```mermaid
erDiagram
    TENANTS ||--o{ USERS : has
    TENANTS ||--o{ LEARNER_PROFILES : has
    USERS ||--o| LEARNER_PROFILES : owns
    USERS ||--o{ OAUTH_ACCOUNTS : links
    LEARNER_PROFILES ||--o{ ASSESSMENTS : takes
    LEARNER_PROFILES ||--o{ LEARNING_PLANS : follows
    LEARNER_PROFILES ||--o{ CONVERSATIONS : participates
    LEARNER_PROFILES ||--o{ WRITING_SUBMISSIONS : submits
    LEARNER_PROFILES ||--o{ SPEAKING_SESSIONS : records
    LEARNER_PROFILES ||--o{ VOCABULARY_ENTRIES : tracks
    LEARNER_PROFILES ||--o{ ERROR_TRACKING : accumulates
    LEARNER_PROFILES ||--o{ PROGRESS_SNAPSHOTS : snapshots
    LEARNER_PROFILES ||--o{ REPORTS : receives
    LEARNER_PROFILES ||--o{ NOTIFICATIONS : receives
    ASSESSMENTS ||--o{ ASSESSMENT_RESULTS : produces
    CONVERSATIONS ||--o{ CONVERSATION_MESSAGES : contains
    LEARNING_PLANS ||--o{ LEARNING_PLAN_ITEMS : contains

    TENANTS {
        uuid id PK
        varchar name
        varchar slug UK
        varchar plan_tier
        jsonb settings
        boolean is_active
        timestamptz created_at
        timestamptz updated_at
    }

    USERS {
        uuid id PK
        uuid tenant_id FK
        varchar email UK
        varchar password_hash
        varchar role
        varchar first_name
        varchar last_name
        boolean is_active
        timestamptz last_login_at
        timestamptz created_at
    }

    LEARNER_PROFILES {
        uuid id PK
        uuid tenant_id FK
        uuid user_id FK
        varchar target_exam
        varchar current_cefr
        decimal ielts_estimate
        decimal pte_estimate
        jsonb preferences
        timestamptz created_at
    }

    ASSESSMENTS {
        uuid id PK
        uuid tenant_id FK
        uuid learner_id FK
        varchar assessment_type
        varchar status
        jsonb config
        timestamptz started_at
        timestamptz completed_at
    }

    ASSESSMENT_RESULTS {
        uuid id PK
        uuid assessment_id FK
        varchar skill
        decimal score
        decimal confidence
        varchar cefr_estimate
        decimal ielts_estimate
        decimal pte_estimate
        jsonb details
        timestamptz created_at
    }

    ERROR_TRACKING {
        uuid id PK
        uuid tenant_id FK
        uuid learner_id FK
        varchar error_category
        varchar error_type
        text error_text
        text correction
        integer occurrence_count
        vector embedding
        timestamptz last_seen_at
        timestamptz created_at
    }

    VOCABULARY_ENTRIES {
        uuid id PK
        uuid tenant_id FK
        uuid learner_id FK
        varchar word
        varchar mastery_level
        integer exposure_count
        integer correct_count
        vector embedding
        timestamptz next_review_at
        timestamptz created_at
    }

    CONVERSATIONS {
        uuid id PK
        uuid tenant_id FK
        uuid learner_id FK
        varchar scenario
        varchar status
        jsonb context
        timestamptz started_at
        timestamptz ended_at
    }

    CONVERSATION_MESSAGES {
        uuid id PK
        uuid conversation_id FK
        varchar role
        text content
        jsonb metadata
        timestamptz created_at
    }

    WRITING_SUBMISSIONS {
        uuid id PK
        uuid tenant_id FK
        uuid learner_id FK
        text prompt
        text content
        decimal grammar_score
        decimal vocabulary_score
        decimal coherence_score
        decimal overall_score
        jsonb feedback
        timestamptz submitted_at
    }

    SPEAKING_SESSIONS {
        uuid id PK
        uuid tenant_id FK
        uuid learner_id FK
        varchar audio_url
        text transcript
        decimal pronunciation_score
        decimal fluency_score
        decimal grammar_score
        decimal overall_score
        jsonb feedback
        timestamptz recorded_at
    }

    LEARNING_PLANS {
        uuid id PK
        uuid tenant_id FK
        uuid learner_id FK
        varchar status
        jsonb goals
        date start_date
        date end_date
        timestamptz created_at
    }

    LEARNING_PLAN_ITEMS {
        uuid id PK
        uuid plan_id FK
        varchar skill
        varchar item_type
        text description
        varchar status
        integer priority
        timestamptz completed_at
    }

    PROGRESS_SNAPSHOTS {
        uuid id PK
        uuid tenant_id FK
        uuid learner_id FK
        decimal grammar_score
        decimal vocabulary_score
        decimal writing_score
        decimal reading_score
        decimal listening_score
        decimal speaking_score
        varchar cefr_estimate
        decimal ielts_estimate
        decimal pte_estimate
        timestamptz snapshot_at
    }

    REPORTS {
        uuid id PK
        uuid tenant_id FK
        uuid learner_id FK
        varchar report_type
        jsonb content
        varchar file_url
        timestamptz generated_at
    }

    NOTIFICATIONS {
        uuid id PK
        uuid tenant_id FK
        uuid user_id FK
        varchar type
        varchar title
        text message
        boolean is_read
        timestamptz created_at
    }
```

## 2. Table Summary

| Table | Rows (est. 1M users) | Purpose |
|-------|---------------------|---------|
| tenants | 1K | Multi-tenant organizations |
| users | 1.2M | Authentication & RBAC |
| learner_profiles | 1M | Learner metadata & targets |
| assessments | 5M | Assessment sessions |
| assessment_results | 30M | Per-skill assessment scores |
| error_tracking | 50M | Long-term mistake memory |
| vocabulary_entries | 100M | Spaced repetition vocabulary |
| conversations | 10M | Role-play sessions |
| conversation_messages | 100M | Chat history |
| writing_submissions | 8M | Essay submissions |
| speaking_sessions | 6M | Audio practice sessions |
| learning_plans | 2M | Personalized study plans |
| learning_plan_items | 20M | Plan task items |
| progress_snapshots | 12M | Weekly progress data points |
| reports | 3M | Generated reports |
| notifications | 20M | User notifications |

## 3. Indexing Strategy

- All `tenant_id` columns: B-tree index (RLS filter)
- `users.email`: Unique index per tenant
- `error_tracking.embedding`: IVFFlat index (pgvector, lists=100)
- `vocabulary_entries.embedding`: IVFFlat index
- `progress_snapshots(learner_id, snapshot_at)`: Composite B-tree
- `assessments(learner_id, status)`: Composite B-tree
- `notifications(user_id, is_read)`: Partial index where `is_read = false`

## 4. Row-Level Security

All tenant-scoped tables enforce RLS:

```sql
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON assessments
    USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

The application sets `app.tenant_id` at the start of each database transaction via `SET LOCAL`.

## 5. Migration Files

See `database/migrations/` for executable SQL scripts:
- `001_initial_schema.sql` — Core tables, indexes, RLS
- `002_pgvector.sql` — Vector extension and embedding columns
