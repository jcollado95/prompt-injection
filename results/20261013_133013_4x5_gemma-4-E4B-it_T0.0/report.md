# ZebraLogic Brittleness Battery — Results

**Model:** `gemma-4-E4B-it`  
**Dataset:** `4x5`  
**Temperature:** `0.0`  
**Output Tokens:** `3,257`  
**Total Running Time:** `81.67s`  
**Generated:** 2026-10-13 11:31 UTC  
**Variants:** 1

---

## Summary by Category

| Variant | Category | Description | Parse | EM | Cell Acc | Avg Attr Acc | Output Tok | Time (s) |
|---------|----------|-------------|-------|----|----------|--------------|------------|----------|
| V0 | Baseline | Standard ZebraLogic baseline. | ✅ | ✅ | 100.0% | 100.0% | 3257 | 81.67 |

---

## Aggregate Metrics by Category

| Category | # Variants | EM Rate | Avg Cell Acc | Avg Attr Acc |
|----------|-----------|---------|--------------|--------------|
| Baseline | 1 | 100.0% | 100.0% | 100.0% |

---

## Notes
- **EM** = Exact Match: 1 iff all N house cells are completely correct.
- **Cell Acc** = fraction of houses where all attributes are correct.
- **Avg Attr Acc** = overall accuracy of individual attribute resolutions.
- Temperature = 0.0 (greedy decoding) to isolate deterministic reasoning failures.
