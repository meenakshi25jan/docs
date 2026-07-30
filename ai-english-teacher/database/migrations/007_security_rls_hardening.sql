-- Phase 9: Security Hardening & RLS v1
-- Neon-compatible tenant isolation for child tables and voice/memory stores.

-- Helper: tenant UUID from session (empty-safe).
-- Policies use NULLIF(current_setting('app.tenant_id', true), '')::uuid

-- ============================================================
-- CHILD TABLE: conversation_messages (tenant via conversations)
-- ============================================================
ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation ON conversation_messages;
CREATE POLICY tenant_isolation ON conversation_messages
    USING (
        EXISTS (
            SELECT 1 FROM conversations c
            WHERE c.id = conversation_messages.conversation_id
              AND c.tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM conversations c
            WHERE c.id = conversation_messages.conversation_id
              AND c.tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
        )
    );

-- ============================================================
-- CHILD TABLE: assessment_results (tenant via assessments)
-- ============================================================
ALTER TABLE assessment_results ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation ON assessment_results;
CREATE POLICY tenant_isolation ON assessment_results
    USING (
        EXISTS (
            SELECT 1 FROM assessments a
            WHERE a.id = assessment_results.assessment_id
              AND a.tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM assessments a
            WHERE a.id = assessment_results.assessment_id
              AND a.tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
        )
    );

-- ============================================================
-- voice_analyses (direct tenant_id)
-- ============================================================
ALTER TABLE voice_analyses ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation ON voice_analyses;
CREATE POLICY tenant_isolation ON voice_analyses
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

-- ============================================================
-- learner_memories (direct tenant_id)
-- ============================================================
ALTER TABLE learner_memories ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation ON learner_memories;
CREATE POLICY tenant_isolation ON learner_memories
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

-- ============================================================
-- Upgrade legacy tenant_isolation policies (001) with NULLIF + WITH CHECK
-- ============================================================
DROP POLICY IF EXISTS tenant_isolation ON assessments;
CREATE POLICY tenant_isolation ON assessments
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

DROP POLICY IF EXISTS tenant_isolation ON conversations;
CREATE POLICY tenant_isolation ON conversations
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

DROP POLICY IF EXISTS tenant_isolation ON reports;
CREATE POLICY tenant_isolation ON reports
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

DROP POLICY IF EXISTS tenant_isolation ON progress_snapshots;
CREATE POLICY tenant_isolation ON progress_snapshots
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

DROP POLICY IF EXISTS tenant_isolation ON error_tracking;
CREATE POLICY tenant_isolation ON error_tracking
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
