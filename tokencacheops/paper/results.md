# TokenCacheOps: Experimental Validation — Results Section

## V. EXPERIMENTAL RESULTS

### A. Experimental Setup

We evaluated TokenCacheOps against five baseline caching strategies using a synthetic 
enterprise AI workload comprising 100,000 requests across six task categories. 
Each configuration was executed 30 independent times with randomized request orderings.


### B. Cache Hit Ratio

TokenCacheOps achieved a mean cache hit ratio of **56.4%** 
(median: 56.4%, σ = 0.2%), 
representing a **46.9% relative improvement** over the best baseline 
(38.4%). The 95% confidence interval is [56.3%, 56.4%].


| Method | Mean (%) | Median (%) | Std Dev (%) | 95% CI |
|--------|----------|------------|-------------|---------|
| Baseline-A (LRU) | 26.6 | 26.6 | 0.1 | [26.6, 26.6] |
| Baseline-B (LFU) | 36.6 | 36.6 | 0.1 | [36.6, 36.6] |
| Baseline-C (Semantic) | 38.2 | 38.2 | 0.1 | [38.2, 38.2] |
| Baseline-D (Prompt) | 17.4 | 17.4 | 0.1 | [17.4, 17.4] |
| Baseline-E (No-Opt) | 0.0 | 0.0 | 0.0 | [0.0, 0.0] |
| TokenCacheOps | 56.4 | 56.4 | 0.2 | [56.3, 56.4] |

One-way ANOVA: F = 1193522.6, p = 0.00e+00.

### C. Token Consumption and Cost Reduction

TokenCacheOps demonstrated **38.7% ± 0.3%** token reduction 
(95% CI: [38.5%, 38.8%]). 
Cost reduction averaged **45.6% ± 0.1%**.


### D. Latency and Throughput

Mean response latency: **52.0 ms** (85.1% reduction vs. No-Optimization baseline). 
Throughput: **19.2 req/s**.


### E. Cache Efficiency Index and ROI

CEI: **549.21** (σ = 5.10). 
ROI: **52.3x** (95% CI: [52.3, 52.4]).


### F. Ablation Study Results


| Variant | Hit Ratio (%) | Token Red. (%) | Cost Red. (%) |
|---------|--------------|----------------|---------------|
| w/o SemanticReuse | 55.6 | 37.8 | 45.8 |
| w/o BusinessImportance | 56.2 | 38.5 | 45.7 |
| w/o InfluenceRank | 56.4 | 38.7 | 45.6 |
| w/o PenetrationFactor | 56.4 | 38.5 | 45.6 |
| Full TokenCacheOps | 56.4 | 38.7 | 45.6 |

### G. Context and Retrieval Efficiency

Context efficiency: **0.325**. Retrieval efficiency: **0.492**.
