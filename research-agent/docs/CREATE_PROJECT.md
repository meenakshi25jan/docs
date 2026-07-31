# Create This Project — 5-Minute Guide

**Goal:** Get the Research Agent running on your computer.

Pick your operating system below and follow the steps **in order**.

---

## Step 0: What you need

- A computer (Windows, Mac, or Linux)
- Internet connection
- 30 minutes

**You do NOT need:**
- Prior coding experience
- A credit card
- Cloud account (yet)

---

## WINDOWS — Create the project

### 1. Install tools (one time only)

| Tool | Download | Important |
|------|----------|-----------|
| Python 3.12 | https://www.python.org/downloads/ | ✅ Check **"Add Python to PATH"** |
| Git | https://git-scm.com/download/win | Click Next on all screens |
| VS Code | https://code.visualstudio.com/ | Free code editor |

### 2. Open PowerShell

Press `Win + X` → click **Terminal** or **PowerShell**

### 3. Copy and paste these commands one by one

```powershell
# Download the project
git clone https://github.com/meenakshi25jan/docs.git
cd docs\research-agent

# Create the project (installs everything automatically)
powershell -ExecutionPolicy Bypass -File scripts\create-project.ps1

# Activate the project environment
.\.venv\Scripts\Activate.ps1

# Run your first research (takes 1-2 minutes)
python -m app.main search --query "Artificial Intelligence" --depth 1 --pages 3
```

### 4. Success looks like this

```json
{
  "status": "completed",
  "pages": 3,
  "report": "reports/artificial-intelligence_1_....md"
}
```

### 5. Start the web interface

```powershell
python -m app.main serve
```

Open in browser: **http://localhost:8000/docs**

---

## LINUX (Ubuntu) — Create the project

### 1. Open Terminal

Press `Ctrl + Alt + T`

### 2. Run these commands

```bash
# Download the project
git clone https://github.com/meenakshi25jan/docs.git
cd docs/research-agent

# Create the project (installs everything)
chmod +x scripts/create-project.sh
./scripts/create-project.sh

# Activate environment
source .venv/bin/activate

# Run your first research
python -m app.main search --query "Artificial Intelligence" --depth 1 --pages 3

# Start web interface
python -m app.main serve
```

Open in browser: **http://localhost:8000/docs**

---

## macOS — Create the project

### 1. Install Homebrew (one time)

Open Terminal and run:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Create the project

```bash
git clone https://github.com/meenakshi25jan/docs.git
cd docs/research-agent

chmod +x scripts/create-project.sh
./scripts/create-project.sh

source .venv/bin/activate
python -m app.main search --query "Artificial Intelligence" --depth 1 --pages 3
python -m app.main serve
```

Open in browser: **http://localhost:8000/docs**

---

## After the project is created

| What you can do | Command |
|----------------|---------|
| Research any topic | `python -m app.main search --query "Your Topic" --depth 2 --pages 10` |
| Start API server | `python -m app.main serve` |
| Get OS-specific advice | `./scripts/advise.sh` (Linux/Mac) or `powershell -File scripts\advise.ps1` (Windows) |
| Run tests | `pytest -v` |
| View reports | Open the `reports/` folder |

---

## Project folders created for you

```
research-agent/
├── data/       ← Database (your crawled data)
├── reports/    ← Generated reports (PDF, HTML, Markdown)
├── logs/       ← Error and activity logs
├── .env        ← Your settings (created automatically)
└── .venv/      ← Python environment (created automatically)
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `git: command not found` | Install Git from links above |
| `python: command not found` | Reinstall Python, check "Add to PATH" |
| Script won't run (Windows) | Run: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Crawl returns 0 pages | Check internet; try `--pages 3` first |
| Port 8000 busy | Use: `python -m app.main serve --port 8001` |

---

## Next: Put it online (optional, later)

When ready to deploy to the internet (free):
1. Create account at https://render.com
2. Connect your GitHub
3. See: `docs/BEGINNER_PLAYBOOK.md` → Section 14

---

**Need help?** Run the advisor — it detects your OS and tells you exactly what to do:

```bash
# Linux/Mac
./scripts/advise.sh ai

# Windows
powershell -File scripts\advise.ps1 -ProjectType ai
```
