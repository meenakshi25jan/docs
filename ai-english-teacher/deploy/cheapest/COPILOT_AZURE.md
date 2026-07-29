# Microsoft Copilot (Azure OpenAI) — Replace Ollama for Cloud Deploy

Microsoft Copilot uses **Azure OpenAI** under the hood. Your app connects to Azure OpenAI — the same GPT models Copilot uses — instead of local Ollama.

> **Note:** The free Copilot chat app (copilot.microsoft.com) has no public API. For your English Teacher app, use **Azure OpenAI** (free trial credits available).

---

## Step 1 — Create Azure OpenAI resource

1. Go to https://portal.azure.com
2. **Create a resource** → search **Azure OpenAI**
3. Choose:
   - **Region:** East US or Sweden Central (model availability varies)
   - **Pricing tier:** Standard S0
4. Click **Create**

New accounts often get **$200 free credits** for 30 days.

---

## Step 2 — Deploy a model

1. Open your Azure OpenAI resource
2. Click **Go to Azure AI Foundry portal** (or Model deployments)
3. **Deployments** → **Create new deployment**
4. Recommended models:

| Model | Deployment name | Best for |
|-------|-----------------|----------|
| `gpt-4o-mini` | `gpt-4o-mini` | Cheap, fast, great for teaching |
| `gpt-4o` | `gpt-4o` | Best quality conversations |
| `gpt-4.1-mini` | `gpt-4.1-mini` | Newer, efficient |

5. Copy the **deployment name** exactly (e.g. `gpt-4o-mini`)

---

## Step 3 — Get API keys

In Azure portal → your OpenAI resource → **Keys and Endpoint**:

| Value | Example |
|-------|---------|
| **Endpoint** | `https://your-name.openai.azure.com/` |
| **Key 1** | `abc123...` |

---

## Step 4 — Configure Render API

Render → **ai-english-teacher-api** → **Environment**:

| Key | Value |
|-----|-------|
| `AI_PROVIDER` | `copilot` |
| `AZURE_OPENAI_ENDPOINT` | `https://your-name.openai.azure.com/` |
| `AZURE_OPENAI_API_KEY` | Your Key 1 |
| `AZURE_OPENAI_DEPLOYMENT` | `gpt-4o-mini` (must match deployment name) |
| `AZURE_OPENAI_API_VERSION` | `2024-12-01-preview` |

**Manual Deploy** the API after saving.

---

## Step 5 — Verify

```bash
curl https://ai-english-teacher-api.onrender.com/health/ai
```

Expected:

```json
{
  "provider": "copilot",
  "model": "gpt-4o-mini",
  "configured": true,
  "hint": "ready"
}
```

Then test conversation at https://ai-english-teacher-web.onrender.com/conversation

---

## Local development (.env)

```env
AI_PROVIDER=copilot
AZURE_OPENAI_ENDPOINT=https://your-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

---

## Copilot vs Ollama — which to use?

| | Microsoft Copilot (Azure) | Ollama (local) |
|--|---------------------------|----------------|
| **Cost** | ~$0.15–2/M tokens (free trial) | $0 |
| **Quality** | Excellent (GPT-4o) | Good (llama3.2) |
| **Works on Render** | ✅ Yes | ❌ No (needs your PC/VPS) |
| **Setup** | Azure account + keys | Install Ollama locally |
| **Best for** | Production / cloud deploy | Local dev / offline |

**Recommendation:** Use **Copilot (Azure)** on Render for production. Use **Ollama** only for local testing without API costs.

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `provider: mock` | Check all 4 Azure env vars are set on Render |
| `DeploymentNotFound` | `AZURE_OPENAI_DEPLOYMENT` must match exact deployment name |
| `401 Unauthorized` | Regenerate API key in Azure portal |
| `429 Rate limit` | Upgrade Azure quota or switch to gpt-4o-mini |
| Still generic replies | Redeploy API after setting env vars; check `/health/ai` |

---

## Free alternative (no Azure)

Use **Groq** (free tier, fast):

```env
AI_PROVIDER=openai
OPENAI_API_KEY=gsk_your_groq_key
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama-3.1-8b-instant
```

Sign up: https://console.groq.com
