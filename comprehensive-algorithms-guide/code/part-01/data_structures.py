#!/usr/bin/env python3
"""Essential data structures for Chapter 6."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class Stack(Generic[T]):
    """LIFO stack backed by a Python list."""

    _items: list[T] = field(default_factory=list)

    def push(self, item: T) -> None:
        """Push item onto the stack."""
        self._items.append(item)

    def pop(self) -> T:
        """Pop and return the top item."""
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self) -> T:
        """Return top item without removing it."""
        if not self._items:
            raise IndexError("peek from empty stack")
        return self._items[-1]

    def __len__(self) -> int:
        return len(self._items)


@dataclass
class Queue(Generic[T]):
    """FIFO queue backed by collections.deque."""

    _items: deque[T] = field(default_factory=deque)

    def enqueue(self, item: T) -> None:
        """Add item to the back of the queue."""
        self._items.append(item)

    def dequeue(self) -> T:
        """Remove and return the front item."""
        if not self._items:
            raise IndexError("dequeue from empty queue")
        return self._items.popleft()

    def __len__(self) -> int:
        return len(self._items)


class LinkedListNode(Generic[T]):
    """Singly linked list node."""

    def __init__(self, value: T, next_node: LinkedListNode[T] | None = None) -> None:
        self.value: T = value
        self.next: LinkedListNode[T] | None = next_node


def linked_list_to_list(head: LinkedListNode[T] | None) -> list[T]:
    """Convert a linked list to a Python list."""
    result: list[T] = []
    current = head
    while current is not None:
        result.append(current.value)
        current = current.next
    return result


def build_linked_list(values: list[T]) -> LinkedListNode[T] | None:
    """Build a linked list from a list of values."""
    if not values:
        return None
    head = LinkedListNode(values[0])
    current = head
    for v in values[1:]:
        current.next = LinkedListNode(v)
        current = current.next
    return head


def main() -> None:
    """Demonstrate stack, queue, and linked list."""
    stack: Stack[int] = Stack()
    for n in (1, 2, 3):
        stack.push(n)
    print("Stack pop order:", [stack.pop() for _ in range(3)])

    queue: Queue[str] = Queue()
    for item in ("first", "second", "third"):
        queue.enqueue(item)
    print("Queue dequeue order:", [queue.dequeue() for _ in range(3)])

    head = build_linked_list([10, 20, 30])
    print("Linked list:", linked_list_to_list(head))


if __name__ == "__main__":
    main()
