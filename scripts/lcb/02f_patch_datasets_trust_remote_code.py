#!/usr/bin/env python3
"""Patch LiveCodeBench for current Hugging Face datasets behavior.

Recent versions of datasets reject trust_remote_code for datasets that are not
loading-script based. The LiveCodeBench code_generation_lite dataset is a
standard dataset, so the argument should be omitted.

Usage:
  python scripts/02f_patch_datasets_trust_remote_code.py /path/to/LiveCodeBench
"""
from __future__ import annotations

import argparse
from pathlib import Path


OLD = 'load_dataset("livecodebench/code_generation_lite", split="test", version_tag=release_version, trust_remote_code=True)'
NEW = 'load_dataset("livecodebench/code_generation_lite", split="test", version_tag=release_version)'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_root", type=Path, help="Path to the LiveCodeBench repository root")
    args = parser.parse_args()

    target = args.repo_root / "lcb_runner" / "benchmarks" / "code_generation.py"
    if not target.exists():
        raise SystemExit(f"Could not find {target}")

    text = target.read_text()
    if NEW in text and OLD not in text:
        print("code_generation.py already omits trust_remote_code for code_generation_lite; no change needed.")
        return

    if OLD not in text:
        raise SystemExit("Could not find code_generation_lite load_dataset call in code_generation.py; patch manually.")

    backup = target.with_suffix(".py.bak")
    backup.write_text(text)
    target.write_text(text.replace(OLD, NEW, 1))
    print(f"Patched {target} to omit deprecated trust_remote_code.")
    print(f"Backup saved to {backup}")


if __name__ == "__main__":
    main()
