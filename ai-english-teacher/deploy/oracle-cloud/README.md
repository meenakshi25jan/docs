# Oracle Cloud Deploy — AI English Teacher

**$0/month** — web + mobile + API on one VM (Mumbai / India West).

## Start here

| Step | Link |
|------|------|
| **1. Create VM** | https://cloud.oracle.com/compute/instances/create?region=ap-mumbai-1 |
| **2. Full wizard** | [VM_SETUP.md](./VM_SETUP.md) |
| **3. One-shot deploy** | [deploy-now.sh](./deploy-now.sh) |
| **4. Web + mobile** | [FULL_STACK_DEPLOY.md](./FULL_STACK_DEPLOY.md) |

## Deploy in one command (on your VM)

After VM is **Running** and ports **80/443** are open:

```bash
ssh -i ~/.ssh/oci_key ubuntu@YOUR_VM_IP
curl -fsSL https://raw.githubusercontent.com/meenakshi25jan/docs/main/ai-english-teacher/deploy/oracle-cloud/deploy-now.sh | bash
```

Paste when prompted:
- Neon `DATABASE_URL`
- Groq API key (`gsk_...` from https://console.groq.com)

## Or with secrets (no prompts)

```bash
DATABASE_URL="postgresql://...@ep-xxx.neon.tech/neondb?sslmode=require" \
GROQ_KEY="gsk_..." \
bash -c "$(curl -fsSL https://raw.githubusercontent.com/meenakshi25jan/docs/main/ai-english-teacher/deploy/oracle-cloud/deploy-now.sh)"
```

## Recommended VM (50 users)

- Image: **Ubuntu 24.04 Minimal aarch64**
- Shape: **A1.Flex 1 OCPU / 6 GB**
- AI: **Groq** (free API)

## Already live on Render (no VM)

- Web: https://ai-english-teacher-web.onrender.com
- API: https://ai-english-teacher-api.onrender.com
