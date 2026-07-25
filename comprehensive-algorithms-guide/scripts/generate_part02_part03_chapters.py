#!/usr/bin/env python3
"""Generate Part 2 and Part 3 chapter markdown files."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHAPTERS = [
    {
        "num": 9,
        "part": "02",
        "part_title": "Searching Algorithms",
        "dir": "part-02-searching",
        "slug": "linear-search",
        "title": "Linear Search",
        "module": "linear_search.py",
        "func": "linear_search",
        "time": "O(n)",
        "space": "O(1)",
        "analogy": "Checking every locker in a hallway until you find yours.",
        "motivation": "Databases scan rows when no index exists; file systems walk directories sequentially.",
        "math": "Worst case examines all n elements: T(n) = n.",
        "concepts": [
            ("Sequential scan", "Visit elements from index 0 to n-1"),
            ("Early exit", "Stop when target is found"),
            ("Unsorted input", "Works on any sequence without preprocessing"),
        ],
        "mermaid": """```mermaid
flowchart LR
    A[Start index 0] --> B{items[i] == target?}
    B -->|Yes| C[Return i]
    B -->|No| D{i < n?}
    D -->|Yes| E[i += 1] --> B
    D -->|No| F[Return -1]
```""",
        "steps": [
            "Initialize index to 0.",
            "Compare items[index] with target.",
            "If equal, return index.",
            "Increment index; repeat until end.",
            "Return -1 if not found.",
        ],
        "mistakes": [
            "Using linear search on large sorted arrays when binary search applies.",
            "Off-by-one errors when looping to `len(items)` vs `len(items)-1` unnecessarily.",
            "Forgetting that `==` on objects may not mean semantic equality.",
        ],
        "interview_beginner": [
            "What is linear search?",
            "What is its time complexity?",
            "Does linear search require sorted data?",
            "What does the function return when the target is missing?",
            "When is linear search acceptable?",
        ],
        "interview_intermediate": [
            "How would you find all occurrences of a duplicate value?",
            "Compare linear search vs hash-map lookup.",
            "How does sentinel-based search reduce branch checks?",
            "When would you use a predicate-based linear scan?",
            "How do you test linear search for empty input?",
        ],
        "interview_advanced": [
            "Analyze cache behavior of sequential vs random access scans.",
            "How do SIMD instructions accelerate linear scans in production?",
            "Discuss branch prediction effects on tight loops.",
            "When does streaming I/O make linear scan the only option?",
            "How would you parallelize linear search across chunks?",
        ],
        "system_design": [
            "When should a search API fall back to full table scan?",
            "Design a feature flag rollout checker scanning millions of rows.",
            "How do you monitor scan latency in OLAP queries?",
        ],
        "coding_challenge": "Implement `linear_search_all` returning every index of a target in O(n) time.",
        "production": "Full table scans are acceptable for small tables, ETL staging, or when indexes cannot be maintained. Use query plans and limits to avoid unbounded scans in APIs.",
        "architecture": """```mermaid
flowchart TD
    API[Search API] --> Cache{In cache?}
    Cache -->|Hit| Return[Return result]
    Cache -->|Miss| DB[(Database)]
    DB --> Scan[Sequential / index scan]
    Scan --> Return
```""",
        "reading": [
            "[Python enumerate documentation](https://docs.python.org/3/library/functions.html#enumerate)",
            "[CLRS — Introduction to Algorithms, Chapter on elementary search](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)",
        ],
        "prev": "Chapter 8: Algorithm Analysis",
        "next": "Chapter 10: Binary Search",
    },
    {
        "num": 10,
        "part": "02",
        "part_title": "Searching Algorithms",
        "dir": "part-02-searching",
        "slug": "binary-search",
        "title": "Binary Search",
        "module": "binary_search.py",
        "func": "binary_search_iterative",
        "time": "O(log n)",
        "space": "O(1) iterative / O(log n) recursive",
        "analogy": "Finding a name in a phone book by repeatedly opening to the middle.",
        "motivation": "Databases, version control bisect, and load balancers use binary search on sorted data for logarithmic lookups.",
        "math": "Each step halves the search space: T(n) = T(n/2) + O(1) → O(log n).",
        "concepts": [
            ("Sorted precondition", "Input must be ordered"),
            ("Divide and conquer", "Discard half the range each step"),
            ("Lower bound", "First index where target can be inserted"),
        ],
        "mermaid": """```mermaid
flowchart TD
    L[left] --> M[mid = left + (right-left)//2]
    M --> C{arr[mid] vs target}
    C -->|equal| R[return mid]
    C -->|arr[mid] < target| U[left = mid + 1]
    C -->|arr[mid] > target| D[right = mid - 1]
    U --> M
    D --> M
```""",
        "steps": [
            "Set left = 0, right = n - 1.",
            "Compute mid avoiding overflow: left + (right - left) // 2.",
            "Compare arr[mid] to target.",
            "Adjust left or right; stop when left > right.",
        ],
        "mistakes": [
            "Searching unsorted arrays.",
            "Using `(left + right) // 2` on huge indices in other languages (overflow).",
            "Infinite loops from incorrect boundary updates.",
        ],
        "interview_beginner": [
            "Why must data be sorted?",
            "What is the time complexity?",
            "Iterative vs recursive binary search?",
            "What happens if the target is absent?",
            "What is lower bound?",
        ],
        "interview_intermediate": [
            "Find first occurrence of a duplicate in a sorted array.",
            "Implement binary search on answer (parametric search).",
            "Compare bisect module vs hand-written search.",
            "How to search a rotated sorted array?",
            "Off-by-one pitfalls with inclusive bounds.",
        ],
        "interview_advanced": [
            "Prove correctness using loop invariants.",
            "Branchless binary search in systems programming.",
            "Fractional cascading and interpolation search trade-offs.",
            "Binary search on implicit infinite sequences.",
            "Cache effects vs linear scan crossover point.",
        ],
        "system_design": [
            "Use binary search for timestamp-based log retention.",
            "Design autoscaling based on sorted latency samples.",
            "Shard routing via binary search on key ranges.",
        ],
        "coding_challenge": "Given a sorted array with duplicates, return the leftmost index of target in O(log n).",
        "production": "Prefer `bisect` in Python for maintenance. Hand-roll only when you need custom comparators or implicit arrays.",
        "architecture": """```mermaid
flowchart LR
    Client --> LB[Load Balancer]
    LB --> Sorted[Sorted server latency list]
    Sorted --> BS[Binary search pick server]
    BS --> Server[Backend instance]
```""",
        "reading": [
            "[Python bisect module](https://docs.python.org/3/library/bisect.html)",
            "[Binary search — CP-Algorithms](https://cp-algorithms.com/num_methods/binary_search.html)",
        ],
        "prev": "Chapter 9: Linear Search",
        "next": "Chapter 11: Depth-First Search (DFS)",
    },
    {
        "num": 11,
        "part": "02",
        "part_title": "Searching Algorithms",
        "dir": "part-02-searching",
        "slug": "dfs",
        "title": "Depth-First Search (DFS)",
        "module": "dfs.py",
        "func": "dfs_iterative",
        "time": "O(V + E)",
        "space": "O(V)",
        "analogy": "Exploring a maze by always going as deep as possible before backtracking.",
        "motivation": "Topological sort, cycle detection, connected components, and puzzle solvers use DFS.",
        "math": "Each vertex and edge visited once: O(V + E).",
        "concepts": [
            ("Stack / recursion", "LIFO explores depth first"),
            ("Visited set", "Prevents infinite loops in cyclic graphs"),
            ("Backtracking", "Undo choices when path fails"),
        ],
        "mermaid": """```mermaid
flowchart TD
    S[Push start] --> P[Pop node]
    P --> V{Visited?}
    V -->|Yes| P
    V -->|No| M[Mark visited]
    M --> N[Push unvisited neighbors]
    N --> P
```""",
        "steps": [
            "Mark start visited and push onto stack.",
            "Pop node; append to order.",
            "Push unvisited neighbors (reverse order for consistent traversal).",
            "Repeat until stack empty.",
        ],
        "mistakes": [
            "Stack overflow on deep graphs with recursive DFS.",
            "Forgetting visited check before pushing.",
            "Assuming DFS finds shortest paths.",
        ],
        "interview_beginner": [
            "What data structure does DFS use?",
            "DFS vs BFS difference?",
            "Time complexity on a graph?",
            "Can DFS work on disconnected graphs?",
            "What is backtracking?",
        ],
        "interview_intermediate": [
            "Detect cycles in directed graphs with DFS colors.",
            "Count islands in a 2D grid using DFS.",
            "Iterative vs recursive DFS trade-offs.",
            "Topological sort via DFS finish times.",
            "Find articulation points.",
        ],
        "interview_advanced": [
            "DFS on implicit graphs (state space search).",
            "Tarjan's SCC algorithm outline.",
            "Memory-bounded DFS for huge graphs.",
            "Parallel DFS challenges.",
            "DFS for bipartite testing.",
        ],
        "system_design": [
            "Model permission inheritance with DFS on org tree.",
            "Dependency resolution in build systems.",
            "Crawl web pages with depth limits.",
        ],
        "coding_challenge": "Return whether a directed graph has a cycle using DFS.",
        "production": "Set recursion limits or use iterative DFS in Python for deep trees. Add timeout and depth caps for user-generated graphs.",
        "architecture": """```mermaid
flowchart TD
    Build[Build DAG of tasks] --> DFS[DFS topological order]
    DFS --> Queue[Execution queue]
    Queue --> Workers[Worker pool]
```""",
        "reading": [
            "[NetworkX DFS](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.traversal.depth_first_search.dfs_edges.html)",
            "[CLRS — Graph search](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)",
        ],
        "prev": "Chapter 10: Binary Search",
        "next": "Chapter 12: Breadth-First Search (BFS)",
    },
    {
        "num": 12,
        "part": "02",
        "part_title": "Searching Algorithms",
        "dir": "part-02-searching",
        "slug": "bfs",
        "title": "Breadth-First Search (BFS)",
        "module": "bfs.py",
        "func": "bfs",
        "time": "O(V + E)",
        "space": "O(V)",
        "analogy": "Ripples spreading outward in a pond from a dropped stone.",
        "motivation": "Shortest hops in unweighted graphs, social network degrees, and broadcast routing.",
        "math": "Layers expand by one edge per level; still O(V + E) total.",
        "concepts": [
            ("Queue", "FIFO processes nearest nodes first"),
            ("Level order", "Nodes grouped by distance from source"),
            ("Shortest path", "Fewest edges in unweighted graphs"),
        ],
        "mermaid": """```mermaid
flowchart LR
    Q[Queue] --> D[Dequeue node]
    D --> E[Enqueue unvisited neighbors]
    E --> Q
```""",
        "steps": [
            "Enqueue start; mark visited.",
            "Dequeue front node; process it.",
            "Enqueue each unvisited neighbor.",
            "Continue until queue empty.",
        ],
        "mistakes": [
            "Using a list as queue (O(n) pops). Use deque.",
            "Marking visited on dequeue instead of enqueue (duplicate work).",
            "Applying BFS shortest-path claim to weighted graphs.",
        ],
        "interview_beginner": [
            "What structure does BFS use?",
            "Does BFS find shortest paths?",
            "BFS vs DFS?",
            "Complexity?",
            "How to track levels?",
        ],
        "interview_intermediate": [
            "BFS on a grid with obstacles.",
            "Bidirectional BFS speedup.",
            "Multi-source BFS.",
            "0-1 BFS with deque.",
            "Serialize binary tree level order.",
        ],
        "interview_advanced": [
            "BFS on implicit state graphs.",
            "Parallel BFS on shared memory.",
            "When BFS memory blows up.",
            "A* as informed BFS.",
            "BFS for minimum spanning tree on unweighted graphs.",
        ],
        "system_design": [
            "Friend-of-friend recommendations within k hops.",
            "Cache warming breadth-first from hot keys.",
            "Network flood-fill health checks.",
        ],
        "coding_challenge": "Return shortest path length in an unweighted graph or -1 if unreachable.",
        "production": "Cap BFS depth in social graphs to prevent fan-out explosions. Monitor queue size.",
        "architecture": """```mermaid
flowchart TD
    User --> API
    API --> BFS[BFS over social graph]
    BFS --> Limit[Depth limit k]
    Limit --> Results[Ranked connections]
```""",
        "reading": [
            "[CP-Algorithms BFS](https://cp-algorithms.com/graph/breadth-first-search.html)",
            "[NetworkX BFS](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.traversal.breadth_first_search.bfs_edges.html)",
        ],
        "prev": "Chapter 11: DFS",
        "next": "Chapter 13: Dijkstra's Algorithm",
    },
    {
        "num": 13,
        "part": "02",
        "part_title": "Searching Algorithms",
        "dir": "part-02-searching",
        "slug": "dijkstra",
        "title": "Dijkstra's Algorithm",
        "module": "dijkstra.py",
        "func": "dijkstra",
        "time": "O((V + E) log V)",
        "space": "O(V)",
        "analogy": "Spreading cheapest travel cost like ink on a map, always settling the cheapest known city next.",
        "motivation": "GPS routing, network routing protocols, and game pathfinding with non-negative weights.",
        "math": "Greedy choice: settled node's distance is final with non-negative edges.",
        "concepts": [
            ("Priority queue", "Extract minimum tentative distance"),
            ("Relaxation", "Improve neighbor distances"),
            ("Non-negative weights", "Required for correctness"),
        ],
        "mermaid": """```mermaid
flowchart TD
    PQ[Min-heap] --> U[Pop min distance node]
    U --> R[Relax edges]
    R --> PQ
```""",
        "steps": [
            "Initialize distances to infinity; source = 0.",
            "Push (0, source) on min-heap.",
            "Pop smallest; skip stale entries.",
            "Relax each neighbor; push improvements.",
        ],
        "mistakes": [
            "Running on graphs with negative edges.",
            "Not skipping outdated heap entries.",
            "Forgetting disconnected nodes remain at inf.",
        ],
        "interview_beginner": [
            "What does Dijkstra compute?",
            "Why non-negative weights?",
            "What is relaxation?",
            "Time complexity with binary heap?",
            "Difference from BFS?",
        ],
        "interview_intermediate": [
            "Reconstruct shortest path with predecessors.",
            "Dijkstra on sparse vs dense graphs.",
            "When to use Fibonacci heap.",
            "Multi-source Dijkstra.",
            "Early exit when goal is popped.",
        ],
        "interview_advanced": [
            "Proof of correctness via invariant.",
            "Dial's algorithm for bounded integer weights.",
            "Compare with Bellman-Ford trade-offs.",
            "Dynamic shortest paths updates.",
            "Bidirectional Dijkstra.",
        ],
        "system_design": [
            "Route requests across data centers with latency weights.",
            "CDN edge selection by weighted graph.",
            "Service mesh traffic routing.",
        ],
        "coding_challenge": "Implement Dijkstra returning distance map and path to a target.",
        "production": "Precompute routes for static graphs; use contraction hierarchies at map scale. Validate non-negative weights at ingest.",
        "architecture": """```mermaid
flowchart LR
    Graph[(Road network graph)] --> Pre[Preprocessing]
    Pre --> Engine[Routing engine]
    Query[User query] --> Engine
    Engine --> Path[Shortest path]
```""",
        "reading": [
            "[Dijkstra — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)",
            "[NetworkX shortest_path](https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html)",
        ],
        "prev": "Chapter 12: BFS",
        "next": "Chapter 14: Bellman-Ford",
    },
    {
        "num": 14,
        "part": "02",
        "part_title": "Searching Algorithms",
        "dir": "part-02-searching",
        "slug": "bellman-ford",
        "title": "Bellman-Ford Algorithm",
        "module": "bellman_ford.py",
        "func": "bellman_ford",
        "time": "O(V * E)",
        "space": "O(V)",
        "analogy": "Repeatedly sharing gossip until everyone's story stops changing — or a contradiction appears.",
        "motivation": "Currency arbitrage detection, routing with negative costs, and difference constraints.",
        "math": "After k relaxations, shortest paths using at most k edges are known; V-1 passes suffice.",
        "concepts": [
            ("Edge relaxation rounds", "Repeat V-1 times"),
            ("Negative cycles", "Extra improvement on V-th pass"),
            ("Generality", "Handles negative weights"),
        ],
        "mermaid": """```mermaid
flowchart TD
    I[Init distances] --> R[Repeat V-1 relax all edges]
    R --> C{V-th pass improves?}
    C -->|Yes| NC[Negative cycle]
    C -->|No| OK[Done]
```""",
        "steps": [
            "Set dist[source] = 0, others inf.",
            "Repeat |V|-1 times: relax every edge.",
            "One more pass: if any improve, negative cycle.",
        ],
        "mistakes": [
            "Using on graphs needing single-source without checking cycles.",
            "Wrong iteration count (V vs V-1).",
            "Not handling unreachable nodes.",
        ],
        "interview_beginner": [
            "Why use Bellman-Ford over Dijkstra?",
            "Time complexity?",
            "What is a negative cycle?",
            "How many relaxation rounds?",
            "Does it work with negative edges?",
        ],
        "interview_intermediate": [
            "Detect negative cycle reachable from source.",
            "SPFA variant and pitfalls.",
            "Reduce to difference constraints.",
            "Shortest paths in DAG vs general graph.",
            "When Bellman-Ford is still too slow.",
        ],
        "interview_advanced": [
            "Arbitrage as negative cycle on -log rates.",
            "Johnson's algorithm combining BF + Dijkstra.",
            "Dynamic negative cycle detection.",
            "Parallel Bellman-Ford limitations.",
            "Proof of V-1 relaxation sufficiency.",
        ],
        "system_design": [
            "FX arbitrage monitoring pipeline.",
            "Validate pricing graphs in billing systems.",
            "Alert on negative cycles in promo stacking rules.",
        ],
        "coding_challenge": "Return whether a directed graph has a negative cycle reachable from source.",
        "production": "Bellman-Ford is rarely hot-path; use for validation batches. Prefer specialized solvers for large sparse graphs.",
        "architecture": """```mermaid
flowchart TD
    Rates[Exchange rate feed] --> Graph[Build weighted graph]
    Graph --> BF[Bellman-Ford]
    BF --> Alert{Negative cycle?}
    Alert -->|Yes| Ops[Trading ops alert]
```""",
        "reading": [
            "[Bellman-Ford — CP-Algorithms](https://cp-algorithms.com/graph/bellman_ford.html)",
            "[CLRS — Single-source shortest paths](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)",
        ],
        "prev": "Chapter 13: Dijkstra",
        "next": "Chapter 15: A* Search",
    },
    {
        "num": 15,
        "part": "02",
        "part_title": "Searching Algorithms",
        "dir": "part-02-searching",
        "slug": "a-star",
        "title": "A* Search",
        "module": "a_star.py",
        "func": "a_star",
        "time": "O(b^d) worst case; much better with good heuristic",
        "space": "O(V)",
        "analogy": "Walking toward a landmark you can see — you still follow streets, but you prioritize moves that look closer to the goal.",
        "motivation": "Game AI, robotics navigation, and puzzle solving where informed search beats blind BFS.",
        "math": "f(n) = g(n) + h(n); admissible h never overestimates → optimality.",
        "concepts": [
            ("g-score", "Cost from start"),
            ("h-score", "Heuristic estimate to goal"),
            ("f-score", "Priority = g + h"),
        ],
        "mermaid": """```mermaid
flowchart TD
    O[Open set by f-score] --> P[Pop min f]
    P --> G{Goal?}
    G -->|Yes| Done[Reconstruct path]
    G -->|No| Exp[Expand neighbors update g and f]
    Exp --> O
```""",
        "steps": [
            "Initialize open set with start; g(start)=0.",
            "Pop node with smallest f = g + h.",
            "If goal, reconstruct path.",
            "For each neighbor, update g if cheaper; push with new f.",
        ],
        "mistakes": [
            "Inadmissible heuristic breaks optimality.",
            "Re-expanding closed nodes incorrectly.",
            "Using Euclidean heuristic on grid with obstacles without adjustment.",
        ],
        "interview_beginner": [
            "What is a heuristic?",
            "What does admissible mean?",
            "A* vs Dijkstra?",
            "What is f-score?",
            "Common heuristics for grids?",
        ],
        "interview_intermediate": [
            "Manhattan vs Euclidean on grids.",
            "Weighted A* trade-offs.",
            "Jump Point Search idea.",
            "Memory-bounded A* (IDA*).",
            "Consistent vs admissible heuristics.",
        ],
        "interview_advanced": [
            "Prove optimality with admissible consistent h.",
            "Hierarchical pathfinding for open worlds.",
            "Anytime repairing A* (ARA*).",
            "Dynamic replanning in robotics.",
            "Choosing heuristics from ML.",
        ],
        "system_design": [
            "Warehouse robot path planner.",
            "Game NPC navigation mesh.",
            "Autocomplete as graph search with heuristic ranking.",
        ],
        "coding_challenge": "Implement A* on a grid with Manhattan heuristic and obstacles.",
        "production": "Precompute navigation meshes; cache paths; cap expansions per frame in games. Profile heuristic quality.",
        "architecture": """```mermaid
flowchart LR
    Map[Nav mesh / grid] --> Astar[A* planner]
    Sensors[Obstacle updates] --> Astar
    Astar --> Controller[Robot controller]
```""",
        "reading": [
            "[A* search — Red Blob Games](https://www.redblobgames.com/pathfinding/a-star/introduction.html)",
            "[Stanford AI lecture — A*](https://www.cs.stanford.edu/~amitp/GameProgramming/)",
        ],
        "prev": "Chapter 14: Bellman-Ford",
        "next": "Chapter 16: Bubble Sort",
    },
    # Part 3 — Sorting
    {
        "num": 16,
        "part": "03",
        "part_title": "Sorting Algorithms",
        "dir": "part-03-sorting",
        "slug": "bubble-sort",
        "title": "Bubble Sort",
        "module": "bubble_sort.py",
        "func": "bubble_sort",
        "time": "O(n^2) average/worst; O(n) best",
        "space": "O(1)",
        "analogy": "Lighter bubbles rising to the top in a glass of soda.",
        "motivation": "Teaching tool; tiny datasets; detecting nearly sorted streams with early exit.",
        "math": "n passes, each comparing adjacent pairs → ~n^2/2 comparisons.",
        "concepts": [
            ("Adjacent swaps", "Move large elements right"),
            ("Stable", "Equal elements keep order"),
            ("Early exit", "Stop if no swap in a pass"),
        ],
        "mermaid": """```mermaid
flowchart LR
    A[Compare i and i+1] --> B{i > i+1?}
    B -->|Yes| S[Swap]
    B -->|No| N[Next pair]
    S --> N
```""",
        "steps": [
            "Outer loop for each pass.",
            "Inner loop compare neighbors.",
            "Swap if out of order.",
            "Break early if no swaps.",
        ],
        "mistakes": [
            "Using bubble sort on large n in production.",
            "Forgetting early-exit optimization.",
            "Confusing best-case O(n) with average O(n^2).",
        ],
        "interview_beginner": [
            "How does bubble sort work?",
            "Time complexity?",
            "Is it stable?",
            "Best case scenario?",
            "In-place?",
        ],
        "interview_intermediate": [
            "Optimize with last-swap index.",
            "Cocktail shaker sort variant.",
            "When is bubble sort acceptable?",
            "Prove stability.",
            "Compare to insertion sort.",
        ],
        "interview_advanced": [
            "Odd-even transposition sort on parallel hardware.",
            "Adaptive analysis of bubble sort.",
            "Why libraries never use bubble sort.",
            "Network sorting with compare-exchange.",
            "Lower bound for comparison sorts.",
        ],
        "system_design": [
            "When NOT to implement custom sort in hot paths.",
            "Telemetry for nearly-sorted detection.",
            "Educational simulators vs production sort.",
        ],
        "coding_challenge": "Implement bubble sort with early termination and return swap count.",
        "production": "Never use bubble sort in production for general sorting. Use Timsort (`sorted()`).",
        "architecture": """```mermaid
flowchart TD
    Data[Input batch] --> Timsort[sorted / list.sort]
    Timsort --> Downstream[Analytics pipeline]
```""",
        "reading": [
            "[Python sorted — Timsort](https://wiki.python.org/moin/HowTo/Sorting/)",
            "[Sorting algorithm — Wikipedia](https://en.wikipedia.org/wiki/Sorting_algorithm)",
        ],
        "prev": "Chapter 15: A* Search",
        "next": "Chapter 17: Selection Sort",
    },
    {
        "num": 17,
        "part": "03",
        "part_title": "Sorting Algorithms",
        "dir": "part-03-sorting",
        "slug": "selection-sort",
        "title": "Selection Sort",
        "module": "selection_sort.py",
        "func": "selection_sort",
        "time": "O(n^2)",
        "space": "O(1)",
        "analogy": "Picking the smallest remaining item from a messy pile each round.",
        "motivation": "Minimal swaps (O(n)) useful when write cost dominates comparisons.",
        "math": "n passes, each scans remainder → n(n-1)/2 comparisons.",
        "concepts": [
            ("Select minimum", "Find min of unsorted suffix"),
            ("Swap into place", "At most n swaps"),
            ("Not stable", "Long-distance swaps break stability"),
        ],
        "mermaid": """```mermaid
flowchart TD
    I[i = 0] --> F[Find min in i..n-1]
    F --> W[Swap min to i]
    W --> N[i += 1]
    N --> I
```""",
        "steps": [
            "For each index i, find minimum in i..n-1.",
            "Swap minimum element to position i.",
            "Continue until sorted.",
        ],
        "mistakes": [
            "Expecting stability.",
            "Using when insertion sort's nearly-sorted advantage matters.",
            "Off-by-one in inner loop bounds.",
        ],
        "interview_beginner": [
            "How many swaps maximum?",
            "Time complexity?",
            "Stable or not?",
            "In-place?",
            "Compare to bubble sort.",
        ],
        "interview_intermediate": [
            "When minimal writes matter (flash memory).",
            "Heap sort as improved selection.",
            "Bidirectional selection sort.",
            "Prove O(n) swaps.",
            "Selection sort on linked lists.",
        ],
        "interview_advanced": [
            "External memory selection.",
            "Parallel selection sort limits.",
            "Comparison vs non-comparison sorts.",
            "Selection algorithm theory (median of medians).",
            "Cache behavior analysis.",
        ],
        "system_design": [
            "Avoid O(n^2) sorts in data pipelines.",
            "Sort key design for multi-field records.",
            "When to sort in DB vs application.",
        ],
        "coding_challenge": "Sort using selection sort; count comparisons and swaps.",
        "production": "Use only for teaching or when swap count must be bounded and n is tiny.",
        "architecture": """```mermaid
flowchart LR
    App[Application] --> DB[(Database ORDER BY)]
    DB --> Index[Uses B-tree index not selection sort]
```""",
        "reading": [
            "[Selection sort — GeeksforGeeks](https://www.geeksforgeeks.org/selection-sort/)",
            "[CLRS — Sorting](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)",
        ],
        "prev": "Chapter 16: Bubble Sort",
        "next": "Chapter 18: Insertion Sort",
    },
    {
        "num": 18,
        "part": "03",
        "part_title": "Sorting Algorithms",
        "dir": "part-03-sorting",
        "slug": "insertion-sort",
        "title": "Insertion Sort",
        "module": "insertion_sort.py",
        "func": "insertion_sort",
        "time": "O(n^2) average/worst; O(n) best",
        "space": "O(1)",
        "analogy": "Sorting playing cards in your hand one card at a time.",
        "motivation": "Excellent on small or nearly sorted arrays; base case in Timsort.",
        "math": "Inversions determine work; nearly sorted → few shifts.",
        "concepts": [
            ("Growing sorted prefix", "Left side always sorted"),
            ("Shift elements", "Make room for key"),
            ("Stable", "Inserts equal items after existing equals"),
        ],
        "mermaid": """```mermaid
flowchart TD
    K[Pick key at i] --> S[Shift larger elements right]
    S --> I[Insert key]
    I --> N[i += 1]
```""",
        "steps": [
            "Start from index 1.",
            "Save key = arr[i].",
            "Shift larger elements one position right.",
            "Insert key into correct hole.",
        ],
        "mistakes": [
            "Using on large random arrays.",
            "Binary insertion sort confusion (fewer compares, same shifts).",
            "Not leveraging nearly-sorted inputs.",
        ],
        "interview_beginner": [
            "Why good for small n?",
            "Stable?",
            "Best case complexity?",
            "In-place?",
            "Card sorting analogy?",
        ],
        "interview_intermediate": [
            "When does Timsort use insertion sort?",
            "Insertion sort on linked lists.",
            "Count inversions with insertion sort.",
            "Shell sort generalization.",
            "Online sorting property.",
        ],
        "interview_advanced": [
            "Adaptive sorting analysis.",
            "Merge insertion sort (Ford-Johnson).",
            "Cache-friendly insertion sort blocks.",
            "Comparison with binary insertion.",
            "Lower bound proofs.",
        ],
        "system_design": [
            "Incremental ingestion of time-ordered events.",
            "Hybrid sorts in big data frameworks.",
            "When streaming pre-sorted data.",
        ],
        "coding_challenge": "Sort nearly sorted array and measure speedup vs random.",
        "production": "Python's Timsort switches to insertion sort for small runs. Prefer built-in sort.",
        "architecture": """```mermaid
flowchart TD
    Stream[Event stream] --> Buffer[Small in-memory buffer]
    Buffer --> Ins[Insertion sort buffer]
    Ins --> Flush[Flush sorted batch]
```""",
        "reading": [
            "[Timsort description](https://github.com/python/cpython/blob/main/Objects/listsort.txt)",
            "[Insertion sort analysis](https://en.wikipedia.org/wiki/Insertion_sort)",
        ],
        "prev": "Chapter 17: Selection Sort",
        "next": "Chapter 19: Merge Sort",
    },
    {
        "num": 19,
        "part": "03",
        "part_title": "Sorting Algorithms",
        "dir": "part-03-sorting",
        "slug": "merge-sort",
        "title": "Merge Sort",
        "module": "merge_sort.py",
        "func": "merge_sort",
        "time": "O(n log n)",
        "space": "O(n)",
        "analogy": "Splitting a deck in half repeatedly, then merging sorted piles.",
        "motivation": "Stable O(n log n) sort; external sorting; parallel merge in big data.",
        "math": "T(n) = 2T(n/2) + O(n) → O(n log n).",
        "concepts": [
            ("Divide", "Split array in half"),
            ("Conquer", "Recursively sort halves"),
            ("Merge", "Combine two sorted lists"),
        ],
        "mermaid": """```mermaid
flowchart TD
    A[Array] --> B[Split half]
    B --> L[Sort left]
    B --> R[Sort right]
    L --> M[Merge]
    R --> M
    M --> S[Sorted]
```""",
        "steps": [
            "Base case: length <= 1.",
            "Recursively sort left and right halves.",
            "Merge two sorted halves with two pointers.",
        ],
        "mistakes": [
            "O(n) extra space surprise in interviews.",
            "Incorrect merge pointer logic.",
            "Not copying remaining tail elements.",
        ],
        "interview_beginner": [
            "Time and space complexity?",
            "Stable?",
            "Divide-and-conquer steps?",
            "Compare to quicksort?",
            "When prefer merge sort?",
        ],
        "interview_intermediate": [
            "In-place merge sort challenges.",
            "Bottom-up iterative merge sort.",
            "Count inversions during merge.",
            "K-way merge with heap.",
            "External merge sort passes.",
        ],
        "interview_advanced": [
            "Parallel merge sort.",
            "Natural merge sort (Timsort connection).",
            "Cache-oblivious merge sort.",
            "Lower bound Ω(n log n) for comparison sorts.",
            "Stable distributed sort on Spark.",
        ],
        "system_design": [
            "Sort 100GB file on disk.",
            "MapReduce shuffle as distributed merge.",
            "Stable sort requirements in analytics.",
        ],
        "coding_challenge": "Count number of inversions in an array using merge sort.",
        "production": "Use for external sorting and when stability + guaranteed O(n log n) matter. Python uses Timsort, not pure merge sort.",
        "architecture": """```mermaid
flowchart TD
    Disk[Large files] --> Chunks[Sort chunks in memory]
    Chunks --> Runs[Sorted runs on disk]
    Runs --> KMerge[K-way merge]
    KMerge --> Output[Sorted output file]
```""",
        "reading": [
            "[Merge sort — CP-Algorithms](https://cp-algorithms.com/algorithms/master_or_ramey.html)",
            "[External sorting](https://en.wikipedia.org/wiki/External_sorting)",
        ],
        "prev": "Chapter 18: Insertion Sort",
        "next": "Chapter 20: Quick Sort",
    },
    {
        "num": 20,
        "part": "03",
        "part_title": "Sorting Algorithms",
        "dir": "part-03-sorting",
        "slug": "quick-sort",
        "title": "Quick Sort",
        "module": "quick_sort.py",
        "func": "quick_sort",
        "time": "O(n log n) average; O(n^2) worst",
        "space": "O(log n) stack average",
        "analogy": "Organizing books around a pivot shelf: smaller left, larger right, repeat.",
        "motivation": "Fast in-place average case; standard library qsort; introselect.",
        "math": "Average partition balance → O(n log n); bad pivot → O(n^2).",
        "concepts": [
            ("Pivot", "Partition around chosen element"),
            ("Partition", "Lomuto or Hoare schemes"),
            ("Randomized pivot", "Reduces worst-case probability"),
        ],
        "mermaid": """```mermaid
flowchart TD
    P[Choose pivot] --> Part[Partition array]
    Part --> L[Quick sort left]
    Part --> R[Quick sort right]
```""",
        "steps": [
            "Pick pivot (often last element).",
            "Partition: smaller left, larger right.",
            "Recursively sort subarrays excluding pivot.",
        ],
        "mistakes": [
            "Sorted input with first-element pivot → O(n^2).",
            "Incorrect Lomuto partition indices.",
            "Not randomizing pivot in production.",
        ],
        "interview_beginner": [
            "Average vs worst time?",
            "In-place?",
            "Stable?",
            "What is partition?",
            "Why randomize pivot?",
        ],
        "interview_intermediate": [
            "Hoare vs Lomuto partition.",
            "3-way quicksort for duplicates.",
            "Tail recursion elimination.",
            "Introsort hybrid.",
            "Quickselect for kth element.",
        ],
        "interview_advanced": [
            "Expected runtime analysis with random pivot.",
            "Dual-pivot quicksort (Java).",
            "External quicksort.",
            "Parallel quicksort.",
            "Mitigate adversarial inputs.",
        ],
        "system_design": [
            "Never expose quadratic sort to adversarial API input.",
            "Use introsort in standard libraries.",
            "Sort in DB vs app for pagination.",
        ],
        "coding_challenge": "Implement quickselect to find kth smallest in O(n) average.",
        "production": "Use `randomized` pivot or library sort. For kth element use `heapq.nsmallest` or quickselect.",
        "architecture": """```mermaid
flowchart TD
    Input[User data] --> Guard[Input size limits]
    Guard --> Sort[sorted with Timsort]
    Sort --> API[Paginated API response]
```""",
        "reading": [
            "[Quicksort — Wikipedia](https://en.wikipedia.org/wiki/Quicksort)",
            "[Introsort](https://en.wikipedia.org/wiki/Introsort)",
        ],
        "prev": "Chapter 19: Merge Sort",
        "next": "Chapter 21: Heap Sort",
    },
    {
        "num": 21,
        "part": "03",
        "part_title": "Sorting Algorithms",
        "dir": "part-03-sorting",
        "slug": "heap-sort",
        "title": "Heap Sort",
        "module": "heap_sort.py",
        "func": "heap_sort",
        "time": "O(n log n)",
        "space": "O(1)",
        "analogy": "Repeatedly pulling the tallest person from a carefully organized line.",
        "motivation": "Guaranteed O(n log n) in-place; priority queues; top-K problems.",
        "math": "Build heap O(n); n extract-max each O(log n).",
        "concepts": [
            ("Max-heap", "Parent >= children"),
            ("Heapify", "Restore heap property"),
            ("In-place", "Swap root with end, shrink heap"),
        ],
        "mermaid": """```mermaid
flowchart TD
    B[Build max-heap] --> E[Swap root with last]
    E --> H[Heapify reduced heap]
    H --> E
```""",
        "steps": [
            "Build max-heap from array.",
            "Swap root with last unsorted element.",
            "Heapify root on reduced heap.",
            "Repeat until size 1.",
        ],
        "mistakes": [
            "Confusing heap sort with using heapq to collect elements.",
            "Wrong child index in heapify.",
            "Expecting stability.",
        ],
        "interview_beginner": [
            "Time complexity?",
            "In-place?",
            "Stable?",
            "Heap property?",
            "Compare to merge/quick sort?",
        ],
        "interview_intermediate": [
            "Build-heap O(n) proof sketch.",
            "Top K using min-heap of size K.",
            "Heap sort vs priority queue sort.",
            "Index-based heaps.",
            "k-way merge with heap.",
        ],
        "interview_advanced": [
            "Weak heap and other variants.",
            "Parallel heap construction.",
            "Cache behavior of heap sort.",
            "Pairing heap for decrease-key.",
            "When heap sort beats quicksort theoretically.",
        ],
        "system_design": [
            "Real-time top-N leaderboard with heap.",
            "Scheduled job queue by priority.",
            "Streaming median with two heaps.",
        ],
        "coding_challenge": "Return k largest elements from a stream using a min-heap.",
        "production": "Prefer `heapq` for partial sorts. Full heap sort rare; use when in-place O(n log n) guaranteed needed.",
        "architecture": """```mermaid
flowchart LR
    Events[Click stream] --> Heap[Min-heap size K]
    Heap --> Board[Live top-K leaderboard]
```""",
        "reading": [
            "[Python heapq](https://docs.python.org/3/library/heapq.html)",
            "[Heapsort — CLRS](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)",
        ],
        "prev": "Chapter 20: Quick Sort",
        "next": "Chapter 22: Radix Sort",
    },
    {
        "num": 22,
        "part": "03",
        "part_title": "Sorting Algorithms",
        "dir": "part-03-sorting",
        "slug": "radix-sort",
        "title": "Radix Sort",
        "module": "radix_sort.py",
        "func": "radix_sort",
        "time": "O(d * (n + k)) for d digits, radix k",
        "space": "O(n + k)",
        "analogy": "Sorting mail into bins by last digit, then next digit, until fully ordered.",
        "motivation": "Sorting integers, strings, and fixed-width keys faster than O(n log n) when d is small.",
        "math": "Stable digit passes preserve order; d passes over n items.",
        "concepts": [
            ("LSD vs MSD", "Least vs most significant digit first"),
            ("Stable counting sort per digit", "Preserves prior pass order"),
            ("Non-comparison sort", "Beats O(n log n) lower bound for comparisons"),
        ],
        "mermaid": """```mermaid
flowchart TD
    D[For each digit position] --> C[Counting sort by digit]
    C --> N[Next digit]
    N --> D
```""",
        "steps": [
            "Find maximum value to know digit count.",
            "For exp = 1, 10, 100, ...:",
            "Stable counting sort by (value // exp) % 10.",
        ],
        "mistakes": [
            "Using unstable sort per digit (breaks radix).",
            "Negative numbers without offset handling.",
            "Assuming radix beats comparison sorts for all data.",
        ],
        "interview_beginner": [
            "Comparison vs non-comparison sort?",
            "How does LSD radix work?",
            "Time complexity?",
            "Works on strings?",
            "Why stable per-digit sort?",
        ],
        "interview_intermediate": [
            "MSD radix for sparse strings.",
            "Radix sort on fixed-width integers.",
            "Handle negative integers.",
            "Bucket sort relationship.",
            "When d makes radix slow.",
        ],
        "interview_advanced": [
            "Parallel radix sort.",
            "GPU radix sort in databases.",
            "Adaptive radix trees.",
            "Floating-point radix considerations.",
            "External radix sort.",
        ],
        "system_design": [
            "Sort billions of 32-bit IDs.",
            "Columnar storage sort keys.",
            "GPU-accelerated analytics sort.",
        ],
        "coding_challenge": "Sort strings of fixed length using MSD radix sort.",
        "production": "Used in databases and GPU sorts for numeric keys. For general Python objects use Timsort.",
        "architecture": """```mermaid
flowchart TD
    Col[Integer column] --> Radix[GPU / vectorized radix]
    Radix --> Store[Sorted column store]
```""",
        "reading": [
            "[Radix sort — Wikipedia](https://en.wikipedia.org/wiki/Radix_sort)",
            "[Counting sort — CP-Algorithms](https://cp-algorithms.com/algebra/counting-sort.html)",
        ],
        "prev": "Chapter 21: Heap Sort",
        "next": "Chapter 23: Graph Representations",
    },
]


def render_chapter(ch: dict) -> str:
    concepts_table = "\n".join(f"| **{name}** | {desc} |" for name, desc in ch["concepts"])
    steps = "\n".join(f"{i}. {s}" for i, s in enumerate(ch["steps"], 1))
    mistakes = "\n".join(f"- {m}" for m in ch["mistakes"])
    beg = "\n".join(f"{i}. {q}" for i, q in enumerate(ch["interview_beginner"], 1))
    inter = "\n".join(f"{i}. {q}" for i, q in enumerate(ch["interview_intermediate"], 1))
    adv = "\n".join(f"{i}. {q}" for i, q in enumerate(ch["interview_advanced"], 1))
    sd = "\n".join(f"{i}. {q}" for i, q in enumerate(ch["system_design"], 1))
    reading = "\n".join(f"- {r}" for r in ch["reading"])
    code_path = f"code/part-{ch['part']}/{ch['module']}"
    test_path = f"tests/part-{ch['part']}/"

    return f"""# Chapter {ch['num']}: {ch['title']}

**Part {ch['part']} — {ch['part_title']}**

---

## Learning Objectives

By the end of this chapter, you will be able to:

1. Explain how **{ch['title']}** works on representative inputs.
2. Implement the algorithm in Python with type hints and docstrings.
3. Analyze **time complexity** ({ch['time']}) and **space complexity** ({ch['space']}).
4. Choose when {ch['title']} is appropriate in applications and interviews.
5. Avoid common implementation mistakes and debug failing cases systematically.
6. Connect the algorithm to production systems and architecture trade-offs.
7. Answer beginner through senior-level interview questions confidently.
8. Run and extend the book's unit tests and benchmarks.

---

## Introduction

**{ch['title']}** is a foundational algorithm in computer science and software engineering. This chapter provides a complete, runnable treatment aligned with the book's code in `{code_path}`.

You will move from intuition to implementation to complexity analysis, then to interviews and production notes. Every example uses **Python 3.12+** and follows the repository's testing conventions.

---

## Real-World Motivation

{ch['motivation']}

Engineering teams rarely implement every algorithm from scratch, but they **must recognize** when a library, database index, or graph engine is applying this idea under the hood. That recognition saves debugging time and prevents wrong algorithm choices at scale.

---

## Daily-Life Analogy

{ch['analogy']}

The analogy is not a proof — it is a mental model. When you forget details, return to this image and rebuild the steps.

---

## Mathematical Intuition

{ch['math']}

We express complexity with Big-O notation for worst-case or standard-case behavior unless stated otherwise. Measure on your hardware when constants matter.

---

## Core Concepts

| Concept | Meaning |
|---------|---------|
{concepts_table}

---

## Visual Diagram

{ch['mermaid']}

---

## Step-by-Step Explanation

{steps}

Walk through a small example by hand on paper. Tracing two or three steps beats memorizing code.

---

## Python Implementation

Full implementation with type hints and docstrings:

```python
# See {code_path}
```

Run directly:

```bash
cd comprehensive-algorithms-guide
python code/part-{ch['part']}/{ch['module']}
```

Primary entry point: **`{ch['func']}()`**.

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
$ python code/part-{ch['part']}/{ch['module']}
# Demonstration output printed by __main__ block
```

---

## Output Explanation

The demonstration constructs a small sample input, runs `{ch['func']}()`, and prints results. Compare output to your hand trace. If results differ, use Debugging Tips below.

---

## Time Complexity

| Case | Complexity |
|------|------------|
| Typical / stated | **{ch['time']}** |

Dominant operations: comparisons, graph edge relaxations, or passes over the input — depending on the algorithm family.

---

## Space Complexity

| Component | Complexity |
|-----------|------------|
| Auxiliary space | **{ch['space']}** |

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

{mistakes}

---

## Debugging Tips

1. **Print state** — Log indices, distances, or heap contents on small inputs.
2. **Invariant checks** — Assert conditions that must hold each loop iteration.
3. **Compare to brute force** — On tiny inputs, verify against a slow correct reference.
4. **Run tests** — `pytest {test_path} -v`
5. **Draw the diagram** — Mermaid figures in this chapter map directly to code structures.

---

## Unit Tests

Automated tests live in `{test_path}`:

```bash
pytest tests/part-{ch['part']}/ -v
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

{beg}

### Intermediate (5)

{inter}

### Advanced (5)

{adv}

### System Design (3)

{sd}

### Coding Challenge (1)

{ch['coding_challenge']}

---

## Production Notes

{ch['production']}

---

## Architecture Integration

{ch['architecture']}

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
6. Keep chapter code in `code/part-{ch['part']}/` — do not duplicate logic in notebooks only.
7. Profile before replacing a clear O(n log n) library sort with a custom variant.

---

## Engineering Notes

### Beginner Note

Start by running `{ch['module']}` and the pytest file. Modify the sample input in the `__main__` block and predict the output before running. If you are new to Big-O, focus on **how the loop bounds grow** with input size.

### Intermediate Note

Compare this algorithm to its closest relatives in the same part of the book. Implement one variation (iterative vs recursive, randomized pivot, early exit) and measure whether it matters on your machine for n = 10³ and n = 10⁴.

### Senior Engineer Note

At scale, algorithm choice is a **product and reliability** decision: worst-case guarantees, stability, memory caps, adversarial inputs, and operational observability matter as much as Big-O. Integrate with indexes, materialized views, precomputed graphs, or GPU kernels where appropriate. The implementation in this repository is a **reference** — production systems should use battle-tested libraries unless profiling proves a specialized path is required.

---

## Summary

In this chapter you:

- Learned how **{ch['title']}** works and when to use it.
- Studied **{ch['time']}** time and **{ch['space']}** space complexity.
- Ran the Python implementation in `{code_path}`.
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

{reading}

---

**Previous:** {ch['prev']}  
**Next:** {ch['next']}
"""


def main() -> None:
    for ch in CHAPTERS:
        out_dir = ROOT / ch["dir"]
        out_dir.mkdir(parents=True, exist_ok=True)
        filename = f"chapter-{ch['num']:02d}-{ch['slug']}.md"
        path = out_dir / filename
        path.write_text(render_chapter(ch), encoding="utf-8")
        print(f"Wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
