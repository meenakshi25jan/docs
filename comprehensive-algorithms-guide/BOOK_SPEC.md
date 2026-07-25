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

## Algorithm Template (25 sections)

See BOOK_SPEC in repository discussions or contributor guide for the full algorithm template.

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

| Part | Chapter | Status |
|------|---------|--------|
| 0 | Chapter 0: Environment Setup | **Complete** |
| 0.5 | Mathematical Foundations | Planned |
| 1+ | Remaining chapters | Planned |

Reply **Continue** to generate the next chapter.
