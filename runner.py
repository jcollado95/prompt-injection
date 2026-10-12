"""
runner.py — Queries the nodo08 vLLM server for a given variant.

Uses the OpenAI-compatible API via streaming (recommended by nodo08 skill)
so tokens appear as they arrive even when the server is under load.
"""

import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

from variants import Variant
from prompts import build_messages

# ---------------------------------------------------------------------------
# Client setup
# ---------------------------------------------------------------------------

load_dotenv()

_API_KEY = os.getenv("VLLM_API_KEY")
_BASE_URL = "http://ada01.ujaen.es:8080/v1"

client = OpenAI(
    api_key=_API_KEY,
    base_url=_BASE_URL,
    timeout=600.0,  # 10 min — allow for degraded server
)

# ---------------------------------------------------------------------------
# Core query function (streaming)
# ---------------------------------------------------------------------------

def query_variant(
    variant: Variant,
    model: str,
    max_tokens: int = 1024,
    temperature: float = 0.0,
    verbose: bool = True,
) -> dict:
    """
    Sends the prompt for *variant* to *model* and returns a result dict:

    {
        "variant_id":   str,
        "model":        str,
        "raw_response": str,       # full text emitted by the model
        "elapsed_sec":  float,
        "error":        str | None
    }
    """
    messages = build_messages(variant)

    if verbose:
        print(f"\n{'='*60}")
        print(f"[{variant.id}] {variant.category} — {variant.description}")
        print(f"Model: {model}")
        print(f"{'='*60}")

    raw_response = ""
    output_tokens = None
    error = None
    start = time.time()

    try:
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
            stream_options={"include_usage": True},
        )
        for chunk in stream:
            if hasattr(chunk, "usage") and chunk.usage:
                output_tokens = chunk.usage.completion_tokens
            if chunk.choices:
                delta = chunk.choices[0].delta.content or ""
                if verbose:
                    print(delta, end="", flush=True)
                raw_response += delta

        if verbose:
            print()  # newline after streaming ends

    except Exception as exc:
        error = str(exc)
        print(f"\n[ERROR] {variant.id}: {exc}", file=sys.stderr)

    elapsed = time.time() - start

    return {
        "variant_id":    variant.id,
        "model":         model,
        "raw_response":  raw_response,
        "output_tokens": output_tokens,
        "elapsed_sec":   round(elapsed, 2),
        "error":         error,
    }


# ---------------------------------------------------------------------------
# Save raw response to disk
# ---------------------------------------------------------------------------

def save_raw_response(result: dict, output_dir: Path) -> Path:
    """
    Saves the raw LLM response (plus metadata header) to
    <output_dir>/raw/<variant_id>.txt
    Returns the path of the written file.
    """
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    out_path = raw_dir / f"{result['variant_id']}.txt"

    header = (
        f"variant_id    : {result['variant_id']}\n"
        f"model         : {result['model']}\n"
        f"output_tokens : {result.get('output_tokens')}\n"
        f"elapsed_sec   : {result['elapsed_sec']}\n"
        f"error         : {result['error']}\n"
        f"{'='*60}\n\n"
    )

    out_path.write_text(header + result["raw_response"], encoding="utf-8")
    return out_path
