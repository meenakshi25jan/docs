#!/usr/bin/env python3
"""
Universal Project Advisor
=========================
Detects your operating system and installed tools, then prints tailored
recommendations for ANY software project.

Works on: Windows, Linux, macOS

Usage:
    python scripts/project-advisor.py
    python scripts/project-advisor.py --project-type web
    python scripts/project-advisor.py --project-type ai --json
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class ToolStatus:
    name: str
    installed: bool
    version: str | None = None
    download_url: str | None = None
    install_hint: str | None = None


@dataclass
class OSProfile:
    system: str          # Windows, Linux, Darwin
    display_name: str    # Windows 11, Ubuntu 22.04, macOS Sonoma
    architecture: str    # x86_64, arm64
    shell: str           # powershell, bash, zsh
    package_manager: str # winget, apt, brew, etc.
    path_separator: str  # \ or /
    venv_activate: str   # command to activate virtualenv
    python_cmd: str      # python or python3


@dataclass
class ProjectAdvice:
    os: OSProfile
    project_type: str
    installed_tools: list[ToolStatus]
    missing_tools: list[ToolStatus]
    recommended_stack: dict[str, str]
    cloud_recommendation: dict[str, str]
    setup_steps: list[str]
    download_links: dict[str, str]
    cost_estimate: dict[str, str]
    next_commands: list[str]


# ---------------------------------------------------------------------------
# OS detection
# ---------------------------------------------------------------------------

def detect_os() -> OSProfile:
    """Detect operating system and return a profile with OS-specific hints."""
    system = platform.system()  # Windows, Linux, Darwin
    arch = platform.machine()   # x86_64, ARM64, etc.
    release = platform.release()

    if system == "Windows":
        display = f"Windows {release}"
        shell = "powershell"
        pkg_mgr = "winget" if shutil.which("winget") else "choco/manual"
        sep = "\\"
        venv = r".\.venv\Scripts\Activate.ps1"
        python_cmd = "python"
    elif system == "Darwin":
        display = f"macOS {platform.mac_ver()[0] or release}"
        shell = "zsh" if os.environ.get("SHELL", "").endswith("zsh") else "bash"
        pkg_mgr = "brew" if shutil.which("brew") else "manual"
        sep = "/"
        venv = "source .venv/bin/activate"
        python_cmd = "python3"
    else:
        # Linux and other Unix
        try:
            with open("/etc/os-release") as f:
                lines = dict(
                    line.strip().split("=", 1)
                    for line in f
                    if "=" in line
                )
            distro = lines.get("PRETTY_NAME", "Linux").strip('"')
        except OSError:
            distro = f"Linux {release}"
        display = distro
        shell = "bash"
        pkg_mgr = _detect_linux_pkg_manager()
        sep = "/"
        venv = "source .venv/bin/activate"
        python_cmd = "python3"

    return OSProfile(
        system=system,
        display_name=display,
        architecture=arch,
        shell=shell,
        package_manager=pkg_mgr,
        path_separator=sep,
        venv_activate=venv,
        python_cmd=python_cmd,
    )


def _detect_linux_pkg_manager() -> str:
    if shutil.which("apt"):
        return "apt"
    if shutil.which("dnf"):
        return "dnf"
    if shutil.which("yum"):
        return "yum"
    if shutil.which("pacman"):
        return "pacman"
    if shutil.which("zypper"):
        return "zypper"
    return "manual"


# ---------------------------------------------------------------------------
# Tool detection
# ---------------------------------------------------------------------------

def _run_version(cmd: list[str]) -> str | None:
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip().split("\n")[0]
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return None


def check_tool(name: str, cmd: list[str], url: str, install_hint: str) -> ToolStatus:
    version = _run_version(cmd)
    return ToolStatus(
        name=name,
        installed=version is not None,
        version=version,
        download_url=url,
        install_hint=install_hint,
    )


def detect_tools(os_profile: OSProfile) -> list[ToolStatus]:
    """Check which development tools are installed."""
    system = os_profile.system
    pkg = os_profile.package_manager

    install_hints = {
        "python": {
            "Windows": "winget install Python.Python.3.12  OR  https://www.python.org/downloads/ (check 'Add to PATH')",
            "Darwin": "brew install python@3.12",
            "Linux": f"sudo {pkg} install -y python3 python3-pip python3-venv" if pkg != "manual" else "https://www.python.org/downloads/",
        },
        "git": {
            "Windows": "winget install Git.Git  OR  https://git-scm.com/download/win",
            "Darwin": "brew install git",
            "Linux": f"sudo {pkg} install -y git" if pkg != "manual" else "https://git-scm.com/downloads",
        },
        "node": {
            "Windows": "winget install OpenJS.NodeJS.LTS  OR  https://nodejs.org/",
            "Darwin": "brew install node",
            "Linux": f"sudo {pkg} install -y nodejs npm" if pkg != "manual" else "https://nodejs.org/",
        },
        "docker": {
            "Windows": "https://www.docker.com/products/docker-desktop/",
            "Darwin": "brew install --cask docker  OR  https://www.docker.com/products/docker-desktop/",
            "Linux": f"https://docs.docker.com/engine/install/ ({pkg} based)",
        },
        "java": {
            "Windows": "winget install Microsoft.OpenJDK.17",
            "Darwin": "brew install openjdk@17",
            "Linux": f"sudo {pkg} install -y openjdk-17-jdk" if pkg != "manual" else "https://adoptium.net/",
        },
    }

    key = system if system in ("Windows", "Darwin") else "Linux"
    py_cmd = os_profile.python_cmd

    tools = [
        check_tool("Python", [py_cmd, "--version"], "https://www.python.org/downloads/", install_hints["python"][key]),
        check_tool("Git", ["git", "--version"], "https://git-scm.com/downloads", install_hints["git"][key]),
        check_tool("Node.js", ["node", "--version"], "https://nodejs.org/", install_hints["node"][key]),
        check_tool("npm", ["npm", "--version"], "https://nodejs.org/", install_hints["node"][key]),
        check_tool("Docker", ["docker", "--version"], "https://www.docker.com/", install_hints["docker"][key]),
        check_tool("Java", ["java", "-version"], "https://adoptium.net/", install_hints["java"][key]),
        check_tool("pip", [py_cmd, "-m", "pip", "--version"], "https://pip.pypa.io/", f"{py_cmd} -m ensurepip --upgrade"),
        check_tool("curl", ["curl", "--version"], "https://curl.se/", f"sudo {pkg} install curl" if pkg not in ("manual", "winget", "choco/manual") else "Install manually"),
        check_tool("VS Code", ["code", "--version"], "https://code.visualstudio.com/", install_hints.get("vscode", {}).get(key, "https://code.visualstudio.com/")),
    ]
    return tools


# ---------------------------------------------------------------------------
# Recommendations by project type
# ---------------------------------------------------------------------------

PROJECT_STACKS: dict[str, dict[str, str]] = {
    "web": {
        "frontend": "React or Next.js",
        "backend": "Node.js (Express) or Python (FastAPI)",
        "database": "PostgreSQL",
        "cache": "Redis (optional)",
        "hosting": "Vercel (frontend) + Render (backend)",
    },
    "api": {
        "language": "Python (FastAPI) or Node.js (Express)",
        "database": "PostgreSQL or SQLite (learning)",
        "docs": "Swagger (auto with FastAPI)",
        "hosting": "Render or Railway",
    },
    "ai": {
        "language": "Python",
        "framework": "FastAPI + LangChain (optional)",
        "llm": "Ollama (free local) → OpenAI (paid cloud)",
        "vector_db": "ChromaDB or Pinecone",
        "hosting": "Your PC first, then Railway/Render",
    },
    "mobile": {
        "framework": "Flutter (one codebase) or React Native",
        "backend": "Firebase or custom API",
        "database": "Firebase Firestore or PostgreSQL",
        "hosting": "Google Play + Apple App Store",
    },
    "desktop": {
        "framework": "Electron (JS) or Tauri (Rust) or Python (PyQt)",
        "database": "SQLite",
        "distribution": "GitHub Releases or Microsoft Store",
    },
    "data": {
        "language": "Python",
        "tools": "Pandas, Jupyter Notebook",
        "database": "PostgreSQL or SQLite",
        "visualization": "Matplotlib, Plotly",
        "hosting": "Local or Google Colab (free)",
    },
    "ecommerce": {
        "platform": "Shopify (no-code) or Medusa/Stripe (custom)",
        "frontend": "Next.js",
        "database": "PostgreSQL",
        "payments": "Stripe or Razorpay",
        "hosting": "Vercel + Render",
    },
    "general": {
        "language": "Python (easiest start) or Node.js (web focus)",
        "database": "SQLite (learn) → PostgreSQL (production)",
        "version_control": "Git + GitHub",
        "editor": "VS Code",
        "hosting": "Local → Render → DigitalOcean",
    },
}


CLOUD_BY_STAGE: dict[str, dict[str, str]] = {
    "learning": {
        "best": "Your own computer",
        "cost": "$0/month",
        "why": "Free, no credit card, instant feedback",
        "url": "N/A",
    },
    "first_deploy": {
        "best": "Render or Railway",
        "cost": "$0–7/month",
        "why": "Connect GitHub, click deploy, HTTPS free",
        "url": "https://render.com",
    },
    "small_production": {
        "best": "DigitalOcean or Hetzner",
        "cost": "$4–6/month",
        "why": "Predictable pricing, full server control",
        "url": "https://www.digitalocean.com",
    },
    "enterprise": {
        "best": "AWS or Google Cloud",
        "cost": "$50–500+/month",
        "why": "Maximum features, auto-scaling, compliance",
        "url": "https://aws.amazon.com",
    },
}


def get_os_download_links(os_profile: OSProfile) -> dict[str, str]:
    """Return official download links — same for all OS, install method differs."""
    return {
        "Python": "https://www.python.org/downloads/",
        "Git": "https://git-scm.com/downloads",
        "VS Code": "https://code.visualstudio.com/",
        "Node.js": "https://nodejs.org/",
        "Docker Desktop": "https://www.docker.com/products/docker-desktop/",
        "Postman": "https://www.postman.com/downloads/",
        "GitHub Desktop": "https://desktop.github.com/",
        "Java (OpenJDK)": "https://adoptium.net/",
        "Flutter": "https://docs.flutter.dev/get-started/install",
        "Android Studio": "https://developer.android.com/studio",
    }


def get_setup_steps(os_profile: OSProfile, project_type: str, missing: list[ToolStatus]) -> list[str]:
    """Generate OS-specific setup steps."""
    steps: list[str] = []
    system = os_profile.system
    py = os_profile.python_cmd
    venv = os_profile.venv_activate

    steps.append(f"Detected OS: {os_profile.display_name} ({os_profile.architecture})")
    steps.append(f"Package manager: {os_profile.package_manager}")
    steps.append(f"Shell: {os_profile.shell}")

    if missing:
        steps.append("")
        steps.append("STEP 1 — Install missing tools:")
        for tool in missing:
            steps.append(f"  • {tool.name}: {tool.install_hint}")

    steps.append("")
    steps.append("STEP 2 — Create project folder:")
    if system == "Windows":
        steps.append(r"  mkdir my-project && cd my-project")
    else:
        steps.append("  mkdir my-project && cd my-project")

    steps.append("")
    steps.append("STEP 3 — Initialize version control:")
    steps.append("  git init")
    steps.append("  git add .")
    steps.append('  git commit -m "Initial commit"')

    if project_type in ("ai", "api", "data", "general"):
        steps.append("")
        steps.append("STEP 4 — Python virtual environment:")
        steps.append(f"  {py} -m venv .venv")
        steps.append(f"  {venv}")
        steps.append("  pip install -r requirements.txt")

    if project_type in ("web", "mobile", "ecommerce"):
        steps.append("")
        steps.append("STEP 4 — Install Node.js dependencies:")
        steps.append("  npm install")

    steps.append("")
    steps.append("STEP 5 — Create .env file (never commit secrets):")
    if system == "Windows":
        steps.append("  copy .env.example .env")
    else:
        steps.append("  cp .env.example .env")

    steps.append("")
    steps.append("STEP 6 — Run tests:")
    if project_type in ("ai", "api", "data", "general"):
        steps.append("  pytest -v  OR  python -m pytest")
    else:
        steps.append("  npm test")

    steps.append("")
    steps.append("STEP 7 — Start development server:")
    if project_type == "web":
        steps.append("  npm run dev")
    elif project_type in ("ai", "api"):
        steps.append(f"  {py} -m app.main serve")
    else:
        steps.append(f"  {py} app.py  OR  npm start")

    return steps


def get_next_commands(os_profile: OSProfile, project_type: str) -> list[str]:
    """Immediate commands the user can run right now."""
    system = os_profile.system
    py = os_profile.python_cmd
    cmds: list[str] = []

    if system == "Windows":
        cmds.append("powershell -ExecutionPolicy Bypass -File scripts\\setup-windows.ps1")
    elif system == "Darwin":
        cmds.append("chmod +x scripts/setup-mac.sh && ./scripts/setup-mac.sh")
    else:
        cmds.append("chmod +x scripts/setup-linux.sh && ./scripts/setup-linux.sh")

    if project_type in ("ai", "api", "general"):
        cmds.append(f"{py} -m app.main search --query \"test\" --depth 1 --pages 3")
        cmds.append(f"{py} -m app.main serve")

    cmds.append("./scripts/health-check.sh  OR  curl http://localhost:8000/health")
    return cmds


def build_advice(project_type: str) -> ProjectAdvice:
    """Build complete advice for the current machine."""
    os_profile = detect_os()
    tools = detect_tools(os_profile)
    missing = [t for t in tools if not t.installed and t.name in ("Python", "Git", "pip")]
    optional_missing = [t for t in tools if not t.installed and t.name not in ("Python", "Git", "pip")]

    stack = PROJECT_STACKS.get(project_type, PROJECT_STACKS["general"])

    return ProjectAdvice(
        os=os_profile,
        project_type=project_type,
        installed_tools=[t for t in tools if t.installed],
        missing_tools=missing + optional_missing,
        recommended_stack=stack,
        cloud_recommendation=CLOUD_BY_STAGE,
        setup_steps=get_setup_steps(os_profile, project_type, missing + optional_missing),
        download_links=get_os_download_links(os_profile),
        cost_estimate={
            "learning_local": "$0/month",
            "first_cloud_deploy": "$0–7/month (Render/Railway free tier)",
            "small_production": "$10–25/month (VPS + domain)",
            "with_paid_ai": "+$5–50/month depending on usage",
        },
        next_commands=get_next_commands(os_profile, project_type),
    )


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def print_advice(advice: ProjectAdvice) -> None:
    """Print human-readable advice to terminal."""
    os_p = advice.os
    width = 64

    print()
    print("=" * width)
    print("  UNIVERSAL PROJECT ADVISOR")
    print("  Tailored recommendations for YOUR computer")
    print("=" * width)

    print(f"\n{'─' * width}")
    print("  YOUR SYSTEM")
    print(f"{'─' * width}")
    print(f"  OS:              {os_p.display_name}")
    print(f"  Architecture:    {os_p.architecture}")
    print(f"  Shell:           {os_p.shell}")
    print(f"  Package manager: {os_p.package_manager}")
    print(f"  Python command:  {os_p.python_cmd}")
    print(f"  Path separator:  {os_p.path_separator!r}")
    print(f"  Activate venv:   {os_p.venv_activate}")

    print(f"\n{'─' * width}")
    print(f"  PROJECT TYPE: {advice.project_type.upper()}")
    print(f"{'─' * width}")
    for key, value in advice.recommended_stack.items():
        print(f"  {key.replace('_', ' ').title():16} {value}")

    print(f"\n{'─' * width}")
    print("  INSTALLED TOOLS")
    print(f"{'─' * width}")
    for tool in advice.installed_tools:
        ver = f" ({tool.version})" if tool.version else ""
        print(f"  [OK]   {tool.name}{ver}")

    if advice.missing_tools:
        print(f"\n{'─' * width}")
        print("  MISSING TOOLS — INSTALL THESE")
        print(f"{'─' * width}")
        for tool in advice.missing_tools:
            print(f"  [!!]   {tool.name}")
            print(f"         Install: {tool.install_hint}")
            if tool.download_url:
                print(f"         Download: {tool.download_url}")

    print(f"\n{'─' * width}")
    print("  CLOUD RECOMMENDATION (by stage)")
    print(f"{'─' * width}")
    for stage, info in advice.cloud_recommendation.items():
        print(f"\n  {stage.replace('_', ' ').title()}:")
        print(f"    Best:  {info['best']}")
        print(f"    Cost:  {info['cost']}")
        print(f"    Why:   {info['why']}")
        if info.get("url") and info["url"] != "N/A":
            print(f"    URL:   {info['url']}")

    print(f"\n{'─' * width}")
    print("  COST ESTIMATE")
    print(f"{'─' * width}")
    for stage, cost in advice.cost_estimate.items():
        print(f"  {stage.replace('_', ' ').title():24} {cost}")

    print(f"\n{'─' * width}")
    print("  SETUP STEPS FOR YOUR OS")
    print(f"{'─' * width}")
    for step in advice.setup_steps:
        print(f"  {step}")

    print(f"\n{'─' * width}")
    print("  RUN THESE COMMANDS NOW")
    print(f"{'─' * width}")
    for i, cmd in enumerate(advice.next_commands, 1):
        print(f"  {i}. {cmd}")

    print(f"\n{'─' * width}")
    print("  OFFICIAL DOWNLOAD LINKS")
    print(f"{'─' * width}")
    for name, url in advice.download_links.items():
        print(f"  {name:20} {url}")

    print()
    print("=" * width)
    print("  Full guides:")
    print("    docs/BEGINNER_PLAYBOOK.md")
    print("    docs/UNIVERSAL_PROJECT_PLAYBOOK.md")
    print("=" * width)
    print()


def advice_to_dict(advice: ProjectAdvice) -> dict[str, Any]:
    """Convert advice to JSON-serializable dict."""
    return {
        "os": asdict(advice.os),
        "project_type": advice.project_type,
        "installed_tools": [asdict(t) for t in advice.installed_tools],
        "missing_tools": [asdict(t) for t in advice.missing_tools],
        "recommended_stack": advice.recommended_stack,
        "cloud_recommendation": advice.cloud_recommendation,
        "setup_steps": advice.setup_steps,
        "download_links": advice.download_links,
        "cost_estimate": advice.cost_estimate,
        "next_commands": advice.next_commands,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

PROJECT_TYPES = list(PROJECT_STACKS.keys())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Universal Project Advisor — OS-aware setup suggestions for any project"
    )
    parser.add_argument(
        "--project-type", "-t",
        choices=PROJECT_TYPES,
        default="general",
        help="Type of project you want to build (default: general)",
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON (for scripts/automation)",
    )
    parser.add_argument(
        "--list-types",
        action="store_true",
        help="List all supported project types",
    )
    args = parser.parse_args()

    if args.list_types:
        print("Supported project types:")
        for pt in PROJECT_TYPES:
            print(f"  - {pt}")
        sys.exit(0)

    advice = build_advice(args.project_type)

    if args.json:
        print(json.dumps(advice_to_dict(advice), indent=2))
    else:
        print_advice(advice)


if __name__ == "__main__":
    main()
