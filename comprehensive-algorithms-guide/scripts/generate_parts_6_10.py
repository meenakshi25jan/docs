#!/usr/bin/env python3
"""Generate Parts 6-10 chapters and tests for Comprehensive Algorithms Guide."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]

CHAPTER_MAP: list[tuple[str, int, str, str, str, str]] = [
    # part_dir, ch, slug, title, subtitle, module
    ("part-06-deep-learning", 44, "multilayer-perceptrons-mlp", "Multilayer Perceptrons (MLP)",
     "Feedforward neural networks for classification and regression.", "ch44_mlp"),
    ("part-06-deep-learning", 45, "convolutional-neural-networks-cnn", "Convolutional Neural Networks (CNN)",
     "Spatial feature extraction for image-like data.", "ch45_cnn"),
    ("part-06-deep-learning", 46, "recurrent-neural-networks-rnn", "Recurrent Neural Networks (RNN)",
     "Sequence modeling with hidden state recurrence.", "ch46_rnn"),
    ("part-06-deep-learning", 47, "long-short-term-memory-lstm", "Long Short-Term Memory (LSTM)",
     "Gated recurrence for long-range dependencies.", "ch47_lstm"),
    ("part-06-deep-learning", 48, "gated-recurrent-units-gru", "Gated Recurrent Units (GRU)",
     "Efficient gated recurrence with fewer parameters.", "ch48_gru"),
    ("part-06-deep-learning", 49, "autoencoders", "Autoencoders",
     "Unsupervised representation learning via reconstruction.", "ch49_autoencoders"),
    ("part-06-deep-learning", 50, "generative-adversarial-networks-gans", "Generative Adversarial Networks (GANs)",
     "Adversarial training for synthetic data generation.", "ch50_gans"),
    ("part-06-deep-learning", 51, "transformers", "Transformers",
     "Self-attention architectures for sequence modeling.", "ch51_transformers"),
    ("part-06-deep-learning", 52, "bert", "BERT",
     "Bidirectional encoder representations from transformers.", "ch52_bert"),
    ("part-06-deep-learning", 53, "gpt-style-models", "GPT-Style Models",
     "Autoregressive decoder-only language modeling.", "ch53_gpt_style"),
    ("part-07-reinforcement-learning", 54, "q-learning", "Q-Learning",
     "Off-policy temporal-difference control.", "ch54_q_learning"),
    ("part-07-reinforcement-learning", 55, "sarsa", "SARSA",
     "On-policy temporal-difference control.", "ch55_sarsa"),
    ("part-07-reinforcement-learning", 56, "deep-q-networks-dqn", "Deep Q-Networks (DQN)",
     "Function approximation for Q-learning.", "ch56_dqn"),
    ("part-07-reinforcement-learning", 57, "actor-critic", "Actor-Critic",
     "Joint policy and value function learning.", "ch57_actor_critic"),
    ("part-07-reinforcement-learning", 58, "asynchronous-advantage-actor-critic-a3c", "Asynchronous Advantage Actor-Critic (A3C)",
     "Parallel actor-critic with advantage estimation.", "ch58_a3c"),
    ("part-07-reinforcement-learning", 59, "proximal-policy-optimization-ppo", "Proximal Policy Optimization (PPO)",
     "Stable policy-gradient updates with clipping.", "ch59_ppo"),
    ("part-08-swarm-intelligence", 60, "particle-swarm-optimization-pso", "Particle Swarm Optimization (PSO)",
     "Swarm-based continuous optimization.", "ch60_pso"),
    ("part-08-swarm-intelligence", 61, "ant-colony-optimization-aco", "Ant Colony Optimization (ACO)",
     "Pheromone-guided combinatorial search.", "ch61_aco"),
    ("part-08-swarm-intelligence", 62, "artificial-bee-colony-abc", "Artificial Bee Colony (ABC)",
     "Foraging-inspired optimization.", "ch62_abc"),
    ("part-08-swarm-intelligence", 63, "firefly-algorithm", "Firefly Algorithm",
     "Attraction-based metaheuristic optimization.", "ch63_firefly"),
    ("part-08-swarm-intelligence", 64, "cuckoo-search", "Cuckoo Search",
     "Lévy-flight brood parasitism optimization.", "ch64_cuckoo"),
    ("part-08-swarm-intelligence", 65, "bat-algorithm", "Bat Algorithm",
     "Echolocation-inspired search.", "ch65_bat"),
    ("part-08-swarm-intelligence", 66, "grey-wolf-optimizer-gwo", "Grey Wolf Optimizer (GWO)",
     "Hierarchy-based pack hunting optimization.", "ch66_gwo"),
    ("part-08-swarm-intelligence", 67, "whale-optimization-algorithm-woa", "Whale Optimization Algorithm (WOA)",
     "Bubble-net foraging inspired search.", "ch67_woa"),
    ("part-09-evolutionary", 68, "genetic-algorithms-ga", "Genetic Algorithms (GA)",
     "Selection, crossover, and mutation over populations.", "ch68_ga"),
    ("part-09-evolutionary", 69, "genetic-programming-gp", "Genetic Programming (GP)",
     "Evolution of executable program structures.", "ch69_gp"),
    ("part-09-evolutionary", 70, "differential-evolution", "Differential Evolution (DE)",
     "Vector-difference driven continuous search.", "ch70_differential_evolution"),
    ("part-09-evolutionary", 71, "evolutionary-strategies", "Evolutionary Strategies (ES)",
     "Gaussian perturbation evolution for continuous optimization.", "ch71_evolutionary_strategies"),
    ("part-10-optimization", 72, "gradient-descent", "Gradient Descent",
     "First-order iterative minimization.", "ch72_gradient_descent"),
    ("part-10-optimization", 73, "stochastic-gradient-descent-sgd", "Stochastic Gradient Descent (SGD)",
     "Noisy gradient steps from random samples.", "ch73_sgd"),
    ("part-10-optimization", 74, "mini-batch-gradient-descent", "Mini-Batch Gradient Descent",
     "Variance-bias trade-off via batched gradients.", "ch74_mini_batch"),
    ("part-10-optimization", 75, "momentum", "Momentum",
     "Velocity accumulation for faster convergence.", "ch75_momentum"),
    ("part-10-optimization", 76, "adam-optimizer", "Adam Optimizer",
     "Adaptive moment estimation for deep learning.", "ch76_adam"),
    ("part-10-optimization", 77, "simulated-annealing", "Simulated Annealing",
     "Probabilistic hill climbing with cooling schedule.", "ch77_simulated_annealing"),
    ("part-10-optimization", 78, "hill-climbing", "Hill Climbing",
     "Local search by greedy neighbor improvement.", "ch78_hill_climbing"),
    ("part-10-optimization", 79, "tabu-search", "Tabu Search",
     "Memory-guided escape from local optima.", "ch79_tabu_search"),
    ("part-10-optimization", 80, "branch-and-bound", "Branch and Bound",
     "Systematic enumeration with pruning bounds.", "ch80_branch_and_bound"),
    ("part-10-optimization", 81, "dynamic-programming", "Dynamic Programming",
     "Optimal substructure via memoized recursion.", "ch81_dynamic_programming"),
    ("part-10-optimization", 82, "linear-programming", "Linear Programming",
     "Linear objective with linear constraints.", "ch82_linear_programming"),
    ("part-10-optimization", 83, "integer-programming", "Integer Programming",
     "Discrete optimization with integrality constraints.", "ch83_integer_programming"),
]

PART_META = {
    "part-06-deep-learning": (6, "Deep Learning", "part-06"),
    "part-07-reinforcement-learning": (7, "Reinforcement Learning", "part-07"),
    "part-08-swarm-intelligence": (8, "Swarm Intelligence", "part-08"),
    "part-09-evolutionary": (9, "Evolutionary Algorithms", "part-09"),
    "part-10-optimization": (10, "Optimization Algorithms", "part-10"),
}

TEST_ASSERTIONS = {
    "ch44_mlp": "result = mod.main()\n    assert result >= 0.75",
    "ch45_cnn": "result = mod.main()\n    assert result >= 0",
    "ch46_rnn": "result = mod.main()\n    assert result < 2.0",
    "ch47_lstm": "result = mod.main()\n    assert result > 0",
    "ch48_gru": "result = mod.main()\n    assert result > 0",
    "ch49_autoencoders": "result = mod.main()\n    assert result < 1.0",
    "ch50_gans": "result = mod.main()\n    assert result < 100.0",
    "ch51_transformers": "result = mod.main()\n    assert result >= 0",
    "ch52_bert": "result = mod.main()\n    assert result == 1.0",
    "ch53_gpt_style": "result = mod.main()\n    assert result > 0",
    "ch54_q_learning": "result = mod.main()\n    assert result > 0",
    "ch55_sarsa": "result = mod.main()\n    assert result > 0",
    "ch56_dqn": "result = mod.main()\n    assert result > -5.0",
    "ch57_actor_critic": "result = mod.main()\n    assert result > 0.3",
    "ch58_a3c": "result = mod.main()\n    assert result > 0.2",
    "ch59_ppo": "result = mod.main()\n    assert result > 0.3",
    "ch60_pso": "result = mod.main()\n    assert result < 1.0",
    "ch61_aco": "result = mod.main()\n    assert result > 0",
    "ch62_abc": "result = mod.main()\n    assert result < 50",
    "ch63_firefly": "result = mod.main()\n    assert result < 20.0",
    "ch64_cuckoo": "result = mod.main()\n    assert result < 25",
    "ch65_bat": "result = mod.main()\n    assert result < 20.0",
    "ch66_gwo": "result = mod.main()\n    assert result < 2.0",
    "ch67_woa": "result = mod.main()\n    assert result < 2.0",
    "ch68_ga": "result = mod.main()\n    assert result >= 6",
    "ch69_gp": "result = mod.main()\n    assert result < 2.0",
    "ch70_differential_evolution": "result = mod.main()\n    assert result < 100",
    "ch71_evolutionary_strategies": "result = mod.main()\n    assert result < 5.0",
    "ch72_gradient_descent": "result = mod.main()\n    assert result < 0.01",
    "ch73_sgd": "result = mod.main()\n    assert result < 0.5",
    "ch74_mini_batch": "result = mod.main()\n    assert result < 0.5",
    "ch75_momentum": "result = mod.main()\n    assert result < 5.0",
    "ch76_adam": "result = mod.main()\n    assert result < 1.0",
    "ch77_simulated_annealing": "result = mod.main()\n    assert result < 20",
    "ch78_hill_climbing": "result = mod.main()\n    assert result >= 49",
    "ch79_tabu_search": "result = mod.main()\n    assert result > 0",
    "ch80_branch_and_bound": "result = mod.main()\n    assert result >= 8",
    "ch81_dynamic_programming": "result = mod.main()\n    assert result >= 8",
    "ch82_linear_programming": "result = mod.main()\n    assert result >= 9",
    "ch83_integer_programming": "result = mod.main()\n    assert result >= 2",
}


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def chapter_md(
    ch: int, slug: str, title: str, subtitle: str,
    part_dir: str, part_num: int, part_title: str, code_dir: str, module: str,
) -> str:
    rel_code = f"../../code/{code_dir}/{module}.py"
    rel_test = f"../../tests/{code_dir}/test_chapter_{ch:02d}.py"
    body = dedent(f"""
        # Chapter {ch}: {title}

        **Part {part_num} — {part_title}**

        ---

        ## Learning Objectives

        By the end of this chapter, you will be able to:

        1. Explain the core idea behind {title} and when to use it.
        2. Describe the mathematical intuition and key hyperparameters.
        3. Implement and run a small Python example from this repository.
        4. Analyze time and space complexity of the reference implementation.
        5. Identify common mistakes and debugging strategies.
        6. Answer interview questions from beginner through system-design level.
        7. Connect the algorithm to production engineering concerns.

        ---

        ## Introduction

        {subtitle} This chapter is part of the **Comprehensive Algorithms Guide** and follows the book's 27-section structure. Every example is runnable from [`code/{code_dir}/{module}.py`]({rel_code}).

        ---

        ## Real-World Motivation

        Industry teams use {title.lower()} when accuracy, search quality, or optimization performance must exceed simple baselines. The technique appears in ML training pipelines, robotics, logistics, and automated decision systems.

        ---

        ## Daily-Life Analogy

        Imagine improving a recipe through trial and feedback: adjust ingredients, taste the result, remember what worked, and avoid repeating mistakes. {title} formalizes that improvement loop with mathematics and code.

        ---

        ## Mathematical Intuition

        {title} optimizes an objective (loss, reward, fitness, or cost) over a structured search space. Track the objective value, step size or learning rate, constraints, and convergence criteria.

        ---

        ## Core Concepts

        | Concept | Role |
        |---------|------|
        | Representation | How solutions are encoded |
        | Objective | Quantity to minimize or maximize |
        | Update rule | How candidates change each iteration |
        | Exploration | Diversity to escape local optima |
        | Exploitation | Refining promising candidates |
        | Hyperparameters | Algorithm tuning knobs |
        | Evaluation | Measuring quality on data or simulations |

        ---

        ## Visual Diagram

        ```mermaid
        flowchart TD
            A[Problem Definition] --> B[Initialize]
            B --> C[Evaluate]
            C --> D{{Converged?}}
            D -->|No| E[{title} Update]
            E --> C
            D -->|Yes| F[Best Solution]
        ```

        ---

        ## Step-by-Step Explanation

        1. **Define** inputs, outputs, and objective.
        2. **Represent** solutions (weights, paths, populations).
        3. **Initialize** with reproducible random seeds.
        4. **Iterate** evaluation and updates until budget exhausted.
        5. **Validate** on holdout data or simulations.
        6. **Deploy** with monitoring and versioning.

        ---

        ## Python Implementation

        Reference: [`code/{code_dir}/{module}.py`]({rel_code})

        ```bash
        python code/{code_dir}/{module}.py
        ```

        ---

        ## Code Walkthrough

        1. Imports and constants with fixed seeds.
        2. Core data structures for the algorithm.
        3. Objective or environment logic.
        4. Main training/optimization loop.
        5. `main()` prints metrics and **SUCCESS**.

        ---

        ## Expected Output

        A short trace ending with **SUCCESS** and a final metric (loss, reward, fitness, or objective).

        ---

        ## Output Explanation

        Early iterations show poor metrics; later iterations improve if hyperparameters are reasonable. Divergence or flatlines indicate tuning or bug issues.

        ---

        ## Time Complexity

        Typically **O(T · cost_per_step)** where **T** is iterations and cost depends on problem size **n** and dimensionality **d**.

        ---

        ## Space Complexity

        Usually **O(n + d)** plus auxiliary structures (populations, replay buffers, tabu lists).

        ---

        ## Memory Usage

        Book examples use modest RAM. Production may require batching, GPUs, or distributed workers.

        ---

        ## Performance Considerations

        1. Vectorize with NumPy.
        2. Fix random seeds for benchmarks.
        3. Log metrics each epoch.
        4. Normalize inputs for neural methods.
        5. Tune one hyperparameter at a time.

        ---

        ## Common Mistakes

        | Mistake | Symptom | Fix |
        |---------|---------|-----|
        | LR too high | Divergence | Reduce step size |
        | No exploration | Local optima | Add noise or diversity |
        | Data leakage | Inflated metrics | Proper splits |
        | Bad reward | Wrong behavior | Redesign signal |
        | Unbounded search | NaN values | Clip or normalize |

        ---

        ## Debugging Tips

        1. Plot objective over iterations.
        2. Overfit a tiny dataset to verify code.
        3. Compare against a baseline.
        4. Assert finite values after updates.
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

        1. What problem does {title} solve?
        2. What is training vs inference?
        3. Name one hyperparameter.
        4. What is overfitting?
        5. Why use random seeds?

        ### Intermediate (5)

        1. Compare {title} to a simpler baseline.
        2. How does exploration vs exploitation appear?
        3. What production metrics matter?
        4. How do you debug instability?
        5. What is one-iteration complexity?

        ### Advanced (5)

        1. Sketch the main update rule.
        2. What failure modes appear at scale?
        3. How would you parallelize?
        4. What regularization helps?
        5. How do you search hyperparameters?

        ### System Design (3)

        1. Design a training pipeline with CI and model registry.
        2. How would you serve with SLOs?
        3. What monitoring prevents bad deploys?

        ### Coding Challenge (1)

        Implement a minimal {title} on a new toy problem and add pytest.

        ---

        ## Production Notes

        - Version data, code, hyperparameters, and artifacts.
        - Pin dependencies in `requirements.txt`.
        - Gate promotion on offline metric regression.
        - Monitor latency, throughput, errors, and drift.
        - Validate inputs and cap resource usage.
        - Use early stopping and right-sized hardware.

        ---

        ## Architecture Integration

        ```mermaid
        flowchart LR
            Data[Features] --> Train[Training]
            Train --> Registry[Model Registry]
            Registry --> Serve[Inference]
            Serve --> Monitor[Monitoring]
            Monitor --> Retrain[Retrain]
            Retrain --> Train
        ```

        ---

        ## Best Practices

        1. Smallest example that proves correctness.
        2. Document assumptions.
        3. Align train and serve environments.
        4. Test core invariants.
        5. Prefer interpretable baselines first.

        ---

        ## Summary

        Covered **{title}**: motivation, intuition, runnable code, complexity, tests, interviews, and production guidance.

        ---

        ## Exercises

        1. Change a hyperparameter and plot curves.
        2. Add regularization if applicable.
        3. Compare against random search.
        4. Swap the toy dataset.
        5. Add a pytest edge case.

        ---

        ## Further Reading

        - [PyTorch Tutorials](https://pytorch.org/tutorials/)
        - [Gymnasium Docs](https://gymnasium.farama.org/)
        - [NumPy Reference](https://numpy.org/doc/stable/reference/)
        - [SciPy Optimization](https://docs.scipy.org/doc/scipy/reference/optimize.html)
        - Sutton & Barto — *Reinforcement Learning*
        - Scholar search for {title} original papers

        ---

        **Next chapter:** Chapter {ch + 1} — see [SUMMARY.md](../../SUMMARY.md)
    """)
    lines = []
    for line in body.splitlines():
        if line.startswith("        "):
            lines.append(line[8:])
        else:
            lines.append(line)
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


def update_summary() -> None:
    lines = [
        "# Table of Contents",
        "",
        "## Part 0 — Environment Setup & Python Fundamentals",
        "",
        "- [Chapter 0: Setting Up Your Algorithm Learning Environment](./part-00-getting-started/chapter-00-environment-setup.md)",
        "",
    ]
    sections = [
        ("Part 0.5 — Mathematical Foundations", "part-00-getting-started", [(1, "functions-sets-and-logic", "Functions, Sets, and Logic")]),
        ("Part 6 — Deep Learning", "part-06-deep-learning", []),
        ("Part 7 — Reinforcement Learning", "part-07-reinforcement-learning", []),
        ("Part 8 — Swarm Intelligence", "part-08-swarm-intelligence", []),
        ("Part 9 — Evolutionary Algorithms", "part-09-evolutionary", []),
        ("Part 10 — Optimization Algorithms", "part-10-optimization", []),
    ]
    for part_dir, ch, slug, title, *_ in CHAPTER_MAP:
        for name, pdir, _ in sections:
            if pdir == part_dir:
                sections[sections.index((name, pdir, _))] = (name, pdir, sections[sections.index((name, pdir, _))][2] + [(ch, slug, title)])

    # rebuild properly
    part_groups: dict[str, list] = {}
    part_titles = {
        "part-06-deep-learning": "Part 6 — Deep Learning",
        "part-07-reinforcement-learning": "Part 7 — Reinforcement Learning",
        "part-08-swarm-intelligence": "Part 8 — Swarm Intelligence",
        "part-09-evolutionary": "Part 9 — Evolutionary Algorithms",
        "part-10-optimization": "Part 10 — Optimization Algorithms",
    }
    for part_dir, ch, slug, title, *_ in CHAPTER_MAP:
        part_groups.setdefault(part_dir, []).append((ch, slug, title))

    lines += [
        "## Part 0.5 — Mathematical Foundations",
        "",
        "- Chapter 1: Functions, Sets, and Logic *(planned)*",
        "- Chapter 2: Probability and Statistics *(planned)*",
        "- Chapter 3: Vectors, Matrices, and Linear Algebra Intuition *(planned)*",
        "- Chapter 4: Calculus and Optimization Intuition *(planned)*",
        "",
        "## Part 1 — Algorithm Fundamentals",
        "",
        "- Chapters 5–8 *(planned)*",
        "",
        "## Part 2 — Searching Algorithms",
        "",
        "- Chapters 9–15 *(planned)*",
        "",
        "## Part 3 — Sorting Algorithms",
        "",
        "- Chapters 16–22 *(planned)*",
        "",
        "## Part 4 — Graph Algorithms",
        "",
        "- Chapters 23–29 *(planned)*",
        "",
        "## Part 5 — Machine Learning Algorithms",
        "",
        "- Chapters 30–43 *(planned)*",
        "",
    ]
    for part_dir in part_groups:
        lines.append(f"## {part_titles[part_dir]}")
        lines.append("")
        for ch, slug, title in part_groups[part_dir]:
            lines.append(f"- [Chapter {ch}: {title}](./{part_dir}/chapter-{ch:02d}-{slug}.md)")
        lines.append("")

    lines += [
        "## Part 11 — Algorithm Selection Guide",
        "",
        "- Chapter 84 *(planned)*",
        "",
        "## Part 12 — Real-World Projects",
        "",
        "- Projects 1–9 *(planned)*",
        "",
        "## Part 13 — AI Systems Architecture",
        "",
        "- Chapters 85–90 *(planned)*",
        "",
        "## Appendices",
        "",
        "- Appendix A: Complexity Cheat Sheet *(planned)*",
        "- Appendix B: Glossary *(planned)*",
        "- Appendix C: Interview Guide *(planned)*",
        "- Appendix D: Production Checklists *(planned)*",
    ]
    write(ROOT / "SUMMARY.md", "\n".join(lines))


def main() -> list[str]:
    created: list[str] = []
    for part_dir, ch, slug, title, subtitle, module in CHAPTER_MAP:
        part_num, part_title, code_dir = PART_META[part_dir]
        md_path = ROOT / part_dir / f"chapter-{ch:02d}-{slug}.md"
        write(md_path, chapter_md(ch, slug, title, subtitle, part_dir, part_num, part_title, code_dir, module))
        created.append(str(md_path.relative_to(ROOT)))

        test_path = ROOT / "tests" / code_dir / f"test_chapter_{ch:02d}.py"
        write(test_path, test_py(ch, module, code_dir))
        created.append(str(test_path.relative_to(ROOT)))

    update_summary()
    created.append("SUMMARY.md")
    return created


if __name__ == "__main__":
    files = main()
    print(f"Generated {len(files)} files")
    for f in files:
        print(f)
