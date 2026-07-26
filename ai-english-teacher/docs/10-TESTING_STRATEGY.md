# Testing Strategy

## 1. Testing Pyramid

```
         ╱  E2E (10%)  ╲         Playwright / Cypress
        ╱ Integration (20%) ╲     API + DB integration tests
       ╱  Unit Tests (70%)    ╲   pytest, Jest/Vitest
```

## 2. Backend Testing

### Unit Tests (`backend/tests/unit/`)
- Scoring engine formulas (all skill calculations, CEFR/IELTS/PTE mapping)
- Prompt injection detection
- JWT creation/validation
- Pydantic schema validation

### Integration Tests (`backend/tests/integration/`)
- Auth flow: register → login → access protected endpoint
- Assessment lifecycle: create → start → submit → results
- Conversation flow: start → message → response
- Database RLS tenant isolation

### AI Agent Tests (`backend/tests/agents/`)
- Mock LLM responses for deterministic agent output
- Schema validation on agent input/output
- Prompt template rendering

```bash
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing
```

## 3. Frontend Testing

### Component Tests (Vitest + React Testing Library)
- Dashboard chart rendering with mock data
- Form validation on login/register
- Responsive layout breakpoints

### E2E Tests (Playwright)
- User registration and login flow
- Complete placement assessment
- Role-play conversation interaction
- Dashboard data display

```bash
cd frontend
npm run test        # unit/component
npx playwright test # e2e
```

## 4. API Contract Testing

- OpenAPI spec validation against running server
- Schemathesis for property-based API testing
- Postman/Newman collection in CI

## 5. Performance Testing

| Test | Tool | Target |
|------|------|--------|
| API load test | k6 | 10K req/s, p95 < 500ms |
| AI endpoint stress | k6 | 100 concurrent assessments |
| Database query perf | pgbench | < 10ms for dashboard queries |
| Frontend Lighthouse | Lighthouse CI | Performance > 90 |

## 6. Security Testing

- OWASP ZAP automated scan in CI
- Dependency vulnerability scanning (Snyk/Trivy)
- Prompt injection test suite (50+ attack vectors)
- RBAC authorization matrix tests
- SQL injection tests on all endpoints

## 7. CI Pipeline Test Gates

| Stage | Tests | Pass Criteria |
|-------|-------|---------------|
| PR | Unit + lint | 100% pass, coverage > 70% |
| Merge to main | Integration + contract | 100% pass |
| Staging deploy | E2E + security scan | 100% pass, 0 critical vulns |
| Production deploy | Smoke tests | Health check + auth flow |

## 8. Test Data Management

- Factory fixtures via `factory_boy` (backend)
- Seed script: `database/seeds/dev_seed.sql`
- Test database isolated per CI run (Docker PostgreSQL)
- No production data in test environments
