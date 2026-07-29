# Oracle Cloud VM — Step-by-Step Setup

Create your **free Oracle Cloud VM** and deploy the AI English Teacher app.

**Time:** ~30 minutes  
**Cost:** $0/month (Always Free tier)

---

## Part A — Create the VM (OCI Console)

### A1. Sign up

1. Go to https://www.oracle.com/cloud/free/
2. Click **Start for free**
3. Complete registration (credit card required for verification — **not charged** for Always Free resources)
4. Choose your **Home Region** (e.g. `US East (Ashburn)` or closest to you)  
   ⚠️ **Cannot change home region later**

### A2. Create compute instance

1. Open https://cloud.oracle.com
2. Menu ☰ → **Compute** → **Instances**
3. Click **Create instance**

Fill in these fields:

| Field | Value |
|-------|-------|
| **Name** | `ai-english-teacher` |
| **Compartment** | (keep default) |
| **Placement** | Pick any **Availability domain** (if one fails, try another) |

**Image and shape** — click **Edit**:

| Field | Value |
|-------|-------|
| **Image** | Ubuntu 24.04 (click **Change image** → Ubuntu → Canonical Ubuntu 24.04 → **aarch64**) |
| **Shape** | Ampere → **VM.Standard.A1.Flex** → **2 OCPU**, **12 GB memory** |

> If you get **"Out of host capacity"**: try another availability domain, or use **1 OCPU / 6 GB** and skip Ollama (use Groq instead).

**Networking** — keep defaults (assign public IP: **Yes**)

**Add SSH keys** — choose one:

- **Option 1 (Windows):** Generate key in PowerShell:
  ```powershell
  ssh-keygen -t ed25519 -f $env:USERPROFILE\.ssh\oci_key
  type $env:USERPROFILE\.ssh\oci_key.pub
  ```
  Copy the output and paste into **Paste public key**

- **Option 2 (Mac/Linux):**
  ```bash
  cat ~/.ssh/id_ed25519.pub
  ```
  Paste into **Paste public key**

**Boot volume:** 50 GB (default is fine)

4. Click **Create**

5. Wait until **State** = **Running** (green)

6. Copy the **Public IP address** (e.g. `123.45.67.89`)

### A3. Open firewall ports (required!)

Without this, the app won't load in your browser.

1. On the instance page, click your **Subnet** link (under Primary VNIC)
2. Click the **Security List** name
3. Click **Add Ingress Rules**
4. Add these rules (one at a time or all together):

| Source CIDR | Protocol | Dest Port | Description |
|-------------|----------|-----------|-------------|
| `0.0.0.0/0` | TCP | 80 | HTTP |
| `0.0.0.0/0` | TCP | 443 | HTTPS |

5. Click **Add Ingress Rules**

Port 22 (SSH) is usually already open.

---

## Part B — Create database (Neon, free)

1. Go to https://neon.tech → sign up
2. **New Project** → name: `ai-english-teacher`
3. Copy the connection string (looks like):
   ```
   postgresql://user:password@ep-cool-name-12345678.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. Open **SQL Editor** and run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

Keep this connection string — you'll need it in Part C.

---

## Part C — Connect to VM and deploy

### C1. SSH into your VM

**Windows (PowerShell):**
```powershell
ssh -i $env:USERPROFILE\.ssh\oci_key ubuntu@YOUR_PUBLIC_IP
```

**Mac/Linux:**
```bash
ssh ubuntu@YOUR_PUBLIC_IP
```

Replace `YOUR_PUBLIC_IP` with the IP from step A2.

### C2. Run the setup script

On the VM:

```bash
curl -fsSL https://raw.githubusercontent.com/meenakshi25jan/docs/cursor/oracle-cloud-deploy-d164/ai-english-teacher/deploy/oracle-cloud/setup-vm.sh | bash
```

This installs Docker, clones the app, and starts containers (~5–10 min).

### C3. Set your database URL

```bash
nano ~/docs/ai-english-teacher/deploy/oracle-cloud/.env
```

Find `DATABASE_URL=` and paste your Neon connection string.

Save: `Ctrl+O`, Enter, `Ctrl+X`

Restart the backend:
```bash
cd ~/docs/ai-english-teacher/deploy/oracle-cloud
docker compose -f docker-compose.oracle.yml --env-file .env restart backend
```

### C4. Pull Ollama model (if using local AI)

```bash
cd ~/docs/ai-english-teacher/deploy/oracle-cloud
docker compose -f docker-compose.oracle.yml exec ollama ollama pull llama3.2
```

This downloads ~2 GB and takes 5–15 minutes.

---

## Part D — Test your app

Open in browser:

| URL | What |
|-----|------|
| `http://YOUR_PUBLIC_IP` | App homepage |
| `http://YOUR_PUBLIC_IP/register` | Create account |
| `http://YOUR_PUBLIC_IP/conversation` | AI chat |
| `http://YOUR_PUBLIC_IP/docs` | API documentation |
| `http://YOUR_PUBLIC_IP/health` | Health check (should return `{"status":"ok"}`) |

---

## Quick reference commands (on VM)

```bash
cd ~/docs/ai-english-teacher/deploy/oracle-cloud

# View logs
docker compose -f docker-compose.oracle.yml logs -f

# Restart everything
docker compose -f docker-compose.oracle.yml restart

# Stop
docker compose -f docker-compose.oracle.yml down

# Start again
docker compose -f docker-compose.oracle.yml --env-file .env --profile ollama up -d
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| **Out of host capacity** | Try different availability domain; or 1 OCPU / 6 GB |
| **Can't SSH** | Check security list has port 22; verify SSH key |
| **Browser can't connect** | Open ports 80/443 in OCI Security List (Part A3) |
| **Register/login fails** | Set `DATABASE_URL` in `.env` and restart backend |
| **AI not responding** | Pull Ollama model, or switch to Groq (see below) |
| **Ollama too slow** | Use Groq instead — set in `.env`: `AI_PROVIDER=openai`, `OPENAI_API_KEY=gsk_xxx`, `OPENAI_BASE_URL=https://api.groq.com/openai/v1` |

---

## Use Groq instead of Ollama (faster, no local LLM)

If Ollama is slow on your VM, edit `.env`:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=gsk_your_groq_key
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama-3.1-8b-instant
```

Get free key: https://console.groq.com

Then restart without Ollama:
```bash
docker compose -f docker-compose.oracle.yml --env-file .env up -d --build
```

---

## Next steps

- [OCI_DEPLOY.md](./OCI_DEPLOY.md) — full deployment reference
- [RUNBOOK.md](../../RUNBOOK.md) — errors and API docs
