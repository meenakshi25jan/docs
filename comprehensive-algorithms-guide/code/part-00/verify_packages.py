#!/usr/bin/env python3
"""
Verify that core book dependencies import successfully.

Run after: pip install -r requirements.txt
"""

from __future__ import annotations

import importlib
import sys
from typing import Final

REQUIRED_PACKAGES: Final[list[str]] = [
    "numpy",
    "pandas",
    "scipy",
    "matplotlib",
    "sklearn",
    "networkx",
    "pytest",
]


def check_imports() -> list[tuple[str, str]]:
    """
    Attempt to import each required package.

    Returns:
        List of (package_name, version_or_error) tuples.
    """
    results: list[tuple[str, str]] = []
    for package in REQUIRED_PACKAGES:
        try:
            module = importlib.import_module(package)
            version: str = getattr(module, "__version__", "unknown")
            results.append((package, version))
        except ImportError as exc:
            results.append((package, f"MISSING: {exc}"))
    return results


def main() -> None:
    """Print import verification report."""
    print("Package Import Verification")
    print("=" * 50)
    print(f"Python: {sys.version}")
    print("-" * 50)

    all_ok: bool = True
    for name, status in check_imports():
        marker: str = "OK" if not status.startswith("MISSING") else "FAIL"
        if marker == "FAIL":
            all_ok = False
        print(f"[{marker:4}] {name:12} -> {status}")

    print("-" * 50)
    if all_ok:
        print("All checked packages imported successfully.")
    else:
        print("Some packages are missing. Run: pip install -r requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    main()
