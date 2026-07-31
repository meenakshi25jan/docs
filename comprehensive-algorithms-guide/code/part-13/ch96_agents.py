"""Chapter 96 — AI agents and orchestration reference."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Tool:
    name: str
    fn: Callable[..., Any]
    description: str


@dataclass
class AgentState:
    goal: str
    steps: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)


class AgentOrchestrator:
    def __init__(self, tools: list[Tool]) -> None:
        self.tools = {t.name: t for t in tools}

    def plan(self, goal: str) -> list[str]:
        if "sum" in goal.lower():
            return ["calculator", "summarize"]
        if "search" in goal.lower():
            return ["search", "summarize"]
        return ["summarize"]

    def execute(self, goal: str) -> AgentState:
        state = AgentState(goal=goal)
        for tool_name in self.plan(goal):
            tool = self.tools[tool_name]
            if tool_name == "calculator":
                result = tool.fn(2, 3)
                state.context["calc"] = result
            elif tool_name == "search":
                result = tool.fn(goal)
                state.context["search"] = result
            else:
                result = tool.fn(state.context)
            state.steps.append(f"{tool_name}: {result}")
        return state


def calculator(a: int, b: int) -> int:
    return a + b


def search(query: str) -> str:
    return f"results for '{query}'"


def summarize(ctx: dict[str, Any]) -> str:
    return f"Summary of context keys: {list(ctx.keys())}"


def main() -> bool:
    tools = [
        Tool("calculator", calculator, "Add two numbers"),
        Tool("search", search, "Search knowledge base"),
        Tool("summarize", summarize, "Summarize gathered context"),
    ]
    orch = AgentOrchestrator(tools)
    state = orch.execute("compute sum and summarize")
    print(f"Goal: {state.goal}")
    for step in state.steps:
        print(f"  -> {step}")
    print("SUCCESS: Agent orchestration completed")
    return len(state.steps) >= 2


if __name__ == "__main__":
    main()
