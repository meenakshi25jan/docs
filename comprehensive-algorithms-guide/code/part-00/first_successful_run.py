#!/usr/bin/env python3
"""
First successful run for the Comprehensive Algorithms Guide.

This script verifies that Python is working and prints a welcome message
with the installed Python version.
"""

from __future__ import annotations

import platform
import sys


def main() -> None:
    """Print a welcome banner and environment details."""
    python_version: str = platform.python_version()
    implementation: str = platform.python_implementation()

    print("=" * 60)
    print("Comprehensive Algorithms Guide — Environment Check")
    print("=" * 60)
    print(f"Python version     : {python_version}")
    print(f"Implementation     : {implementation}")
    print(f"Executable         : {sys.executable}")
    print(f"Platform           : {platform.system()} {platform.release()}")
    print("-" * 60)
    print("Status             : SUCCESS")
    print("Your environment is ready for Chapter 0 exercises.")
    print("=" * 60)


if __name__ == "__main__":
    main()
