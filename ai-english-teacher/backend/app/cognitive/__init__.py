"""Layer 1 — Cognitive Orchestration (event-driven control plane)."""

__all__ = ["CognitiveOrchestrator", "process_cognitive_turn"]


def __getattr__(name: str):
    if name in ("CognitiveOrchestrator", "process_cognitive_turn"):
        from app.cognitive.orchestrator import CognitiveOrchestrator, process_cognitive_turn
        return CognitiveOrchestrator if name == "CognitiveOrchestrator" else process_cognitive_turn
    raise AttributeError(name)
