# ZebraLogic Brittleness Battery: Results and Future Directions

## 1. Experimental Results Summary

We conducted zero-shot empirical evaluations using `gemma-4-E4B-it` (temperature = 0.0, greedy decoding) to evaluate the fragility and scalability of Small Language Models (SLMs) on constraint-satisfaction tasks across different puzzle dimensions and perturbation axes.

Our benchmark design and complexity taxonomy follow the **ZebraLogic** framework (Lin et al., 2025)[^1], which categorizes logic grid puzzles by search-space size |S| = (N!)^M for an N×M grid: **Small** (|S| < 10³), **Medium** (10³ ≤ |S| < 10⁶), **Large** (10⁶ ≤ |S| < 10¹⁰), and **X-Large** (|S| ≥ 10¹⁰).

[^1]: Bill Yuchen Lin, Ronan Le Bras, et al. *ZebraLogic: On the Scaling Limits of LLMs for Logical Reasoning.* arXiv:2502.01100, 2025.

### Comparative Cross-Complexity Overview

| Dataset | ZebraLogic Size | \|S\| = (N!)^M | Evaluated Variants | EM | Cell Acc | Avg Attr Acc | Tokens | Total Time | Avg Tok/Var | Avg Lat/Var |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| 3×3 | Small | 216 | 9 (Full Battery) | 100.0% (9/9) | 100.0% | 100.0% | 7,733 | 190.15s (~3.2m) | 859 tok | 21.13s |
| 4×4 | Medium | 331,776 | 1 (Baseline V0) | 100.0% (1/1) | 100.0% | 100.0% | 2,375 | 59.21s (~1.0m) | 2,375 tok | 59.21s |
| 4×5 | Large | ~7.96 × 10⁶ | 1 (Baseline V0) | 100.0% (1/1) | 100.0% | 100.0% | 3,257 | 81.67s (~1.4m) | 3,257 tok | 81.67s |
| 5×5 | X-Large | ~2.49 × 10¹⁰ | 1 (Baseline V0) | 0.0% (0/1) | 0.0% | 16.0% (4/25) | 11,055 | 287.33s (~4.8m) | 11,055 tok | 287.33s |

---

## 2. Methodological Challenges for Automated Scaling

To scale this evaluation from fixed hand-crafted puzzles to arbitrary puzzles from the **WildEval/ZebraLogic dataset**, the pipeline must proceduralize variant generation across two major dimensions.

### Challenge 1: Variable-Bias Mapping
When sampling a random puzzle, the attributes (variables) are arbitrary (e.g., *Colors, Pets, Cars, Nationalities, Occupations, Drinks, Instruments*).
- **The Problem:** Bias perturbations are not universally applicable. While *Occupation* and *Hobby* naturally map to gender or social biases, variables like *Nationality* or *Language* map to cultural/geopolitical biases, and *Color* or *Beverage* have few direct social priors.
- **Requirement:** A programmatic mechanism to analyze arbitrary attribute schemas and assign appropriate perturbation axes (Gender, Culture, Semantic, Positional).

### Challenge 2: Automated Entity Extraction and Template Filling
Once perturbation axes are identified for a sampled puzzle, entities in both the puzzle narrative and clues must be systematically substituted.
- **The Problem:** Generating counter-factual or stereotype-violating variants requires sourcing entity pairs with well-calibrated semantic distances (e.g., strong co-occurrence vs. strong contradiction) without manual authoring.
- **Requirement:** High-precision substitution that preserves problem isomorphism (guaranteeing that the underlying constraint graph and unique solution remain strictly unchanged).

---

## 3. Proposed Next Steps

### A. Knowledge Graph (KG) and Ontology-Grounded Substitutions
Leverage structured knowledge sources (e.g., ConceptNet, Wikidata) to automate entity generation:
- Mine relation triples (e.g., `(Architect, RelatedTo, Building)`) to dynamically construct high co-occurrence and counter-factual variants.
- Utilize demographic frequency distributions to generate culturally grounded or out-of-distribution entity sets.

### B. Complexity-Adaptive Battery Benchmarking
Given the stark performance divergence between 4×5 (Large, 100% EM) and 5×5 (X-Large, 0% EM):
- The 4×5 result narrows the phase-transition window to [Large → X-Large], i.e., |S| ∈ [~10⁷, ~10¹⁰].
- Benchmark intermediate complexity classes (e.g., 5x4, 6x3) to locate the exact phase-transition point where greedy decoding breaks down.
