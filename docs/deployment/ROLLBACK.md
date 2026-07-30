# Rollback

## Application rollback (Render)

1. Render → Service → **Deploys**
2. Select last known good deploy → **Rollback to this version**
3. Roll back **both** API and web if needed
4. Run `deploy_verify.py` locally or wait for deploy workflow

## Git rollback

```bash
git revert <bad-commit>
git push origin main
```

CI runs → autoDeploy rebuilds from reverted commit.

## Database rollback

- Migrations are forward-only SQL files
- **No automatic down migrations**
- To undo schema: restore Neon **point-in-time branch** or backup
- Test migrations on Neon branch before production apply

## Emergency recovery

1. Restore web/API from Render deploy history
2. If DB corrupted: Neon PITR or restore backup
3. Verify `/health`, `/grammar-class`, `/api/v1/grammar/grades`
4. Post-mortem: update `docs/deployment/TROUBLESHOOTING.md`

## Prevention

- CI required on `main`
- Deploy workflow verification gates
- Migration check before deploy
