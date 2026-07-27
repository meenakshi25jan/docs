-- Fix RLS policies: avoid uuid cast errors when tenant context is unset.
DROP POLICY IF EXISTS tenant_isolation ON users;
CREATE POLICY tenant_isolation ON users
    USING (
        tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
        OR current_setting('app.auth_lookup', true) = 'on'
    )
    WITH CHECK (
        tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
    );

DROP POLICY IF EXISTS tenant_isolation ON learner_profiles;
CREATE POLICY tenant_isolation ON learner_profiles
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
