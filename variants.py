"""
variants.py — Loads dynamic N×M constraint variants from JSON.
"""

import json
from dataclasses import dataclass
from typing import Dict, List, Any


@dataclass
class Variant:
    """Represents one ZebraLogic puzzle variant dynamically sized."""
    id: str
    category: str
    description: str
    attributes: Dict[str, List[str]]
    clues: List[str]
    ground_truth: Dict[str, Dict[str, str]]
    puzzle_text: str = ""


def build_puzzle(attributes: Dict[str, List[str]], clues: List[str]) -> str:
    """
    Builds the puzzle preamble and clue block dynamically based on the 
    number of houses (length of attribute lists) and variables.
    """
    if not attributes:
        raise ValueError("Attributes dictionary cannot be empty.")
    
    # Infer N (number of houses) from the first attribute list
    n_houses = len(list(attributes.values())[0])

    text = (f"There are {n_houses} houses, numbered 1 to {n_houses} from left to right, "
            "as seen from across the street. Each house is occupied by a different "
            "person. Each house has a unique attribute for each of the following "
            "characteristics:\n")
    
    for category, items in attributes.items():
        items_str = ", ".join(f"`{x}`" for x in items)
        text += f"- Each person has a unique {category.lower()}: {items_str}\n"

    text += "\n## Clues:\n"
    for i, c in enumerate(clues):
        text += f"{i+1}. {c}\n"

    return text.strip()


def load_variants(filepath: str) -> List[Variant]:
    """Loads a list of Variant objects from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    variants = []
    for v_dict in data:
        # Build the puzzle text derived from JSON fields
        puzzle_text = build_puzzle(v_dict["attributes"], v_dict["clues"])
        
        variant = Variant(
            id=v_dict["id"],
            category=v_dict["category"],
            description=v_dict["description"],
            attributes=v_dict["attributes"],
            clues=v_dict["clues"],
            ground_truth=v_dict["ground_truth"],
            puzzle_text=puzzle_text
        )
        variants.append(variant)

    return variants
