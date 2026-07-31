# Chapter 11: Depth-First Search (DFS)

**Part 02 — Searching Algorithms**

---

## Learning Objectives

By the end of this chapter, you will be able to:

1. Explain how **Depth-First Search (DFS)** works on representative inputs.
2. Implement the algorithm in Python with type hints and docstrings.
3. Analyze **time complexity** (O(V + E)) and **space complexity** (O(V)).
4. Choose when Depth-First Search (DFS) is appropriate in applications and interviews.
5. Avoid common implementation mistakes and debug failing cases systematically.
6. Connect the algorithm to production systems and architecture trade-offs.
7. Answer beginner through senior-level interview questions confidently.
8. Run and extend the book's unit tests and benchmarks.

---

## Introduction

**Depth-First Search (DFS)** is a foundational algorithm in computer science and software engineering. This chapter provides a complete, runnable treatment aligned with the book's code in `code/part-02/dfs.py`.

You will move from intuition to implementation to complexity analysis, then to interviews and production notes. Every example uses **Python 3.12+** and follows the repository's testing conventions.

---

## Real-World Motivation

Topological sort, cycle detection, connected components, and puzzle solvers use DFS.

Engineering teams rarely implement every algorithm from scratch, but they **must recognize** when a library, database index, or graph engine is applying this idea under the hood. That recognition saves debugging time and prevents wrong algorithm choices at scale.

---

## Daily-Life Analogy

Exploring a maze by always going as deep as possible before backtracking.

The analogy is not a proof — it is a mental model. When you forget details, return to this image and rebuild the steps.

---

## Mathematical Intuition

Each vertex and edge visited once: O(V + E).

We express complexity with Big-O notation for worst-case or standard-case behavior unless stated otherwise. Measure on your hardware when constants matter.

---

## Core Concepts

| Concept | Meaning |
|---------|---------|
| **Stack / recursion** | LIFO explores depth first |
| **Visited set** | Prevents infinite loops in cyclic graphs |
| **Backtracking** | Undo choices when path fails |

---

## Visual Diagram

```mermaid
flowchart TD
    S[Push start] --> P[Pop node]
    P --> V{Visited?}
    V -->|Yes| P
    V -->|No| M[Mark visited]
    M --> N[Push unvisited neighbors]
    N --> P
```

---

## Step-by-Step Explanation

1. Mark start visited and push onto stack.
2. Pop node; append to order.
3. Push unvisited neighbors (reverse order for consistent traversal).
4. Repeat until stack empty.

Walk through a small example by hand on paper. Tracing two or three steps beats memorizing code.

---

## Python Implementation

Full implementation with type hints and docstrings:

```python
# See code/part-02/dfs.py
```

Run directly:

```bash
cd comprehensive-algorithms-guide
python code/part-02/dfs.py
```

Primary entry point: **`dfs_iterative()`**.

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
$ python code/part-02/dfs.py
# Demonstration output printed by __main__ block
```

---

## Output Explanation

The demonstration constructs a small sample input, runs `dfs_iterative()`, and prints results. Compare output to your hand trace. If results differ, use Debugging Tips below.

---

## Time Complexity

| Case | Complexity |
|------|------------|
| Typical / stated | **O(V + E)** |

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

- Stack overflow on deep graphs with recursive DFS.
- Forgetting visited check before pushing.
- Assuming DFS finds shortest paths.

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

1. What data structure does DFS use?
2. DFS vs BFS difference?
3. Time complexity on a graph?
4. Can DFS work on disconnected graphs?
5. What is backtracking?

### Intermediate (5)

1. Detect cycles in directed graphs with DFS colors.
2. Count islands in a 2D grid using DFS.
3. Iterative vs recursive DFS trade-offs.
4. Topological sort via DFS finish times.
5. Find articulation points.

### Advanced (5)

1. DFS on implicit graphs (state space search).
2. Tarjan's SCC algorithm outline.
3. Memory-bounded DFS for huge graphs.
4. Parallel DFS challenges.
5. DFS for bipartite testing.

### System Design (3)

1. Model permission inheritance with DFS on org tree.
2. Dependency resolution in build systems.
3. Crawl web pages with depth limits.

### Coding Challenge (1)

Return whether a directed graph has a cycle using DFS.

---

## Production Notes

Set recursion limits or use iterative DFS in Python for deep trees. Add timeout and depth caps for user-generated graphs.

---

## Architecture Integration

```mermaid
flowchart TD
    Build[Build DAG of tasks] --> DFS[DFS topological order]
    DFS --> Queue[Execution queue]
    Queue --> Workers[Worker pool]
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

Start by running `dfs.py` and the pytest file. Modify the sample input in the `__main__` block and predict the output before running. If you are new to Big-O, focus on **how the loop bounds grow** with input size.

### Intermediate Note

Compare this algorithm to its closest relatives in the same part of the book. Implement one variation (iterative vs recursive, randomized pivot, early exit) and measure whether it matters on your machine for n = 10³ and n = 10⁴.

### Senior Engineer Note

At scale, algorithm choice is a **product and reliability** decision: worst-case guarantees, stability, memory caps, adversarial inputs, and operational observability matter as much as Big-O. Integrate with indexes, materialized views, precomputed graphs, or GPU kernels where appropriate. The implementation in this repository is a **reference** — production systems should use battle-tested libraries unless profiling proves a specialized path is required.

---

## Summary

In this chapter you:

- Learned how **Depth-First Search (DFS)** works and when to use it.
- Studied **O(V + E)** time and **O(V)** space complexity.
- Ran the Python implementation in `code/part-02/dfs.py`.
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

- [NetworkX DFS](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.traversal.depth_first_search.dfs_edges.html)
- [CLRS — Graph search](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)

---

**Previous:** Chapter 10: Binary Search  
**Next:** Chapter 12: Breadth-First Search (BFS)
