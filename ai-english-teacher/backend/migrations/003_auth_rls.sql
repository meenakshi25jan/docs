-- Allow email lookup during login without disabling row-level security.
CREATE POLICY auth_email_lookup ON users
    FOR SELECT
    USING (current_setting('app.auth_lookup', true) = 'on');
