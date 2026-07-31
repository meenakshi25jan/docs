"""Chapter 99 — AI observability: metrics, drift, and alerts."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

import numpy as np

RNG = np.random.default_rng(42)


@dataclass
class MetricEvent:
    name: str
    value: float
    timestamp: int


@dataclass
class ObservabilityStack:
    window: int = 100
    events: dict[str, deque[float]] = field(default_factory=dict)
    alerts: list[str] = field(default_factory=list)

    def record(self, name: str, value: float) -> None:
        if name not in self.events:
            self.events[name] = deque(maxlen=self.window)
        self.events[name].append(value)

    def p99_latency(self) -> float:
        latencies = list(self.events.get("latency_ms", []))
        if not latencies:
            return 0.0
        return float(np.percentile(latencies, 99))

    def error_rate(self) -> float:
        errors = list(self.events.get("errors", []))
        if not errors:
            return 0.0
        return float(np.mean(errors))

    def detect_drift(self, baseline: np.ndarray, current: np.ndarray, threshold: float = 0.5) -> bool:
        base_mean, cur_mean = baseline.mean(), current.mean()
        base_std = baseline.std() + 1e-6
        z = abs(cur_mean - base_mean) / base_std
        if z > threshold:
            self.alerts.append(f"drift detected z={z:.2f}")
            return True
        return False

    def check_slos(self, max_p99: float = 200.0, max_error_rate: float = 0.05) -> bool:
        ok = True
        if self.p99_latency() > max_p99:
            self.alerts.append(f"p99 latency {self.p99_latency():.1f}ms exceeds {max_p99}")
            ok = False
        if self.error_rate() > max_error_rate:
            self.alerts.append(f"error rate {self.error_rate():.3f} exceeds {max_error_rate}")
            ok = False
        return ok


def main() -> float:
    stack = ObservabilityStack()
    for i in range(50):
        stack.record("latency_ms", float(RNG.normal(80, 10)))
        stack.record("errors", float(RNG.random() < 0.02))

    baseline = RNG.normal(0, 1, 200)
    current = RNG.normal(0.1, 1, 200)
    drift = stack.detect_drift(baseline, current, threshold=1.5)
    slo_ok = stack.check_slos()

    print(f"P99 latency: {stack.p99_latency():.1f} ms")
    print(f"Error rate:  {stack.error_rate():.3f}")
    print(f"Drift:       {drift}")
    print(f"SLO OK:      {slo_ok}")
    print(f"Alerts:      {stack.alerts}")
    print("SUCCESS: AI observability demo completed")
    return stack.p99_latency()


if __name__ == "__main__":
    main()
