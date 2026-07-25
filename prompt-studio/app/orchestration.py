from pathlib import Path

from app.config import Settings
from app.models import GenerateRequest, OutputFormat, StudioMode


def load_system_prompt(settings: Settings) -> str:
    path = settings.prompts_dir / "system_prompt.txt"
    if not path.is_file():
        raise FileNotFoundError(f"System prompt not found: {path}")
    return path.read_text(encoding="utf-8")


def resolve_mode(request: GenerateRequest) -> StudioMode:
    if request.mode != StudioMode.AUTO:
        return request.mode
    text = request.user_request.lower()
    if any(token in text for token in ("enterprise", "orchestrat", "multi-agent", "rag ", "tool")):
        return StudioMode.EXPERT
    if any(token in text for token in ("beginner", "simple", "easy", "student", "new to")):
        return StudioMode.BEGINNER
    return StudioMode.PROFESSIONAL


def build_user_message(request: GenerateRequest, mode: StudioMode) -> str:
    lines = [
        "Generate a production-ready prompt for the following request.",
        "",
        f"Requested mode: {mode.value}",
    ]
    if request.target_model:
        lines.append(f"Target model/platform: {request.target_model}")
    if request.output_format == OutputFormat.JSON:
        lines.append("Output format: JSON (use the JSON export schema from your instructions).")
    else:
        lines.append("Output format: Markdown (use the Prompt Studio Output structure).")

    lines.extend(["", "USER REQUEST:", request.user_request.strip()])
    return "\n".join(lines)


def build_messages(
    settings: Settings,
    request: GenerateRequest,
) -> tuple[list[dict[str, str]], StudioMode]:
    system_prompt = load_system_prompt(settings)
    mode = resolve_mode(request)
    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]

    for turn in request.conversation_history:
        messages.append(turn)

    messages.append({"role": "user", "content": build_user_message(request, mode)})
    return messages, mode
