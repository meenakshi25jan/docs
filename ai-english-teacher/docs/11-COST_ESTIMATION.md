# Cost Estimation

## Assumptions

- 1M registered users, 50K monthly active users (MAU)
- 5 assessments/user/month, 10 conversations/user/month
- Average AI call: 2K input tokens + 1K output tokens
- Azure East US pricing (July 2026 estimates)

## Monthly Cost Breakdown (Production)

| Category | Service | Specification | Monthly Cost (USD) |
|----------|---------|---------------|-------------------|
| **Compute** | AKS (app pool) | 5x D4s_v5 (reserved) | $1,200 |
| | AKS (AI workers) | 3x D4s_v5 (spot) | $270 |
| | AKS (system) | 2x D2s_v5 | $140 |
| **Database** | PostgreSQL Flexible | GP D4s_v3 + 256GB + HA | $650 |
| | PgBouncer (in-cluster) | Included in AKS | $0 |
| **Cache** | Azure Cache Redis | Premium P1 (6GB) | $400 |
| **AI** | Azure OpenAI GPT-5.5 | 75M tokens/month | $3,750 |
| | Azure Speech | 500K minutes/month | $1,000 |
| **Storage** | Blob Storage | 500GB hot + 2TB cool | $85 |
| **Networking** | Front Door + bandwidth | 5TB egress | $350 |
| **Monitoring** | App Insights + Grafana Cloud | 50GB logs/month | $200 |
| **Secrets** | Key Vault | 10K operations | $5 |
| **CI/CD** | GitHub Actions | 5K minutes | $0 (included) |
| **Container Registry** | ACR Premium | 100GB | $50 |
| | | **Total** | **~$8,100/mo** |

## Cost Per User

| Metric | Value |
|--------|-------|
| Cost per MAU | $0.16/month |
| Cost per registered user | $0.008/month |
| Cost per AI assessment | ~$0.05 |
| Cost per conversation turn | ~$0.02 |

## Scaling Projections

| Users (MAU) | Monthly Cost | Cost/MAU |
|-------------|-------------|----------|
| 10K | $2,500 | $0.25 |
| 50K | $8,100 | $0.16 |
| 200K | $22,000 | $0.11 |
| 500K | $45,000 | $0.09 |
| 1M | $75,000 | $0.075 |

*Economies of scale from reserved instances, token caching, and right-sizing.*

## Cost Optimization Opportunities

| Optimization | Estimated Savings | Implementation |
|-------------|-------------------|----------------|
| 1-year reserved AKS nodes | $400/mo (25%) | Terraform reserved capacity |
| Spot nodes for AI workers | $540/mo (67% of worker cost) | Already planned |
| AI response caching | $750/mo (20% of AI) | Redis cache for common prompts |
| PG read replicas for analytics | Avoid $200 upgrade | Route analytics to replica |
| CDN for static assets | $100/mo bandwidth | Front Door caching rules |
| Off-peak scaling (AI workers) | $135/mo (50% worker) | HPA scale-to-zero nights |
| Storage lifecycle policies | $30/mo | Auto-tier after 30/90 days |

**Optimized monthly cost: ~$6,200/mo (24% reduction)**

## Revenue Model (Reference)

| Tier | Price/user/mo | Break-even MAU |
|------|--------------|----------------|
| Free | $0 | N/A (acquisition) |
| Pro ($19/mo) | $19 | 430 paying users |
| Enterprise ($49/user/mo) | $49 | 170 paying users |

## Dev/Staging Environments

| Environment | Monthly Cost |
|-------------|-------------|
| Dev (local Docker) | $0 |
| Staging (AKS 1-node + Burstable PG) | ~$350 |
| **Total non-prod** | **~$350/mo** |
