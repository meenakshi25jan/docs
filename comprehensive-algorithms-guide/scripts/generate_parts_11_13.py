#!/usr/bin/env python3
"""Generate Parts 11-13, projects, appendices for Comprehensive Algorithms Guide."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]

# (part_dir, chapter, slug, title, subtitle, code_dir, module)
CHAPTERS_11_13: list[tuple[str, int, str, str, str, str, str]] = [
    (
        "part-11-algorithm-selection",
        84,
        "algorithm-selection-guide",
        "Algorithm Selection Guide",
        "Decision frameworks for choosing the right algorithm for each problem class.",
        "part-11",
        "ch84_algorithm_selection",
    ),
    (
        "part-13-ai-architecture",
        94,
        "llms-and-rag",
        "LLMs and RAG",
        "Retrieval-augmented generation patterns for grounded LLM applications.",
        "part-13",
        "ch94_llms_rag",
    ),
    (
        "part-13-ai-architecture",
        95,
        "vector-databases-embeddings",
        "Vector Databases and Embeddings",
        "Embedding pipelines and vector search for semantic retrieval.",
        "part-13",
        "ch95_vector_db",
    ),
    (
        "part-13-ai-architecture",
        96,
        "ai-agents-orchestration",
        "AI Agents and Orchestration",
        "Multi-step agent workflows, tools, and orchestration patterns.",
        "part-13",
        "ch96_agents",
    ),
    (
        "part-13-ai-architecture",
        97,
        "responsible-ai-governance",
        "Responsible AI and Governance",
        "Fairness, safety, privacy, and compliance for production AI.",
        "part-13",
        "ch97_responsible_ai",
    ),
    (
        "part-13-ai-architecture",
        98,
        "mlops-deployment",
        "MLOps and Deployment",
        "CI/CD, model registry, serving, and release management.",
        "part-13",
        "ch98_mlops",
    ),
    (
        "part-13-ai-architecture",
        99,
        "ai-observability",
        "AI Observability",
        "Logging, tracing, metrics, and drift detection for AI systems.",
        "part-13",
        "ch99_observability",
    ),
]

PROJECTS: list[tuple[int, str, str, str, str]] = [
    (85, "route-planner", "Route Planner", "BFS, Dijkstra, and A* pathfinding on weighted graphs.", "project_01_route_planner"),
    (86, "sorting-benchmark", "Sorting Benchmark Tool", "Benchmark classical sorting algorithms across input sizes.", "project_02_sorting_benchmark"),
    (87, "customer-segmentation", "Customer Segmentation", "k-Means, hierarchical clustering, and DBSCAN on retail data.", "project_03_customer_segmentation"),
    (88, "house-price-prediction", "House Price Prediction", "Linear regression, Random Forest, XGBoost, and LightGBM.", "project_04_house_price"),
    (89, "spam-detection", "Spam Detection", "Naive Bayes, logistic regression, and SVM for text classification.", "project_05_spam_detection"),
    (90, "image-classification", "Image Classification", "CNN from scratch and transfer learning on digit images.", "project_06_image_classification"),
    (91, "text-classification", "Text Classification", "TF-IDF baselines and transformer-style embeddings.", "project_07_text_classification"),
    (92, "optimization-problem", "Optimization Problem", "GA, PSO, simulated annealing, and differential evolution.", "project_08_optimization"),
    (93, "rl-agent", "RL Agent", "Tabular Q-learning and DQN on Gymnasium environments.", "project_09_rl_agent"),
]

PART_META = {
    "part-11-algorithm-selection": (11, "Algorithm Selection Guide"),
    "part-13-ai-architecture": (13, "AI Systems Architecture"),
}

TEST_ASSERTIONS: dict[str, str] = {
    "ch84_algorithm_selection": "result = mod.main()\n    assert result in ('bfs', 'dijkstra', 'astar', 'kmeans', 'linear_regression', 'naive_bayes', 'cnn', 'tfidf_logistic', 'genetic_algorithm', 'q_learning')",
    "ch94_llms_rag": "result = mod.main()\n    assert result >= 0.5",
    "ch95_vector_db": "result = mod.main()\n    assert result >= 0.5",
    "ch96_agents": "result = mod.main()\n    assert result is True",
    "ch97_responsible_ai": "result = mod.main()\n    assert result is True",
    "ch98_mlops": "result = mod.main()\n    assert result is True",
    "ch99_observability": "result = mod.main()\n    assert result >= 0.0",
    "project_01_route_planner": "result = mod.main()\n    assert result >= 3",
    "project_02_sorting_benchmark": "result = mod.main()\n    assert result > 0",
    "project_03_customer_segmentation": "result = mod.main()\n    assert result >= 2",
    "project_04_house_price": "result = mod.main()\n    assert result > 0",
    "project_05_spam_detection": "result = mod.main()\n    assert result >= 0.7",
    "project_06_image_classification": "result = mod.main()\n    assert result >= 0.7",
    "project_07_text_classification": "result = mod.main()\n    assert result >= 0.7",
    "project_08_optimization": "result = mod.main()\n    assert result < 50",
    "project_09_rl_agent": "result = mod.main()\n    assert result > 0",
}


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def chapter_md(
    ch: int,
    slug: str,
    title: str,
    subtitle: str,
    part_dir: str,
    part_num: int,
    part_title: str,
    code_dir: str,
    module: str,
    is_project: bool = False,
) -> str:
    rel_code = f"../../code/{code_dir}/{module}.py"
    rel_test = f"../../tests/{code_dir}/test_chapter_{ch:02d}.py"
    label = f"Project {ch - 84}: {title}" if is_project else f"Chapter {ch}: {title}"
    body = dedent(f"""
        # {label}

        **Part {part_num} — {part_title}**

        ---

        ## Learning Objectives

        By the end of this chapter, you will be able to:

        1. Explain the core idea behind {title} and when to use it.
        2. Describe the mathematical intuition and key design decisions.
        3. Implement and run a Python example from this repository.
        4. Analyze time and space complexity of the reference implementation.
        5. Identify common mistakes and debugging strategies.
        6. Answer interview questions from beginner through system-design level.
        7. Connect the solution to production engineering concerns.

        ---

        ## Introduction

        {subtitle} This chapter follows the book's 27-section structure. Every example is runnable from [`code/{code_dir}/{module}.py`]({rel_code}).

        ---

        ## Real-World Motivation

        Teams adopt {title.lower()} when baseline heuristics fail to meet latency, accuracy, or maintainability goals. The pattern appears in search, recommendations, forecasting, NLP, computer vision, and autonomous systems.

        ---

        ## Daily-Life Analogy

        Choosing the right tool for a job—hammer vs screwdriver—mirrors algorithm selection: match the technique to constraints (data size, interpretability, latency, budget).

        ---

        ## Mathematical Intuition

        Formalize inputs **X**, outputs **Y**, objective **L**, and constraints **C**. Compare candidate algorithms by asymptotic cost, bias-variance trade-offs, and operational envelopes.

        ---

        ## Core Concepts

        | Concept | Role |
        |---------|------|
        | Problem framing | Search, classification, regression, clustering, RL |
        | Data profile | Size, dimensionality, sparsity, labels |
        | Constraints | Latency, memory, interpretability, compliance |
        | Baselines | Simple methods before complex ones |
        | Evaluation | Holdout metrics and error analysis |
        | Deployment | Serving, monitoring, retraining |
        | Selection | Pick algorithm matching problem + constraints |

        ---

        ## Visual Diagram

        ```mermaid
        flowchart TD
            A[Define Problem] --> B[Gather Constraints]
            B --> C[Shortlist Algorithms]
            C --> D[Prototype & Benchmark]
            D --> E{{Meets SLOs?}}
            E -->|No| C
            E -->|Yes| F[Deploy & Monitor]
        ```

        ---

        ## Step-by-Step Explanation

        1. **Frame** the problem (optimization, prediction, planning).
        2. **Profile** data and non-functional requirements.
        3. **Baseline** with the simplest viable method.
        4. **Iterate** with stronger models and ablations.
        5. **Validate** on representative holdout sets.
        6. **Ship** with observability and rollback plans.

        ---

        ## Python Implementation

        Reference: [`code/{code_dir}/{module}.py`]({rel_code})

        ```bash
        python code/{code_dir}/{module}.py
        ```

        ---

        ## Code Walkthrough

        1. Imports, seeds, and configuration constants.
        2. Core data structures and algorithm logic.
        3. Training or search loop with clear metrics.
        4. Evaluation on holdout or simulation data.
        5. `main()` prints results and **SUCCESS**.

        ---

        ## Expected Output

        Console trace ending with **SUCCESS** and key metrics (path cost, accuracy, RMSE, silhouette score, reward).

        ---

        ## Output Explanation

        Metrics should improve over naive baselines. Flat or diverging curves signal bugs, leakage, or poor hyperparameters.

        ---

        ## Time Complexity

        Depends on algorithm class: graph search **O((V+E) log V)**, sorting **O(n log n)**, k-Means **O(n·k·d·i)**, neural training **O(epochs · batch_cost)**.

        ---

        ## Space Complexity

        Typically **O(n)** for data plus model structures (graphs, centroids, weights, replay buffers).

        ---

        ## Memory Usage

        Book examples fit in laptop RAM. Production may shard data, stream features, or use GPUs.

        ---

        ## Performance Considerations

        1. Profile before optimizing.
        2. Vectorize hot paths with NumPy.
        3. Cache embeddings and graph precomputations.
        4. Batch inference for throughput.
        5. Log latency percentiles, not just means.

        ---

        ## Common Mistakes

        | Mistake | Symptom | Fix |
        |---------|---------|-----|
        | Wrong algorithm class | Poor metrics | Revisit problem framing |
        | Data leakage | Inflated offline scores | Strict temporal splits |
        | Ignoring latency | Timeouts in prod | Benchmark P99 |
        | No baseline | Unknown uplift | Always compare simple methods |
        | Skipping monitoring | Silent drift | Add observability hooks |

        ---

        ## Debugging Tips

        1. Reproduce on a tiny subset.
        2. Plot learning curves and residuals.
        3. Compare against a known-good baseline.
        4. Assert invariants in unit tests.
        5. Run `pytest {rel_test}`.

        ---

        ## Unit Tests

        [`tests/{code_dir}/test_chapter_{ch:02d}.py`]({rel_test})

        ```bash
        pytest tests/{code_dir}/test_chapter_{ch:02d}.py -v
        ```

        ---

        ## Benchmarking

        ```python
        import timeit
        elapsed = timeit.timeit("main()", setup="from {module} import main", number=3)
        print(f"Average: {{elapsed/3:.4f}}s")
        ```

        ---

        ## Interview Questions

        ### Beginner (5)

        1. When would you choose {title} over a simpler alternative?
        2. What metrics evaluate this problem?
        3. What is train vs test split?
        4. Name one hyperparameter that matters here.
        5. Why fix random seeds?

        ### Intermediate (5)

        1. Compare two algorithms applicable to this chapter.
        2. How do you detect overfitting?
        3. What production SLOs matter?
        4. How would you debug a metric regression?
        5. What is the dominant complexity term?

        ### Advanced (5)

        1. Design an A/B test for a model upgrade.
        2. How would you scale this to 10× data?
        3. What failure modes appear under distribution shift?
        4. How do you version data and models together?
        5. Sketch the serving architecture.

        ### System Design (3)

        1. Design an end-to-end pipeline with CI and model registry.
        2. How do you meet latency SLOs under load?
        3. What alerts prevent bad deployments?

        ### Coding Challenge (1)

        Extend the reference implementation with one new feature and pytest coverage.

        ---

        ## Production Notes

        - Pin dependencies and containerize runtimes.
        - Gate releases on offline + shadow metrics.
        - Log inputs, outputs, and latencies (respecting privacy).
        - Automate retraining triggers on drift.
        - Document assumptions and known limitations.
        - Plan rollback and feature flags for model changes.

        ---

        ## Architecture Integration

        ```mermaid
        flowchart LR
            Data[Data Sources] --> Features[Feature Pipeline]
            Features --> Train[Training / Search]
            Train --> Registry[Artifact Registry]
            Registry --> Serve[Inference API]
            Serve --> Monitor[Observability]
            Monitor --> Retrain[Retrain Loop]
            Retrain --> Train
        ```

        ---

        ## Best Practices

        1. Start simple; add complexity only with measured gain.
        2. Keep train and serve feature logic identical.
        3. Test edge cases and failure modes.
        4. Document trade-offs for stakeholders.
        5. Review fairness and security implications.

        ---

        ## Summary

        Covered **{title}**: motivation, selection criteria, runnable code, complexity, tests, interviews, and production guidance.

        ---

        ## Exercises

        1. Swap datasets and compare metrics.
        2. Add a new algorithm from an earlier chapter.
        3. Plot runtime vs input size.
        4. Write an additional pytest for an edge case.
        5. Draft a one-page system design for production deployment.

        ---

        ## Further Reading

        - [scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)
        - [PyTorch Tutorials](https://pytorch.org/tutorials/)
        - [Gymnasium Documentation](https://gymnasium.farama.org/)
        - [MLOps Principles](https://ml-ops.org/)
        - [OWASP ML Security](https://owasp.org/www-project-machine-learning-security-top-10/)
        - Original papers for algorithms referenced in this chapter

        ---

        **Next:** See [SUMMARY.md](../../SUMMARY.md)
    """)
    lines = [line[8:] if line.startswith("        ") else line for line in body.splitlines()]
    return "\n".join(lines)


def test_py(ch: int, module: str, code_dir: str) -> str:
    assertion = TEST_ASSERTIONS.get(module, "mod.main()")
    return f'''"""Tests for Chapter {ch}."""

from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parents[2] / "code" / "{code_dir}"
MODULE = "{module}"


def test_script_success() -> None:
    result = subprocess.run(
        [sys.executable, str(CODE_DIR / f"{{MODULE}}.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "SUCCESS" in result.stdout


def test_core_behavior() -> None:
    mod = importlib.import_module(MODULE)
    {assertion}
'''


def appendix_md(letter: str, title: str, slug: str, focus: str) -> str:
    return dedent(f"""
        # Appendix {letter}: {title}

        **Comprehensive Algorithms Guide — Reference Appendix**

        ---

        ## Learning Objectives

        By the end of this appendix, you will be able to:

        1. Quickly reference {focus.lower()} during study or interviews.
        2. Apply tables and checklists to real design decisions.
        3. Cross-link concepts to earlier chapters.
        4. Use production checklists before shipping systems.
        5. Prepare structured interview responses.
        6. Compare algorithm families at a glance.
        7. Maintain a personal study index from this material.

        ---

        ## Introduction

        This appendix consolidates **{title.lower()}** for fast lookup. It complements Chapters 0–99 and is designed for interview prep, system design, and on-call reference.

        ---

        ## Real-World Motivation

        Senior engineers rarely memorize every detail—they rely on curated references, checklists, and pattern libraries. This appendix is that library for algorithmic and AI systems work.

        ---

        ## Daily-Life Analogy

        Like a pilot's checklist before takeoff: the appendix ensures you do not skip critical steps under pressure.

        ---

        ## Mathematical Intuition

        Reference material groups complexity classes, notation, and metric definitions used throughout the book.

        ---

        ## Core Concepts

        | Area | Contents |
        |------|----------|
        | Complexity | Big-O for search, sort, graph, ML |
        | Terminology | Glossary entries A–Z |
        | Interviews | Question banks by level |
        | Production | Pre-launch and post-launch checklists |

        ---

        ## Visual Diagram

        ```mermaid
        flowchart LR
            Study[Chapters 0-99] --> Appendix[Appendices A-D]
            Appendix --> Interview[Interview Prep]
            Appendix --> Prod[Production Launch]
            Appendix --> Ref[Quick Reference]
        ```

        ---

        ## Step-by-Step Explanation

        1. Identify your task (interview, deploy, debug).
        2. Open the relevant appendix section.
        3. Cross-reference linked chapters for depth.
        4. Apply checklists or tables to your scenario.
        5. Record gaps for further study.

        ---

        ## Python Implementation

        Appendices are reference documents; runnable code lives in [`code/`](../../code/) by part and chapter.

        ---

        ## Code Walkthrough

        N/A — reference appendix. See linked chapter modules for implementations.

        ---

        ## Expected Output

        Faster decisions, fewer omitted production steps, and structured interview answers.

        ---

        ## Output Explanation

        Use tables as starting points; always validate against your workload and SLOs.

        ---

        ## Time Complexity

        Lookup is **O(1)** for humans with a good index; mastering content is **O(chapters studied)**.

        ---

        ## Space Complexity

        Keep printed or offline copies for interviews without network access.

        ---

        ## Memory Usage

        Bookmark frequently used sections in your editor or note-taking system.

        ---

        ## Performance Considerations

        Prefer measured benchmarks over complexity alone when choosing algorithms.

        ---

        ## Common Mistakes

        | Mistake | Symptom | Fix |
        |---------|---------|-----|
        | Rote memorization | Fragile interviews | Understand trade-offs |
        | Skipping checklists | Incidents | Use Appendix D before launch |
        | Ignoring context | Wrong algorithm | Match problem to constraints |

        ---

        ## Debugging Tips

        1. Start from symptom → metric → component.
        2. Compare to baseline from Appendix A complexity expectations.
        3. Use glossary for precise terminology.

        ---

        ## Unit Tests

        Appendix content is validated by book-wide `pytest` suites in [`tests/`](../../tests/).

        ---

        ## Benchmarking

        See Part 12 Project 2 (Sorting Benchmark) and per-chapter benchmarking sections.

        ---

        ## Interview Questions

        ### Beginner (5)

        1. What is Big-O notation?
        2. Define overfitting.
        3. What is a baseline model?
        4. Name one graph traversal algorithm.
        5. What does CI/CD mean for ML?

        ### Intermediate (5)

        1. Compare BFS and Dijkstra.
        2. When use Random Forest vs linear models?
        3. Explain train/serve skew.
        4. What is embedding dimension trade-off?
        5. How detect data drift?

        ### Advanced (5)

        1. Design RAG with citation grounding.
        2. Shard a vector index at scale.
        3. Multi-agent failure recovery.
        4. Fairness metrics for classification.
        5. Canary vs blue-green for models.

        ### System Design (3)

        1. End-to-end ML platform for 50 teams.
        2. Real-time feature store architecture.
        3. LLM gateway with rate limits and audit logs.

        ### Coding Challenge (1)

        Implement one algorithm from Appendix A from scratch with tests.

        ---

        ## Production Notes

        - Treat appendices as living documents; update after incidents and retros.
        - Share checklists in PR templates.
        - Link runbooks to observability dashboards.

        ---

        ## Architecture Integration

        ```mermaid
        flowchart TD
            Dev[Development] --> CI[CI Tests]
            CI --> Staging[Staging]
            Staging --> Checklist[Appendix D Checklist]
            Checklist --> Prod[Production]
            Prod --> Monitor[Appendix D Post-Launch]
        ```

        ---

        ## Best Practices

        1. Print or pin complexity cheat sheet during study.
        2. Maintain a personal glossary of project-specific terms.
        3. Rehearse system design with Appendix C prompts.
        4. Run production checklists on every release.

        ---

        ## Summary

        **Appendix {letter}** provides {focus.lower()} for the Comprehensive Algorithms Guide.

        ---

        ## Exercises

        1. Memorize five complexity entries and explain each.
        2. Answer three system design prompts aloud in 25 minutes.
        3. Complete Appendix D checklist for a toy service.
        4. Add ten glossary terms from your workplace.
        5. Map five interview questions to specific chapters.

        ---

        ## Further Reading

        - [CLRS Introduction to Algorithms](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
        - [Designing Machine Learning Systems](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/)
        - [Google SRE Workbook](https://sre.google/workbook/table-of-contents/)

        ---

        **See also:** [SUMMARY.md](../../SUMMARY.md)
    """).strip() + "\n"


APPENDIX_DETAILS = {
    "a": ("Complexity Cheat Sheet", "complexity-cheat-sheet", "asymptotic complexity tables for classical and ML algorithms"),
    "b": ("Glossary", "glossary", "definitions of key terms from across the book"),
    "c": ("Interview Guide", "interview-guide", "structured question banks and study plans"),
    "d": ("Production Checklists", "production-checklists", "pre-launch and post-launch engineering checklists"),
}


def build_summary() -> str:
    """Build complete SUMMARY.md linking all chapters 0-99 and appendices."""
    entries: list[tuple[str, list[tuple[str, str]]]] = [
        (
            "Part 0 — Environment Setup & Python Fundamentals",
            [
                ("Chapter 0: Setting Up Your Algorithm Learning Environment", "./part-00-getting-started/chapter-00-environment-setup.md"),
            ],
        ),
        (
            "Part 0.5 — Mathematical Foundations",
            [
                ("Chapter 1: Functions, Sets, and Logic", "./part-05-mathematical-foundations/chapter-01-functions-sets-logic.md"),
                ("Chapter 2: Probability and Statistics", "./part-05-mathematical-foundations/chapter-02-probability-statistics.md"),
                ("Chapter 3: Vectors, Matrices, and Linear Algebra Intuition", "./part-05-mathematical-foundations/chapter-03-linear-algebra.md"),
                ("Chapter 4: Calculus and Optimization Intuition", "./part-05-mathematical-foundations/chapter-04-calculus-optimization.md"),
            ],
        ),
        (
            "Part 1 — Algorithm Fundamentals",
            [
                ("Chapter 5: What Is an Algorithm?", "./part-01-algorithm-fundamentals/chapter-05-what-is-an-algorithm.md"),
                ("Chapter 6: Essential Data Structures", "./part-01-algorithm-fundamentals/chapter-06-essential-data-structures.md"),
                ("Chapter 7: Big-O Complexity", "./part-01-algorithm-fundamentals/chapter-07-big-o-complexity.md"),
                ("Chapter 8: Design Techniques", "./part-01-algorithm-fundamentals/chapter-08-design-techniques.md"),
            ],
        ),
        (
            "Part 2 — Searching Algorithms",
            [
                ("Chapter 9: Linear Search", "./part-02-searching/chapter-09-linear-search.md"),
                ("Chapter 10: Binary Search", "./part-02-searching/chapter-10-binary-search.md"),
                ("Chapter 11: Depth-First Search (DFS)", "./part-02-searching/chapter-11-dfs.md"),
                ("Chapter 12: Breadth-First Search (BFS)", "./part-02-searching/chapter-12-bfs.md"),
                ("Chapter 13: Dijkstra's Algorithm", "./part-02-searching/chapter-13-dijkstra.md"),
                ("Chapter 14: Bellman-Ford", "./part-02-searching/chapter-14-bellman-ford.md"),
                ("Chapter 15: A* Search", "./part-02-searching/chapter-15-a-star.md"),
            ],
        ),
        (
            "Part 3 — Sorting Algorithms",
            [
                ("Chapter 16: Bubble Sort", "./part-03-sorting/chapter-16-bubble-sort.md"),
                ("Chapter 17: Selection Sort", "./part-03-sorting/chapter-17-selection-sort.md"),
                ("Chapter 18: Insertion Sort", "./part-03-sorting/chapter-18-insertion-sort.md"),
                ("Chapter 19: Merge Sort", "./part-03-sorting/chapter-19-merge-sort.md"),
                ("Chapter 20: Quick Sort", "./part-03-sorting/chapter-20-quick-sort.md"),
                ("Chapter 21: Heap Sort", "./part-03-sorting/chapter-21-heap-sort.md"),
                ("Chapter 22: Radix Sort", "./part-03-sorting/chapter-22-radix-sort.md"),
            ],
        ),
        (
            "Part 4 — Graph Algorithms",
            [
                ("Chapter 23: Graph Representations", "./part-04-graph-algorithms/chapter-23-graph-representations.md"),
                ("Chapter 24: Prim's Algorithm", "./part-04-graph-algorithms/chapter-24-prims-algorithm.md"),
                ("Chapter 25: Kruskal's Algorithm", "./part-04-graph-algorithms/chapter-25-kruskals-algorithm.md"),
                ("Chapter 26: Floyd-Warshall", "./part-04-graph-algorithms/chapter-26-floyd-warshall.md"),
                ("Chapter 27: Topological Sort", "./part-04-graph-algorithms/chapter-27-topological-sort.md"),
                ("Chapter 28: PageRank", "./part-04-graph-algorithms/chapter-28-pagerank.md"),
                ("Chapter 29: Graph Algorithms Integration", "./part-04-graph-algorithms/chapter-29-graph-algorithms-integration.md"),
            ],
        ),
        (
            "Part 5 — Machine Learning Algorithms",
            [
                ("Chapter 30: Linear Regression", "./part-05-machine-learning/chapter-30-linear-regression.md"),
                ("Chapter 31: Logistic Regression", "./part-05-machine-learning/chapter-31-logistic-regression.md"),
                ("Chapter 32: Decision Trees", "./part-05-machine-learning/chapter-32-decision-tree.md"),
                ("Chapter 33: Random Forest", "./part-05-machine-learning/chapter-33-random-forest.md"),
                ("Chapter 34: Naive Bayes", "./part-05-machine-learning/chapter-34-naive-bayes.md"),
                ("Chapter 35: Support Vector Machines (SVM)", "./part-05-machine-learning/chapter-35-svm.md"),
                ("Chapter 36: k-Nearest Neighbors (kNN)", "./part-05-machine-learning/chapter-36-knn.md"),
                ("Chapter 37: XGBoost", "./part-05-machine-learning/chapter-37-xgboost.md"),
                ("Chapter 38: LightGBM", "./part-05-machine-learning/chapter-38-lightgbm.md"),
                ("Chapter 39: k-Means Clustering", "./part-05-machine-learning/chapter-39-kmeans.md"),
                ("Chapter 40: Hierarchical Clustering", "./part-05-machine-learning/chapter-40-hierarchical-clustering.md"),
                ("Chapter 41: DBSCAN", "./part-05-machine-learning/chapter-41-dbscan.md"),
                ("Chapter 42: Principal Component Analysis (PCA)", "./part-05-machine-learning/chapter-42-pca.md"),
                ("Chapter 43: Apriori", "./part-05-machine-learning/chapter-43-apriori.md"),
            ],
        ),
    ]

    part6_10 = [
        ("part-06-deep-learning", "Part 6 — Deep Learning", [
            (44, "multilayer-perceptrons-mlp", "Multilayer Perceptrons (MLP)"),
            (45, "convolutional-neural-networks-cnn", "Convolutional Neural Networks (CNN)"),
            (46, "recurrent-neural-networks-rnn", "Recurrent Neural Networks (RNN)"),
            (47, "long-short-term-memory-lstm", "Long Short-Term Memory (LSTM)"),
            (48, "gated-recurrent-units-gru", "Gated Recurrent Units (GRU)"),
            (49, "autoencoders", "Autoencoders"),
            (50, "generative-adversarial-networks-gans", "Generative Adversarial Networks (GANs)"),
            (51, "transformers", "Transformers"),
            (52, "bert", "BERT"),
            (53, "gpt-style-models", "GPT-Style Models"),
        ]),
        ("part-07-reinforcement-learning", "Part 7 — Reinforcement Learning", [
            (54, "q-learning", "Q-Learning"),
            (55, "sarsa", "SARSA"),
            (56, "deep-q-networks-dqn", "Deep Q-Networks (DQN)"),
            (57, "actor-critic", "Actor-Critic"),
            (58, "asynchronous-advantage-actor-critic-a3c", "Asynchronous Advantage Actor-Critic (A3C)"),
            (59, "proximal-policy-optimization-ppo", "Proximal Policy Optimization (PPO)"),
        ]),
        ("part-08-swarm-intelligence", "Part 8 — Swarm Intelligence", [
            (60, "particle-swarm-optimization-pso", "Particle Swarm Optimization (PSO)"),
            (61, "ant-colony-optimization-aco", "Ant Colony Optimization (ACO)"),
            (62, "artificial-bee-colony-abc", "Artificial Bee Colony (ABC)"),
            (63, "firefly-algorithm", "Firefly Algorithm"),
            (64, "cuckoo-search", "Cuckoo Search"),
            (65, "bat-algorithm", "Bat Algorithm"),
            (66, "grey-wolf-optimizer-gwo", "Grey Wolf Optimizer (GWO)"),
            (67, "whale-optimization-algorithm-woa", "Whale Optimization Algorithm (WOA)"),
        ]),
        ("part-09-evolutionary", "Part 9 — Evolutionary Algorithms", [
            (68, "genetic-algorithms-ga", "Genetic Algorithms (GA)"),
            (69, "genetic-programming-gp", "Genetic Programming (GP)"),
            (70, "differential-evolution", "Differential Evolution (DE)"),
            (71, "evolutionary-strategies", "Evolutionary Strategies (ES)"),
        ]),
        ("part-10-optimization", "Part 10 — Optimization Algorithms", [
            (72, "gradient-descent", "Gradient Descent"),
            (73, "stochastic-gradient-descent-sgd", "Stochastic Gradient Descent (SGD)"),
            (74, "mini-batch-gradient-descent", "Mini-Batch Gradient Descent"),
            (75, "momentum", "Momentum"),
            (76, "adam-optimizer", "Adam Optimizer"),
            (77, "simulated-annealing", "Simulated Annealing"),
            (78, "hill-climbing", "Hill Climbing"),
            (79, "tabu-search", "Tabu Search"),
            (80, "branch-and-bound", "Branch and Bound"),
            (81, "dynamic-programming", "Dynamic Programming"),
            (82, "linear-programming", "Linear Programming"),
            (83, "integer-programming", "Integer Programming"),
        ]),
    ]

    for _dir, part_title, chapters in part6_10:
        items = [(f"Chapter {ch}: {title}", f"./{_dir}/chapter-{ch:02d}-{slug}.md") for ch, slug, title in chapters]
        entries.append((part_title, items))

    entries.append((
        "Part 11 — Algorithm Selection Guide",
        [("Chapter 84: Algorithm Selection Guide", "./part-11-algorithm-selection/chapter-84-algorithm-selection-guide.md")],
    ))

    project_items = [
        (f"Chapter {ch} / Project {ch - 84}: {title}", f"./part-12-projects/project-{ch - 84:02d}-{slug}.md")
        for ch, slug, title, _, _ in [(p[0], p[1], p[2], p[3], p[4]) for p in PROJECTS]
    ]
    entries.append(("Part 12 — Real-World Projects", project_items))

    ch13_items = [
        (f"Chapter {ch}: {title}", f"./part-13-ai-architecture/chapter-{ch}-{slug}.md")
        for _, ch, slug, title, _, _, _ in CHAPTERS_11_13
        if ch >= 94
    ]
    entries.append(("Part 13 — AI Systems Architecture", ch13_items))

    appendix_items = [
        (f"Appendix {letter}: {title}", f"./appendices/appendix-{letter.lower()}-{slug}.md")
        for letter, (title, slug, _) in APPENDIX_DETAILS.items()
    ]
    entries.append(("Appendices", appendix_items))

    lines = ["# Table of Contents", ""]
    for part_title, items in entries:
        lines.append(f"## {part_title}")
        lines.append("")
        for label, link in items:
            lines.append(f"- [{label}]({link})")
        lines.append("")
    return "\n".join(lines)


def update_book_spec() -> str:
    return dedent("""
        # Book Generation Specification

        This file records the authoritative specification for **Comprehensive Algorithms Guide**.
        Use it when generating new chapters with AI tools or when onboarding contributors.

        ## Title

        **Comprehensive Algorithms Guide**

        ### Subtitle

        From Beginner to Senior Level — Classical Algorithms, Artificial Intelligence, Machine Learning, Deep Learning, Reinforcement Learning, Optimization, Production Engineering, System Design, and Real-World Applications Using Python

        ## Generation Rules

        1. Generate **one chapter only** per request.
        2. Stop after each chapter; wait for **Continue**.
        3. Never skip explanations or shorten code.
        4. Every code example must be runnable.
        5. Use only free/public datasets.
        6. Pin package versions in Chapter 0.
        7. Use Python 3.12+.

        ## Chapter Structure (27 sections)

        Every chapter must contain:

        1. Learning Objectives
        2. Introduction
        3. Real-World Motivation
        4. Daily-Life Analogy
        5. Mathematical Intuition
        6. Core Concepts
        7. Visual Diagram (Mermaid)
        8. Step-by-Step Explanation
        9. Python Implementation
        10. Code Walkthrough
        11. Expected Output
        12. Output Explanation
        13. Time Complexity
        14. Space Complexity
        15. Memory Usage
        16. Performance Considerations
        17. Common Mistakes
        18. Debugging Tips
        19. Unit Tests
        20. Benchmarking
        21. Interview Questions (Beginner, Intermediate, Advanced, System Design, Coding Challenge)
        22. Production Notes
        23. Architecture Integration
        24. Best Practices
        25. Summary
        26. Exercises
        27. Further Reading

        ## Book Parts

        0. Environment Setup & Python Fundamentals
        0.5. Mathematical Foundations
        1. Algorithm Fundamentals
        2. Searching Algorithms
        3. Sorting Algorithms
        4. Graph Algorithms
        5. Machine Learning Algorithms
        6. Deep Learning
        7. Reinforcement Learning
        8. Swarm Intelligence
        9. Evolutionary Algorithms
        10. Optimization Algorithms
        11. Algorithm Selection Guide
        12. Real-World Projects
        13. AI Systems Architecture
        Appendices

        ## Quality Targets

        - 1,000–1,500 pages
        - 300+ figures
        - 500+ Python programs
        - 200+ interview questions
        - 15+ capstone projects

        ## Current Status

        | Part | Chapters | Status |
        |------|----------|--------|
        | 0 | Chapter 0: Environment Setup | **Complete** |
        | 0.5 | Chapters 1–4: Mathematical Foundations | **Complete** |
        | 1 | Chapters 5–8: Algorithm Fundamentals | **Complete** |
        | 2 | Chapters 9–15: Searching | **Complete** |
        | 3 | Chapters 16–22: Sorting | **Complete** |
        | 4 | Chapters 23–29: Graph Algorithms | **Complete** |
        | 5 | Chapters 30–43: Machine Learning | **Complete** |
        | 6 | Chapters 44–53: Deep Learning | **Complete** |
        | 7 | Chapters 54–59: Reinforcement Learning | **Complete** |
        | 8 | Chapters 60–67: Swarm Intelligence | **Complete** |
        | 9 | Chapters 68–71: Evolutionary Algorithms | **Complete** |
        | 10 | Chapters 72–83: Optimization | **Complete** |
        | 11 | Chapter 84: Algorithm Selection Guide | **Complete** |
        | 12 | Chapters 85–93: Real-World Projects (9 projects) | **Complete** |
        | 13 | Chapters 94–99: AI Systems Architecture | **Complete** |
        | Appendices | A–D | **Complete** |

        ## Book Status

        **The Comprehensive Algorithms Guide is complete.** All chapters (0–99), nine capstone projects, code modules, tests, and appendices are available in this repository.
    """).strip() + "\n"


def main() -> list[str]:
    created: list[str] = []

    for part_dir, ch, slug, title, subtitle, code_dir, module in CHAPTERS_11_13:
        part_num, part_title = PART_META[part_dir]
        md_path = ROOT / part_dir / f"chapter-{ch}-{slug}.md"
        write(md_path, chapter_md(ch, slug, title, subtitle, part_dir, part_num, part_title, code_dir, module))
        created.append(str(md_path.relative_to(ROOT)))

        test_path = ROOT / "tests" / code_dir / f"test_chapter_{ch:02d}.py"
        write(test_path, test_py(ch, module, code_dir))
        created.append(str(test_path.relative_to(ROOT)))

    for ch, slug, title, subtitle, module in PROJECTS:
        md_path = ROOT / "part-12-projects" / f"project-{ch - 84:02d}-{slug}.md"
        write(
            md_path,
            chapter_md(ch, slug, title, subtitle, "part-12-projects", 12, "Real-World Projects", "part-12", module, is_project=True),
        )
        created.append(str(md_path.relative_to(ROOT)))

        test_path = ROOT / "tests" / "part-12" / f"test_chapter_{ch:02d}.py"
        write(test_path, test_py(ch, module, "part-12"))
        created.append(str(test_path.relative_to(ROOT)))

    for letter, (title, slug, focus) in APPENDIX_DETAILS.items():
        md_path = ROOT / "appendices" / f"appendix-{letter.lower()}-{slug}.md"
        write(md_path, appendix_md(letter.upper(), title, slug, focus))
        created.append(str(md_path.relative_to(ROOT)))

    write(ROOT / "SUMMARY.md", build_summary())
    created.append("SUMMARY.md")

    write(ROOT / "BOOK_SPEC.md", update_book_spec())
    created.append("BOOK_SPEC.md")

    return created


if __name__ == "__main__":
    files = main()
    print(f"Generated {len(files)} markdown/test/spec files")
    for f in files:
        print(f)
