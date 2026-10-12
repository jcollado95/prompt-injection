"""
evaluator.py — Parses LLM output and evaluates against ground-truth solutions.
Infers houses and attributes dynamically from ground_truth keys.
"""

import json
import re
from typing import Optional

from variants import Variant

# Extractors
_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def extract_json(text: str) -> Optional[dict]:
    """Attempts to extract JSON object via fences, direct parse, or finding the broadest valid block."""
    for match in _JSON_FENCE_RE.finditer(text):
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            continue

    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    candidates: list[dict] = []
    i = 0
    while i < len(text):
        if text[i] == "{":
            depth = 0
            for j in range(i, len(text)):
                if text[j] == "{":
                    depth += 1
                elif text[j] == "}":
                    depth -= 1
                    if depth == 0:
                        candidate_str = text[i : j + 1]
                        try:
                            parsed = json.loads(candidate_str)
                            candidates.append(parsed)
                        except json.JSONDecodeError:
                            pass
                        break
        i += 1

    for c in candidates:
        if isinstance(c, dict) and any("House" in k for k in c):
            return c
    return candidates[0] if candidates else None


def evaluate(variant: Variant, raw_response: str) -> dict:
    """
    Parses *raw_response* and computes accuracy metrics against varying dimensions.
    Returns general metric dictionaries.
    """
    parsed = extract_json(raw_response)
    parse_success = parsed is not None

    # Dynamically extract houses and attributes from ground truth
    houses = list(variant.ground_truth.keys())
    if len(houses) == 0:
        return {"error": "Empty ground truth"}
    
    attrs = list(variant.ground_truth[houses[0]].keys())
    n_houses = len(houses)

    def norm(s):
        return str(s).strip().lower() if s is not None else ""

    # Map each ground truth attribute to any prompt attribute whose value domain matches
    gt_to_prompt_attr: dict[str, str] = {}
    if hasattr(variant, "attributes") and isinstance(variant.attributes, dict):
        for gt_attr in attrs:
            gt_values = {norm(variant.ground_truth[h].get(gt_attr, "")) for h in houses} - {""}
            for prompt_attr, prompt_values in variant.attributes.items():
                prompt_set = {norm(v) for v in prompt_values}
                if gt_values and gt_values.issubset(prompt_set):
                    gt_to_prompt_attr[gt_attr] = prompt_attr
                    break

    # Build attribute domain sets for value-based fallback matching
    attr_domains: dict[str, set[str]] = {}
    for gt_attr in attrs:
        domain = {norm(variant.ground_truth[h].get(gt_attr, "")) for h in houses} - {""}
        mapped_key = gt_to_prompt_attr.get(gt_attr)
        if mapped_key and hasattr(variant, "attributes") and mapped_key in variant.attributes:
            domain.update(norm(v) for v in variant.attributes[mapped_key])
        attr_domains[gt_attr] = domain

    # We track hits per attribute
    attr_hits = {attr: 0 for attr in attrs}
    cell_correct = 0

    if parse_success:
        # Normalize house keys in parsed output: e.g. "house 1", "1", etc.
        parsed_norm: dict[str, dict] = {}
        if isinstance(parsed, dict):
            for k, v in parsed.items():
                norm_k = norm(k)
                parsed_norm[norm_k] = v
                k_str = str(k).strip()
                if k_str.isdigit():
                    parsed_norm[f"house {k_str}"] = v

        for house in houses:
            gt_cell = variant.ground_truth.get(house, {})
            pred_cell = parsed_norm.get(norm(house), {})
            if not isinstance(pred_cell, dict):
                pred_cell = {}

            pred_cell_norm = {norm(k): v for k, v in pred_cell.items()}

            house_fully_correct = True
            for attr in attrs:
                expected_val = norm(gt_cell.get(attr, ""))
                mapped_prompt_key = norm(gt_to_prompt_attr.get(attr, ""))

                # 1. Exact or case-insensitive match on ground truth attribute key
                pred_val = norm(pred_cell_norm.get(norm(attr), ""))

                # 2. Match on mapped prompt attribute key (e.g. Lunch vs Food)
                if not pred_val and mapped_prompt_key:
                    pred_val = norm(pred_cell_norm.get(mapped_prompt_key, ""))

                # 3. Domain value fallback: check if any value in pred_cell matches this attribute's domain
                if not pred_val:
                    domain = attr_domains.get(attr, set())
                    for pk, pv in pred_cell_norm.items():
                        if norm(pv) in domain:
                            pred_val = norm(pv)
                            break

                if pred_val == expected_val:
                    attr_hits[attr] += 1
                else:
                    house_fully_correct = False
            
            if house_fully_correct:
                cell_correct += 1

    exact_match = int(cell_correct == n_houses and parse_success)
    cell_accuracy = cell_correct / n_houses if parse_success else 0.0
    
    # Calculate average attribute accuracy across all dynamic attributes
    total_attr_hits = sum(attr_hits.values())
    total_possible_attrs = n_houses * len(attrs)
    avg_attr_acc = total_attr_hits / total_possible_attrs if parse_success and total_possible_attrs > 0 else 0.0

    ret = {
        "variant_id":        variant.id,
        "category":          variant.category,
        "description":       variant.description,
        "parse_success":     parse_success,
        "exact_match":       exact_match,
        "cell_accuracy":     round(cell_accuracy, 4),
        "avg_attr_acc":      round(avg_attr_acc, 4),
        "cells_correct":     cell_correct,
        "total_cells":       n_houses
    }
    
    # Also attach the individual attribute hits for verbose reporting
    for attr, hits in attr_hits.items():
        ret[f"hits_{attr}"] = hits
        
    return ret
