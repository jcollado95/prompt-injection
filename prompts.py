"""
prompts.py — Zero-shot Chain-of-Thought prompt formatter for dynamic ZebraLogic variants.
"""

from variants import Variant

SYSTEM_PROMPT = (
    "You are a precise logic puzzle solver. "
    "Work through each clue carefully and reason step by step before giving your final answer. "
    "Your final answer MUST be a single, valid JSON object — no markdown fences, no extra text after it."
)

_USER_TEMPLATE = """{puzzle_text}

---

Think step by step. After your reasoning, output ONLY the following JSON object (fill in the blanks):

{json_schema}

Your final answer (JSON only after reasoning):"""


def _build_json_schema(variant: Variant) -> str:
    """Dynamically builds the expected JSON format based on N houses and arbitrary attributes."""
    n_houses = len(list(variant.attributes.values())[0])
    attr_keys = list(variant.attributes.keys())
    
    inner = ", ".join(f'"{k}": "..."' for k in attr_keys)
    
    lines = ["{"]
    for i in range(1, n_houses + 1):
        line = f'  "House {i}": {{{inner}}}'
        if i < n_houses:
            line += ","
        lines.append(line)
    lines.append("}")
    return "\n".join(lines)


def format_prompt(variant: Variant) -> tuple[str, str]:
    """Returns (system_prompt, user_prompt) for the variant."""
    schema = _build_json_schema(variant)
    user_prompt = _USER_TEMPLATE.format(puzzle_text=variant.puzzle_text, json_schema=schema)
    return SYSTEM_PROMPT, user_prompt


def build_messages(variant: Variant) -> list[dict]:
    """Returns OpenAI-style messages list for the variant."""
    system, user = format_prompt(variant)
    return [
        {"role": "system", "content": system},
        {"role": "user",   "content": user},
    ]
