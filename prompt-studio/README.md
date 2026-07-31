# Prompt Studio

Production-ready **Prompt Studio** service: transforms raw ideas into optimized, safe, structured, copy-paste-ready prompts.

- **No Copilot Studio dependency** — works with any OpenAI-compatible LLM API
- **Web UI** + **REST API**
- **Three modes**: Beginner, Professional, Expert/Enterprise (auto-detect supported)
- **Guardrails**: safety, accuracy, privacy, RAG, tool-use, enterprise workflow
- **Docker** ready for deployment

## Quick Start (Local)

```bash
cd prompt-studio
cp .env.example .env
# Edit .env and set OPENAI_API_KEY

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Open **http://localhost:8080**

Or use the helper script:

```bash
chmod +x run.sh
./run.sh
```

## Docker Deploy

```bash
cd prompt-studio
cp .env.example .env
# Set OPENAI_API_KEY in .env

docker compose up --build -d
```

App: **http://localhost:8080**

## API

### `GET /health`

```json
{
  "status": "ok",
  "version": "1.0.0",
  "llm_configured": true,
  "model": "gpt-4o"
}
```

### `POST /api/generate`

**Request:**

```json
{
  "user_request": "Create a prompt for teaching binary search to beginners with Python.",
  "mode": "auto",
  "target_model": "GPT-5",
  "output_format": "markdown",
  "conversation_history": []
}
```

**`mode` values:** `auto` | `beginner` | `professional` | `expert`

**`output_format` values:** `markdown` | `json`

**Response:**

```json
{
  "output": "# Prompt Studio Output\n\n...",
  "mode_used": "beginner",
  "model": "gpt-4o",
  "usage": { "prompt_tokens": 1200, "completion_tokens": 800, "total_tokens": 2000 }
}
```

### Example (curl)

```bash
curl -s http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_request": "Prompt for customer support ticket triage with priority and draft reply",
    "mode": "professional",
    "output_format": "markdown"
  }' | jq -r '.output'
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | **Required** for generation |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | Azure OpenAI, Ollama, LiteLLM, etc. |
| `OPENAI_MODEL` | `gpt-4o` | Model name |
| `OPENAI_TEMPERATURE` | `0.4` | Sampling temperature |
| `OPENAI_MAX_TOKENS` | `4096` | Max completion tokens |
| `PORT` | `8080` | HTTP port |

## Project Structure

```
prompt-studio/
├── app/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── models.py            # Request/response schemas
│   ├── orchestration.py     # Mode resolution + message building
│   ├── llm.py               # OpenAI-compatible client
│   ├── prompts/
│   │   └── system_prompt.txt
│   ├── routes/
│   │   ├── health.py
│   │   └── generate.py
│   └── static/              # Web UI
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Customizing the System Prompt

Edit `app/prompts/system_prompt.txt` and restart the server. No code changes required.

## License

MIT (or match your repository license).
