#!/usr/bin/env python3
"""Main experiment runner for TokenCacheOps evaluation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import ExperimentConfig
from src.simulation import SimulationEngine
from src.statistics import (
    generate_ablation_table,
    generate_summary_table,
    run_statistical_analysis,
)
from src.visualization import generate_all_figures


def main():
    parser = argparse.ArgumentParser(description="TokenCacheOps Experiment Runner")
    parser.add_argument("--num-requests", type=int, default=100_000)
    parser.add_argument("--num-runs", type=int, default=30)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=str, default="outputs")
    parser.add_argument("--quick", action="store_true", help="Quick mode: 10k requests, 5 runs")
    args = parser.parse_args()

    if args.quick:
        args.num_requests = 10_000
        args.num_runs = 5

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "figures").mkdir(exist_ok=True)
    (output_dir / "data").mkdir(exist_ok=True)

    config = ExperimentConfig(
        num_requests=args.num_requests,
        num_runs=args.num_runs,
        random_seed=args.seed,
        output_dir=str(output_dir),
    )

    print("=" * 60)
    print("TokenCacheOps Experimental Validation")
    print("=" * 60)
    print(f"Requests: {config.num_requests:,}")
    print(f"Runs: {config.num_runs}")
    print(f"Seed: {config.random_seed}")
    print("=" * 60)

    engine = SimulationEngine(config)
    results_df, ablation_df = engine.run_all_experiments(include_ablation=True)

    # Save raw results
    results_df.to_csv(output_dir / "data" / "experiment_results.csv", index=False)
    ablation_df.to_csv(output_dir / "data" / "ablation_results.csv", index=False)
    if engine.dataset_df is not None:
        engine.dataset_df.to_csv(output_dir / "data" / "workload_dataset.csv", index=False)

    # Summary tables
    summary_table = generate_summary_table(results_df)
    summary_table.to_csv(output_dir / "data" / "summary_table.csv", index=False)
    ablation_table = generate_ablation_table(ablation_df)
    ablation_table.to_csv(output_dir / "data" / "ablation_table.csv", index=False)

    # Statistical analysis
    stats_results = {}
    for metric in ["cache_hit_ratio", "token_reduction_pct", "cost_reduction_pct",
                    "avg_latency_ms", "throughput_rps", "roi"]:
        stats_results[metric] = run_statistical_analysis(results_df, metric)
    with open(output_dir / "data" / "statistical_analysis.json", "w") as f:
        json.dump(stats_results, f, indent=2, default=str)

    # Generate figures
    generate_all_figures(results_df, ablation_df, output_dir / "figures")

    # Print summary
    print("\n" + "=" * 60)
    print("EXPERIMENTAL RESULTS SUMMARY")
    print("=" * 60)
    tco = results_df[results_df["method"] == "TokenCacheOps"]
    print(f"\nTokenCacheOps Performance (n={config.num_runs}):")
    print(f"  Cache Hit Ratio:    {tco['cache_hit_ratio'].mean()*100:.1f}% ± {tco['cache_hit_ratio'].std()*100:.1f}%")
    print(f"  Token Reduction:    {tco['token_reduction_pct'].mean():.1f}% ± {tco['token_reduction_pct'].std():.1f}%")
    print(f"  Cost Reduction:     {tco['cost_reduction_pct'].mean():.1f}% ± {tco['cost_reduction_pct'].std():.1f}%")
    print(f"  Latency Reduction:  {(1 - tco['avg_latency_ms'].mean() / results_df[results_df['method']=='Baseline-E (No-Opt)']['avg_latency_ms'].mean())*100:.1f}%")
    print(f"  Throughput:         {tco['throughput_rps'].mean():.1f} req/s")
    print(f"  ROI:                {tco['roi'].mean():.1f}x")
    print(f"  CEI:                {tco['cache_efficiency_index'].mean():.2f}")

    print(f"\nOutputs saved to: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
