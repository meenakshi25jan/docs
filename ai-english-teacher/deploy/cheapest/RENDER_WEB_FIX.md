# Fix Grammar Class 404 — Web Service Setup

The API (`ai-english-teacher-api`) and website (`ai-english-teacher-web`) are **two separate services**.

Grammar Class lives at: **https://ai-english-teacher-web.onrender.com/grammar-class**

---

## Step 1 — Open the WEB service (not API)

https://dashboard.render.com → click **ai-english-teacher-web**

Do **not** use:
- `ai-english-teacher-api` (backend only)
- `docs` or `docs-wtrv` (wrong service — delete if you created it by mistake)

---

## Step 2 — Settings → Build & Deploy

Copy these values **exactly**:

| Field | Value |
|-------|--------|
| **Branch** | `main` |
| **Root Directory** | `ai-english-teacher/frontend` |
| **Runtime** | **Node** (not Docker) |
| **Build Command** | `npm ci && npm run build` |
| **Start Command** | `npm start` |
| **Region** | Oregon or Ohio (any is fine) |

Click **Save Changes**.

---

## Step 3 — Environment variables

| Key | Value |
|-----|-------|
| `NODE_VERSION` | `20` |
| `NEXT_PUBLIC_API_URL` | `/api/v1` |
| `API_PROXY_URL` | `https://ai-english-teacher-api.onrender.com` |

---

## Step 4 — Manual Deploy

**Manual Deploy** → **Deploy latest commit** → wait for **Live** (~5 min).

### Build log must show:
```
○ /grammar-class
```

---

## Step 5 — Test

https://ai-english-teacher-web.onrender.com/grammar-class

---

## If build fails

| Error | Fix |
|-------|-----|
| `ESLint` / `@typescript-eslint` | Deploy latest `main` (fixed in next.config.js) |
| `COPY /app/public not found` | Switch runtime to **Node** OR deploy latest `main` (Docker fix) |
| Still 404 after Live | Confirm service name is **ai-english-teacher-web**, not `docs` |

---

## API service (separate)

**ai-english-teacher-api** settings:

| Field | Value |
|-------|--------|
| Branch | `main` |
| Root Directory | `ai-english-teacher/backend` |
| Runtime | Python or Docker (both work) |
| Start Command | `python3 -m uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

Test API: https://ai-english-teacher-api.onrender.com/api/v1/grammar/grades
