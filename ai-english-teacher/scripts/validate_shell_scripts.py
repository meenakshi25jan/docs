#!/usr/bin/env python3
"""Validate shell scripts for Bash vs POSIX sh compatibility (Render startup safety)."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AI_ROOT = REPO_ROOT / "ai-english-teacher"
RENDER_FILE = REPO_ROOT / "render.yaml"

BASH_SHEBANGS = ("#!/usr/bin/env bash", "#/bin/bash", "#/usr/bin/bash")

# Patterns that require bash when present in a script
BASH_ONLY_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("set -o pipefail", re.compile(r"set\s+-[a-zA-Z]*o\s+pipefail")),
    ("[[ ... ]]", re.compile(r"\[\[")),
    ("(( arithmetic ))", re.compile(r"\(\([^)]+\)\)")),
    ("source", re.compile(r"(?<![\w-])source\s+")),
    ("declare", re.compile(r"\bdeclare\s+")),
    ("BASH_SOURCE", re.compile(r"BASH_SOURCE")),
    ("process substitution", re.compile(r"[<(]\s*\(")),
]

FORBIDDEN_RENDER_START = [
    re.compile(r"startCommand:\s*\./start\.sh\s*$", re.M),
    re.compile(r"startCommand:\s*sh\s+\./start\.sh", re.M),
]


def is_bash_shebang(first_line: str) -> bool:
    line = first_line.strip()
    return any(line.startswith(s) for s in BASH_SHEBANGS)


def audit_shell_file(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    first = lines[0] if lines else ""
    bash_script = is_bash_shebang(first)

    for label, pattern in BASH_ONLY_PATTERNS:
        if pattern.search(text) and not bash_script:
            errors.append(
                f"{path}: uses bash-only syntax ({label}) but shebang is not bash: {first!r}"
            )

    if path.name == "start.sh" and not bash_script:
        errors.append(f"{path}: production start.sh must use #!/usr/bin/env bash")

    if path.name == "start.sh" and not os.access(path, os.X_OK):
        errors.append(f"{path}: start.sh must be executable (git mode 100755; buildCommand chmod +x)")

    return errors


def find_shell_scripts() -> list[Path]:
    scripts: list[Path] = []
    for base in (AI_ROOT, REPO_ROOT / "archive"):
        if not base.is_dir():
            continue
        for path in base.rglob("*.sh"):
            if "node_modules" in path.parts or ".next" in path.parts:
                continue
            scripts.append(path)
    return sorted(scripts)


def audit_render_yaml() -> list[str]:
    errors: list[str] = []
    if not RENDER_FILE.is_file():
        return [f"missing {RENDER_FILE}"]
    text = RENDER_FILE.read_text(encoding="utf-8")
    if "bash ./start.sh" not in text:
        errors.append("render.yaml API must use startCommand: bash ./start.sh")
    for pattern in FORBIDDEN_RENDER_START:
        if pattern.search(text):
            errors.append(
                "render.yaml must not use startCommand: ./start.sh or sh ./start.sh "
                "(use bash ./start.sh)"
            )
    return errors


def run_shellcheck(scripts: list[Path]) -> list[str]:
    errors: list[str] = []
    try:
        subprocess.run(["shellcheck", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("NOTE: shellcheck not installed — skipping external lint")
        return errors

    bash_scripts = [p for p in scripts if is_bash_shebang(p.read_text(encoding="utf-8").splitlines()[0])]
    if not bash_scripts:
        return errors

    result = subprocess.run(
        ["shellcheck", "-S", "error", "-x", *[str(p) for p in bash_scripts]],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        errors.append(f"shellcheck failed:\n{result.stdout}\n{result.stderr}")
    return errors


def main() -> int:
    errors: list[str] = []
    scripts = find_shell_scripts()

    print("Shell script audit")
    print("==================")
    for path in scripts:
        rel = path.relative_to(REPO_ROOT)
        first = path.read_text(encoding="utf-8").splitlines()[0] if path.read_text(encoding="utf-8") else ""
        bash_only = []
        text = path.read_text(encoding="utf-8")
        for label, pattern in BASH_ONLY_PATTERNS:
            if pattern.search(text):
                bash_only.append(label)
        compat = "bash" if is_bash_shebang(first) else "sh/unknown"
        print(f"  {rel}")
        print(f"    shebang: {first.strip()}")
        print(f"    runtime: {compat}")
        if bash_only:
            print(f"    bash features: {', '.join(bash_only)}")
        errors.extend(audit_shell_file(path))

    print()
    errors.extend(audit_render_yaml())
    errors.extend(run_shellcheck(scripts))

    if errors:
        print("Shell validation FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"OK: {len(scripts)} shell script(s), render.yaml start command validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
