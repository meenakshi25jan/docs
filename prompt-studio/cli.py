#!/usr/bin/env python3
"""CLI for Prompt Studio — generate prompts from the terminal."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Allow running from prompt-studio/ without installing as package
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.config import get_settings
from app.llm import LLMError, chat_completion
from app.models import GenerateRequest, OutputFormat, StudioMode
from app.orchestration import build_messages


async def run(args: argparse.Namespace) -> int:
    request = GenerateRequest(
        user_request=args.request,
        mode=StudioMode(args.mode),
        target_model=args.target_model,
        output_format=OutputFormat(args.format),
    )
    settings = get_settings()
    messages, mode = build_messages(settings, request)

    try:
        output, usage = await chat_completion(settings, messages)
    except LLMError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json_out:
        payload = {
            "output": output,
            "mode_used": mode.value,
            "model": settings.openai_model,
            "usage": usage,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(output)

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Prompt Studio CLI")
    parser.add_argument("request", help="Your prompt generation request")
    parser.add_argument(
        "--mode",
        choices=["auto", "beginner", "professional", "expert"],
        default="auto",
    )
    parser.add_argument("--target-model", default=None)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--json-out", action="store_true", help="Print full API-style JSON")
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args)))


if __name__ == "__main__":
    main()
