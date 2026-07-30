-- Curriculum Intelligence v1 — lesson completions and revision schedule

CREATE TABLE IF NOT EXISTS lesson_completions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    learner_id      UUID NOT NULL REFERENCES learner_profiles(id) ON DELETE CASCADE,
    lesson_id       VARCHAR(120) NOT NULL,
    title           VARCHAR(255) NOT NULL,
    skill_focus     VARCHAR(50) NOT NULL DEFAULT 'general',
    route           VARCHAR(500) NOT NULL,
    score           NUMERIC(5, 2),
    metadata        JSONB NOT NULL DEFAULT '{}',
    completed_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lesson_completions_learner
    ON lesson_completions(learner_id, completed_at DESC);
CREATE INDEX IF NOT EXISTS idx_lesson_completions_lesson
    ON lesson_completions(learner_id, lesson_id);

CREATE TABLE IF NOT EXISTS revision_schedule (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    learner_id      UUID NOT NULL REFERENCES learner_profiles(id) ON DELETE CASCADE,
    lesson_id       VARCHAR(120) NOT NULL,
    source_type     VARCHAR(50) NOT NULL,
    source_ref      VARCHAR(200),
    title           VARCHAR(255) NOT NULL,
    skill_focus     VARCHAR(50) NOT NULL DEFAULT 'general',
    route           VARCHAR(500) NOT NULL,
    due_at          TIMESTAMPTZ NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    priority        INTEGER NOT NULL DEFAULT 5,
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_revision_schedule_learner
    ON revision_schedule(learner_id, due_at);
CREATE INDEX IF NOT EXISTS idx_revision_schedule_due
    ON revision_schedule(learner_id, status, due_at);

ALTER TABLE lesson_completions ENABLE ROW LEVEL SECURITY;
ALTER TABLE revision_schedule ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation ON lesson_completions;
CREATE POLICY tenant_isolation ON lesson_completions
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

DROP POLICY IF EXISTS tenant_isolation ON revision_schedule;
CREATE POLICY tenant_isolation ON revision_schedule
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

CREATE TRIGGER trg_lesson_completions_updated BEFORE UPDATE ON lesson_completions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_revision_schedule_updated BEFORE UPDATE ON revision_schedule
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
