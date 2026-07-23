# TokenCacheOps

**A Cloud-Agnostic Architecture for Intelligent Token Optimization, Semantic Caching, and AI FinOps Governance**

## Overview

TokenCacheOps is a research framework for evaluating intelligent caching strategies in enterprise AI workloads. It implements five baseline methods and the proposed five-tier TokenCacheOps architecture with semantic similarity, retention scoring, and model routing.

## Quick Start

```bash
cd tokencacheops
pip install -r requirements.txt
python3 scripts/run_experiments.py --quick          # 10K requests, 5 runs
python3 scripts/run_experiments.py                  # 100K requests, 30 runs
```

## Project Structure

```
tokencacheops/
├── src/                    # Core framework
│   ├── baselines.py        # LRU, LFU, Semantic, Prompt, No-Opt
│   ├── tokencacheops.py    # Five-tier cache + retention formula
│   ├── simulation.py       # Experiment engine
│   ├── statistics.py       # ANOVA, t-tests, effect sizes
│   └── visualization.py    # Publication figures
├── scripts/
│   ├── run_experiments.py  # Main experiment runner
│   └── generate_paper.py   # Auto-generate results section
├── notebooks/
│   └── experiment.ipynb    # Interactive reproduction
├── paper/                  # IEEE-style paper sections
└── outputs/                # Generated results, figures, CSVs
```

## Retention Formula

```
RetentionScore = w₁·Recency + w₂·Frequency + w₃·SemanticReuse
              + w₄·BusinessImportance + w₅·InfluenceRank + w₆·PenetrationFactor
              + w₇·TokenEfficiency + w₈·Freshness − w₉·SecuritySensitivity
```

## Deliverables

1. Complete Python source code
2. Experiment notebook (`notebooks/experiment.ipynb`)
3. CSV result datasets (`outputs/data/`)
4. Publication figures (`outputs/figures/`)
5. IEEE-style paper sections (`paper/`)
6. Reproducibility guide (`REPRODUCIBILITY.md`)

See `REPRODUCIBILITY.md` for full reproduction instructions.
