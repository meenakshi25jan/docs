# Chapter 13: Dijkstra's Algorithm

**Part 02 — Searching Algorithms**

---

## Learning Objectives

By the end of this chapter, you will be able to:

1. Explain how **Dijkstra's Algorithm** works on representative inputs.
2. Implement the algorithm in Python with type hints and docstrings.
3. Analyze **time complexity** (O((V + E) log V)) and **space complexity** (O(V)).
4. Choose when Dijkstra's Algorithm is appropriate in applications and interviews.
5. Avoid common implementation mistakes and debug failing cases systematically.
6. Connect the algorithm to production systems and architecture trade-offs.
7. Answer beginner through senior-level interview questions confidently.
8. Run and extend the book's unit tests and benchmarks.

---

## Introduction

**Dijkstra's Algorithm** is a foundational algorithm in computer science and software engineering. This chapter provides a complete, runnable treatment aligned with the book's code in `code/part-02/dijkstra.py`.

You will move from intuition to implementation to complexity analysis, then to interviews and production notes. Every example uses **Python 3.12+** and follows the repository's testing conventions.

---

## Real-World Motivation

GPS routing, network routing protocols, and game pathfinding with non-negative weights.

Engineering teams rarely implement every algorithm from scratch, but they **must recognize** when a library, database index, or graph engine is applying this idea under the hood. That recognition saves debugging time and prevents wrong algorithm choices at scale.

---

## Daily-Life Analogy

Spreading cheapest travel cost like ink on a map, always settling the cheapest known city next.

The analogy is not a proof — it is a mental model. When you forget details, return to this image and rebuild the steps.

---

## Mathematical Intuition

Greedy choice: settled node's distance is final with non-negative edges.

We express complexity with Big-O notation for worst-case or standard-case behavior unless stated otherwise. Measure on your hardware when constants matter.

---

## Core Concepts

| Concept | Meaning |
|---------|---------|
| **Priority queue** | Extract minimum tentative distance |
| **Relaxation** | Improve neighbor distances |
| **Non-negative weights** | Required for correctness |

---

## Visual Diagram

```mermaid
flowchart TD
    PQ[Min-heap] --> U[Pop min distance node]
    U --> R[Relax edges]
    R --> PQ
```

---

## Step-by-Step Explanation

1. Initialize distances to infinity; source = 0.
2. Push (0, source) on min-heap.
3. Pop smallest; skip stale entries.
4. Relax each neighbor; push improvements.

Walk through a small example by hand on paper. Tracing two or three steps beats memorizing code.

---

## Python Implementation

Full implementation with type hints and docstrings:

```python
# See code/part-02/dijkstra.py
```

Run directly:

```bash
cd comprehensive-algorithms-guide
python code/part-02/dijkstra.py
```

Primary entry point: **`dijkstra()`**.

---

## Code Walkthrough

1. **Inputs and types** — The implementation uses explicit type hints for clarity and static checking.
2. **Core loop / recursion** — The algorithm's invariant is maintained at each step (see Mathematical Intuition).
3. **Return value** — Documented in the function docstring; tests assert expected behavior.
4. **`if __name__ == "__main__"`** — Demonstrates sample input/output for quick manual verification.

Read the source file line by line alongside this chapter. The docstring includes complexity analysis.

---

## Expected Output

Example session (values may vary slightly for stochastic algorithms):

```text
$ python code/part-02/dijkstra.py
# Demonstration output printed by __main__ block
```

---

## Output Explanation

The demonstration constructs a small sample input, runs `dijkstra()`, and prints results. Compare output to your hand trace. If results differ, use Debugging Tips below.

---

## Time Complexity

| Case | Complexity |
|------|------------|
| Typical / stated | **O((V + E) log V)** |

Dominant operations: comparisons, graph edge relaxations, or passes over the input — depending on the algorithm family.

---

## Space Complexity

| Component | Complexity |
|-----------|------------|
| Auxiliary space | **O(V)** |

Auxiliary structures may include stacks, queues, heaps, or temporary arrays. In-place sorts use O(1) extra space excluding recursion stack.

---

## Memory Usage

Memory includes:

- The input structure itself (O(n) or O(V+E) for graphs).
- Auxiliary buffers (visited sets, heaps, merge buffers).
- Recursion stack depth for recursive implementations.

Profile with `sys.getsizeof` for shallow sizes; use `tracemalloc` for deeper insight on large inputs.

---

## Performance Considerations

- **Input size** — Asymptotic complexity dominates for large n.
- **Constants** — Built-in Python sorts (Timsort) are highly optimized; custom sorts are for learning.
- **Cache locality** — Sequential access often beats pointer-chasing on large arrays.
- **Early termination** — Some variants stop early on sorted or goal-found conditions.

---

## Common Mistakes

- Running on graphs with negative edges.
- Not skipping outdated heap entries.
- Forgetting disconnected nodes remain at inf.

---

## Debugging Tips

1. **Print state** — Log indices, distances, or heap contents on small inputs.
2. **Invariant checks** — Assert conditions that must hold each loop iteration.
3. **Compare to brute force** — On tiny inputs, verify against a slow correct reference.
4. **Run tests** — `pytest tests/part-02/ -v`
5. **Draw the diagram** — Mermaid figures in this chapter map directly to code structures.

---

## Unit Tests

Automated tests live in `tests/part-02/`:

```bash
pytest tests/part-02/ -v
```

Tests cover typical cases, edge cases (empty input, single element), and error conditions where applicable.

---

## Benchmarking

For sorting chapters, run the comparison benchmark:

```bash
python code/part-03/benchmark_sorts.py
```

For searching graph algorithms, time BFS/DFS/Dijkstra on larger graphs built in a loop. Use `time.perf_counter()` and fixed random seeds.

---

## Interview Questions

### Beginner (5)

1. What does Dijkstra compute?
2. Why non-negative weights?
3. What is relaxation?
4. Time complexity with binary heap?
5. Difference from BFS?

### Intermediate (5)

1. Reconstruct shortest path with predecessors.
2. Dijkstra on sparse vs dense graphs.
3. When to use Fibonacci heap.
4. Multi-source Dijkstra.
5. Early exit when goal is popped.

### Advanced (5)

1. Proof of correctness via invariant.
2. Dial's algorithm for bounded integer weights.
3. Compare with Bellman-Ford trade-offs.
4. Dynamic shortest paths updates.
5. Bidirectional Dijkstra.

### System Design (3)

1. Route requests across data centers with latency weights.
2. CDN edge selection by weighted graph.
3. Service mesh traffic routing.

### Coding Challenge (1)

Implement Dijkstra returning distance map and path to a target.

---

## Production Notes

Precompute routes for static graphs; use contraction hierarchies at map scale. Validate non-negative weights at ingest.

---

## Architecture Integration

```mermaid
flowchart LR
    Graph[(Road network graph)] --> Pre[Preprocessing]
    Pre --> Engine[Routing engine]
    Query[User query] --> Engine
    Engine --> Path[Shortest path]
```

| Layer | Role |
|-------|------|
| Application | Chooses algorithm or library API |
| Library / runtime | Optimized implementation (e.g., `sorted`, `heapq`, NetworkX) |
| Infrastructure | Indexes, caches, precomputed graphs |
| Observability | Latency, correctness checks, adversarial input guards |

---

## Best Practices

1. Prefer standard library implementations in production hot paths.
2. Document preconditions (sorted input, non-negative weights, etc.).
3. Write property-based or table-driven tests for edge cases.
4. Pin benchmarks to seeds and hardware when reporting numbers.
5. Fail fast on invalid input with clear exceptions.
6. Keep chapter code in `code/part-02/` — do not duplicate logic in notebooks only.
7. Profile before replacing a clear O(n log n) library sort with a custom variant.

---

## Engineering Notes

### Beginner Note

Start by running `dijkstra.py` and the pytest file. Modify the sample input in the `__main__` block and predict the output before running. If you are new to Big-O, focus on **how the loop bounds grow** with input size.

### Intermediate Note

Compare this algorithm to its closest relatives in the same part of the book. Implement one variation (iterative vs recursive, randomized pivot, early exit) and measure whether it matters on your machine for n = 10³ and n = 10⁴.

### Senior Engineer Note

At scale, algorithm choice is a **product and reliability** decision: worst-case guarantees, stability, memory caps, adversarial inputs, and operational observability matter as much as Big-O. Integrate with indexes, materialized views, precomputed graphs, or GPU kernels where appropriate. The implementation in this repository is a **reference** — production systems should use battle-tested libraries unless profiling proves a specialized path is required.

---

## Summary

In this chapter you:

- Learned how **Dijkstra's Algorithm** works and when to use it.
- Studied **O((V + E) log V)** time and **O(V)** space complexity.
- Ran the Python implementation in `code/part-02/dijkstra.py`.
- Practiced interview questions from beginner to system design level.
- Connected the algorithm to production and architecture concerns.

---

## Exercises

### Exercise 1 — Trace by Hand

Apply the algorithm to a custom input of size 5–8. Write each step.

### Exercise 2 — Implement a Variant

Add one optimization or variant described in Engineering Notes. Prove it preserves correctness.

### Exercise 3 — Complexity Proof Sketch

Explain in 5–10 sentences why the stated time complexity holds.

### Exercise 4 — Test Case

Add a new pytest case covering an edge case not yet tested.

### Exercise 5 — Benchmark

Time the implementation for increasing input sizes. Plot or tabulate results.

---

## Further Reading

- [Dijkstra — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [NetworkX shortest_path](https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html)

---

**Previous:** Chapter 12: BFS  
**Next:** Chapter 14: Bellman-Ford
