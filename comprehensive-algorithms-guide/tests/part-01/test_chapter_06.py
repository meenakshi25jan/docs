"""Tests for Chapter 6 — Essential Data Structures."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from data_structures import Queue, Stack, build_linked_list, linked_list_to_list

CODE_DIR: Path = Path(__file__).resolve().parents[2] / "code" / "part-01"


def test_data_structures_script_runs() -> None:
    """data_structures.py should exit cleanly."""
    result = subprocess.run(
        [sys.executable, str(CODE_DIR / "data_structures.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "Stack" in result.stdout


def test_stack_lifo() -> None:
    """Stack returns last-in-first-out."""
    s: Stack[int] = Stack()
    s.push(1)
    s.push(2)
    assert s.pop() == 2
    assert s.pop() == 1


def test_stack_empty_pop() -> None:
    """Pop from empty stack raises."""
    s: Stack[int] = Stack()
    with pytest.raises(IndexError):
        s.pop()


def test_queue_fifo() -> None:
    """Queue returns first-in-first-out."""
    q: Queue[str] = Queue()
    q.enqueue("a")
    q.enqueue("b")
    assert q.dequeue() == "a"
    assert q.dequeue() == "b"


def test_linked_list_roundtrip() -> None:
    """Build and flatten linked list."""
    head = build_linked_list([1, 2, 3])
    assert linked_list_to_list(head) == [1, 2, 3]
