"""
reeval.py — Re-evaluates all saved raw responses using the current evaluator.

Useful when the evaluator logic is updated after the experiment has run.
Reads from results/raw/<variant_id>.txt (written by runner.save_raw_response),
strips the 6-line metadata header, and re-runs evaluation.

Usage:
    python reeval.py [--output-dir results] [--model MODEL]
"""

import argparse
import json
import re
from pathlib import Path

from variants import load_variants
from evaluator import evaluate
from report import generate_reports


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Re-evaluate saved raw LLM responses with the current evaluator."
    )
    parser.add_argument("--output-dir", default="results")
    parser.add_argument("--model", default="gemma-4-E4B-it")
    parser.add_argument("--variants-file", default="data/3x3.json")
    parser.add_argument("--temperature", type=float, default=None, help="Sampling temperature")
    return parser.parse_args()


def parse_header_meta(raw_file_text: str) -> dict:
    """Parses key-value metadata from the raw file header before the separator."""
    meta = {}
    for line in raw_file_text.split("\n"):
        if line.startswith("=" * 20):
            break
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta


def strip_header(raw_file_text: str) -> str:
    """
    The raw files written by runner.save_raw_response have a metadata header
    followed by a separator line of equals signs ('=' * 20+).
    Strip those header lines and return the remaining LLM response text.
    """
    lines = raw_file_text.split("\n")
    # Find the separator line and skip past it + the blank line
    for i, line in enumerate(lines):
        if line.startswith("=" * 20):
            return "\n".join(lines[i + 2:])  # skip separator + blank line
    # Fallback: skip first 6 lines
    return "\n".join(lines[6:])


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    raw_dir = output_dir / "raw"

    if not raw_dir.exists():
        print(f"[ERROR] Raw response directory not found: {raw_dir}")
        return

    data_name = Path(args.variants_file).stem
    all_variants = load_variants(args.variants_file)
    variant_map = {v.id: v for v in all_variants}
    results: list[dict] = []

    # Infer temperature if not provided
    temp = args.temperature
    if temp is None:
        match = re.search(r"_T([0-9.]+)", output_dir.name)
        if match:
            try:
                temp = float(match.group(1))
            except ValueError:
                temp = None

    # Load existing results.json for elapsed_sec / error metadata
    existing_meta: dict[str, dict] = {}
    json_path = output_dir / "results.json"
    if json_path.exists():
        for r in json.loads(json_path.read_text()):
            existing_meta[r["variant_id"]] = r

    for raw_file in sorted(raw_dir.glob("*.txt")):
        variant_id = raw_file.stem
        variant = variant_map.get(variant_id)
        if variant is None:
            print(f"[WARN] Unknown variant {variant_id}, skipping.")
            continue

        raw_text = raw_file.read_text(encoding="utf-8")
        header_meta = parse_header_meta(raw_text)
        response = strip_header(raw_text)

        eval_result = evaluate(variant, response)
        meta = existing_meta.get(variant_id, {})

        # Extract output_tokens if present in meta or header
        raw_toks = meta.get("output_tokens") or header_meta.get("output_tokens")
        try:
            output_tokens = int(raw_toks) if raw_toks is not None and str(raw_toks) != "None" else None
        except ValueError:
            output_tokens = None

        raw_elapsed = meta.get("elapsed_sec") or header_meta.get("elapsed_sec")
        try:
            elapsed_sec = float(raw_elapsed) if raw_elapsed is not None and str(raw_elapsed) != "None" else None
        except ValueError:
            elapsed_sec = None

        merged = {
            **eval_result,
            "dataset":       meta.get("dataset", data_name),
            "model":         meta.get("model", args.model),
            "temperature":   meta.get("temperature", temp),
            "output_tokens": output_tokens,
            "elapsed_sec":   elapsed_sec,
            "error":         meta.get("error", header_meta.get("error")),
        }
        results.append(merged)

        em  = "✅ EM" if merged["exact_match"]   else "❌"
        prs = "parsed" if merged["parse_success"] else "NO PARSE"
        toks = f"{merged['output_tokens']} tok" if merged['output_tokens'] is not None else "— tok"
        print(f"  [{variant_id}] {prs} | {em} | cell={merged['cell_accuracy']:.0%} | {toks}")

    if not results:
        print("[WARN] No results found.")
        return

    # Sort to canonical order
    id_order = [v.id for v in all_variants]
    results.sort(key=lambda r: id_order.index(r["variant_id"]) if r["variant_id"] in id_order else 99)

    # Re-save results.json
    json_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[reeval] Updated results.json → {json_path}")

    # Re-generate reports
    generate_reports(results, output_dir, model=args.model, dataset=data_name, temperature=temp)
    print("\nDone.")


if __name__ == "__main__":
    main()
