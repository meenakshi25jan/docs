# Fix AI + Audio on Render (Groq — free)

Your chat shows **"Could you tell me more about that?"** because the API is in **mock mode** (no LLM key configured).

Check: https://ai-english-teacher-api.onrender.com/health/ai  
Should show `"configured": true` — not `"provider": "mock"`.

---

## Step 1 — Get Groq API key (2 min)

1. https://console.groq.com → sign up (free)
2. **API Keys** → **Create API Key**
3. Copy key (`gsk_...`)

---

## Step 2 — Set Render environment variables (5 min)

1. https://dashboard.render.com
2. Open **ai-english-teacher-api**
3. **Environment** → add/update:

| Key | Value |
|-----|-------|
| `AI_PROVIDER` | `openai` |
| `OPENAI_API_KEY` | `gsk_your_groq_key` |
| `OPENAI_BASE_URL` | `https://api.groq.com/openai/v1` |
| `OPENAI_MODEL` | `llama-3.1-8b-instant` |
| `WHISPER_MODEL` | `whisper-large-v3-turbo` |
| `DATABASE_URL` | Your Neon connection string (with `?sslmode=require`) |

4. Click **Save Changes**
5. **Manual Deploy** → Deploy latest commit

Wait 3–5 minutes for redeploy.

---

## Step 3 — Verify LLM works

```bash
curl https://ai-english-teacher-api.onrender.com/health/ai
```

Expected:
```json
{
  "provider": "openai",
  "model": "llama-3.1-8b-instant",
  "configured": true
}
```

---

## Step 4 — Test chat (text)

1. https://ai-english-teacher-web.onrender.com/conversation
2. Start practice
3. Type: **"Please correct my sentence: I go to school yesterday"**
4. You should get **grammar correction** — not "Could you tell me more?"

---

## Step 5 — Test audio (voice teacher)

### Web (Chrome recommended)

1. Open **Conversation** page
2. Enable **Auto-play voice** (text-to-speech)
3. Click **mic button** 🎤
4. Speak in English
5. You get:
   - Transcript of your speech
   - Fluency / pronunciation scores
   - AI reply with corrections

### Mobile (Expo)

```env
EXPO_PUBLIC_API_URL=https://ai-english-teacher-api.onrender.com/api/v1
```

Practice tab → mic button → speak → scores + AI reply.

---

## What each part does

| Feature | Technology |
|---------|------------|
| **Text chat** | Groq LLM (`llama-3.1-8b-instant`) |
| **Grammar correction** | LangGraph orchestration + LLM |
| **Speech-to-text** | Groq Whisper (`whisper-large-v3-turbo`) |
| **Text-to-speech (web)** | Browser Web Speech API |
| **Voice scores** | Wave 2 voice agents (`/voice/analyze`) |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Still "Could you tell me more?" | `/health/ai` shows mock → set Groq keys, redeploy API |
| Register/login fails | Set `DATABASE_URL` on Render API |
| Mic not working | Use **Chrome**; allow microphone permission |
| Voice scores missing | Groq key required; check API logs on Render |
| Slow first message | Render free tier cold start — wait 30–60 sec |

---

## Optional — Azure Copilot instead of Groq

See [COPILOT_AZURE.md](./COPILOT_AZURE.md) if you prefer Microsoft Azure OpenAI.
