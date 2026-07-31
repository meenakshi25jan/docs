# TokenCacheOps: Reproducibility Guide

## Overview

This guide provides step-by-step instructions to reproduce all experimental results presented in the TokenCacheOps research paper.

## System Requirements

- Python 3.9+
- 8 GB RAM minimum (16 GB recommended for full 100K request experiments)
- 2 GB disk space for outputs
- CPU with AVX2 support (for sentence-transformers)

## Installation

```bash
cd tokencacheops
pip install -r requirements.txt
```

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| numpy | ≥1.24.0 | Numerical computation |
| pandas | ≥2.0.0 | Data manipulation |
| scikit-learn | ≥1.3.0 | Cosine similarity |
| sentence-transformers | ≥2.2.0 | Semantic embeddings |
| matplotlib | ≥3.7.0 | Figure generation |
| seaborn | ≥0.12.0 | Statistical visualizations |
| scipy | ≥1.11.0 | Statistical tests |

## Running Experiments

### Full Experiment Suite (100K requests, 30 runs)

```bash
python scripts/run_experiments.py --num-requests 100000 --num-runs 30 --seed 42
```

Expected runtime: 45–90 minutes depending on hardware.

### Quick Validation (10K requests, 5 runs)

```bash
python scripts/run_experiments.py --quick
```

Expected runtime: 5–10 minutes.

### Custom Configuration

```bash
python scripts/run_experiments.py \
  --num-requests 50000 \
  --num-runs 15 \
  --seed 123 \
  --output-dir my_outputs
```

## Output Structure

```
outputs/
├── data/
│   ├── experiment_results.csv      # Raw per-run metrics (all methods)
│   ├── ablation_results.csv        # Ablation study per-run metrics
│   ├── workload_dataset.csv        # Generated synthetic dataset
│   ├── summary_table.csv           # Aggregated statistics with CI
│   ├── ablation_table.csv          # Ablation comparison table
│   └── statistical_analysis.json   # ANOVA, t-tests, effect sizes
├── figures/
│   ├── figure1_architecture.png/pdf
│   ├── figure2_cache_hit_rate.png/pdf
│   ├── figure3_token_savings.png/pdf
│   ├── figure4_latency.png/pdf
│   ├── figure5_cost_reduction.png/pdf
│   ├── figure6_ablation.png/pdf
│   ├── figure7_roi.png/pdf
│   └── figure8_retention_heatmap.png/pdf
```

## Reproducing Individual Components

### Dataset Generation Only

```python
from src.dataset_generator import DatasetGenerator
gen = DatasetGenerator(num_requests=100_000, seed=42)
df, requests = gen.generate()
df.to_csv("workload.csv", index=False)
```

### Single Method Simulation

```python
from src.config import ExperimentConfig
from src.simulation import SimulationEngine

config = ExperimentConfig(num_requests=100_000, num_runs=1)
engine = SimulationEngine(config)
engine.prepare_dataset()
metrics = engine.run_single("TokenCacheOps", run_id=0)
print(metrics.to_dict())
```

### Statistical Analysis

```python
import pandas as pd
from src.statistics import run_statistical_analysis, generate_summary_table

results = pd.read_csv("outputs/data/experiment_results.csv")
stats = run_statistical_analysis(results, "cache_hit_ratio")
summary = generate_summary_table(results)
```

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `NUM_REQUESTS` | 100,000 | Total workload requests |
| `NUM_RUNS` | 30 | Independent experimental runs |
| `RANDOM_SEED` | 42 | Reproducibility seed |
| `SEMANTIC_THRESHOLD` | 0.82 | Cosine similarity threshold |
| `CACHE_CAPACITY` | 10,000 | Maximum cache entries |
| `INPUT_COST_PER_MILLION` | $5.00 | Input token pricing |
| `OUTPUT_COST_PER_MILLION` | $15.00 | Output token pricing |

## Retention Formula

```
RetentionScore =
  w₁·Recency + w₂·Frequency + w₃·SemanticReuse +
  w₄·BusinessImportance + w₅·InfluenceRank + w₆·PenetrationFactor +
  w₇·TokenEfficiency + w₈·Freshness − w₉·SecuritySensitivity
```

Default weights: w₁=0.15, w₂=0.12, w₃=0.18, w₄=0.12, w₅=0.10, w₆=0.13, w₇=0.15, w₈=0.08, w₉=0.07

## Verification Checklist

- [ ] All 6 methods produce results in `experiment_results.csv`
- [ ] 30 runs per method (180 total rows in results)
- [ ] 5 ablation variants × 30 runs = 150 rows in ablation results
- [ ] TokenCacheOps cache hit ratio: 38–46%
- [ ] TokenCacheOps token reduction: 33–44%
- [ ] All 8 figures generated in PNG and PDF formats
- [ ] Statistical analysis JSON contains ANOVA p < 0.001

## Troubleshooting

**Memory Error**: Use `--quick` mode or reduce `--num-requests`.

**Slow Embedding**: The `all-MiniLM-L6-v2` model downloads (~90 MB) on first run. Subsequent runs use cached model.

**Import Errors**: Ensure you run from the `tokencacheops` directory or add it to `PYTHONPATH`.

## Citation

```bibtex
@article{tokencacheops2026,
  title={TokenCacheOps: A Cloud-Agnostic Architecture for Intelligent
         Token Optimization, Semantic Caching, and AI FinOps Governance},
  year={2026},
  note={Experimental validation framework}
}
```
