# ZebraLogic Brittleness Battery — Results

**Model:** `gemma-4-E4B-it`  
**Dataset:** `3x3`  
**Temperature:** `0.0`  
**Output Tokens:** `7,551`  
**Total Running Time:** `185.51s`  
**Generated:** 2026-10-12 16:09 UTC  
**Variants:** 9

---

## Summary by Category

| Variant | Category | Description | Parse | EM | Cell Acc | Avg Attr Acc | Output Tok | Time (s) |
|---------|----------|-------------|-------|----|----------|--------------|------------|----------|
| V0 | Baseline | Standard ZebraLogic baseline — canonical names, occupat… | ✅ | ✅ | 100.0% | 100.0% | 775 | 19.43 |
| V1a | Gender Bias | Stereotype-aligned names | ✅ | ✅ | 100.0% | 100.0% | 828 | 20.28 |
| V1b | Gender Bias | Stereotype-violating names: male teacher (James), femal… | ✅ | ✅ | 100.0% | 100.0% | 913 | 22.36 |
| V2a | Culture | High-frequency Anglo names: David, William, Robert. | ✅ | ✅ | 100.0% | 100.0% | 902 | 22.11 |
| V2b | Culture | Non-Western names. | ✅ | ✅ | 100.0% | 100.0% | 781 | 19.15 |
| V2c | Culture | Synthetic/OOD names. | ✅ | ✅ | 100.0% | 100.0% | 842 | 20.64 |
| V3a | Semantic | High co-occurrence semantic priors. | ✅ | ✅ | 100.0% | 100.0% | 819 | 20.08 |
| V3b | Semantic | Counter-factual semantic priors. | ✅ | ✅ | 100.0% | 100.0% | 917 | 22.49 |
| V4a | Positional | Inverted order of the clues. | ✅ | ✅ | 100.0% | 100.0% | 774 | 18.98 |

---

## Aggregate Metrics by Category

| Category | # Variants | EM Rate | Avg Cell Acc | Avg Attr Acc |
|----------|-----------|---------|--------------|--------------|
| Baseline | 1 | 100.0% | 100.0% | 100.0% |
| Gender Bias | 2 | 100.0% | 100.0% | 100.0% |
| Culture | 3 | 100.0% | 100.0% | 100.0% |
| Semantic | 2 | 100.0% | 100.0% | 100.0% |
| Positional | 1 | 100.0% | 100.0% | 100.0% |

---

## Notes
- **EM** = Exact Match: 1 iff all N house cells are completely correct.
- **Cell Acc** = fraction of houses where all attributes are correct.
- **Avg Attr Acc** = overall accuracy of individual attribute resolutions.
- Temperature = 0.0 (greedy decoding) to isolate deterministic reasoning failures.
