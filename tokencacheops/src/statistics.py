"""Statistical validation: ANOVA, t-tests, effect sizes, confidence intervals."""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats


def confidence_interval(data: np.ndarray, confidence: float = 0.95) -> Tuple[float, float]:
    """Compute confidence interval for sample mean."""
    n = len(data)
    if n < 2:
        return float(np.mean(data)), float(np.mean(data))
    mean = np.mean(data)
    se = stats.sem(data)
    h = se * stats.t.ppf((1 + confidence) / 2, n - 1)
    return float(mean - h), float(mean + h)


def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Compute Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std == 0:
        return 0.0
    return float((np.mean(group1) - np.mean(group2)) / pooled_std)


def run_statistical_analysis(
    results_df: pd.DataFrame,
    metric: str = "cache_hit_ratio",
    reference_method: str = "TokenCacheOps",
) -> Dict:
    """Perform comprehensive statistical analysis."""
    methods = results_df["method"].unique()
    groups = [results_df[results_df["method"] == m][metric].values for m in methods]

    # One-way ANOVA
    f_stat, p_anova = stats.f_oneway(*groups)

    # Pairwise t-tests vs reference
    ttest_results = {}
    effect_sizes = {}
    ref_data = results_df[results_df["method"] == reference_method][metric].values

    for method in methods:
        if method == reference_method:
            continue
        method_data = results_df[results_df["method"] == method][metric].values
        t_stat, p_val = stats.ttest_ind(ref_data, method_data, equal_var=False)
        ttest_results[method] = {"t_statistic": float(t_stat), "p_value": float(p_val)}
        effect_sizes[method] = cohens_d(ref_data, method_data)

    # Summary statistics per method
    summary = {}
    for method in methods:
        data = results_df[results_df["method"] == method][metric].values
        ci_low, ci_high = confidence_interval(data)
        summary[method] = {
            "mean": float(np.mean(data)),
            "median": float(np.median(data)),
            "std": float(np.std(data, ddof=1)),
            "ci_95_low": ci_low,
            "ci_95_high": ci_high,
            "n": len(data),
        }

    return {
        "metric": metric,
        "anova": {"f_statistic": float(f_stat), "p_value": float(p_anova)},
        "summary": summary,
        "ttest_vs_reference": ttest_results,
        "effect_sizes_vs_reference": effect_sizes,
    }


def generate_summary_table(results_df: pd.DataFrame) -> pd.DataFrame:
    """Generate publication-ready summary statistics table."""
    metrics = [
        "cache_hit_ratio", "semantic_hit_ratio", "token_reduction_pct",
        "avg_latency_ms", "throughput_rps", "cost_reduction_pct",
        "cache_efficiency_index", "roi", "context_efficiency", "retrieval_efficiency",
    ]
    rows = []
    for method in results_df["method"].unique():
        subset = results_df[results_df["method"] == method]
        row = {"Method": method}
        for metric in metrics:
            data = subset[metric].values
            ci_low, ci_high = confidence_interval(data)
            row[f"{metric}_mean"] = np.mean(data)
            row[f"{metric}_median"] = np.median(data)
            row[f"{metric}_std"] = np.std(data, ddof=1)
            row[f"{metric}_ci_low"] = ci_low
            row[f"{metric}_ci_high"] = ci_high
        rows.append(row)
    return pd.DataFrame(rows)


def generate_ablation_table(ablation_df: pd.DataFrame) -> pd.DataFrame:
    """Generate ablation study comparison table."""
    metrics = ["cache_hit_ratio", "token_reduction_pct", "cost_reduction_pct", "avg_latency_ms", "roi"]
    rows = []
    for variant in ablation_df["variant"].unique():
        subset = ablation_df[ablation_df["variant"] == variant]
        row = {"Variant": variant}
        for metric in metrics:
            data = subset[metric].values
            row[f"{metric}_mean"] = np.mean(data)
            row[f"{metric}_std"] = np.std(data, ddof=1)
        rows.append(row)
    return pd.DataFrame(rows)
