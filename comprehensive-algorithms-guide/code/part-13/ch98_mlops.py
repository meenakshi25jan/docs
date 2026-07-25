"""Chapter 98 — MLOps deployment pipeline reference."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ModelArtifact:
    name: str
    version: str
    metrics: dict[str, float]
    path: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ModelRegistry:
    def __init__(self) -> None:
        self.artifacts: dict[str, list[ModelArtifact]] = {}

    def register(self, artifact: ModelArtifact) -> None:
        self.artifacts.setdefault(artifact.name, []).append(artifact)

    def promote(self, name: str, min_accuracy: float = 0.8) -> ModelArtifact | None:
        versions = self.artifacts.get(name, [])
        eligible = [a for a in versions if a.metrics.get("accuracy", 0) >= min_accuracy]
        if not eligible:
            return None
        return max(eligible, key=lambda a: a.metrics.get("accuracy", 0))


@dataclass
class DeploymentPipeline:
    registry: ModelRegistry
    stages: list[str] = field(default_factory=lambda: ["lint", "test", "train", "evaluate", "register", "deploy"])

    def run(self, name: str, metrics: dict[str, float]) -> dict[str, Any]:
        log: dict[str, Any] = {"stages": [], "deployed": False}
        for stage in self.stages:
            log["stages"].append({"stage": stage, "status": "ok"})
        artifact = ModelArtifact(name=name, version="1.0.0", metrics=metrics, path=f"/models/{name}/1.0.0")
        self.registry.register(artifact)
        promoted = self.registry.promote(name)
        log["deployed"] = promoted is not None
        log["artifact"] = promoted
        return log


def export_manifest(artifact: ModelArtifact, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "name": artifact.name,
        "version": artifact.version,
        "metrics": artifact.metrics,
        "path": artifact.path,
        "created_at": artifact.created_at,
    }
    path = out_dir / f"{artifact.name}_{artifact.version}.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path


def main() -> bool:
    registry = ModelRegistry()
    pipeline = DeploymentPipeline(registry)
    result = pipeline.run("house-price", {"accuracy": 0.87, "rmse": 12000})
    artifact = result["artifact"]
    assert artifact is not None
    manifest = export_manifest(artifact, Path("/tmp/mlops_demo"))
    print(f"Deployed: {result['deployed']}")
    print(f"Manifest: {manifest}")
    print("SUCCESS: MLOps deployment pipeline completed")
    return bool(result["deployed"])


if __name__ == "__main__":
    main()
