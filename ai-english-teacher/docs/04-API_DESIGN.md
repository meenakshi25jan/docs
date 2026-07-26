# API Design

## Base URL

```
Production:  https://api.ai-english-teacher.com/api/v1
Staging:     https://api-staging.ai-english-teacher.com/api/v1
Local:       http://localhost:8000/api/v1
```

## Authentication

All endpoints (except `/auth/*` and `/health`) require:

```
Authorization: Bearer <access_token>
X-Tenant-ID: <tenant_slug>  (optional, resolved from JWT)
```

## OpenAPI Specification

Full OpenAPI 3.1 spec: [`backend/openapi.yaml`](../backend/openapi.yaml)

Interactive docs: `http://localhost:8000/docs` (Swagger UI)

---

## 1. Authentication APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register with email/password |
| POST | `/auth/login` | Login, returns JWT pair |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | Revoke refresh token |
| GET | `/auth/google` | Initiate Google OAuth2 |
| GET | `/auth/google/callback` | Google OAuth2 callback |
| GET | `/auth/microsoft` | Initiate Microsoft OAuth2 |
| GET | `/auth/microsoft/callback` | Microsoft OAuth2 callback |
| GET | `/auth/me` | Get current user profile |

### POST `/auth/register`

```json
// Request
{
  "email": "student@example.com",
  "password": "SecureP@ss123",
  "first_name": "Jane",
  "last_name": "Doe",
  "tenant_slug": "default"
}

// Response 201
{
  "user": {
    "id": "uuid",
    "email": "student@example.com",
    "role": "student",
    "first_name": "Jane",
    "last_name": "Doe"
  },
  "tokens": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 900
  }
}
```

### POST `/auth/login`

```json
// Request
{
  "email": "student@example.com",
  "password": "SecureP@ss123"
}

// Response 200
{
  "user": { "id": "uuid", "email": "...", "role": "student" },
  "tokens": { "access_token": "...", "refresh_token": "...", "expires_in": 900 }
}
```

---

## 2. Assessment APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/assessments` | Create new assessment |
| GET | `/assessments` | List learner assessments |
| GET | `/assessments/{id}` | Get assessment details |
| POST | `/assessments/{id}/start` | Start assessment |
| POST | `/assessments/{id}/submit` | Submit answers |
| GET | `/assessments/{id}/results` | Get assessment results |
| POST | `/assessments/placement` | Quick placement test |

### POST `/assessments`

```json
// Request
{
  "assessment_type": "full",
  "config": {
    "skills": ["grammar", "vocabulary", "reading", "listening", "writing", "speaking"],
    "difficulty": "adaptive",
    "time_limit_minutes": 60
  }
}

// Response 201
{
  "id": "uuid",
  "assessment_type": "full",
  "status": "pending",
  "config": { ... },
  "created_at": "2026-07-26T08:00:00Z"
}
```

### POST `/assessments/{id}/submit`

```json
// Request
{
  "answers": [
    {
      "skill": "grammar",
      "question_id": "q1",
      "response": "She has been working here for five years.",
      "metadata": {}
    }
  ]
}

// Response 200
{
  "assessment_id": "uuid",
  "status": "completed",
  "results": {
    "grammar": { "score": 78.5, "cefr": "B2", "ielts": 6.5 },
    "vocabulary": { "score": 72.0, "cefr": "B1", "ielts": 6.0 },
    "overall": { "cefr": "B2", "ielts": 6.5, "pte": 58, "confidence": 0.82 }
  }
}
```

---

## 3. Conversation APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/conversations` | Start role-play conversation |
| GET | `/conversations` | List conversations |
| GET | `/conversations/{id}` | Get conversation with messages |
| POST | `/conversations/{id}/messages` | Send message |
| POST | `/conversations/{id}/end` | End conversation |

### POST `/conversations`

```json
// Request
{
  "scenario": "job_interview",
  "context": {
    "role": "interviewer",
    "company": "Tech Corp",
    "position": "Software Engineer",
    "difficulty": "B2"
  }
}

// Response 201
{
  "id": "uuid",
  "scenario": "job_interview",
  "status": "active",
  "initial_message": {
    "role": "assistant",
    "content": "Good morning! Thank you for coming in today..."
  }
}
```

### POST `/conversations/{id}/messages`

```json
// Request
{
  "content": "Thank you for having me. I'm excited about this opportunity."
}

// Response 200
{
  "user_message": { "role": "user", "content": "...", "created_at": "..." },
  "assistant_message": {
    "role": "assistant",
    "content": "That's great to hear! Can you tell me about your experience with Python?",
    "metadata": {
      "grammar_feedback": [],
      "vocabulary_suggestions": ["opportunity → role"]
    }
  }
}
```

---

## 4. Writing APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/writing/submit` | Submit essay for scoring |
| GET | `/writing/submissions` | List submissions |
| GET | `/writing/submissions/{id}` | Get submission with feedback |
| GET | `/writing/prompts` | Get writing prompts |

### POST `/writing/submit`

```json
// Request
{
  "prompt": "Some people believe that technology has made life more complicated...",
  "content": "In recent years, technology has profoundly transformed...",
  "task_type": "ielts_task2"
}

// Response 200
{
  "id": "uuid",
  "scores": {
    "grammar": 75.0,
    "vocabulary": 80.0,
    "coherence": 70.0,
    "overall": 75.0
  },
  "feedback": {
    "strengths": ["Good use of linking words", "Clear thesis statement"],
    "improvements": ["Subject-verb agreement in paragraph 2", "More varied vocabulary"],
    "errors": [
      { "text": "peoples lives", "correction": "people's lives", "category": "punctuation" }
    ]
  },
  "estimates": { "cefr": "B2", "ielts": 6.5, "pte": 58 }
}
```

---

## 5. Speaking APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/speaking/sessions` | Upload audio for analysis |
| GET | `/speaking/sessions` | List speaking sessions |
| GET | `/speaking/sessions/{id}` | Get session with feedback |
| POST | `/speaking/pronunciation` | Pronunciation-only check |

---

## 6. Learning Plan APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/learning-plans` | Generate learning plan |
| GET | `/learning-plans/current` | Get active plan |
| PATCH | `/learning-plans/{id}/items/{item_id}` | Update item status |
| GET | `/learning-plans/{id}/progress` | Plan completion progress |

---

## 7. Reporting APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/reports/generate` | Generate learner report |
| GET | `/reports` | List reports |
| GET | `/reports/{id}` | Get report content |
| GET | `/reports/{id}/download` | Download PDF |

### POST `/reports/generate`

```json
// Request
{
  "report_type": "progress_summary",
  "period_days": 30,
  "format": "json"
}

// Response 200
{
  "id": "uuid",
  "report_type": "progress_summary",
  "content": {
    "period": { "start": "2026-06-26", "end": "2026-07-26" },
    "skill_progress": {
      "grammar": { "start": 65, "end": 78, "change": 13 },
      "vocabulary": { "start": 60, "end": 72, "change": 12 }
    },
    "cefr_trend": ["B1", "B1", "B2", "B2"],
    "ielts_prediction": { "current": 6.5, "projected_90d": 7.0 },
    "top_errors": [...],
    "recommendations": [...]
  }
}
```

---

## 8. Dashboard APIs

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| GET | `/dashboard/student` | Student dashboard data | student |
| GET | `/dashboard/teacher` | Teacher class overview | teacher |
| GET | `/dashboard/admin` | Platform analytics | admin |
| GET | `/dashboard/student/progress` | Skill progress time series | student |
| GET | `/dashboard/student/estimates` | CEFR/IELTS/PTE trends | student |

### GET `/dashboard/student`

```json
// Response 200
{
  "learner": {
    "current_cefr": "B2",
    "ielts_estimate": 6.5,
    "pte_estimate": 58
  },
  "skill_scores": {
    "grammar": 78, "vocabulary": 72, "writing": 75,
    "reading": 80, "listening": 70, "speaking": 68
  },
  "recent_activity": [...],
  "learning_plan_progress": { "completed": 12, "total": 20, "percentage": 60 },
  "upcoming_reviews": { "vocabulary": 15, "grammar_topics": 3 }
}
```

---

## Error Responses

All errors follow RFC 7807 Problem Details:

```json
{
  "type": "https://api.ai-english-teacher.com/errors/validation",
  "title": "Validation Error",
  "status": 422,
  "detail": "Password must be at least 8 characters",
  "instance": "/api/v1/auth/register"
}
```

| Status | Meaning |
|--------|---------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden (RBAC) |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Rate Limited |
| 500 | Internal Server Error |
