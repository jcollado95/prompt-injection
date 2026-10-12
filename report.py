"""
report.py — Generates CSV and Markdown summary reports from evaluation results.
Supports dynamic attributes based on inference logic.
"""

import csv
from pathlib import Path
from datetime import datetime

_CATEGORY_ORDER = ["Baseline", "Gender Bias", "Culture", "Semantic", "Positional"]

def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"

def generate_reports(
    results: list[dict],
    output_dir: Path,
    model: str,
    dataset: str = "",
    temperature: float = None,
    total_time: float = None,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    # Resolve temperature if not explicitly passed
    if temperature is None:
        for r in results:
            if "temperature" in r and r["temperature"] is not None:
                temperature = r["temperature"]
                break

    # Calculate token usage and total time
    total_tokens = sum(r["output_tokens"] for r in results if r.get("output_tokens") is not None)
    has_tokens = any(r.get("output_tokens") is not None for r in results)
    tokens_str = f"{total_tokens:,}" if has_tokens else "—"

    if total_time is None:
        valid_times = [r["elapsed_sec"] for r in results if r.get("elapsed_sec") is not None]
        total_time = sum(valid_times) if valid_times else None
    total_time_str = f"{total_time:.2f}s" if total_time is not None else "—"

    # 1. Discover all unique keys for the CSV (including dynamic hits_XYZ)
    csv_fields = [
        "variant_id", "category", "description", "dataset", "model", 
        "temperature", "output_tokens", "elapsed_sec", "parse_success", "exact_match", 
        "cell_accuracy", "avg_attr_acc", "cells_correct", "total_cells", "error"
    ]
    dynamic_fields = set()
    for r in results:
        if "dataset" not in r and dataset:
            r["dataset"] = dataset
        if "temperature" not in r and temperature is not None:
            r["temperature"] = temperature
        for k in r.keys():
            if k.startswith("hits_"):
                dynamic_fields.add(k)
    
    csv_fields.extend(sorted(list(dynamic_fields)))

    # ------------------------------------------------------------------ CSV
    csv_path = output_dir / "report.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
    print(f"\n[report] CSV written → {csv_path}")

    # ------------------------------------------------------------------ Markdown
    md_path = output_dir / "report.md"
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    temp_str = f"{temperature}" if temperature is not None else "—"

    lines = [
        "# ZebraLogic Brittleness Battery — Results",
        "",
        f"**Model:** `{model}`  ",
    ]
    if dataset:
        lines.append(f"**Dataset:** `{dataset}`  ")
    lines.append(f"**Temperature:** `{temp_str}`  ")
    lines.append(f"**Output Tokens:** `{tokens_str}`  ")
    lines.append(f"**Total Running Time:** `{total_time_str}`  ")
    lines.extend([
        f"**Generated:** {timestamp}  ",
        f"**Variants:** {len(results)}",
        "",
        "---",
        "",
        "## Summary by Category",
        "",
        "| Variant | Category | Description | Parse | EM | Cell Acc | Avg Attr Acc | Output Tok | Time (s) |",
        "|---------|----------|-------------|-------|----|----------|--------------|------------|----------|",
    ])

    by_cat = {c: [] for c in _CATEGORY_ORDER}
    for r in results:
        cat = r.get("category", "Unknown")
        by_cat.setdefault(cat, []).append(r)

    for cat in _CATEGORY_ORDER:
        for r in by_cat.get(cat, []):
            parse_ok = "✅" if r.get("parse_success") else "❌"
            em       = "✅" if r.get("exact_match")   else "❌"
            desc     = r.get("description", "")[:55] + ("…" if len(r.get("description", "")) > 55 else "")
            tok_val  = str(r["output_tokens"]) if r.get("output_tokens") is not None else "—"
            lines.append(
                f"| {r['variant_id']} | {r['category']} | {desc} "
                f"| {parse_ok} | {em} "
                f"| {_pct(r.get('cell_accuracy', 0.0))} "
                f"| {_pct(r.get('avg_attr_acc', 0.0))} "
                f"| {tok_val} "
                f"| {r.get('elapsed_sec', '—')} |"
            )

    lines += [
        "",
        "---",
        "",
        "## Aggregate Metrics by Category",
        "",
        "| Category | # Variants | EM Rate | Avg Cell Acc | Avg Attr Acc |",
        "|----------|-----------|---------|--------------|--------------|",
    ]

    for cat in _CATEGORY_ORDER:
        cat_results = by_cat.get(cat, [])
        if not cat_results:
            continue
        n = len(cat_results)
        em_rate     = sum(r.get("exact_match",    0) for r in cat_results) / n
        cell_avg    = sum(r.get("cell_accuracy",  0) for r in cat_results) / n
        attr_avg    = sum(r.get("avg_attr_acc",   0) for r in cat_results) / n
        lines.append(
            f"| {cat} | {n} "
            f"| {_pct(em_rate)} "
            f"| {_pct(cell_avg)} "
            f"| {_pct(attr_avg)} |"
        )

    temp_note = f"{temperature} (greedy decoding)" if temperature == 0.0 else f"{temperature}" if temperature is not None else "—"
    lines += [
        "",
        "---",
        "",
        "## Notes",
        "- **EM** = Exact Match: 1 iff all N house cells are completely correct.",
        "- **Cell Acc** = fraction of houses where all attributes are correct.",
        "- **Avg Attr Acc** = overall accuracy of individual attribute resolutions.",
        f"- Temperature = {temp_note} to isolate deterministic reasoning failures.",
        "",
    ]

    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[report] Markdown written → {md_path}")

    # ------------------------------------------------------------------ stdout summary
    print("\n" + "=" * 60)
    print(f"RESULTS SUMMARY — {model}")
    print("=" * 60)
    print(f"{'Variant':<6} {'Category':<14} {'Parse':<6} {'EM':<4} {'Cell Acc':>8} {'Avg Attr':>8}")
    print("-" * 60)
    for r in results:
        print(
            f"{r['variant_id']:<6} {r['category']:<14} "
            f"{'Y' if r.get('parse_success') else 'N':<6} "
            f"{'1' if r.get('exact_match') else '0':<4} "
            f"{_pct(r.get('cell_accuracy', 0)):>8} "
            f"{_pct(r.get('avg_attr_acc', 0)):>8}"
        )
    print("=" * 60)
