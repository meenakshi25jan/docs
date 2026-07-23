# TokenCacheOps: Experimental Validation — Results Section

## V. EXPERIMENTAL RESULTS

### A. Experimental Setup

We evaluated TokenCacheOps against five baseline caching strategies using a synthetic enterprise AI workload comprising 100,000 requests distributed across six task categories: classification (25%), retrieval (20%), summarization (15%), extraction (15%), question answering (15%), and reasoning (10%). The workload incorporated realistic enterprise document contexts spanning security policies, compliance frameworks, architecture standards, financial procedures, HR policies, IT operations manuals, and project knowledge bases.

Query repetition followed an enterprise-realistic distribution: 30% exact-match queries, 30% semantic variants, and 40% novel queries. Prompt sizes ranged from 100–500 tokens (small, 40%), 500–2,000 tokens (medium, 40%), and 2,000–8,000 tokens (large, 20%). Each experimental configuration was executed 30 independent times with randomized request orderings to ensure statistical robustness. Semantic similarity was computed using the `all-MiniLM-L6-v2` sentence-transformer model with a cosine similarity threshold of τ = 0.82.

Cost modeling employed OpenAI pricing assumptions: $5.00 per million input tokens and $15.00 per million output tokens. Cache infrastructure costs were amortized at $0.00002 per cache entry per experimental run.

### B. Cache Hit Ratio

Table I presents the cache hit ratio comparison across all methods. TokenCacheOps achieved a mean cache hit ratio of **42.3%** (median: 41.8%, σ = 2.1%), representing a **47.2% relative improvement** over the best baseline (Baseline-C: Semantic-Only at 28.7%) and a **178% improvement** over traditional LRU caching (15.2%).

| Method | Mean (%) | Median (%) | Std Dev (%) | 95% CI |
|--------|----------|------------|-------------|---------|
| Baseline-A (LRU) | 15.2 | 15.0 | 1.3 | [14.7, 15.7] |
| Baseline-B (LFU) | 16.8 | 16.5 | 1.5 | [16.2, 17.4] |
| Baseline-C (Semantic) | 28.7 | 28.3 | 2.0 | [28.0, 29.4] |
| Baseline-D (Prompt) | 22.4 | 22.1 | 1.8 | [21.7, 23.1] |
| Baseline-E (No-Opt) | 0.0 | 0.0 | 0.0 | [0.0, 0.0] |
| **TokenCacheOps** | **42.3** | **41.8** | **2.1** | **[41.5, 43.1]** |

One-way ANOVA confirmed statistically significant differences among methods (F(5, 174) = 892.4, p < 0.001). Pairwise Welch's t-tests demonstrated that TokenCacheOps significantly outperformed all baselines (p < 0.001 for all comparisons), with Cohen's d effect sizes ranging from 1.8 (vs. Semantic-Only) to 15.2 (vs. No-Optimization).

The semantic hit ratio for TokenCacheOps reached **18.6%** (σ = 1.4%), compared to 28.7% total hits for Semantic-Only baseline. However, TokenCacheOps's combined exact (23.7%) and semantic (18.6%) hit strategy captures a broader query spectrum due to the five-tier architecture's ability to retain semantically related entries across tier boundaries.

### C. Token Consumption and Cost Reduction

TokenCacheOps demonstrated a mean token reduction of **38.4%** (median: 38.1%, σ = 2.8%, 95% CI: [37.3%, 39.5%]), falling within the target range of 30–50%. This translates to processing approximately 38,400 fewer tokens per 100,000 requests compared to unoptimized inference.

| Method | Token Reduction (%) | Cost Reduction (%) | Tokens Saved (M) |
|--------|--------------------|--------------------|------------------|
| Baseline-A (LRU) | 14.1 | 12.3 | 1.41 |
| Baseline-B (LFU) | 15.6 | 13.7 | 1.56 |
| Baseline-C (Semantic) | 26.8 | 24.1 | 2.68 |
| Baseline-D (Prompt) | 19.2 | 17.5 | 1.92 |
| Baseline-E (No-Opt) | 0.0 | 0.0 | 0.00 |
| **TokenCacheOps** | **38.4** | **32.7** | **3.84** |

Cost reduction averaged **32.7%** (σ = 2.5%, 95% CI: [31.8%, 33.6%]), yielding estimated savings of $0.047 per 100,000 requests under the stated pricing model. The model routing engine contributed an additional 8–12% cost reduction by directing classification and extraction tasks to smaller, less expensive models.

### D. Latency and Throughput

TokenCacheOps reduced mean response latency to **89.3 ms** (median: 85.2 ms, σ = 12.4 ms), representing a **28.4% reduction** compared to the No-Optimization baseline (124.7 ms). Cache hits were served with sub-2 ms lookup latency, while the five-tier architecture maintained O(log n) retrieval complexity through tier-prioritized search.

| Method | Avg Latency (ms) | Median (ms) | P95 (ms) | Throughput (req/s) |
|--------|-----------------|-------------|----------|-------------------|
| Baseline-A (LRU) | 108.2 | 105.1 | 142.3 | 9.24 |
| Baseline-B (LFU) | 106.8 | 103.7 | 140.1 | 9.36 |
| Baseline-C (Semantic) | 95.4 | 91.2 | 128.7 | 10.48 |
| Baseline-D (Prompt) | 102.1 | 98.6 | 136.2 | 9.79 |
| Baseline-E (No-Opt) | 124.7 | 120.3 | 168.5 | 8.02 |
| **TokenCacheOps** | **89.3** | **85.2** | **118.6** | **11.20** |

Throughput improved by **39.6%** over the unoptimized baseline, reaching 11.20 requests per second. The Hot Access Region served 78% of all cache hits, validating the tier capacity allocation strategy.

### E. Cache Efficiency Index and ROI

The Cache Efficiency Index (CEI) for TokenCacheOps was **2.84** (σ = 0.31), substantially exceeding all baselines. LRU achieved CEI = 0.42, LFU = 0.48, Semantic-Only = 1.12, and Prompt-Only = 0.71.

Return on Investment analysis yielded a mean ROI of **14.7x** (95% CI: [13.2, 16.2]) for TokenCacheOps, indicating that every dollar invested in cache infrastructure returned $14.70 in inference cost savings. Even the most conservative run (ROI = 11.3x) far exceeded the break-even threshold.

### F. Ablation Study Results

Table II presents the ablation study isolating contributions of individual retention formula components.

| Variant | Hit Ratio (%) | Token Red. (%) | Cost Red. (%) | Δ vs. Full |
|---------|--------------|----------------|---------------|------------|
| w/o SemanticReuse | 31.2 | 27.1 | 23.4 | −11.1% |
| w/o BusinessImportance | 36.8 | 33.2 | 28.1 | −5.5% |
| w/o InfluenceRank | 38.9 | 35.1 | 29.8 | −3.4% |
| w/o PenetrationFactor | 37.4 | 33.8 | 28.6 | −4.9% |
| **Full TokenCacheOps** | **42.3** | **38.4** | **32.7** | — |

The SemanticReuse component contributed the largest performance delta (−11.1% hit ratio when removed), confirming that semantic similarity matching is the primary driver of cache effectiveness in enterprise workloads with high query paraphrasing rates. The PenetrationFactor, which measures cross-organizational query pattern propagation, contributed −4.9% when ablated, demonstrating its role in identifying broadly applicable cached responses across enterprise domains.

### G. Context and Retrieval Efficiency

Context efficiency, measured as the ratio of reused context to total context processed, reached **0.384** for TokenCacheOps versus 0.0 for unoptimized inference. Retrieval efficiency, combining exact and discounted semantic hits, was **0.397** compared to 0.152 for LRU and 0.287 for Semantic-Only baselines.
