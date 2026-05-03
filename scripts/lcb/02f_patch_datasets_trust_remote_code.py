#!/usr/bin/env python3
"""Patch LiveCodeBench for Hugging Face datasets 3.x behavior.

LiveCodeBench's code_generation_lite dataset still uses a dataset loading
script. Datasets 4.x removed support for dataset scripts, so setup pins
datasets==3.6.0. With datasets 3.x, the load call needs trust_remote_code=True.

Usage:
  python scripts/02f_patch_datasets_trust_remote_code.py /path/to/LiveCodeBench
"""
from __future__ import annotations

import argparse
from pathlib import Path


OLD = 'load_dataset("livecodebench/code_generation_lite", split="test", version_tag=release_version)'
NEW = 'load_dataset("livecodebench/code_generation_lite", split="test", version_tag=release_version, trust_remote_code=True)'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_root", type=Path, help="Path to the LiveCodeBench repository root")
    args = parser.parse_args()

    target = args.repo_root / "lcb_runner" / "benchmarks" / "code_generation.py"
    if not target.exists():
        raise SystemExit(f"Could not find {target}")

    text = target.read_text()
    if NEW in text:
        print("code_generation.py already enables trust_remote_code for code_generation_lite; no change needed.")
        return

    if OLD not in text:
        raise SystemExit("Could not find code_generation_lite load_dataset call without trust_remote_code in code_generation.py; patch manually.")

    backup = target.with_suffix(".py.bak")
    backup.write_text(text)
    target.write_text(text.replace(OLD, NEW, 1))
    print(f"Patched {target} to enable trust_remote_code for datasets 3.x.")
    print(f"Backup saved to {backup}")


if __name__ == "__main__":
    main()
