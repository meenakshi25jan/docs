"""Pytest configuration for Comprehensive Algorithms Guide."""

from __future__ import annotations

import sys
from pathlib import Path

CODE_ROOT: Path = Path(__file__).resolve().parent.parent / "code"

# Add each part's code directory so tests can import chapter modules.
for part_dir in CODE_ROOT.glob("part-*"):
    part_str = str(part_dir)
    if part_str not in sys.path:
        sys.path.insert(0, part_str)
