#!/usr/bin/env python3
"""Generate Part 4 and Part 5 chapter markdown files (27 sections each)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHAPTERS: list[dict] = [
    # Part 4 — Graph Algorithms
    {
        "num": 23,
        "part": 4,
        "part_dir": "part-04-graph-algorithms",
        "title": "Graph Representations",
        "slug": "graph-representations",
        "subtitle": "Adjacency Lists, Matrices, and Edge Lists",
        "algo": "Graph Representations",
        "time": "O(V + E) to build adjacency list; O(V²) for dense matrix",
        "space": "O(V + E) adjacency list; O(V²) matrix",
        "code_file": "chapter_23_graph_representations.py",
        "code_path": "../../code/part-04/chapter_23_graph_representations.py",
        "test_path": "../../tests/part-04/test_chapter_23.py",
        "mermaid": """flowchart LR
    G[Graph G] --> EL[Edge List]
    G --> AL[Adjacency List]
    G --> AM[Adjacency Matrix]
    AL --> NX[NetworkX Graph]
    AM --> FW[Floyd-Warshall Input]""",
        "analogy": "A road map can be a list of every road (edge list), a city-by-city neighbor chart (adjacency list), or a big table of distances between all cities (matrix).",
        "math": "A graph $G = (V, E)$ has vertices $V$ and edges $E$. Weighted edges add $w: E \\rightarrow \\mathbb{R}^+$.",
        "concepts": [
            ("Adjacency list", "Map each vertex to its neighbors — sparse graphs"),
            ("Adjacency matrix", "V×V table — fast edge lookup, dense graphs"),
            ("Edge list", "Simple list of (u, v, w) tuples — easy to serialize"),
            ("Directed vs undirected", "Symmetric matrix for undirected graphs"),
            ("NetworkX", "Production-grade graph library in Python"),
        ],
        "interview_b": [
            "When would you use an adjacency list vs matrix?",
            "How do you represent a weighted graph in Python?",
            "What is the space complexity of an adjacency matrix?",
            "How do you convert between representations?",
            "What graph library would you use in production?",
        ],
        "interview_i": [
            "Compare CSR vs COO sparse matrix formats for graphs.",
            "How would you store a billion-edge social graph?",
            "When is an edge list preferable for distributed processing?",
            "How do self-loops and multi-edges affect representations?",
            "Design a graph schema for a routing service.",
        ],
        "interview_a": [
            "How would you shard a graph across machines for PageRank?",
            "Compare in-memory vs disk-based graph stores (Neo4j, TigerGraph).",
            "How do GPU graph frameworks represent adjacency?",
            "What are trade-offs of property graphs vs RDF?",
            "How would you version graph snapshots for ML pipelines?",
        ],
        "production": [
            "Choose representation based on density: sparse → adjacency list; dense → matrix.",
            "Use NetworkX for prototyping; migrate to specialized stores at scale.",
            "Serialize edge lists to Parquet for analytics pipelines.",
            "Validate graph connectivity before running MST or shortest-path algorithms.",
            "Log vertex/edge counts at ingestion for capacity planning.",
        ],
        "refs": [
            "https://networkx.org/documentation/stable/",
            "https://docs.python.org/3/library/collections.html",
            "Cormen et al., Introduction to Algorithms — Graph Representations",
        ],
        "prev": "Part 3 — Sorting Algorithms",
        "next": "Chapter 24: Prim's Algorithm",
    },
    {
        "num": 24,
        "part": 4,
        "part_dir": "part-04-graph-algorithms",
        "title": "Prim's Algorithm",
        "slug": "prims-algorithm",
        "subtitle": "Greedy Minimum Spanning Tree via Growing Frontier",
        "algo": "Prim's MST",
        "time": "O(E log V) with binary heap",
        "space": "O(V + E)",
        "code_file": "chapter_24_prims.py",
        "code_path": "../../code/part-04/chapter_24_prims.py",
        "test_path": "../../tests/part-04/test_chapter_24.py",
        "mermaid": """flowchart TD
    S[Start at seed vertex] --> H[Min-heap of frontier edges]
    H --> P[Pop lightest edge to unvisited vertex]
    P --> A[Add edge to MST]
    A --> E[Push new frontier edges]
    E --> H
    A --> D{All vertices visited?}
    D -->|No| H
    D -->|Yes| M[MST complete]""",
        "analogy": "Grow a tree like ivy on a wall: always attach the cheapest new branch that connects to something already covered.",
        "math": "MST minimizes $\\sum_{e \\in T} w(e)$ subject to $T$ spanning all vertices with no cycles.",
        "concepts": [
            ("Greedy choice", "Always pick minimum-weight edge crossing the cut"),
            ("Cut property", "Lightest edge across any cut belongs to some MST"),
            ("Min-heap", "Efficiently extract minimum frontier edge"),
            ("Disconnected graphs", "Prim requires connected graph or component handling"),
            ("vs Kruskal", "Prim grows one tree; Kruskal merges forests"),
        ],
        "interview_b": [
            "What problem does Prim's algorithm solve?",
            "Why do we use a priority queue in Prim's?",
            "What happens if the graph is disconnected?",
            "Is Prim's greedy choice always optimal? Why?",
            "Compare Prim's time complexity with naive O(V²) implementation.",
        ],
        "interview_i": [
            "When is Prim better than Kruskal?",
            "How would you implement Prim for dense graphs without a heap?",
            "How do you parallelize Prim's algorithm?",
            "Apply Prim to design a minimum-cost network cable layout.",
            "What edge cases break naive Prim implementations?",
        ],
        "interview_a": [
            "Design MST computation for a streaming graph with edge updates.",
            "How would you run MST on a graph stored in a distributed file system?",
            "Compare Prim, Kruskal, and Borůvka for billion-edge graphs.",
            "How do dynamic MST algorithms handle edge insertions/deletions?",
            "Integrate MST into a facility-location optimizer at scale.",
        ],
        "production": [
            "Use Prim for dense graphs; Kruskal for sparse edge lists.",
            "Pre-validate connectivity to avoid partial MST silently.",
            "Cache MST results when graph changes infrequently.",
            "Use integer weights when possible for faster comparisons.",
            "For road networks, combine with spatial indexing for nearest-neighbor queries.",
        ],
        "refs": [
            "Cormen et al. — Minimum Spanning Trees",
            "https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.tree.mst.prim.html",
        ],
        "prev": "Chapter 23: Graph Representations",
        "next": "Chapter 25: Kruskal's Algorithm",
    },
    {
        "num": 25,
        "part": 4,
        "part_dir": "part-04-graph-algorithms",
        "title": "Kruskal's Algorithm",
        "slug": "kruskals-algorithm",
        "subtitle": "Minimum Spanning Tree via Union-Find",
        "algo": "Kruskal's MST",
        "time": "O(E log E) dominated by sorting edges",
        "space": "O(V) for Union-Find",
        "code_file": "chapter_25_kruskals.py",
        "code_path": "../../code/part-04/chapter_25_kruskals.py",
        "test_path": "../../tests/part-04/test_chapter_25.py",
        "mermaid": """flowchart TD
    E[Sort edges by weight] --> L[Iterate lightest to heaviest]
    L --> U{Union-Find: same component?}
    U -->|Yes| Skip[Skip edge - would cycle]
    U -->|No| Add[Add edge to MST]
    Add --> M{MST has V-1 edges?}
    M -->|No| L
    M -->|Yes| Done[MST complete]""",
        "analogy": "Sort all possible bridges by cost; connect islands only if they are not already linked — cheapest bridges first.",
        "math": "Union-Find with path compression and union by rank achieves nearly O(1) amortized per operation.",
        "concepts": [
            ("Edge sorting", "Process edges in non-decreasing weight order"),
            ("Union-Find", "Track connected components efficiently"),
            ("Cycle detection", "Skip edge if endpoints already connected"),
            ("Sparse graphs", "Kruskal excels when E ≈ V"),
            ("MST uniqueness", "Unique iff all edge weights distinct"),
        ],
        "interview_b": [
            "How does Kruskal detect cycles without DFS?",
            "What is Union-Find and why is it used?",
            "What is the time complexity of Kruskal's?",
            "How many edges are in an MST of V vertices?",
            "Compare Kruskal and Prim conceptually.",
        ],
        "interview_i": [
            "Implement Union-Find with path compression.",
            "When does Kruskal outperform Prim?",
            "How would you handle parallel Kruskal?",
            "What if edges arrive in a stream?",
            "Prove the cut property used by Kruskal.",
        ],
        "interview_a": [
            "Design distributed MST for MapReduce/Spark.",
            "How do you update MST after edge weight changes?",
            "Compare Borůvka's algorithm for GPU MST.",
            "MST in network design with latency constraints.",
            "How would you test MST correctness at scale?",
        ],
        "production": [
            "Sort edges once; reuse for multiple MST queries on same topology.",
            "Union-Find is memory-efficient for sparse graphs.",
            "Detect disconnected components before reporting MST.",
            "For equal weights, define deterministic tie-breaking.",
            "Log MST weight as a sanity metric in network pipelines.",
        ],
        "refs": [
            "Cormen et al. — Kruskal's Algorithm",
            "https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.tree.mst.kruskal.html",
        ],
        "prev": "Chapter 24: Prim's Algorithm",
        "next": "Chapter 26: Floyd-Warshall",
    },
    {
        "num": 26,
        "part": 4,
        "part_dir": "part-04-graph-algorithms",
        "title": "Floyd-Warshall Algorithm",
        "slug": "floyd-warshall",
        "subtitle": "All-Pairs Shortest Paths via Dynamic Programming",
        "algo": "Floyd-Warshall",
        "time": "O(V³)",
        "space": "O(V²)",
        "code_file": "chapter_26_floyd_warshall.py",
        "code_path": "../../code/part-04/chapter_26_floyd_warshall.py",
        "test_path": "../../tests/part-04/test_chapter_26.py",
        "mermaid": """flowchart TD
    D0[Initialize distance matrix] --> K[For each intermediate k]
    K --> I[For each pair i j]
    I --> R{dist i k + dist k j < dist i j?}
    R -->|Yes| U[Update dist i j]
    R -->|No| I
    U --> I
    I --> K
    K --> F[All-pairs distances ready]""",
        "analogy": "For every pair of cities, ask: is it faster to route through a specific hub city k?",
        "math": "$dist[i][j] = \\min(dist[i][j], dist[i][k] + dist[k][j])$ for all $k$.",
        "concepts": [
            ("All-pairs shortest paths", "Distance between every pair of vertices"),
            ("Dynamic programming", "Build solution from intermediate vertices"),
            ("Negative weights", "Handles negatives if no negative cycles"),
            ("Path reconstruction", "Next-hop matrix for rebuilding paths"),
            ("vs Dijkstra", "Run V times Dijkstra = O(VE log V); FW better for dense small V"),
        ],
        "interview_b": [
            "What problem does Floyd-Warshall solve?",
            "What is its time complexity?",
            "Can it handle negative edge weights?",
            "How do you detect negative cycles?",
            "When prefer Floyd-Warshall over repeated Dijkstra?",
        ],
        "interview_i": [
            "Reconstruct shortest paths from Floyd-Warshall output.",
            "Optimize space to O(V²) in-place updates.",
            "Apply FW to transitive closure (reachability).",
            "Compare Johnson's algorithm for sparse all-pairs.",
            "How does FW relate to matrix multiplication?",
        ],
        "interview_a": [
            "Design all-pairs routing for airline hub networks.",
            "GPU acceleration of Floyd-Warshall.",
            "Incremental updates when one edge weight changes.",
            "FW vs landmark-based heuristics for road networks.",
            "Integrate with Part 2 Dijkstra for hybrid routing systems.",
        ],
        "production": [
            "Use only for small V (< 500) due to O(V³) cost.",
            "For large sparse graphs, run Dijkstra from each hub (Part 2).",
            "Precompute distance matrix for static topology; invalidate on changes.",
            "Watch for overflow with large integer weights.",
            "Cache next-hop matrix for O(path length) route reconstruction.",
        ],
        "refs": [
            "Cormen et al. — All-Pairs Shortest Paths",
            "Part 2 Chapters 11-12: Dijkstra and Bellman-Ford",
        ],
        "prev": "Chapter 25: Kruskal's Algorithm",
        "next": "Chapter 27: Topological Sort",
    },
    {
        "num": 27,
        "part": 4,
        "part_dir": "part-04-graph-algorithms",
        "title": "Topological Sort",
        "slug": "topological-sort",
        "subtitle": "Ordering DAG Vertices with Kahn and DFS",
        "algo": "Topological Sort",
        "time": "O(V + E)",
        "space": "O(V)",
        "code_file": "chapter_27_topological_sort.py",
        "code_path": "../../code/part-04/chapter_27_topological_sort.py",
        "test_path": "../../tests/part-04/test_chapter_27.py",
        "mermaid": """flowchart TD
    DAG[Directed Acyclic Graph] --> K[Kahn BFS: zero in-degree queue]
    DAG --> D[DFS: finish-time ordering]
    K --> O[Valid topological order]
    D --> O
    C[Cycle detected] --> X[No valid order]""",
        "analogy": "Course prerequisites: you cannot take Advanced ML until you finish Linear Algebra and Probability.",
        "math": "A topological ordering $\\pi$ satisfies: for every edge $(u,v)$, $\\pi(u) < \\pi(v)$.",
        "concepts": [
            ("DAG requirement", "Cycles make topological sort impossible"),
            ("Kahn's algorithm", "BFS peeling vertices with in-degree 0"),
            ("DFS approach", "Reverse finish order of DFS"),
            ("Task scheduling", "Build systems, CI pipelines, course plans"),
            ("Multiple valid orders", "Often many correct topological orderings"),
        ],
        "interview_b": [
            "What is a topological sort?",
            "Why must the graph be a DAG?",
            "Explain Kahn's algorithm.",
            "How is DFS topological sort different?",
            "Give a real-world use case.",
        ],
        "interview_i": [
            "Detect cycles while attempting topological sort.",
            "Find lexicographically smallest topological order.",
            "Schedule parallel tasks with dependencies.",
            "Topological sort in a build system (Make, Bazel).",
            "Count number of valid topological orderings.",
        ],
        "interview_a": [
            "Design a distributed task orchestrator with dependency graphs.",
            "Handle dynamic dependency insertion at runtime.",
            "Topological sort for ML pipeline DAGs (Airflow, Kubeflow).",
            "Cycle detection in large dependency graphs.",
            "Integrate with critical path method for project management.",
        ],
        "production": [
            "Validate DAG before scheduling — fail fast on cycles.",
            "Use Kahn for level-by-level parallel execution.",
            "Persist topological levels for batch parallelism.",
            "Monitor longest dependency chain (critical path).",
            "Version dependency graphs for reproducible builds.",
        ],
        "refs": [
            "Cormen et al. — Topological Sort",
            "https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.dag.topological_sort.html",
        ],
        "prev": "Chapter 26: Floyd-Warshall",
        "next": "Chapter 28: PageRank",
    },
    {
        "num": 28,
        "part": 4,
        "part_dir": "part-04-graph-algorithms",
        "title": "PageRank",
        "slug": "pagerank",
        "subtitle": "Measuring Node Importance on the Web Graph",
        "algo": "PageRank",
        "time": "O(k(E + V)) for k power iterations",
        "space": "O(V + E)",
        "code_file": "chapter_28_pagerank.py",
        "code_path": "../../code/part-04/chapter_28_pagerank.py",
        "test_path": "../../tests/part-04/test_chapter_28.py",
        "mermaid": """flowchart LR
    W[Web Graph] --> PI[Power Iteration]
    PI --> R[Rank Vector]
    R --> D{Damping factor 0.85}
    D --> T[Teleport to random page]
    T --> PI
    R --> OUT[Ranked pages]""",
        "analogy": "Important pages are those linked by other important pages — like academic citations or word-of-mouth reputation.",
        "math": "$\\mathbf{r} = d \\mathbf{M}\\mathbf{r} + \\frac{1-d}{n}\\mathbf{1}$ where $\\mathbf{M}$ is the stochastic adjacency matrix.",
        "concepts": [
            ("Random surfer model", "Surfer follows links or teleports randomly"),
            ("Damping factor", "Typically 0.85 — probability of following links"),
            ("Power iteration", "Repeatedly multiply by transition matrix"),
            ("Dangling nodes", "Pages with no outlinks redistribute rank uniformly"),
            ("Personalized PageRank", "Biased teleport toward seed nodes"),
        ],
        "interview_b": [
            "What does PageRank measure?",
            "What is the damping factor?",
            "Why do dangling nodes need special handling?",
            "What is power iteration?",
            "How is PageRank related to eigenvectors?",
        ],
        "interview_i": [
            "Implement PageRank with convergence tolerance.",
            "Compare PageRank to in-degree centrality.",
            "Explain Personalized PageRank for recommendations.",
            "How would you scale PageRank to billions of pages?",
            "What is the relationship to Markov chains?",
        ],
        "interview_a": [
            "Design distributed PageRank (Google Pregel model).",
            "PageRank for fraud detection in transaction graphs.",
            "Combine PageRank with content features for search ranking.",
            "Incremental PageRank when graph updates frequently.",
            "Compare HITS (hubs/authorities) vs PageRank.",
        ],
        "production": [
            "Use NetworkX or GraphX for moderate graphs; custom Spark for web scale.",
            "Set convergence tolerance (e.g., 1e-6) to stop early.",
            "Handle dangling nodes explicitly — do not ignore them.",
            "Combine PageRank with domain-specific signals in hybrid rankers.",
            "Monitor iteration count as a graph health metric.",
        ],
        "refs": [
            "Brin & Page, The Anatomy of a Large-Scale Hypertextual Web Search Engine",
            "https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.link_analysis.pagerank_alg.pagerank.html",
        ],
        "prev": "Chapter 27: Topological Sort",
        "next": "Chapter 29: Graph Algorithms Integration",
    },
    {
        "num": 29,
        "part": 4,
        "part_dir": "part-04-graph-algorithms",
        "title": "Graph Algorithms Integration",
        "slug": "graph-algorithms-integration",
        "subtitle": "Selecting and Combining Graph Techniques",
        "algo": "Graph Algorithm Selection",
        "time": "Varies by chosen algorithm",
        "space": "Varies by representation",
        "code_file": "chapter_29_graph_integration.py",
        "code_path": "../../code/part-04/chapter_29_graph_integration.py",
        "test_path": "../../tests/part-04/test_chapter_29.py",
        "mermaid": """flowchart TD
    P[Problem] --> Q{Weighted?}
    Q -->|Single source| D[Dijkstra Part 2]
    Q -->|Negative edges| B[Bellman-Ford Part 2]
    Q -->|All pairs| F[Floyd-Warshall Ch 26]
    P --> MST{Spanning tree?}
    MST -->|Dense| PR[Prim Ch 24]
    MST -->|Sparse| KR[Kruskal Ch 25]
    P --> DAG{Scheduling?}
    DAG --> TS[Topological Sort Ch 27]
    P --> AUTH{Authority?}
    AUTH --> PG[PageRank Ch 28]""",
        "analogy": "A toolbox: you pick the right wrench for the bolt — shortest path, spanning tree, ordering, or ranking.",
        "math": "Algorithm choice depends on $|V|$, $|E|$, directedness, weights, and query pattern (single vs all-pairs).",
        "concepts": [
            ("Single-source shortest path", "Dijkstra (Part 2) for non-negative weights"),
            ("Negative weights", "Bellman-Ford (Part 2)"),
            ("All-pairs shortest paths", "Floyd-Warshall (Ch. 26)"),
            ("MST", "Prim (Ch. 24) or Kruskal (Ch. 25)"),
            ("DAG scheduling", "Topological Sort (Ch. 27)"),
            ("Link analysis", "PageRank (Ch. 28)"),
        ],
        "interview_b": [
            "When use Dijkstra vs Floyd-Warshall?",
            "When use Prim vs Kruskal?",
            "What graph problems need topological sort?",
            "Name algorithms from Part 2 referenced here.",
            "What representation for a social network graph?",
        ],
        "interview_i": [
            "Design a navigation system picking the right algorithm.",
            "Compare BFS/DFS (Part 2) with shortest-path algorithms.",
            "How would you benchmark graph algorithms on your data?",
            "Pipeline: ingest edges → validate → choose algorithm.",
            "Handle disconnected components across algorithms.",
        ],
        "interview_a": [
            "Architecture for real-time routing + offline MST analytics.",
            "Graph algorithm microservices: when to split?",
            "Observability for graph pipelines at scale.",
            "ML feature extraction from graph algorithms.",
            "Cost model: in-memory vs distributed graph processing.",
        ],
        "production": [
            "Document algorithm selection criteria in runbooks.",
            "Reference Part 2 for Dijkstra/Bellman-Ford — do not duplicate.",
            "Use NetworkX for < 1M edges; migrate beyond that.",
            "Integration tests across MST, shortest path, and PageRank.",
            "Version graph snapshots for reproducible analytics.",
        ],
        "refs": [
            "Part 2 Chapters 11-12: Dijkstra and Bellman-Ford",
            "Part 4 Chapters 23-28",
            "https://networkx.org/",
        ],
        "prev": "Chapter 28: PageRank",
        "next": "Chapter 30: Linear Regression",
    },
]

ML_CHAPTERS = [
    ("30", "linear-regression", "Linear Regression", "chapter_30_linear_regression.py",
     "California Housing", "Regression", "O(n·d²) fit", "O(d²)",
     "Fit a hyperplane minimizing squared error: $\\hat{y} = \\mathbf{w}^T\\mathbf{x} + b$.",
     "Predicting house prices from features like income and location.",
     "Least squares finds weights minimizing $\\sum (y_i - \\hat{y}_i)^2$.",
     "flowchart LR\n    X[Features] --> M[Linear Model]\n    M --> Y[Predictions]\n    Y --> L[MSE Loss]\n    L --> G[Gradient Update]"),
    ("31", "logistic-regression", "Logistic Regression", "chapter_31_logistic_regression.py",
     "Breast Cancer Wisconsin", "Classification", "O(n·d·iter)", "O(d)",
     "Binary classification via sigmoid: $P(y=1|x) = \\sigma(\\mathbf{w}^T\\mathbf{x})$.",
     "Medical diagnosis: malignant vs benign from cell measurements.",
     "Log-odds are linear; sigmoid maps to probability in (0,1).",
     "flowchart TD\n    X[Features] --> Z[Linear Score]\n    Z --> S[Sigmoid]\n    S --> P[Probability]\n    P --> C[Class Label]"),
    ("32", "decision-tree", "Decision Tree", "chapter_32_decision_tree.py",
     "Iris", "Classification", "O(n·d·log n) build", "O(nodes)",
     "Recursive partitioning by feature splits maximizing information gain.",
     "Twenty Questions: each answer splits possibilities until one remains.",
     "Split on feature maximizing Gini impurity or entropy reduction.",
     "flowchart TD\n    R[Root Node] --> S1[Split on feature]\n    S1 --> L[Left Child]\n    S1 --> R2[Right Child]\n    L --> Leaf[Leaf: class]"),
    ("33", "random-forest", "Random Forest", "chapter_33_random_forest.py",
     "Wine", "Classification", "O(trees·n·d·log n)", "O(trees·nodes)",
     "Ensemble of bagged decision trees with random feature subsets.",
     "Committee of experts voting on wine variety.",
     "Bagging reduces variance; random features decorrelate trees.",
     "flowchart LR\n    D[Dataset] --> B1[Bootstrap 1]\n    D --> B2[Bootstrap 2]\n    B1 --> T1[Tree 1]\n    B2 --> T2[Tree 2]\n    T1 --> V[Majority Vote]\n    T2 --> V"),
    ("34", "naive-bayes", "Naive Bayes", "chapter_34_naive_bayes.py",
     "Digits", "Classification", "O(n·d·classes)", "O(d·classes)",
     "Bayes rule with independence assumption: $P(x|y) = \\prod P(x_i|y)$.",
     "Spam filter: word probabilities independently suggest spam or ham.",
     "Posterior $\\propto$ prior × likelihood; 'naive' assumes feature independence.",
     "flowchart LR\n    X[Features] --> L[Likelihood per class]\n    P[Prior] --> B[Bayes Rule]\n    L --> B\n    B --> C[Predicted Class]"),
    ("35", "svm", "Support Vector Machine", "chapter_35_svm.py",
     "Breast Cancer Wisconsin", "Classification", "O(n²) to O(n³)", "O(n) support vectors",
     "Find maximum-margin hyperplane; kernel trick for non-linear boundaries.",
     "Draw the widest street between two neighborhoods on a map.",
     "Optimize margin $2/\\|\\mathbf{w}\\|$ subject to correct classification.",
     "flowchart TD\n    D[Data] --> H[Hyperplane]\n    H --> M[Maximum Margin]\n    K[Kernel] --> H\n    M --> SV[Support Vectors]"),
    ("36", "knn", "k-Nearest Neighbors", "chapter_36_knn.py",
     "Iris", "Classification", "O(n·d) predict", "O(n·d) store",
     "Classify by majority vote of k closest training points.",
     "You are similar to your neighbors — classify by their labels.",
     "Distance metric (Euclidean) ranks neighbors; k balances bias-variance.",
     "flowchart LR\n    Q[Query Point] --> D[Compute Distances]\n    D --> K[Select k Nearest]\n    K --> V[Majority Vote]"),
    ("37", "xgboost", "XGBoost", "chapter_37_xgboost.py",
     "Diabetes", "Regression", "O(trees·n·d·log n)", "O(trees·nodes)",
     "Gradient boosted trees with regularization and second-order optimization.",
     "Each new tree corrects mistakes of the previous ensemble.",
     "Add tree $f_t$ minimizing loss + $\\Omega(f_t)$ via gradient boosting.",
     "flowchart TD\n    R[Residuals] --> T[New Tree]\n    T --> E[Ensemble]\n    E --> R"),
    ("38", "lightgbm", "LightGBM", "chapter_38_lightgbm.py",
     "Diabetes", "Regression", "O(trees·n·d)", "O(trees·leaves)",
     "Histogram-based gradient boosting with leaf-wise growth.",
     "Same boosting idea as XGBoost but faster histogram binning.",
     "GOSS and EFB reduce computation on large datasets.",
     "flowchart LR\n    H[Histogram Bins] --> L[Leaf-wise Growth]\n    L --> B[Boosted Ensemble]"),
    ("39", "kmeans", "k-Means Clustering", "chapter_39_kmeans.py",
     "Iris", "Clustering", "O(k·n·d·iter)", "O(k·d) centroids",
     "Partition data into k clusters minimizing within-cluster variance.",
     "Group customers by shopping behavior into k segments.",
     "Alternate: assign points to nearest centroid, update centroids to mean.",
     "flowchart TD\n    C[Random Centroids] --> A[Assign Points]\n    A --> U[Update Centroids]\n    U --> A"),
    ("40", "hierarchical-clustering", "Hierarchical Clustering", "chapter_40_hierarchical_clustering.py",
     "Wine", "Clustering", "O(n² log n) linkage", "O(n²) dendrogram",
     "Build cluster hierarchy via agglomerative or divisive merging.",
     "Family tree of species — merge closest relatives iteratively.",
     "Linkage (single, complete, ward) defines inter-cluster distance.",
     "flowchart BT\n    L[Leaves: single points] --> M[Merge closest pair]\n    M --> R[Repeat until one cluster]"),
    ("41", "dbscan", "DBSCAN", "chapter_41_dbscan.py",
     "make_moons (synthetic)", "Clustering", "O(n log n) with index", "O(n)",
     "Density-based clustering: core points, borders, and noise.",
     "Find crowded neighborhoods; isolated points are noise.",
     "ε-neighborhood density determines core vs border points.",
     "flowchart TD\n    P[Point] --> E{ε-neighbors >= minPts?}\n    E -->|Yes| C[Core Point]\n    E -->|No| N[Border or Noise]"),
    ("42", "pca", "Principal Component Analysis", "chapter_42_pca.py",
     "Digits", "Dimensionality Reduction", "O(min(n·d², d³))", "O(d·k)",
     "Orthogonal projection onto directions of maximum variance.",
     "Summarize a photo with fewer numbers keeping most detail.",
     "Eigendecomposition of covariance matrix; keep top-k eigenvectors.",
     "flowchart LR\n    X[High-D Data] --> C[Covariance]\n    C --> E[Eigenvectors]\n    E --> P[Project to k-D]"),
    ("43", "apriori", "Apriori", "chapter_43_apriori.py",
     "Synthetic grocery baskets", "Association Rules", "O(2^d) worst case", "O(candidates)",
     "Find frequent itemsets; anti-monotone pruning of candidates.",
     "Market basket: customers who buy bread often buy butter.",
     "Support = count(itemset)/N; if subset infrequent, superset is too.",
     "flowchart TD\n    L1[Frequent 1-itemsets] --> C[Join Candidates]\n    C --> P[Prune by support]\n    P --> L1"),
]

for num, slug, title, code_file, dataset, task, time_c, space_c, math, motivation, analogy, mermaid in ML_CHAPTERS:
    n = int(num)
    CHAPTERS.append({
        "num": n,
        "part": 5,
        "part_dir": "part-05-machine-learning",
        "title": title,
        "slug": slug,
        "subtitle": f"{task} with scikit-learn",
        "algo": title,
        "time": time_c,
        "space": space_c,
        "code_file": code_file,
        "code_path": f"../../code/part-05/{code_file}",
        "test_path": f"../../tests/part-05/test_chapter_{num}.py",
        "mermaid": mermaid,
        "analogy": analogy,
        "math": math,
        "dataset": dataset,
        "task": task,
        "motivation": motivation,
        "concepts": [
            (f"sklearn {title}", f"Implementation via scikit-learn / related library"),
            ("Train/test split", "Hold-out evaluation with random_state=42"),
            ("Feature scaling", "StandardScaler when distance or gradient matters"),
            ("Metrics", f"{'MSE/R²' if task == 'Regression' else 'Accuracy/F1' if task == 'Classification' else 'ARI' if task == 'Clustering' else 'Explained variance' if task == 'Dimensionality Reduction' else 'Support'}"),
            ("Public dataset", f"{dataset} — free sklearn built-in dataset"),
        ],
        "interview_b": [
            f"What is {title} used for?",
            f"What dataset does this chapter use?",
            f"What is the time complexity of training?",
            "Why split train and test data?",
            "What metric evaluates this model?",
        ],
        "interview_i": [
            f"Hyperparameters for {title}?",
            "How does feature scaling affect this algorithm?",
            "Bias-variance trade-off for this method?",
            "When would you NOT use this algorithm?",
            "How to cross-validate this model?",
        ],
        "interview_a": [
            f"Deploy {title} in production serving pipeline.",
            "Monitor model drift for this algorithm.",
            f"Scale {title} to millions of samples.",
            "A/B test this model against a baseline.",
            "Feature store integration for this model type.",
        ],
        "production": [
            f"Pin sklearn/xgboost/lightgbm versions (see requirements.txt).",
            "Serialize model with joblib or ONNX for serving.",
            "Log training metrics and dataset hash for reproducibility.",
            f"Use {dataset} patterns for integration tests.",
            "Monitor latency and memory in inference path.",
        ],
        "refs": [
            "https://scikit-learn.org/stable/",
            f"https://scikit-learn.org/stable/modules/classes.html",
        ],
        "prev": f"Chapter {n-1}" if n > 30 else "Chapter 29: Graph Algorithms Integration",
        "next": f"Chapter {n+1}" if n < 43 else "Part 6 — Deep Learning",
    })


def render_chapter(ch: dict) -> str:
    part_name = "Graph Algorithms" if ch["part"] == 4 else "Machine Learning Algorithms"
    concepts_table = "\n".join(f"| **{name}** | {desc} |" for name, desc in ch["concepts"])
    objectives = "\n".join(
        f"{i}. Understand {ch['algo']} and when to apply it."
        if i == 1
        else (
            f"{i}. Implement and run the chapter Python example."
            if i == 2
            else (
                f"{i}. Analyze time and space complexity."
                if i == 3
                else (
                    f"{i}. Avoid common mistakes and debug failures."
                    if i == 4
                    else (
                        f"{i}. Answer interview questions at multiple difficulty levels."
                        if i == 5
                        else f"{i}. Apply production best practices for {ch['algo']}."
                    )
                )
            )
        )
        for i in range(1, 10)
    )

    dataset_line = ""
    if ch.get("dataset"):
        dataset_line = f"\nThis chapter uses the **{ch['dataset']}** dataset from scikit-learn — a free, public dataset requiring no API keys.\n"

    motivation = ch.get("motivation", (
        "Graphs model networks, dependencies, and relationships in routing, social media, "
        "build systems, and recommendation engines."
        if ch["part"] == 4
        else f"Machine learning powers prediction and pattern discovery in production systems."
    ))

    lines = [
        f"# Chapter {ch['num']}: {ch['title']}",
        "",
        f"**Part {ch['part']} — {part_name}**",
        "",
        "---",
        "",
        "## Learning Objectives",
        "",
        f"By the end of this chapter, you will be able to:",
        "",
        objectives,
        "",
        "---",
        "",
        "## Introduction",
        "",
        f"This chapter covers **{ch['title']}** ({ch['subtitle']}). "
        f"You will learn the theory, see a Mermaid diagram, implement runnable Python, "
        f"and practice interview questions used at top technology companies.",
        dataset_line,
        "",
        "---",
        "",
        "## Real-World Motivation",
        "",
        motivation,
        "",
        "---",
        "",
        "## Daily-Life Analogy",
        "",
        ch["analogy"],
        "",
        "---",
        "",
        "## Mathematical Intuition",
        "",
        ch["math"],
        "",
        "---",
        "",
        "## Core Concepts",
        "",
        "| Concept | Meaning |",
        "|---------|---------|",
        concepts_table,
        "",
        "---",
        "",
        "## Visual Diagram",
        "",
        "```mermaid",
        ch["mermaid"],
        "```",
        "",
        "---",
        "",
        "## Step-by-Step Explanation",
        "",
        f"### Step 1: Understand the Problem",
        "",
        f"Define inputs, outputs, and constraints for {ch['algo']}.",
        "",
        "### Step 2: Choose Data Structures",
        "",
        "Select adjacency list, matrix, or library abstractions as appropriate.",
        "",
        "### Step 3: Implement Core Logic",
        "",
        f"Follow the algorithm pseudocode; see [`{ch['code_path']}`]({ch['code_path']}).",
        "",
        "### Step 4: Validate on Sample Data",
        "",
        "Run the script and compare output to expected results.",
        "",
        "### Step 5: Test Edge Cases",
        "",
        "Empty graphs, disconnected components, cycles (for topological sort), or class imbalance (ML).",
        "",
        "---",
        "",
        "## Python Implementation",
        "",
        f"**Runnable script:** [`code/part-0{ch['part']}/{ch['code_file']}`]({ch['code_path']})",
        "",
        "```bash",
        f"python code/part-0{ch['part']}/{ch['code_file']}",
        "```",
        "",
        "See the full source in the repository. The implementation uses type hints, docstrings, and follows PEP 8.",
        "",
        "---",
        "",
        "## Code Walkthrough",
        "",
        "| Component | Role |",
        "|-----------|------|",
        f"| `main()` | Entry point; loads data and prints results |",
        f"| Core algorithm | Implements {ch['algo']} |",
        "| Helper utilities | Shared functions from `graph_utils.py` or `ml_utils.py` |",
        "| `if __name__ == '__main__'` | Runs demo when executed directly |",
        "",
        "---",
        "",
        "## Expected Output",
        "",
        "```bash",
        f"python code/part-0{ch['part']}/{ch['code_file']}",
        "```",
        "",
        "The script prints a banner, key metrics or results, and a SUCCESS separator. Exact numbers may vary slightly by hardware and library version.",
        "",
        "---",
        "",
        "## Output Explanation",
        "",
        "Read each printed metric in context. For graph algorithms, verify MST weight, shortest distances, or rank ordering. "
        "For ML chapters, check accuracy, MSE, R², or clustering scores against reasonable baselines.",
        "",
        "---",
        "",
        "## Time Complexity",
        "",
        f"**{ch['algo']}:** {ch['time']}",
        "",
        "---",
        "",
        "## Space Complexity",
        "",
        f"**{ch['algo']}:** {ch['space']}",
        "",
        "---",
        "",
        "## Memory Usage",
        "",
        "Memory scales with input size. For large graphs use streaming edge ingestion; for large ML datasets use batching or `partial_fit` where supported.",
        "",
        "---",
        "",
        "## Performance Considerations",
        "",
        "1. Profile before optimizing — measure on representative data.",
        "2. Use appropriate libraries (NetworkX, sklearn, XGBoost) rather than pure Python hot loops.",
        "3. Set `random_state` for reproducible ML experiments.",
        "4. For graphs with > 1M edges, consider distributed frameworks.",
        "5. Cache preprocessed features in production ML pipelines.",
        "",
        "---",
        "",
        "## Common Mistakes",
        "",
        "| Mistake | Symptom | Fix |",
        "|---------|---------|-----|",
        "| Wrong graph representation | Slow lookups or high memory | Match representation to density |",
        "| Ignoring disconnected graph | Partial MST or wrong distances | Validate connectivity first |",
        "| Cycle in topological sort | Infinite loop or error | Detect cycles with Kahn/DFS |",
        "| Unscaled features in SVM/k-NN | Poor accuracy | Apply StandardScaler |",
        "| Data leakage in ML | Inflated test scores | Fit scaler only on train split |",
        "",
        "---",
        "",
        "## Debugging Tips",
        "",
        "1. Print intermediate state (distances, MST edges, cluster labels).",
        "2. Compare custom implementation to NetworkX or sklearn reference.",
        "3. Run `pytest` for the chapter test file.",
        "4. Use small hand-crafted examples where you know the answer.",
        "5. Check `requirements.txt` versions if results diverge.",
        "",
        "---",
        "",
        "## Unit Tests",
        "",
        f"Automated tests: [`{ch['test_path']}`]({ch['test_path']})",
        "",
        "```bash",
        f"pytest tests/part-0{ch['part']}/test_chapter_{ch['num']}.py -v",
        "```",
        "",
        "---",
        "",
        "## Benchmarking",
        "",
        "```python",
        "import timeit",
        "",
        f"# Example: time the chapter {ch['num']} main function",
        "elapsed = timeit.timeit(",
        f"    \"main()\",",
        f"    setup=\"from {ch['code_file'].replace('.py', '')} import main\",",
        "    number=5,",
        ")",
        "print(f'Average: {elapsed/5:.4f}s')",
        "```",
        "",
        "---",
        "",
        "## Interview Questions",
        "",
        "### Beginner",
        "",
    ]
    for i, q in enumerate(ch["interview_b"], 1):
        lines.append(f"{i}. {q}")
    lines += ["", "### Intermediate", ""]
    for i, q in enumerate(ch["interview_i"], 1):
        lines.append(f"{i}. {q}")
    lines += ["", "### Advanced", ""]
    for i, q in enumerate(ch["interview_a"], 1):
        lines.append(f"{i}. {q}")
    lines += [
        "",
        "### System Design",
        "",
        f"1. How would you productionize {ch['algo']} at scale?",
        f"2. Design monitoring and alerting for a {ch['algo']} pipeline.",
        f"3. How would you A/B test changes to a {ch['algo']} system?",
        "",
        "### Coding Challenge",
        "",
        f"Implement or extend {ch['algo']} on a new test case and write pytest coverage.",
        "",
        "---",
        "",
        "## Production Notes",
        "",
    ]
    for note in ch["production"]:
        lines.append(f"- {note}")
    lines += [
        "",
        "---",
        "",
        "## Architecture Integration",
        "",
        "```mermaid",
        "flowchart LR",
        "    Data[Data Source] --> Prep[Preprocessing]",
        f"    Prep --> Algo[{ch['algo']}]",
        "    Algo --> Metrics[Evaluation]",
        "    Metrics --> Serve[API / Batch Job]",
        "    Serve --> Monitor[Observability]",
        "```",
        "",
        "---",
        "",
        "## Best Practices",
        "",
        "1. Write runnable, tested code for every algorithm.",
        "2. Document assumptions (DAG, non-negative weights, etc.).",
        "3. Use version-pinned dependencies.",
        "4. Separate training and inference code paths in production.",
        "5. Keep chapter code in `code/part-0X/` directories.",
        "",
        "---",
        "",
        "## Summary",
        "",
        f"In this chapter you studied **{ch['title']}**, implemented it in Python, analyzed complexity, "
        f"practiced interview questions, and reviewed production considerations.",
        "",
        "---",
        "",
        "## Exercises",
        "",
        f"### Exercise 1 — Run and Modify",
        "",
        f"Run `python code/part-0{ch['part']}/{ch['code_file']}` and change one parameter. Document the effect.",
        "",
        "### Exercise 2 — Test Coverage",
        "",
        f"Add one new test case to `tests/part-0{ch['part']}/test_chapter_{ch['num']}.py`.",
        "",
        "### Exercise 3 — Complexity",
        "",
        f"Prove or justify the stated time complexity for {ch['algo']}.",
        "",
        "### Exercise 4 — Interview Practice",
        "",
        "Answer all Beginner and Intermediate interview questions in writing.",
        "",
        "### Exercise 5 — Production",
        "",
        "Write a one-page design doc for deploying this algorithm in a microservice.",
        "",
        "---",
        "",
        "## Further Reading",
        "",
    ]
    for ref in ch["refs"]:
        if ref.startswith("http"):
            lines.append(f"- [{ref}]({ref})")
        else:
            lines.append(f"- {ref}")
    lines += [
        "",
        "---",
        "",
        f"**Previous:** {ch['prev']}",
        f"**Next:** {ch['next']}",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    for ch in CHAPTERS:
        part_dir = ROOT / ch["part_dir"]
        part_dir.mkdir(parents=True, exist_ok=True)
        filename = f"chapter-{ch['num']}-{ch['slug']}.md"
        path = part_dir / filename
        path.write_text(render_chapter(ch), encoding="utf-8")
        print(f"Wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
