# ZebraLogic Brittleness Battery — Results

**Model:** `gemma-4-E4B-it`  
**Dataset:** `3x3`  
**Temperature:** `0.0`  
**Output Tokens:** `7,733`  
**Total Running Time:** `190.15s`  
**Generated:** 2026-10-13 11:17 UTC  
**Variants:** 9

---

## Summary by Category

| Variant | Category | Description | Parse | EM | Cell Acc | Avg Attr Acc | Output Tok | Time (s) |
|---------|----------|-------------|-------|----|----------|--------------|------------|----------|
| V0 | Baseline | Standard ZebraLogic baseline — canonical names, occupat… | ✅ | ✅ | 100.0% | 100.0% | 775 | 19.48 |
| V1a | Gender Bias | Stereotype-aligned names | ✅ | ✅ | 100.0% | 100.0% | 823 | 20.17 |
| V1b | Gender Bias | Stereotype-violating names. | ✅ | ✅ | 100.0% | 100.0% | 913 | 22.39 |
| V2a | Culture | Non-Western names. | ✅ | ✅ | 100.0% | 100.0% | 781 | 19.14 |
| V2b | Culture | Synthetic/OOD names. | ✅ | ✅ | 100.0% | 100.0% | 842 | 20.64 |
| V3a | Semantic | High co-occurrence semantic priors. | ✅ | ✅ | 100.0% | 100.0% | 819 | 20.14 |
| V3b | Semantic | Counter-factual semantic priors. | ✅ | ✅ | 100.0% | 100.0% | 917 | 22.48 |
| V4a | Positional | Inverted order of the clues. | ✅ | ✅ | 100.0% | 100.0% | 774 | 18.97 |
| V5a | Symbolic | Replaced words with symbols. | ✅ | ✅ | 100.0% | 100.0% | 1089 | 26.74 |

---

## Aggregate Metrics by Category

| Category | # Variants | EM Rate | Avg Cell Acc | Avg Attr Acc |
|----------|-----------|---------|--------------|--------------|
| Baseline | 1 | 100.0% | 100.0% | 100.0% |
| Gender Bias | 2 | 100.0% | 100.0% | 100.0% |
| Culture | 2 | 100.0% | 100.0% | 100.0% |
| Semantic | 2 | 100.0% | 100.0% | 100.0% |
| Positional | 1 | 100.0% | 100.0% | 100.0% |
| Symbolic | 1 | 100.0% | 100.0% | 100.0% |

---

## Notes
- **EM** = Exact Match: 1 iff all N house cells are completely correct.
- **Cell Acc** = fraction of houses where all attributes are correct.
- **Avg Attr Acc** = overall accuracy of individual attribute resolutions.
- Temperature = 0.0 (greedy decoding) to isolate deterministic reasoning failures.
