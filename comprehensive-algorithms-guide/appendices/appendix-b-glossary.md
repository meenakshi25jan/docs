# Appendix B: Glossary

**Comprehensive Algorithms Guide — Reference Appendix**

---

## Learning Objectives

By the end of this appendix, you will be able to:

1. Quickly reference definitions of key terms from across the book during study or interviews.
2. Apply tables and checklists to real design decisions.
3. Cross-link concepts to earlier chapters.
4. Use production checklists before shipping systems.
5. Prepare structured interview responses.
6. Compare algorithm families at a glance.
7. Maintain a personal study index from this material.

---

## Introduction

This appendix consolidates **glossary** for fast lookup. It complements Chapters 0–99 and is designed for interview prep, system design, and on-call reference.

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

| Term | Definition |
|------|------------|
| **Algorithm** | Finite sequence of steps transforming input to output (Ch. 5) |
| **Big-O** | Upper bound on growth rate of runtime or space (Ch. 7) |
| **Bias-Variance** | Error decomposition: underfit vs overfit trade-off (Ch. 30) |
| **Cross-Validation** | Resampled evaluation to estimate generalization (Ch. 30) |
| **Embedding** | Dense vector representation of discrete objects (Ch. 95) |
| **Epoch** | One full pass over training data (Ch. 44) |
| **Exploration** | Trying unknown actions/states in RL (Ch. 54) |
| **Feature Store** | Centralized serving layer for ML features (Ch. 98) |
| **Gradient** | Direction of steepest increase of a function (Ch. 72) |
| **Heuristic** | Estimated cost-to-go guiding search (Ch. 15) |
| **Hyperparameter** | Configuration set before training (Ch. 44) |
| **Inference** | Running a trained model on new data (Ch. 44) |
| **Loss Function** | Scalar objective minimized during training (Ch. 72) |
| **MLOps** | Practices for building and operating ML systems (Ch. 98) |
| **Overfitting** | Model memorizes training data, poor on test (Ch. 30) |
| **RAG** | Retrieval-Augmented Generation for grounded LLM answers (Ch. 94) |
| **Regularization** | Penalty discouraging complex models (Ch. 30) |
| **Replay Buffer** | Experience storage for off-policy RL (Ch. 56) |
| **Silhouette Score** | Cluster cohesion/separation metric (Ch. 39) |
| **Transfer Learning** | Reuse pretrained representations (Ch. 45, 90) |
| **Vector Database** | Index optimized for similarity search on embeddings (Ch. 95) |

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

**Appendix B** provides definitions of key terms from across the book for the Comprehensive Algorithms Guide.

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
