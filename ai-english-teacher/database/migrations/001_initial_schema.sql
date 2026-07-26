-- AI English Teacher Platform - Initial Schema
-- PostgreSQL 16+

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- TENANTS
-- ============================================================
CREATE TABLE tenants (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(255) NOT NULL,
    slug        VARCHAR(100) NOT NULL UNIQUE,
    plan_tier   VARCHAR(50) NOT NULL DEFAULT 'free'
                CHECK (plan_tier IN ('free', 'pro', 'enterprise')),
    settings    JSONB NOT NULL DEFAULT '{}',
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- USERS
-- ============================================================
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email           VARCHAR(320) NOT NULL,
    password_hash   VARCHAR(255),
    role            VARCHAR(50) NOT NULL DEFAULT 'student'
                    CHECK (role IN ('student', 'teacher', 'admin', 'super_admin')),
    first_name      VARCHAR(100),
    last_name       VARCHAR(100),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, email)
);

CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);

-- ============================================================
-- OAUTH ACCOUNTS
-- ============================================================
CREATE TABLE oauth_accounts (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider        VARCHAR(50) NOT NULL CHECK (provider IN ('google', 'microsoft')),
    provider_uid    VARCHAR(255) NOT NULL,
    access_token    TEXT,
    refresh_token   TEXT,
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (provider, provider_uid)
);

CREATE INDEX idx_oauth_user ON oauth_accounts(user_id);

-- ============================================================
-- LEARNER PROFILES
-- ============================================================
CREATE TABLE learner_profiles (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    target_exam     VARCHAR(50) CHECK (target_exam IN ('ielts', 'pte', 'toefl', 'corporate', 'general')),
    current_cefr    VARCHAR(5) CHECK (current_cefr IN ('A1','A2','B1','B2','C1','C2')),
    ielts_estimate  DECIMAL(3,1) CHECK (ielts_estimate BETWEEN 0 AND 9),
    pte_estimate    INTEGER CHECK (pte_estimate BETWEEN 10 AND 90),
    preferences     JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_learner_tenant ON learner_profiles(tenant_id);

-- ============================================================
-- ASSESSMENTS
-- ============================================================
CREATE TABLE assessments (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    learner_id      UUID NOT NULL REFERENCES learner_profiles(id) ON DELETE CASCADE,
    assessment_type VARCHAR(50) NOT NULL
                    CHECK (assessment_type IN ('placement','grammar','vocabulary','writing',
                           'reading','listening','speaking','full')),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending','in_progress','completed','cancelled')),
    config          JSONB NOT NULL DEFAULT '{}',
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_assessments_learner ON assessments(learner_id, status);
CREATE INDEX idx_assessments_tenant ON assessments(tenant_id);

-- ============================================================
-- ASSESSMENT RESULTS
-- ============================================================
CREATE TABLE assessment_results (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id   UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    skill           VARCHAR(50) NOT NULL,
    score           DECIMAL(5,2) NOT NULL CHECK (score BETWEEN 0 AND 100),
    confidence      DECIMAL(3,2) CHECK (confidence BETWEEN 0 AND 1),
    cefr_estimate   VARCHAR(5),
    ielts_estimate  DECIMAL(3,1),
    pte_estimate    INTEGER,
    details         JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_results_assessment ON assessment_results(assessment_id);

-- ============================================================
-- ERROR TRACKING (Long-term mistake memory)
-- ============================================================
CREATE TABLE error_tracking (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    learner_id      UUID NOT NULL REFERENCES learner_profiles(id) ON DELETE CASCADE,
    error_category  VARCHAR(50) NOT NULL,
    error_type      VARCHAR(100) NOT NULL,
    error_text      TEXT NOT NULL,
    correction      TEXT,
    occurrence_count INTEGER NOT NULL DEFAULT 1,
    last_seen_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_errors_learner ON error_tracking(learner_id, error_category);
CREATE INDEX idx_errors_tenant ON error_tracking(tenant_id);

-- ============================================================
-- VOCABULARY TRACKING
-- ============================================================
CREATE TABLE vocabulary_entries (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    learner_id      UUID NOT NULL REFERENCES learner_profiles(id) ON DELETE CASCADE,
    word            VARCHAR(200) NOT NULL,
    mastery_level   VARCHAR(20) NOT NULL DEFAULT 'new'
                    CHECK (mastery_level IN ('new','learning','familiar','mastered')),
    exposure_count  INTEGER NOT NULL DEFAULT 0,
    correct_count   INTEGER NOT NULL DEFAULT 0,
    next_review_at  TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (learner_id, word)
);

CREATE INDEX idx_vocab_learner ON vocabulary_entries(learner_id, mastery_level);
CREATE INDEX idx_vocab_review ON vocabulary_entries(learner_id, next_review_at)
    WHERE next_review_at IS NOT NULL;

-- ============================================================
-- CONVERSATIONS
-- ============================================================
CREATE TABLE conversations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    learner_id      UUID NOT NULL REFERENCES learner_profiles(id) ON DELETE CASCADE,
    scenario        VARCHAR(100) NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active','completed','abandoned')),
    context         JSONB NOT NULL DEFAULT '{}',
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at        TIMESTAMPTZ
);

CREATE INDEX idx_conv_learner ON conversations(learner_id, status);

-- ============================================================
-- CONVERSATION MESSAGES
-- ============================================================
CREATE TABLE conversation_messages (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role            VARCHAR(20) NOT NULL CHECK (role IN ('user','assistant','system')),
    content         TEXT NOT NULL,
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conv ON conversation_messages(conversation_id, created_at);

-- ============================================================
-- WRITING SUBMISSIONS
-- ============================================================
CREATE TABLE writing_submissions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    learner_id      UUID NOT NULL REFERENCES learner_profiles(id) ON DELETE CASCADE,
    prompt          TEXT NOT NULL,
    content         TEXT NOT NULL,
    word_count      INTEGER,
    grammar_score   DECIMAL(5,2),
    vocabulary_score DECIMAL(5,2),
    coherence_score DECIMAL(5,2),
    overall_score   DECIMAL(5,2),
    feedback        JSONB,
    submitted_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_writing_learner ON writing_submissions(learner_id, submitted_at DESC);

-- ============================================================
-- SPEAKING SESSIONS
-- ============================================================
CREATE TABLE speaking_sessions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id           UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    learner_id          UUID NOT NULL REFERENCES learner_profiles(id) ON DELETE CASCADE,
    audio_url           VARCHAR(500),
    transcript          TEXT,
    duration_seconds    INTEGER,
    pronunciation_score DECIMAL(5,2),
    fluency_score       DECIMAL(5,2),
    grammar_score       DECIMAL(5,2),
    overall_score       DECIMAL(5,2),
    feedback            JSONB,
    recorded_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_speaking_learner ON speaking_sessions(learner_id, recorded_at DESC);

-- ============================================================
-- LEARNING PLANS
-- ============================================================
CREATE TABLE learning_plans (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    learner_id      UUID NOT NULL REFERENCES learner_profiles(id) ON DELETE CASCADE,
    status          VARCHAR(20) NOT NULL DEFAULT 'active'
                    CHECK (status IN ('draft','active','completed','archived')),
    goals           JSONB NOT NULL DEFAULT '[]',
    start_date      DATE NOT NULL,
    end_date        DATE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_plans_learner ON learning_plans(learner_id, status);

-- ============================================================
-- LEARNING PLAN ITEMS
-- ============================================================
CREATE TABLE learning_plan_items (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plan_id         UUID NOT NULL REFERENCES learning_plans(id) ON DELETE CASCADE,
    skill           VARCHAR(50) NOT NULL,
    item_type       VARCHAR(50) NOT NULL,
    description     TEXT NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending','in_progress','completed','skipped')),
    priority        INTEGER NOT NULL DEFAULT 0,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_plan_items ON learning_plan_items(plan_id, status);

-- ============================================================
-- PROGRESS SNAPSHOTS
-- ============================================================
CREATE TABLE progress_snapshots (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    learner_id      UUID NOT NULL REFERENCES learner_profiles(id) ON DELETE CASCADE,
    grammar_score   DECIMAL(5,2),
    vocabulary_score DECIMAL(5,2),
    writing_score   DECIMAL(5,2),
    reading_score   DECIMAL(5,2),
    listening_score DECIMAL(5,2),
    speaking_score  DECIMAL(5,2),
    confidence_score DECIMAL(5,2),
    cefr_estimate   VARCHAR(5),
    ielts_estimate  DECIMAL(3,1),
    pte_estimate    INTEGER,
    snapshot_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_progress_learner ON progress_snapshots(learner_id, snapshot_at DESC);

-- ============================================================
-- REPORTS
-- ============================================================
CREATE TABLE reports (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    learner_id      UUID NOT NULL REFERENCES learner_profiles(id) ON DELETE CASCADE,
    report_type     VARCHAR(50) NOT NULL,
    content         JSONB NOT NULL,
    file_url        VARCHAR(500),
    generated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_reports_learner ON reports(learner_id, generated_at DESC);

-- ============================================================
-- NOTIFICATIONS
-- ============================================================
CREATE TABLE notifications (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type            VARCHAR(50) NOT NULL,
    title           VARCHAR(255) NOT NULL,
    message         TEXT NOT NULL,
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notif_user ON notifications(user_id, is_read)
    WHERE is_read = FALSE;

-- ============================================================
-- REFRESH TOKENS
-- ============================================================
CREATE TABLE refresh_tokens (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash      VARCHAR(255) NOT NULL UNIQUE,
    expires_at      TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_refresh_user ON refresh_tokens(user_id);

-- ============================================================
-- ROW-LEVEL SECURITY
-- ============================================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE learner_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE error_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE vocabulary_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE writing_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE speaking_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE progress_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- RLS policies (tenant_id isolation)
DO $$
DECLARE
    tbl TEXT;
BEGIN
    FOREACH tbl IN ARRAY ARRAY[
        'users','learner_profiles','assessments','error_tracking',
        'vocabulary_entries','conversations','writing_submissions',
        'speaking_sessions','learning_plans','progress_snapshots',
        'reports','notifications'
    ] LOOP
        EXECUTE format(
            'CREATE POLICY tenant_isolation ON %I USING (tenant_id = current_setting(''app.tenant_id'', true)::uuid)',
            tbl
        );
    END LOOP;
END $$;

-- ============================================================
-- UPDATED_AT TRIGGER
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_tenants_updated BEFORE UPDATE ON tenants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_users_updated BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_learner_updated BEFORE UPDATE ON learner_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_vocab_updated BEFORE UPDATE ON vocabulary_entries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_plans_updated BEFORE UPDATE ON learning_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
