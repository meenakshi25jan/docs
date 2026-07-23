"""Synthetic enterprise AI workload dataset generator."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from .config import (
    ENTERPRISE_CATEGORIES,
    EXACT_MATCH_RATIO,
    NEW_QUERY_RATIO,
    PROMPT_SIZE_DISTRIBUTION,
    PROMPT_SIZE_RANGES,
    SEMANTIC_VARIANT_RATIO,
    WORKLOAD_MIX,
)


ENTERPRISE_TEMPLATES: Dict[str, List[str]] = {
    "security_policy": [
        "Review access control policy for {system} under SOC2 requirements",
        "Evaluate MFA enforcement for {system} privileged accounts",
        "Assess data encryption standards for {system} at rest and in transit",
        "Analyze incident response procedures for {system} security breaches",
        "Validate network segmentation rules for {system} production environment",
    ],
    "compliance": [
        "Verify GDPR data retention compliance for {system} customer records",
        "Audit HIPAA safeguards for {system} healthcare data processing",
        "Check PCI-DSS requirements for {system} payment processing",
        "Review SOX controls for {system} financial reporting systems",
        "Assess ISO 27001 alignment for {system} information security program",
    ],
    "architecture_standards": [
        "Evaluate microservices decomposition strategy for {system}",
        "Review API gateway design patterns for {system} integration layer",
        "Assess event-driven architecture suitability for {system}",
        "Analyze container orchestration approach for {system} workloads",
        "Validate service mesh implementation for {system} inter-service communication",
    ],
    "financial_procedures": [
        "Review budget allocation process for {system} capital expenditure",
        "Analyze expense approval workflow for {system} operational costs",
        "Evaluate revenue recognition policy for {system} subscription services",
        "Assess procurement compliance for {system} vendor contracts",
        "Validate financial close procedures for {system} quarterly reporting",
    ],
    "hr_policies": [
        "Review remote work policy applicability to {system} engineering teams",
        "Evaluate performance review criteria for {system} project contributors",
        "Assess onboarding procedures for {system} new team members",
        "Analyze compensation benchmarking for {system} technical roles",
        "Validate diversity and inclusion initiatives for {system} hiring pipeline",
    ],
    "it_operations": [
        "Review SLA targets for {system} production availability",
        "Evaluate monitoring and alerting configuration for {system}",
        "Assess disaster recovery plan for {system} critical services",
        "Analyze capacity planning projections for {system} infrastructure",
        "Validate change management process for {system} deployments",
    ],
    "project_knowledge": [
        "Summarize sprint deliverables for {system} Q3 roadmap",
        "Extract key requirements from {system} stakeholder meeting notes",
        "Classify risk items identified in {system} project retrospective",
        "Answer questions about {system} technical debt backlog",
        "Reason through trade-offs for {system} technology migration path",
    ],
}

SYSTEMS = [
    "CloudPlatform", "DataLake", "CustomerPortal", "PaymentGateway",
    "IdentityService", "AnalyticsEngine", "MobileApp", "LegacyERP",
    "MLPipeline", "SecurityOps", "DevOpsToolchain", "ContentCMS",
]

SEMANTIC_VARIANT_PATTERNS = [
    ("Review", "Examine"),
    ("Evaluate", "Assess"),
    ("Analyze", "Investigate"),
    ("Validate", "Confirm"),
    ("Check", "Verify"),
    ("for", "regarding"),
    ("under", "in accordance with"),
    ("requirements", "specifications"),
    ("procedures", "protocols"),
    ("policy", "guideline"),
]


@dataclass
class WorkloadRequest:
    """Single synthetic enterprise AI request."""

    request_id: int
    task_type: str
    category: str
    query_text: str
    base_query_id: int
    repetition_type: str  # exact, semantic, new
    prompt_tokens: int
    output_tokens: int
    business_importance: float
    security_sensitivity: float
  # embedding filled later
    embedding: Optional[np.ndarray] = None


def _tokens_from_text(text: str) -> int:
    """Approximate token count (4 chars per token heuristic)."""
    return max(1, len(text) // 4)


def _generate_context_block(category: str, system: str, size_class: str) -> str:
    """Generate enterprise context document block."""
    base = (
        f"[{category.replace('_', ' ').title()}] System: {system}. "
        f"This document outlines enterprise standards, controls, and operational "
        f"requirements governing {system} within the organization. "
    )
    rng = PROMPT_SIZE_RANGES[size_class]
    target = np.random.randint(rng[0], rng[1] + 1) * 4
    filler_phrases = [
        "Stakeholders must ensure compliance with organizational policies.",
        "Regular audits and reviews are mandated quarterly.",
        "Risk assessments should be documented and tracked.",
        "Cross-functional teams coordinate implementation efforts.",
        "Metrics and KPIs measure operational effectiveness.",
        "Escalation paths are defined for exception handling.",
        "Training programs support policy awareness and adoption.",
    ]
    while len(base) < target:
        base += np.random.choice(filler_phrases) + " "
    return base[:target]


def _apply_semantic_variant(text: str) -> str:
    """Create semantic variant of query text with moderate divergence."""
    result = text
    n_changes = np.random.randint(4, 8)
    patterns = list(SEMANTIC_VARIANT_PATTERNS)
    np.random.shuffle(patterns)
    for old, new in patterns[:n_changes]:
        if old in result:
            result = result.replace(old, new, 1)
    # Add structural variation to reduce embedding similarity
    prefixes = [
        "Can you help me ",
        "I need to ",
        "Please assist with ",
        "Could you ",
    ]
    suffixes = [
        " for our team?",
        " as soon as possible.",
        " based on current guidelines.",
        " within the enterprise framework.",
    ]
    if result == text:
        result = np.random.choice(prefixes) + result[0].lower() + result[1:]
    result = result + np.random.choice(suffixes)
    return result


def _task_for_template(category: str, template_idx: int) -> str:
    """Map template to task type based on workload mix."""
    if category == "project_knowledge":
        tasks = ["summarization", "extraction", "classification", "question_answering", "reasoning"]
        return tasks[template_idx % len(tasks)]
    weights = list(WORKLOAD_MIX.keys())
    probs = list(WORKLOAD_MIX.values())
    return str(np.random.choice(weights, p=probs))


class DatasetGenerator:
    """Generate synthetic enterprise AI workload datasets."""

    def __init__(self, num_requests: int = 100_000, seed: int = 42):
        self.num_requests = num_requests
        self.seed = seed

    def generate(self) -> Tuple[pd.DataFrame, List[WorkloadRequest]]:
        """Generate full workload dataset."""
        np.random.seed(self.seed)
        base_queries: List[Dict] = []
        base_id = 0

        # Generate base query pool (~8% of total for repetition sources)
        pool_size = max(800, int(self.num_requests * 0.08))
        for _ in range(pool_size):
            category = str(np.random.choice(ENTERPRISE_CATEGORIES))
            templates = ENTERPRISE_TEMPLATES[category]
            template = templates[np.random.randint(len(templates))]
            system = str(np.random.choice(SYSTEMS))
            query = template.format(system=system)
            size_class = str(np.random.choice(
                list(PROMPT_SIZE_DISTRIBUTION.keys()),
                p=list(PROMPT_SIZE_DISTRIBUTION.values()),
            ))
            context = _generate_context_block(category, system, size_class)
            full_prompt = f"Context:\n{context}\n\nQuery: {query}"
            base_queries.append({
                "base_id": base_id,
                "category": category,
                "task_type": _task_for_template(category, base_id),
                "query_text": query,
                "full_prompt": full_prompt,
                "prompt_tokens": _tokens_from_text(full_prompt),
                "business_importance": np.random.beta(5, 2),
                "security_sensitivity": np.random.beta(2, 5) if category == "security_policy" else np.random.beta(1.5, 6),
            })
            base_id += 1

        requests: List[WorkloadRequest] = []
        rep_types = (
            ["exact"] * int(EXACT_MATCH_RATIO * 100)
            + ["semantic"] * int(SEMANTIC_VARIANT_RATIO * 100)
            + ["new"] * int(NEW_QUERY_RATIO * 100)
        )
        while len(rep_types) < 100:
            rep_types.append("new")
        rep_types = rep_types[:100]

        # Zipf popularity weights for repeated queries (realistic enterprise hot-spots)
        zipf_weights = 1.0 / (np.arange(1, pool_size + 1) ** 0.8)
        zipf_weights /= zipf_weights.sum()

        for i in range(self.num_requests):
            rep_type = str(np.random.choice(rep_types))
            if rep_type in ("exact", "semantic"):
                base = base_queries[int(np.random.choice(len(base_queries), p=zipf_weights))]
                query_text = base["query_text"]
                if rep_type == "semantic":
                    query_text = _apply_semantic_variant(query_text)
                category = base["category"]
                task_type = base["task_type"]
                prompt_tokens = base["prompt_tokens"] + np.random.randint(-20, 21)
                biz_imp = base["business_importance"]
                sec_sens = base["security_sensitivity"]
                base_query_id = base["base_id"]
            else:
                category = str(np.random.choice(ENTERPRISE_CATEGORIES))
                templates = ENTERPRISE_TEMPLATES[category]
                template = templates[np.random.randint(len(templates))]
                system = str(np.random.choice(SYSTEMS))
                query_text = template.format(system=system)
                # Ensure novel queries are unique to avoid accidental cache hits
                query_text = f"{query_text} [ref:{i}-{np.random.randint(1_000_000)}]"
                task_type = _task_for_template(category, i)
                size_class = str(np.random.choice(
                    list(PROMPT_SIZE_DISTRIBUTION.keys()),
                    p=list(PROMPT_SIZE_DISTRIBUTION.values()),
                ))
                context = _generate_context_block(category, system, size_class)
                full_prompt = f"Context:\n{context}\n\nQuery: {query_text}"
                prompt_tokens = _tokens_from_text(full_prompt)
                biz_imp = np.random.beta(5, 2)
                sec_sens = np.random.beta(2, 5) if category == "security_policy" else np.random.beta(1.5, 6)
                base_query_id = -1

            output_tokens = int(prompt_tokens * np.random.uniform(0.1, 0.4))
            output_tokens = max(20, min(output_tokens, 2000))

            requests.append(WorkloadRequest(
                request_id=i,
                task_type=task_type,
                category=category,
                query_text=query_text,
                base_query_id=base_query_id,
                repetition_type=rep_type,
                prompt_tokens=max(50, prompt_tokens),
                output_tokens=output_tokens,
                business_importance=float(biz_imp),
                security_sensitivity=float(sec_sens),
            ))

        df = pd.DataFrame([{
            "request_id": r.request_id,
            "task_type": r.task_type,
            "category": r.category,
            "query_text": r.query_text,
            "base_query_id": r.base_query_id,
            "repetition_type": r.repetition_type,
            "prompt_tokens": r.prompt_tokens,
            "output_tokens": r.output_tokens,
            "business_importance": r.business_importance,
            "security_sensitivity": r.security_sensitivity,
        } for r in requests])

        return df, requests

    @staticmethod
    def query_hash(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()[:16]
