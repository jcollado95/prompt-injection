# ZebraLogic Brittleness Battery — Results

**Model:** `gemma-4-E4B-it`  
**Dataset:** `5x5`  
**Temperature:** `0.0`  
**Output Tokens:** `11,055`  
**Total Running Time:** `287.33s`  
**Generated:** 2026-10-12 15:37 UTC  
**Variants:** 1

---

## Summary by Category

| Variant | Category | Description | Parse | EM | Cell Acc | Avg Attr Acc | Output Tok | Time (s) |
|---------|----------|-------------|-------|----|----------|--------------|------------|----------|
| V0 | Baseline | Standard ZebraLogic baseline canonical names, occupatio… | ✅ | ❌ | 0.0% | 16.0% | 11055 | 287.32 |

---

## Aggregate Metrics by Category

| Category | # Variants | EM Rate | Avg Cell Acc | Avg Attr Acc |
|----------|-----------|---------|--------------|--------------|
| Baseline | 1 | 0.0% | 0.0% | 16.0% |

---

## Notes
- **EM** = Exact Match: 1 iff all N house cells are completely correct.
- **Cell Acc** = fraction of houses where all attributes are correct.
- **Avg Attr Acc** = overall accuracy of individual attribute resolutions.
- Temperature = 0.0 (greedy decoding) to isolate deterministic reasoning failures.
