"""Chapter 97 — Responsible AI and governance checks."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ModelCard:
    name: str
    intended_use: str
    limitations: list[str]
    metrics: dict[str, float]


@dataclass
class GovernanceReport:
    passed: bool
    checks: dict[str, bool]
    notes: list[str]


def demographic_parity_ratio(y_true_group_a: list[int], y_pred_group_a: list[int],
                             y_true_group_b: list[int], y_pred_group_b: list[int]) -> float:
    rate_a = sum(y_pred_group_a) / max(len(y_pred_group_a), 1)
    rate_b = sum(y_pred_group_b) / max(len(y_pred_group_b), 1)
    if rate_a == 0 and rate_b == 0:
        return 1.0
    return min(rate_a, rate_b) / max(rate_a, rate_b) if max(rate_a, rate_b) > 0 else 0.0


def run_governance_checks(card: ModelCard, fairness_ratio: float, has_pii_guard: bool) -> GovernanceReport:
    checks = {
        "model_card_complete": bool(card.name and card.intended_use and card.limitations),
        "fairness_threshold": fairness_ratio >= 0.8,
        "accuracy_documented": "accuracy" in card.metrics,
        "pii_guardrails": has_pii_guard,
    }
    notes = []
    if not checks["fairness_threshold"]:
        notes.append("Fairness ratio below 0.8 — review for disparate impact.")
    if not checks["pii_guardrails"]:
        notes.append("Enable PII detection before production.")
    return GovernanceReport(passed=all(checks.values()), checks=checks, notes=notes)


def main() -> bool:
    card = ModelCard(
        name="spam-classifier-v1",
        intended_use="Filter promotional email in enterprise inboxes",
        limitations=["English only", "Not for legal discovery"],
        metrics={"accuracy": 0.94, "f1": 0.91},
    )
    ratio = demographic_parity_ratio(
        [1, 0, 1, 0], [1, 0, 1, 0],
        [1, 0, 0, 1], [1, 0, 0, 1],
    )
    report = run_governance_checks(card, ratio, has_pii_guard=True)
    print(f"Model: {card.name}")
    print(f"Fairness ratio: {ratio:.2f}")
    for check, ok in report.checks.items():
        print(f"  {check}: {'PASS' if ok else 'FAIL'}")
    print(f"Overall: {'PASS' if report.passed else 'FAIL'}")
    print("SUCCESS: Responsible AI governance completed")
    return report.passed


if __name__ == "__main__":
    main()
