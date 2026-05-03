#!/usr/bin/env python3
"""Patch LiveCodeBench self-repair to honor start/end date filters.

Current LiveCodeBench applies --start_date/--end_date to code generation, but
the self-repair scenario loads the full release. If code generation was run on a
filtered window, self-repair then fails because its benchmark list no longer
matches codegeneration_*_eval_all.json. This patch makes self-repair use the
same date window as code generation.

Usage:
  python scripts/02c_patch_selfrepair_date_filter.py /path/to/LiveCodeBench
"""
from __future__ import annotations

import argparse
from pathlib import Path


OLD = """    elif scenario == Scenario.selfrepair:
        benchmark = load_code_generation_dataset(args.release_version)
        benchmark = sorted(benchmark, key=lambda x: x.question_id)
        format_prompt = format_prompt_self_repair
"""

NEW = """    elif scenario == Scenario.selfrepair:
        benchmark = load_code_generation_dataset(
            args.release_version,
            start_date=args.start_date,
            end_date=args.end_date,
        )
        benchmark = sorted(benchmark, key=lambda x: x.question_id)
        format_prompt = format_prompt_self_repair
"""


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("repo_root", type=Path, help="Path to the LiveCodeBench repository root")
    args = p.parse_args()

    target = args.repo_root / "lcb_runner" / "runner" / "scenario_router.py"
    if not target.exists():
        raise SystemExit(f"Could not find {target}")

    text = target.read_text()
    if NEW in text:
        print("scenario_router.py already filters self-repair by date; no change needed.")
        return

    if OLD not in text:
        raise SystemExit("Could not find the self-repair dataset block in scenario_router.py; patch manually.")

    backup = target.with_suffix(".py.bak")
    backup.write_text(text)
    target.write_text(text.replace(OLD, NEW, 1))
    print(f"Patched {target} so self-repair uses --start_date/--end_date.")
    print(f"Backup saved to {backup}")


if __name__ == "__main__":
    main()
