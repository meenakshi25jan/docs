# Oracle Cloud VM — Complete Setup (India West / Mumbai)

Create your **free Oracle Cloud VM** and deploy the AI English Teacher app (web + mobile + API).

**Time:** ~45–60 minutes  
**Cost:** $0/month (Always Free tier)  
**Region:** India West (Mumbai) — `ap-mumbai-1`

---

## Quick links

| Step | Link |
|------|------|
| **Create VM (Mumbai)** | https://cloud.oracle.com/compute/instances/create?region=ap-mumbai-1 |
| **Oracle sign up** | https://www.oracle.com/cloud/free/ |
| **Neon database** | https://neon.tech |
| **Groq API (free AI)** | https://console.groq.com |

---

## Part A — Sign up (one time)

1. Go to https://www.oracle.com/cloud/free/
2. Click **Start for free**
3. **Debit or credit card** works (Visa/Mastercard) — enable international payments with your bank
4. Small verification hold (~$1–15) is refunded in a few days; **Always Free resources are not charged**
5. Choose **Home Region** closest to you (e.g. **India West (Mumbai)**)  
   ⚠️ Cannot change home region later

---

## Part B — Create the VM (4-step wizard)

Open the Mumbai create-instance page:

**https://cloud.oracle.com/compute/instances/create?region=ap-mumbai-1**

### B1. Basic information (Step 1 of 4)

| Field | Value |
|-------|-------|
| **Name** | `ai-english-teacher` |
| **Compartment** | Your root compartment (e.g. `ShreeGanesh (root)`) |
| **Placement** | Any availability domain (if capacity fails, try another) |

Click **Next**.

---

### B2. Image and shape (Step 2 of 4)

#### Image — click **Change image**

| Field | Value |
|-------|-------|
| **Publisher** | Canonical Ubuntu |
| **Image** | **Canonical Ubuntu 24.04 Minimal aarch64** |
| **Price** | Free |

> ⚠️ Must include **aarch64** in the name (ARM). Do **not** pick Ubuntu 20.04 or x86-only images.

Click **Select image**.

#### Shape — click **Change shape**

| Field | Value |
|-------|-------|
| **Series** | **Ampere** (Arm-based processor) |
| **Shape** | **VM.Standard.A1.Flex** |
| **OCPU** | **1** (minimum for ~50 users) |
| **Memory** | **6 GB** |

> **Do not use** `VM.Standard.E2.1.Micro` (1 GB RAM) — too small for this app.

| Shape | RAM | Use for this app? |
|-------|-----|-------------------|
| E2.1.Micro | 1 GB | ❌ No |
| A1.Flex 1 OCPU / 6 GB | 6 GB | ✅ Recommended (+ Groq AI) |
| A1.Flex 2 OCPU / 12 GB | 12 GB | ✅ Best free tier (can run Ollama) |

> **Out of host capacity?** Try another availability domain, retry later, or use 1 OCPU / 6 GB.

Click **Select shape** → **Next**.

---

### B3. Networking (Step 3 of 4)

#### Primary network

Select **Create new virtual cloud network** (not "Select existing" if dropdown is empty).

| Field | Value |
|-------|-------|
| **VCN name** | Leave default (e.g. `vcn-20260729-...`) |
| **Compartment** | Your root compartment |
| **CIDR** | Leave default `10.0.0.0/16` |

#### Subnet

Select **Create new public subnet**.

| Field | Value |
|-------|-------|
| **Subnet name** | Leave default (e.g. `subnet-20260729-...`) |
| **CIDR** | Leave default `10.0.0.0/24` |

#### IP addresses

| Setting | Value |
|---------|-------|
| **Private IPv4** | Automatically assign private IPv4 address |
| **Public IPv4** | **ON** — Automatically assign public IPv4 address |
| **IPv6** | OFF (not needed) |

> If Public IPv4 won't turn on: you must use a **public subnet** (see above).

**VNIC name:** `ai-english-teacher-vnic` (optional)

Click **Next**.

---

### B4. SSH keys (Step 4 of 4)

Choose one option:

#### Option A — Oracle generates keys (easiest)

1. Select **Generate a key pair for me**
2. Click **Download private key** → save as `oci_key` (no extension)
3. Click **Download public key** → save as `oci_key.pub`

> ⚠️ Download the **private key now** — Oracle will not show it again.

#### Option B — Paste your own key

**Windows PowerShell:**
```powershell
ssh-keygen -t ed25519 -f $env:USERPROFILE\.ssh\oci_key -N ""
type $env:USERPROFILE\.ssh\oci_key.pub
```

**Mac/Linux:**
```bash
ssh-keygen -t ed25519 -f ~/.ssh/oci_key -N ""
cat ~/.ssh/oci_key.pub
```

Select **Paste public keys** → paste the full `ssh-ed25519 ...` line.

---

### B5. Storage and create

| Field | Value |
|-------|-------|
| **Boot volume** | 50 GB (default) |

Click **Create**. Wait until **State = Running** (green).

Copy the **Public IP address** — you need it everywhere below as `YOUR_VM_IP`.

---

### B6. Open firewall ports (required!)

Without this, the browser cannot load your app.

1. On the instance page → **Primary VNIC** → click **Subnet** link
2. Click **Security List** name
3. **Add Ingress Rules**:

| Source CIDR | Protocol | Dest Port | Description |
|-------------|----------|-----------|-------------|
| `0.0.0.0/0` | TCP | 80 | HTTP |
| `0.0.0.0/0` | TCP | 443 | HTTPS |

4. Click **Add Ingress Rules**

Port 22 (SSH) is usually already open.

---

## Part C — Database (Neon, free)

1. https://neon.tech → sign up (no card)
2. **New Project** → name: `ai-english-teacher`
3. Copy connection string:
   ```
   postgresql://user:password@ep-xxx.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
   ```
4. **SQL Editor** → run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

---

## Part D — AI key (Groq — recommended for ~50 users)

1. https://console.groq.com → sign up
2. **API Keys** → **Create API Key**
3. Copy key (`gsk_...`)

Groq is faster than local Ollama on a small VM and handles multiple users better.

---

## Part E — Deploy on the VM

### E1. SSH into your VM

**Windows (PowerShell):**
```powershell
ssh -i path\to\oci_key ubuntu@YOUR_VM_IP
```

**Mac/Linux:**
```bash
chmod 600 ~/.ssh/oci_key
ssh -i ~/.ssh/oci_key ubuntu@YOUR_VM_IP
```

### E2. Install Docker

```bash
sudo apt-get update
sudo apt-get install -y git curl ca-certificates openssl
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
```

Log out and SSH back in, then:

```bash
docker --version
```

### E3. Clone app

```bash
git clone --branch main https://github.com/meenakshi25jan/docs.git
cd docs/ai-english-teacher/deploy/oracle-cloud
```

### E4. VM firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

### E5. Configure `.env`

```bash
cp .env.example .env
nano .env
```

Paste (replace YOUR values):

```env
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require
JWT_SECRET_KEY=PASTE_OUTPUT_OF_openssl_rand_hex_32
PUBLIC_URL=http://YOUR_VM_IP

AI_PROVIDER=openai
OPENAI_API_KEY=gsk_your_groq_key
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama-3.1-8b-instant

SKIP_MIGRATIONS=false
DEBUG=false
```

Generate JWT secret:
```bash
openssl rand -hex 32
```

Save in nano: `Ctrl+O` → Enter → `Ctrl+X`

### E6. Start the app

```bash
docker compose -f docker-compose.oracle.yml --env-file .env up -d --build
```

First build takes **5–15 minutes**.

Check status:
```bash
docker compose -f docker-compose.oracle.yml ps
curl http://localhost/health
curl http://localhost/health/ai
```

---

## Part F — Test in browser

| URL | What |
|-----|------|
| `http://YOUR_VM_IP/health` | Health check |
| `http://YOUR_VM_IP/register` | Create account |
| `http://YOUR_VM_IP/conversation` | AI chat |
| `http://YOUR_VM_IP/docs` | API docs |

---

## Part G — Mobile app

On your PC:

```bash
git clone --branch main https://github.com/meenakshi25jan/docs.git
cd docs/ai-english-teacher/mobile
npm install
```

Create `mobile/.env`:

```env
EXPO_PUBLIC_API_URL=http://YOUR_VM_IP/api/v1
```

```bash
npm start
```

Scan QR with **Expo Go** on Android.

---

## Optional — Ollama (local AI, no API key)

Requires **2 OCPU / 12 GB** VM. Edit `.env`:

```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2
```

Start with Ollama profile:
```bash
docker compose -f docker-compose.oracle.yml --env-file .env --profile ollama up -d --build
docker compose -f docker-compose.oracle.yml exec ollama ollama pull llama3.2
```

---

## Quick reference (on VM)

```bash
cd ~/docs/ai-english-teacher/deploy/oracle-cloud

# Logs
docker compose -f docker-compose.oracle.yml logs -f

# Restart after .env change
docker compose -f docker-compose.oracle.yml --env-file .env up -d --build

# Stop / start
docker compose -f docker-compose.oracle.yml down
docker compose -f docker-compose.oracle.yml --env-file .env up -d
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| **VCN dropdown empty** | Select **Create new virtual cloud network** |
| **Public IPv4 won't turn on** | Use **Create new public subnet** |
| **Out of host capacity** | Try another availability domain; retry later |
| **Used E2.1.Micro by mistake** | Delete instance; recreate with **A1.Flex** |
| **Can't SSH** | Check port 22; use correct private key path |
| **Browser can't connect** | Open ports 80/443 in Security List (B6) |
| **Register/login fails** | Check `DATABASE_URL`; restart containers |
| **AI mock / "Tell me more"** | Set Groq key; `AI_PROVIDER=openai` |
| **CORS error** | `PUBLIC_URL` must match `http://YOUR_VM_IP` exactly |
| **Mobile can't connect** | Use `http://` not `https://` for raw IP |

---

## Always Free limits (2026)

| Resource | Limit |
|----------|-------|
| Ampere A1 total | **2 OCPU, 12 GB RAM** |
| Boot storage | 200 GB total |
| After free trial | Only Always Free resources stay $0 |

---

## Next steps

- [FULL_STACK_DEPLOY.md](./FULL_STACK_DEPLOY.md) — architecture and mobile
- [OCI_DEPLOY.md](./OCI_DEPLOY.md) — technical reference
- [RUNBOOK.md](../../RUNBOOK.md) — errors and API docs
