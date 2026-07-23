#!/usr/bin/env python3
"""Generate IEEE paper sections from experiment results."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.statistics import confidence_interval, generate_ablation_table, generate_summary_table, run_statistical_analysis


def fmt_pct(val: float, std: float = 0.0) -> str:
    if std > 0:
        return f"{val:.1f}% ± {std:.1f}%"
    return f"{val:.1f}%"


def generate_results_section(results_df: pd.DataFrame, ablation_df: pd.DataFrame, stats: dict) -> str:
    methods = results_df["method"].unique()
    tco = results_df[results_df["method"] == "TokenCacheOps"]
    noopt = results_df[results_df["method"] == "Baseline-E (No-Opt)"]
    best_base = results_df[results_df["method"].str.startswith("Baseline")]["cache_hit_ratio"].max()

    hit_mean = tco["cache_hit_ratio"].mean() * 100
    hit_std = tco["cache_hit_ratio"].std() * 100
    hit_ci = confidence_interval(tco["cache_hit_ratio"].values * 100)

    token_mean = tco["token_reduction_pct"].mean()
    token_std = tco["token_reduction_pct"].std()
    token_ci = confidence_interval(tco["token_reduction_pct"].values)

    cost_mean = tco["cost_reduction_pct"].mean()
    cost_std = tco["cost_reduction_pct"].std()

    lat_tco = tco["avg_latency_ms"].mean()
    lat_no = noopt["avg_latency_ms"].mean()
    lat_red = (1 - lat_tco / lat_no) * 100

    hit_imp = (tco["cache_hit_ratio"].mean() / best_base - 1) * 100

    lines = [
        "# TokenCacheOps: Experimental Validation — Results Section\n",
        "## V. EXPERIMENTAL RESULTS\n",
        "### A. Experimental Setup\n",
        "We evaluated TokenCacheOps against five baseline caching strategies using a synthetic ",
        "enterprise AI workload comprising 100,000 requests across six task categories. ",
        f"Each configuration was executed {len(tco)} independent times with randomized request orderings.\n",
        "",
        "### B. Cache Hit Ratio\n",
        f"TokenCacheOps achieved a mean cache hit ratio of **{hit_mean:.1f}%** ",
        f"(median: {tco['cache_hit_ratio'].median()*100:.1f}%, σ = {hit_std:.1f}%), ",
        f"representing a **{hit_imp:.1f}% relative improvement** over the best baseline ",
        f"({best_base*100:.1f}%). The 95% confidence interval is [{hit_ci[0]:.1f}%, {hit_ci[1]:.1f}%].\n",
        "",
        "| Method | Mean (%) | Median (%) | Std Dev (%) | 95% CI |",
        "|--------|----------|------------|-------------|---------|",
    ]

    for method in methods:
        sub = results_df[results_df["method"] == method]
        data = sub["cache_hit_ratio"].values * 100
        ci = confidence_interval(data)
        lines.append(
            f"| {method} | {data.mean():.1f} | {np.median(data):.1f} | "
            f"{data.std(ddof=1):.1f} | [{ci[0]:.1f}, {ci[1]:.1f}] |"
        )

    anova = stats["cache_hit_ratio"]["anova"]
    lines.extend([
        "",
        f"One-way ANOVA: F = {anova['f_statistic']:.1f}, p = {anova['p_value']:.2e}.\n",
        "### C. Token Consumption and Cost Reduction\n",
        f"TokenCacheOps demonstrated **{fmt_pct(token_mean, token_std)}** token reduction ",
        f"(95% CI: [{token_ci[0]:.1f}%, {token_ci[1]:.1f}%]). ",
        f"Cost reduction averaged **{fmt_pct(cost_mean, cost_std)}**.\n",
        "",
        "### D. Latency and Throughput\n",
        f"Mean response latency: **{lat_tco:.1f} ms** ({lat_red:.1f}% reduction vs. No-Optimization baseline). ",
        f"Throughput: **{tco['throughput_rps'].mean():.1f} req/s**.\n",
        "",
        "### E. Cache Efficiency Index and ROI\n",
        f"CEI: **{tco['cache_efficiency_index'].mean():.2f}** (σ = {tco['cache_efficiency_index'].std():.2f}). ",
        f"ROI: **{tco['roi'].mean():.1f}x** (95% CI: [{confidence_interval(tco['roi'].values)[0]:.1f}, {confidence_interval(tco['roi'].values)[1]:.1f}]).\n",
        "",
        "### F. Ablation Study Results\n",
        "",
        "| Variant | Hit Ratio (%) | Token Red. (%) | Cost Red. (%) |",
        "|---------|--------------|----------------|---------------|",
    ])

    for variant in ablation_df["variant"].unique():
        sub = ablation_df[ablation_df["variant"] == variant]
        lines.append(
            f"| {variant} | {sub['cache_hit_ratio'].mean()*100:.1f} | "
            f"{sub['token_reduction_pct'].mean():.1f} | {sub['cost_reduction_pct'].mean():.1f} |"
        )

    lines.append("\n### G. Context and Retrieval Efficiency\n")
    lines.append(
        f"Context efficiency: **{tco['context_efficiency'].mean():.3f}**. "
        f"Retrieval efficiency: **{tco['retrieval_efficiency'].mean():.3f}**.\n"
    )
    return "\n".join(lines)


def main():
    output_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "outputs")
    results_df = pd.read_csv(output_dir / "data" / "experiment_results.csv")
    ablation_df = pd.read_csv(output_dir / "data" / "ablation_results.csv")

    stats = {}
    for metric in ["cache_hit_ratio", "token_reduction_pct", "cost_reduction_pct", "avg_latency_ms", "roi"]:
        stats[metric] = run_statistical_analysis(results_df, metric)

    paper_dir = Path(__file__).parent.parent / "paper"
    paper_dir.mkdir(exist_ok=True)
    (paper_dir / "results.md").write_text(generate_results_section(results_df, ablation_df, stats))

    summary = generate_summary_table(results_df)
    summary.to_csv(output_dir / "data" / "final_summary_table.csv", index=False)
    print(f"Generated paper/results.md from {output_dir}")

if __name__ == "__main__":
    main()
