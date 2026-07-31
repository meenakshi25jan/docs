"""Configuration constants for TokenCacheOps experiments."""

from dataclasses import dataclass, field
from typing import Dict

# OpenAI pricing (USD per million tokens)
INPUT_COST_PER_MILLION = 5.0
OUTPUT_COST_PER_MILLION = 15.0

# Workload distribution
WORKLOAD_MIX: Dict[str, float] = {
    "classification": 0.25,
    "retrieval": 0.20,
    "summarization": 0.15,
    "extraction": 0.15,
    "question_answering": 0.15,
    "reasoning": 0.10,
}

# Query repetition distribution
EXACT_MATCH_RATIO = 0.30
SEMANTIC_VARIANT_RATIO = 0.30
NEW_QUERY_RATIO = 0.40

# Prompt size ranges (tokens)
PROMPT_SIZE_RANGES = {
    "small": (100, 500),
    "medium": (500, 2000),
    "large": (2000, 8000),
}
PROMPT_SIZE_DISTRIBUTION = {"small": 0.40, "medium": 0.40, "large": 0.20}

# Experiment parameters
NUM_REQUESTS = 100_000
NUM_RUNS = 30
RANDOM_SEED = 42
SEMANTIC_THRESHOLD = 0.90
CACHE_CAPACITY = 1_500

# Model routing latencies (ms) and relative costs
MODEL_PROFILES = {
    "small": {"latency_ms": 45, "input_cost_mult": 0.15, "output_cost_mult": 0.15},
    "medium": {"latency_ms": 120, "input_cost_mult": 0.45, "output_cost_mult": 0.45},
    "frontier": {"latency_ms": 350, "input_cost_mult": 1.0, "output_cost_mult": 1.0},
}

TASK_MODEL_ROUTING = {
    "classification": "small",
    "extraction": "small",
    "retrieval": "medium",
    "summarization": "medium",
    "question_answering": "medium",
    "reasoning": "frontier",
}

# Retention formula weights (full TokenCacheOps)
RETENTION_WEIGHTS = {
    "recency": 0.15,
    "frequency": 0.12,
    "semantic_reuse": 0.18,
    "business_importance": 0.12,
    "influence_rank": 0.10,
    "penetration_factor": 0.13,
    "token_efficiency": 0.15,
    "freshness": 0.08,
    "security_sensitivity": 0.07,
}

# Five-tier cache capacity allocation (fraction of total)
TIER_CAPACITIES = {
    "strategic": 0.05,
    "evaluation": 0.10,
    "hot_access": 0.45,
    "archive": 0.30,
    "disposal": 0.10,
}

# Cache infrastructure cost (USD per entry per run, amortized)
CACHE_COST_PER_ENTRY = 0.01

# Enterprise document categories
ENTERPRISE_CATEGORIES = [
    "security_policy",
    "compliance",
    "architecture_standards",
    "financial_procedures",
    "hr_policies",
    "it_operations",
    "project_knowledge",
]


@dataclass
class ExperimentConfig:
    """Runtime experiment configuration."""

    num_requests: int = NUM_REQUESTS
    num_runs: int = NUM_RUNS
    random_seed: int = RANDOM_SEED
    semantic_threshold: float = SEMANTIC_THRESHOLD
    cache_capacity: int = CACHE_CAPACITY
    retention_weights: Dict[str, float] = field(default_factory=lambda: RETENTION_WEIGHTS.copy())
    output_dir: str = "outputs"
