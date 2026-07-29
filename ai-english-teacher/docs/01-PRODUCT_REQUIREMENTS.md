# Product Requirements Document (PRD)

## AI English Teacher Platform

**Version:** 1.0.0  
**Status:** Draft  
**Last Updated:** 2026-07-26

---

## 1. Executive Summary

The AI English Teacher Platform is an enterprise-grade, AI-powered English learning system designed to assess, train, and track learners across IELTS, PTE, TOEFL, and Corporate English domains. The platform leverages Azure OpenAI GPT-5.5, Azure Speech Services, and a microservice architecture to deliver personalized, scalable learning experiences for up to 1 million concurrent users.

## 2. Problem Statement

Traditional English learning platforms lack:
- Real-time, multi-skill AI assessment with standardized score predictions (CEFR, IELTS, PTE)
- Long-term memory of learner mistakes for targeted remediation
- Integrated role-play conversation practice with pronunciation feedback
- Unified dashboards for students, teachers, and administrators
- Enterprise-grade security, multi-tenancy, and cloud portability

## 3. Goals & Success Metrics

| Goal | KPI | Target |
|------|-----|--------|
| Assessment accuracy | CEFR prediction within ±0.5 level | ≥ 85% |
| User engagement | Weekly active sessions per learner | ≥ 3 |
| Learning outcomes | IELTS band improvement over 90 days | ≥ 0.5 bands |
| Platform reliability | Uptime SLA | 99.9% |
| Response latency | API p95 latency | < 500ms (non-AI) |
| AI response time | Assessment completion | < 30s |

## 4. User Personas

### 4.1 Learner (Student)
- Age 18–45, preparing for IELTS/PTE/TOEFL or improving workplace English
- Needs: skill assessment, personalized study plans, progress tracking, role-play practice

### 4.2 Teacher / Tutor
- English language instructors managing cohorts
- Needs: class dashboards, assignment creation, learner analytics, report generation

### 4.3 Administrator
- Platform operators and institutional admins
- Needs: tenant management, user provisioning, billing, system health monitoring

### 4.4 Corporate L&D Manager
- Enterprise clients training employees
- Needs: bulk enrollment, compliance reporting, skill gap analysis

## 5. Functional Requirements

### 5.1 Assessment Module (FR-001 – FR-010)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-001 | System shall assess English proficiency across 6 skills | P0 |
| FR-002 | System shall estimate CEFR level (A1–C2) | P0 |
| FR-003 | System shall estimate IELTS band (0–9) | P0 |
| FR-004 | System shall estimate PTE score (10–90) | P0 |
| FR-005 | System shall evaluate grammar with error categorization | P0 |
| FR-006 | System shall evaluate vocabulary range and accuracy | P0 |
| FR-007 | System shall evaluate speaking with pronunciation scoring | P0 |
| FR-008 | System shall evaluate writing with rubric-based scoring | P0 |
| FR-009 | System shall evaluate reading comprehension | P0 |
| FR-010 | System shall evaluate listening comprehension | P0 |

### 5.2 Learning Module (FR-011 – FR-018)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-011 | System shall generate personalized learning plans | P0 |
| FR-012 | System shall track learner progress over time | P0 |
| FR-013 | System shall maintain long-term memory of learner mistakes | P0 |
| FR-014 | System shall support role-play conversations with AI teacher | P0 |
| FR-015 | System shall provide pronunciation assessment and feedback | P0 |
| FR-016 | System shall adapt difficulty based on performance | P1 |
| FR-017 | System shall recommend vocabulary and grammar exercises | P1 |
| FR-018 | System shall support spaced repetition for vocabulary | P2 |

### 5.3 Reporting Module (FR-019 – FR-022)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-019 | System shall generate individual learner reports (PDF/JSON) | P0 |
| FR-020 | System shall provide teacher class analytics | P0 |
| FR-021 | System shall provide admin platform analytics | P1 |
| FR-022 | System shall export data for LMS integration (xAPI/SCORM) | P2 |

### 5.4 Authentication & Authorization (FR-023 – FR-027)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-023 | System shall support email/password registration | P0 |
| FR-024 | System shall support Google OAuth2 login | P0 |
| FR-025 | System shall support Microsoft OAuth2 login | P0 |
| FR-026 | System shall implement RBAC (student, teacher, admin) | P0 |
| FR-027 | System shall support multi-tenant data isolation | P0 |

## 6. Non-Functional Requirements

### 6.1 Performance
- Support 1M registered users, 50K concurrent
- API gateway throughput: 10K req/s
- Database connection pooling with PgBouncer
- Redis caching for session and frequently accessed data

### 6.2 Security
- TLS 1.3 everywhere
- AES-256 encryption at rest
- JWT with RS256, 15-min access / 7-day refresh tokens
- Rate limiting: 100 req/min per user, 1000 req/min per tenant
- OWASP Top 10 compliance
- Prompt injection protection on all AI endpoints

### 6.3 Scalability
- Horizontal pod autoscaling (HPA) on CPU/memory/custom metrics
- Database read replicas for analytics queries
- Async job queue (Celery/ARQ) for long-running AI tasks
- CDN for static assets

### 6.4 Availability
- Multi-AZ deployment
- RPO < 1 hour, RTO < 15 minutes
- Health checks and circuit breakers

### 6.5 Compliance
- GDPR data portability and right to deletion
- PII anonymization in analytics
- Audit logging for all data access

## 7. User Stories

### Student
- As a student, I want to take a placement test so that I know my CEFR level and IELTS band estimate.
- As a student, I want to practice speaking with an AI tutor so that I can improve my fluency before the exam.
- As a student, I want to see my grammar and vocabulary progress on a dashboard so that I stay motivated.

### Teacher
- As a teacher, I want to view my class's aggregate progress so that I can adjust my teaching focus.
- As a teacher, I want to assign writing tasks and receive AI-scored results so that I save grading time.

### Admin
- As an admin, I want to manage tenants and users so that I can onboard corporate clients.
- As an admin, I want to monitor system health and costs so that I can ensure SLA compliance.

## 8. Out of Scope (v1)

- Native mobile apps (responsive web only)
- Offline mode
- Live human tutor video calls
- Payment/billing integration (placeholder hooks only)
- SCORM package import

## 9. Release Plan

| Phase | Scope | Milestone |
|-------|-------|-----------|
| MVP (v0.1) | Auth, placement assessment, basic dashboard | Alpha |
| v0.5 | All 6 skill assessments, learning plans, role-play | Beta |
| v1.0 | Multi-tenant, teacher/admin dashboards, reports | GA |
| v1.5 | Advanced analytics, LMS integration, mobile PWA | Enhancement |

## 10. Assumptions & Dependencies

- Azure OpenAI GPT-5.5 API availability in target regions
- Azure Speech Services for pronunciation assessment
- PostgreSQL 16 with pgvector extension
- Kubernetes cluster (AKS preferred) for production deployment
