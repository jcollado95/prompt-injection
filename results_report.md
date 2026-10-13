# ZebraLogic Brittleness Battery: Results and Future Directions

## 1. Experimental Results Summary

We conducted zero-shot empirical evaluations using `gemma-4-E4B-it` (temperature = 0.0, greedy decoding) to evaluate the fragility and scalability of Small Language Models (SLMs) on constraint-satisfaction tasks across different puzzle dimensions and perturbation axes.

### Comparative Cross-Complexity Overview

| Dataset Dimension | Evaluated Variants | Exact Match (EM) | Cell Accuracy | Avg Attr Accuracy | Output Tokens | Total Running Time | Avg Tokens / Variant | Avg Latency / Variant |
|:------------------|:-------------------|:-----------------|:--------------|:------------------|:--------------|:-------------------|:---------------------|:----------------------|
| **3x3** | 9 (Full Battery) | **100.0%** (9/9) | **100.0%** | **100.0%** | 7,733 | 190.15s (~3.2m) | 859 tok | 21.13s |
| **4x4** | 1 (Baseline V0) | **100.0%** (1/1) | **100.0%** | **100.0%** | 2,375 | 59.21s (~1.0m) | 2,375 tok | 59.21s |
| **5x5** | 1 (Baseline V0) | **0.0%** (0/1) | **0.0%** | **16.0%** (4/25) | 11,055 | 287.33s (~4.8m) | 11,055 tok | 287.33s |

---

## 2. Key Empirical Findings

### A. Surface & Structural Robustness on 3x3 Puzzles
In the 3x3 battery, `gemma-4-E4B-it` was tested across five distinct perturbation categories totaling 9 variants:
- **Baseline (V0):** 100% EM (775 tokens, 19.48s).
- **Gender Bias (V1a stereotype-aligned, V1b stereotype-violating):** 100% EM for both variants, showing no vulnerability to gendered occupation priors.
- **Culture (V2a Non-Western, V2b Synthetic/OOD):** 100% EM across both variants, proving resilient to low-frequency and synthetic name entities.
- **Semantic Priors (V3a High co-occurrence, V3b Counter-factual):** 100% EM on both variants, demonstrating robust adherence to logical clues over semantic associations.
- **Positional Perturbation (V4a Inverted clue order):** 100% EM (774 tokens, 18.97s), demonstrating immunity to clue presentation ordering on smaller constraint spaces.
- **Symbolic (V5a Replaced words with symbols):** 100% EM (1,089 tokens, 26.74s). Replacing natural-language entities with arbitrary symbols tests pure structural reasoning, isolated from any lexical or semantic priors. The model solved correctly despite the higher token cost, suggesting robust constraint propagation independent of token familiarity.

### B. Moderate Scaling on 4x4 Puzzles
On the 4x4 baseline (`data/4x4.json`):
- The model generated 2,375 output tokens and completed reasoning in 59.21 seconds.
- The model achieved **100% Exact Match**, correctly resolving all 16 attributes across 4 houses.
- Token consumption scaled by ~2.8× relative to the 3x3 baseline, maintaining complete reasoning integrity.

### C. The 5x5 Complexity Cliff & Reasoning Breakdown
On the 5x5 baseline (`data/5x5.json`), a severe reasoning collapse occurred:
- **Token Inflation:** The model generated **11,055 tokens** (nearly 5× the 4x4 requirement and 14× the 3x3 requirement) over **287.33s** before terminating.
- **Search-Space Thrashing:** Inspection of the raw reasoning trace (`raw/V0.txt`) revealed repetitive case analysis (testing hypotheses across cases A, B.1, B.2, C.1, C.2, D). The model repeatedly encountered dead ends and failed to propagate negative constraints globally.
- **Constraint Amnesia:** After exhausting hypotheses, the model settled on a solution that violated explicit negative clues (e.g. violating clue 4: *"Peter is not in the first house"*, placing Peter in House 1).
- **Final Accuracy:** 0.0% EM and only 16.0% attribute accuracy (4/25 correct attributes).

This empirical threshold demonstrates that while `gemma-4-E4B-it` is highly robust to surface perturbations on small search spaces, it experiences a sharp reasoning breakdown when the combinatorial search space expands to 5 entities × 5 attributes.

---

## 3. Methodological Challenges for Automated Scaling

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

## 4. Proposed Next Steps

### A. Semantic Annotation via Auxiliary Teacher LLMs (discarded)
Use an auxiliary high-capacity model (e.g., Claude 3.5 Sonnet / GPT-4o) as a specialized offline annotator:
1. **Schema Parsing:** Extract entity sets and constraint graph types from sampled ZebraLogic puzzles.
2. **Bias Eligibility Classification:** Prompt the teacher model to identify which attribute pairs support meaningful societal or semantic perturbations.
3. **Isomorphic Substitution:** Generate calibrated entity replacement tables and re-render clue texts while verifying that the ground-truth solution maps 1-to-1 without ambiguity.

### B. Knowledge Graph (KG) and Ontology-Grounded Substitutions
Leverage structured knowledge sources (e.g., ConceptNet, Wikidata) to automate entity generation:
- Mine relation triples (e.g., `(Architect, RelatedTo, Building)`) to dynamically construct high co-occurrence and counter-factual variants.
- Utilize demographic frequency distributions to generate culturally grounded or out-of-distribution entity sets.

### C. Complexity-Adaptive Battery Benchmarking
Given the stark performance divergence between 4x4 and 5x5:
- Benchmark intermediate complexity classes (e.g., 4x5, 5x4) to locate the exact phase-transition point where greedy decoding breaks down.
