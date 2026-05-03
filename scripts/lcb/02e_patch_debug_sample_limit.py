#!/usr/bin/env python3
"""Patch LiveCodeBench debug mode to honor LCB_DEBUG_LIMIT.

The upstream runner hardcodes --debug to 15 problems. For paid API models, even
15 can be more than we want for a first sanity check. This patch changes debug
mode to use int(os.environ.get("LCB_DEBUG_LIMIT", "15")).

Usage:
  python scripts/02e_patch_debug_sample_limit.py /path/to/LiveCodeBench
"""
from __future__ import annotations

import argparse
from pathlib import Path

OLD = """    if args.debug:
        print(f"Running with {len(benchmark)} instances in debug mode")
        benchmark = benchmark[:15]
"""

NEW = """    if args.debug:
        debug_limit = int(os.environ.get("LCB_DEBUG_LIMIT", "15"))
        print(f"Running with {len(benchmark)} instances in debug mode; limiting to {debug_limit}")
        benchmark = benchmark[:debug_limit]
"""


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("repo_root", type=Path, help="Path to the LiveCodeBench repository root")
    args = p.parse_args()

    target = args.repo_root / "lcb_runner" / "runner" / "main.py"
    if not target.exists():
        raise SystemExit(f"Could not find {target}")

    text = target.read_text()
    if "LCB_DEBUG_LIMIT" in text:
        print("main.py already honors LCB_DEBUG_LIMIT; no change needed.")
        return
    if OLD not in text:
        raise SystemExit("Could not find the debug benchmark slice in main.py; patch manually.")

    backup = target.with_suffix(".py.bak")
    backup.write_text(text)
    target.write_text(text.replace(OLD, NEW, 1))
    print(f"Patched {target} so --debug honors LCB_DEBUG_LIMIT.")
    print(f"Backup saved to {backup}")


if __name__ == "__main__":
    main()
