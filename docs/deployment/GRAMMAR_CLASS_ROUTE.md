# Grammar Class route — production 404 fix

## Canonical URL

**https://ai-english-teacher-web.onrender.com/grammar-class**

Aliases (redirect after deploy): `/grammer`, `/grammar`

## Root cause (production 404)

| Factor | Detail |
|--------|--------|
| **Not missing in code** | `src/app/grammar-class/page.tsx` exists (App Router) |
| **Not missing in build** | `app-path-routes-manifest.json` includes `/grammar-class` |
| **Standalone includes route** | `.next/standalone/frontend/.next/server/app/grammar-class/` |
| **Production failure** | **Stale Render web deploy** — build ID `WjWnTF_iSLNiPaqsi9n8e` predates the route |

API grammar endpoints work: `/api/v1/grammar/grades` → 200.

## Permanent prevention

1. `npm run build` → `postbuild.js` copies assets, writes `build-info.json`, runs `verify-build-routes.js`
2. `verify-build-routes.js` discovers all routes from `src/app/**/page.tsx`, checks manifest + standalone for each
3. CI `frontend` job fails if build or verify fails; `ci-success` blocks deploy workflow
4. `post_deploy_verify.py` checks `/build-info.json` lists `/grammar-class` and `/grammar-class` returns 200

Post-deploy: https://ai-english-teacher-web.onrender.com/build-info.json — confirm `commit` and `routes` include `/grammar-class`.

## Fix stale production

1. Render → **ai-english-teacher-web**
2. **Manual Deploy** → **Clear build cache & deploy**
3. Confirm https://ai-english-teacher-web.onrender.com/public/build-info.json shows latest `main` commit
4. Confirm `/grammar-class` → **200**

## Route tree (App Router)

```text
src/app/
├── page.tsx                 → /
├── grammar-class/page.tsx   → /grammar-class
├── conversation/page.tsx    → /conversation
├── login/page.tsx           → /login
├── register/page.tsx        → /register
├── assessment/page.tsx      → /assessment
└── dashboard/
    ├── student/page.tsx
    ├── teacher/page.tsx
    └── admin/page.tsx
```

No `middleware.ts`. No `pages/` router.
