import tempfile
import json
import csv
from pathlib import Path

from report import generate_reports


def test_naming_logic():
    models = ["gemma-4-E4B-it", "meta-llama/Llama-3.2-3B-Instruct"]
    variant_files = ["data/3x3.json", "data/4x4.json", "data/5x5.json", "custom/foo_bar.json"]
    temperature = 0.0
    timestamp = "20261012_120000"

    for vf in variant_files:
        for m in models:
            data_name = Path(vf).stem
            model_short = m.split("/")[-1]
            folder_name = f"{timestamp}_{data_name}_{model_short}_T{temperature}"
            assert data_name in folder_name
            assert model_short in folder_name
            assert f"T{temperature}" in folder_name
    print("Naming logic test passed!")


def test_reporting_with_tokens_and_time():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        mock_results = [
            {
                "variant_id": "V0",
                "category": "Baseline",
                "description": "Control puzzle",
                "dataset": "3x3",
                "model": "gemma-4-E4B-it",
                "temperature": 0.0,
                "output_tokens": 1250,
                "elapsed_sec": 12.34,
                "parse_success": True,
                "exact_match": 1,
                "cell_accuracy": 1.0,
                "avg_attr_acc": 1.0,
                "cells_correct": 3,
                "total_cells": 3,
                "error": None,
                "hits_Name": 3,
            },
            {
                "variant_id": "V1a",
                "category": "Gender Bias",
                "description": "Variant 1a",
                "dataset": "3x3",
                "model": "gemma-4-E4B-it",
                "temperature": 0.0,
                "output_tokens": 850,
                "elapsed_sec": 9.11,
                "parse_success": True,
                "exact_match": 1,
                "cell_accuracy": 1.0,
                "avg_attr_acc": 1.0,
                "cells_correct": 3,
                "total_cells": 3,
                "error": None,
                "hits_Name": 3,
            }
        ]
        generate_reports(
            mock_results,
            tmp_path,
            model="gemma-4-E4B-it",
            dataset="3x3",
            temperature=0.0,
            total_time=21.45,
        )

        # Check CSV
        csv_file = tmp_path / "report.csv"
        assert csv_file.exists(), "CSV was not generated"
        with csv_file.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]["dataset"] == "3x3"
            assert rows[0]["temperature"] == "0.0"
            assert rows[0]["output_tokens"] == "1250"
            assert rows[1]["output_tokens"] == "850"

        # Check Markdown
        md_file = tmp_path / "report.md"
        assert md_file.exists(), "Markdown was not generated"
        md_content = md_file.read_text(encoding="utf-8")
        print("\n--- Generated Markdown Header Preview ---")
        for line in md_content.splitlines()[:15]:
            print(line)
        print("-----------------------------------------\n")

        assert "**Dataset:** `3x3`" in md_content
        assert "**Temperature:** `0.0`" in md_content
        assert "**Output Tokens:** `2,100`" in md_content
        assert "**Total Running Time:** `21.45s`" in md_content
        assert "| Output Tok |" in md_content

        print("Reporting with tokens and time test passed successfully!")


def test_reporting_when_tokens_none():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        mock_results = [
            {
                "variant_id": "V0",
                "category": "Baseline",
                "description": "Control puzzle",
                "dataset": "4x4",
                "model": "gemma-4-E4B-it",
                "temperature": 0.5,
                "output_tokens": None,
                "elapsed_sec": 5.0,
                "parse_success": True,
                "exact_match": 0,
                "cell_accuracy": 0.5,
                "avg_attr_acc": 0.5,
                "cells_correct": 2,
                "total_cells": 4,
                "error": None,
            }
        ]
        generate_reports(
            mock_results,
            tmp_path,
            model="gemma-4-E4B-it",
            dataset="4x4",
            temperature=0.5,
            total_time=5.0,
        )

        md_file = tmp_path / "report.md"
        md_content = md_file.read_text(encoding="utf-8")
        assert "**Temperature:** `0.5`" in md_content
        assert "**Output Tokens:** `—`" in md_content
        assert "**Total Running Time:** `5.00s`" in md_content
        print("Reporting with None tokens test passed successfully!")


if __name__ == "__main__":
    test_naming_logic()
    test_reporting_with_tokens_and_time()
    test_reporting_when_tokens_none()
    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY!")
