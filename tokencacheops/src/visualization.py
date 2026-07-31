"""Publication-quality figure generation."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

plt.style.use("seaborn-v0_8-whitegrid")
COLORS = {
    "Baseline-A (LRU)": "#4C72B0",
    "Baseline-B (LFU)": "#55A868",
    "Baseline-C (Semantic)": "#C44E52",
    "Baseline-D (Prompt)": "#8172B2",
    "Baseline-E (No-Opt)": "#CCB974",
    "TokenCacheOps": "#E74C3C",
}


def _method_colors(methods):
    return [COLORS.get(m, "#333333") for m in methods]


def figure1_architecture(output_dir: Path) -> None:
    """Figure 1: TokenCacheOps Architecture Diagram."""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    tiers = [
        ("Strategic Region", 9.0, "#2E86AB", "High business-value\nlong-term retention"),
        ("Evaluation Region", 7.5, "#A23B72", "Candidate promotion\nassessment zone"),
        ("Hot Access Region", 6.0, "#F18F01", "Frequent access\nlow-latency retrieval"),
        ("Archive Region", 4.5, "#C73E1D", "Infrequent but\nsemantically valuable"),
        ("Disposal Region", 3.0, "#6C757D", "Eviction staging\nand TTL expiry"),
    ]

    for name, y, color, desc in tiers:
        rect = plt.Rectangle((1, y - 0.5), 8, 0.9, facecolor=color, alpha=0.7, edgecolor="black", linewidth=1.5)
        ax.add_patch(rect)
        ax.text(5, y, name, ha="center", va="center", fontsize=12, fontweight="bold", color="white")
        ax.text(9.2, y, desc, ha="left", va="center", fontsize=8, style="italic")

    components = [
        (1.5, 1.2, "Semantic\nSimilarity\nEngine"),
        (4.0, 1.2, "Retention\nScore\nCalculator"),
        (6.5, 1.2, "Model\nRouting\nEngine"),
        (9.0, 1.2, "FinOps\nGovernance\nLayer"),
    ]
    for x, y, label in components:
        circle = plt.Circle((x, y), 0.6, facecolor="#E8E8E8", edgecolor="black", linewidth=1.2)
        ax.add_patch(circle)
        ax.text(x, y, label, ha="center", va="center", fontsize=7, fontweight="bold")

    ax.annotate("", xy=(5, 5.5), xytext=(5, 2.0),
                arrowprops=dict(arrowstyle="->", color="black", lw=1.5))
    ax.text(5.3, 3.8, "Retention\nScoring", fontsize=8)

    ax.set_title("TokenCacheOps: Five-Tier Cache Architecture", fontsize=16, fontweight="bold", pad=20)
    fig.tight_layout()
    fig.savefig(output_dir / "figure1_architecture.png", dpi=300, bbox_inches="tight")
    fig.savefig(output_dir / "figure1_architecture.pdf", bbox_inches="tight")
    plt.close(fig)


def figure2_cache_hit_rate(results_df: pd.DataFrame, output_dir: Path) -> None:
    """Figure 2: Cache Hit Rate Comparison."""
    fig, ax = plt.subplots(figsize=(10, 6))
    methods = results_df["method"].unique()
    means = [results_df[results_df["method"] == m]["cache_hit_ratio"].mean() * 100 for m in methods]
    stds = [results_df[results_df["method"] == m]["cache_hit_ratio"].std() * 100 for m in methods]

    bars = ax.bar(range(len(methods)), means, yerr=stds, capsize=5,
                  color=_method_colors(methods), edgecolor="black", linewidth=0.8)
    ax.set_xticks(range(len(methods)))
    ax.set_xticklabels([m.replace("Baseline-", "B-").replace(" (", "\n(") for m in methods],
                       fontsize=9, rotation=0)
    ax.set_ylabel("Cache Hit Ratio (%)", fontsize=12)
    ax.set_title("Cache Hit Rate Comparison Across Methods", fontsize=14, fontweight="bold")
    ax.set_ylim(0, max(means) * 1.25)

    for bar, mean in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"{mean:.1f}%", ha="center", va="bottom", fontsize=9, fontweight="bold")

    fig.tight_layout()
    fig.savefig(output_dir / "figure2_cache_hit_rate.png", dpi=300, bbox_inches="tight")
    fig.savefig(output_dir / "figure2_cache_hit_rate.pdf", bbox_inches="tight")
    plt.close(fig)


def figure3_token_savings(results_df: pd.DataFrame, output_dir: Path) -> None:
    """Figure 3: Token Savings Comparison."""
    fig, ax = plt.subplots(figsize=(10, 6))
    methods = results_df["method"].unique()
    means = [results_df[results_df["method"] == m]["token_reduction_pct"].mean() for m in methods]
    stds = [results_df[results_df["method"] == m]["token_reduction_pct"].std() for m in methods]

    bars = ax.barh(range(len(methods)), means, xerr=stds, capsize=5,
                   color=_method_colors(methods), edgecolor="black", linewidth=0.8)
    ax.set_yticks(range(len(methods)))
    ax.set_yticklabels(methods, fontsize=9)
    ax.set_xlabel("Token Reduction (%)", fontsize=12)
    ax.set_title("Token Savings Comparison", fontsize=14, fontweight="bold")

    for bar, mean in zip(bars, means):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{mean:.1f}%", ha="left", va="center", fontsize=9, fontweight="bold")

    fig.tight_layout()
    fig.savefig(output_dir / "figure3_token_savings.png", dpi=300, bbox_inches="tight")
    fig.savefig(output_dir / "figure3_token_savings.pdf", bbox_inches="tight")
    plt.close(fig)


def figure4_latency(results_df: pd.DataFrame, output_dir: Path) -> None:
    """Figure 4: Latency Comparison."""
    fig, ax = plt.subplots(figsize=(10, 6))
    methods = results_df["method"].unique()
    data = [results_df[results_df["method"] == m]["avg_latency_ms"].values for m in methods]

    bp = ax.boxplot(data, tick_labels=[m.replace("Baseline-", "B-") for m in methods],
                    patch_artist=True, widths=0.6)
    for patch, method in zip(bp["boxes"], methods):
        patch.set_facecolor(COLORS.get(method, "#333333"))
        patch.set_alpha(0.7)

    ax.set_ylabel("Average Response Latency (ms)", fontsize=12)
    ax.set_title("Response Latency Distribution", fontsize=14, fontweight="bold")
    plt.xticks(rotation=15, ha="right", fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "figure4_latency.png", dpi=300, bbox_inches="tight")
    fig.savefig(output_dir / "figure4_latency.pdf", bbox_inches="tight")
    plt.close(fig)


def figure5_cost_reduction(results_df: pd.DataFrame, output_dir: Path) -> None:
    """Figure 5: Cost Reduction."""
    fig, ax = plt.subplots(figsize=(10, 6))
    methods = results_df["method"].unique()
    means = [results_df[results_df["method"] == m]["cost_reduction_pct"].mean() for m in methods]
    stds = [results_df[results_df["method"] == m]["cost_reduction_pct"].std() for m in methods]

    ax.bar(range(len(methods)), means, yerr=stds, capsize=5,
           color=_method_colors(methods), edgecolor="black", linewidth=0.8)
    ax.set_xticks(range(len(methods)))
    ax.set_xticklabels([m.replace("Baseline-", "B-") for m in methods], fontsize=8, rotation=15, ha="right")
    ax.set_ylabel("Cost Reduction (%)", fontsize=12)
    ax.set_title("AI Inference Cost Reduction", fontsize=14, fontweight="bold")
    ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(output_dir / "figure5_cost_reduction.png", dpi=300, bbox_inches="tight")
    fig.savefig(output_dir / "figure5_cost_reduction.pdf", bbox_inches="tight")
    plt.close(fig)


def figure6_ablation(ablation_df: pd.DataFrame, output_dir: Path) -> None:
    """Figure 6: Ablation Study."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    metrics = ["cache_hit_ratio", "token_reduction_pct", "cost_reduction_pct"]
    titles = ["Cache Hit Ratio", "Token Reduction (%)", "Cost Reduction (%)"]

    variants = ablation_df["variant"].unique()
    x = np.arange(len(variants))
    width = 0.25

    for ax, metric, title in zip(axes, metrics, titles):
        means = [ablation_df[ablation_df["variant"] == v][metric].mean() for v in variants]
        if metric == "cache_hit_ratio":
            means = [m * 100 for m in means]
        stds = [ablation_df[ablation_df["variant"] == v][metric].std() for v in variants]
        if metric == "cache_hit_ratio":
            stds = [s * 100 for s in stds]

        colors = ["#E74C3C" if v == "Full TokenCacheOps" else "#95A5A6" for v in variants]
        ax.bar(x, means, yerr=stds, capsize=4, color=colors, edgecolor="black", linewidth=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels([v.replace("w/o ", "−").replace("Full ", "") for v in variants],
                           rotation=30, ha="right", fontsize=7)
        ax.set_title(title, fontsize=11, fontweight="bold")

    fig.suptitle("Ablation Study: Component Contribution Analysis", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(output_dir / "figure6_ablation.png", dpi=300, bbox_inches="tight")
    fig.savefig(output_dir / "figure6_ablation.pdf", bbox_inches="tight")
    plt.close(fig)


def figure7_roi(results_df: pd.DataFrame, output_dir: Path) -> None:
    """Figure 7: ROI Analysis."""
    fig, ax = plt.subplots(figsize=(10, 6))
    methods = [m for m in results_df["method"].unique() if m != "Baseline-E (No-Opt)"]
    means = [results_df[results_df["method"] == m]["roi"].mean() for m in methods]
    stds = [results_df[results_df["method"] == m]["roi"].std() for m in methods]

    ax.errorbar(range(len(methods)), means, yerr=stds, fmt="o-", markersize=8,
                linewidth=2, capsize=5, color="#2E86AB", ecolor="#666666")
    ax.fill_between(range(len(methods)),
                    [m - s for m, s in zip(means, stds)],
                    [m + s for m, s in zip(means, stds)],
                    alpha=0.2, color="#2E86AB")
    ax.set_xticks(range(len(methods)))
    ax.set_xticklabels([m.replace("Baseline-", "B-") for m in methods], fontsize=8, rotation=15, ha="right")
    ax.set_ylabel("Return on Investment (ROI)", fontsize=12)
    ax.set_title("ROI Analysis: Cost Savings vs. Cache Infrastructure", fontsize=14, fontweight="bold")
    ax.axhline(y=0, color="red", linestyle="--", alpha=0.5, label="Break-even")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "figure7_roi.png", dpi=300, bbox_inches="tight")
    fig.savefig(output_dir / "figure7_roi.pdf", bbox_inches="tight")
    plt.close(fig)


def figure8_retention_heatmap(ablation_df: pd.DataFrame, output_dir: Path) -> None:
    """Figure 8: Retention Score Heat Map."""
    from .config import RETENTION_WEIGHTS

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Weight heatmap
    weights = RETENTION_WEIGHTS
    w_names = list(weights.keys())
    w_vals = list(weights.values())
    ax1 = axes[0]
    im1 = ax1.imshow([w_vals], cmap="YlOrRd", aspect="auto")
    ax1.set_xticks(range(len(w_names)))
    ax1.set_xticklabels([n.replace("_", "\n") for n in w_names], fontsize=8)
    ax1.set_yticks([0])
    ax1.set_yticklabels(["Weight"])
    ax1.set_title("Retention Formula Weights", fontweight="bold")
    for i, v in enumerate(w_vals):
        ax1.text(i, 0, f"{v:.2f}", ha="center", va="center", fontsize=9, fontweight="bold")
    plt.colorbar(im1, ax=ax1, shrink=0.6)

    # Ablation impact heatmap
    ax2 = axes[1]
    variants = ablation_df["variant"].unique()
    metrics = ["cache_hit_ratio", "token_reduction_pct", "cost_reduction_pct", "roi"]
    matrix = []
    for v in variants:
        row = []
        for m in metrics:
            val = ablation_df[ablation_df["variant"] == v][m].mean()
            if m == "cache_hit_ratio":
                val *= 100
            row.append(val)
        matrix.append(row)

    im2 = ax2.imshow(matrix, cmap="RdYlGn", aspect="auto")
    ax2.set_xticks(range(len(metrics)))
    ax2.set_xticklabels(["Hit Ratio\n(%)", "Token Red.\n(%)", "Cost Red.\n(%)", "ROI"], fontsize=9)
    ax2.set_yticks(range(len(variants)))
    ax2.set_yticklabels([v.replace("w/o ", "−") for v in variants], fontsize=8)
    ax2.set_title("Ablation Impact Matrix", fontweight="bold")
    plt.colorbar(im2, ax=ax2, shrink=0.6)

    for i in range(len(variants)):
        for j in range(len(metrics)):
            ax2.text(j, i, f"{matrix[i][j]:.1f}", ha="center", va="center", fontsize=8)

    fig.suptitle("Retention Score Analysis", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(output_dir / "figure8_retention_heatmap.png", dpi=300, bbox_inches="tight")
    fig.savefig(output_dir / "figure8_retention_heatmap.pdf", bbox_inches="tight")
    plt.close(fig)


def generate_all_figures(
    results_df: pd.DataFrame,
    ablation_df: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Generate all publication figures."""
    output_dir.mkdir(parents=True, exist_ok=True)
    figure1_architecture(output_dir)
    figure2_cache_hit_rate(results_df, output_dir)
    figure3_token_savings(results_df, output_dir)
    figure4_latency(results_df, output_dir)
    figure5_cost_reduction(results_df, output_dir)
    figure6_ablation(ablation_df, output_dir)
    figure7_roi(results_df, output_dir)
    figure8_retention_heatmap(ablation_df, output_dir)
    print(f"All figures saved to {output_dir}")
