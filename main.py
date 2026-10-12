"""
main.py — End-to-end orchestration for the ZebraLogic Brittleness Battery.

Usage:
    python main.py [--model MODEL] [--base-dir DIR] [--variants-file FILE] [--variants V0 V1a ...]

Defaults:
    --model          gemma-4-E4B-it
    --base-dir       results/
    --variants-file  data/3x3.json
    --variants       All variants in the file
"""

import argparse
import json
import sys
import time
from pathlib import Path
from datetime import datetime

from variants import load_variants
from runner   import query_variant, save_raw_response
from evaluator import evaluate
from report   import generate_reports


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the ZebraLogic Surface & Sequential Brittleness Battery."
    )
    parser.add_argument(
        "--model",
        default="gemma-4-E4B-it",
        help="Model identifier on the nodo08 vLLM server (default: gemma-4-E4B-it)",
    )
    parser.add_argument(
        "--base-dir",
        default="results",
        help="Base directory to right reports (default: results/)",
    )
    parser.add_argument(
        "--variants-file",
        default="data/3x3.json",
        help="Path to the JSON definitions of the puzzle variants",
    )
    parser.add_argument(
        "--variants",
        nargs="+",
        default=None,
        help="Subset of variant IDs to run (e.g. V0 V1a). Default: all.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=8192,
        help="Max tokens for each LLM response (default: 8192)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature (default: 0.0 — greedy)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    
    # Create dynamic run directory: base-dir/YYYYMMDD_HHMMSS_data_model_T0.0
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    data_name = Path(args.variants_file).stem
    run_folder = f"{timestamp}_{data_name}_{args.model.split('/')[-1]}_T{args.temperature}"
    output_dir = Path(args.base_dir) / run_folder

    # ------------------------------------------------------------------ Select variants
    all_variants = load_variants(args.variants_file)
    variant_ids = set(args.variants) if args.variants else None
    variants = [v for v in all_variants if variant_ids is None or v.id in variant_ids]

    if not variants:
        print(f"[ERROR] No matching variants for {args.variants}", file=sys.stderr)
        sys.exit(1)

    print(f"\nZebraLogic Brittleness Battery")
    print(f"  Model      : {args.model}")
    print(f"  Dataset    : {args.variants_file} ({data_name})")
    print(f"  Variants   : {[v.id for v in variants]}")
    print(f"  Output dir : {output_dir}")
    print(f"  Temperature: {args.temperature}")
    print()

    # ------------------------------------------------------------------ Run
    all_results: list[dict] = []
    start_time = time.time()

    for variant in variants:
        # 1. Query LLM
        run_result = query_variant(
            variant=variant,
            model=args.model,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
            verbose=True,
        )

        # 2. Save raw response
        raw_path = save_raw_response(run_result, output_dir)
        print(f"[raw] Saved → {raw_path}")

        # 3. Evaluate
        eval_result = evaluate(variant, run_result["raw_response"])

        # 4. Merge into one record
        merged = {**eval_result, **{
            "dataset":       data_name,
            "model":         run_result["model"],
            "temperature":   args.temperature,
            "output_tokens": run_result.get("output_tokens"),
            "elapsed_sec":   run_result["elapsed_sec"],
            "error":         run_result["error"],
        }}

        all_results.append(merged)

        # Quick per-variant status line
        em   = "✅ EM" if merged["exact_match"]   else "❌"
        prs  = "parsed" if merged["parse_success"] else "NO PARSE"
        toks = f"{merged['output_tokens']} tok" if merged['output_tokens'] is not None else "— tok"
        print(f"  → [{variant.id}] {prs} | {em} | cell={merged['cell_accuracy']:.0%} | {toks}")

    total_runtime = round(time.time() - start_time, 2)

    # ------------------------------------------------------------------ Save JSON (all results)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "results.json"
    json_path.write_text(json.dumps(all_results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[main] Full results JSON → {json_path}")

    # ------------------------------------------------------------------ Reports
    generate_reports(
        all_results,
        output_dir,
        model=args.model,
        dataset=data_name,
        temperature=args.temperature,
        total_time=total_runtime,
    )

    print("\nDone.")


if __name__ == "__main__":
    main()
