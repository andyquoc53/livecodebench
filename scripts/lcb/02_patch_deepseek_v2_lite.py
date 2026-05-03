#!/usr/bin/env python3
"""Patch LiveCodeBench lm_styles.py to add DeepSeek-Coder-V2-Lite-Instruct if missing.

LiveCodeBench main already includes Qwen/Qwen2.5-Coder-7B-Instruct.
Some versions do not include deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct as a local HF/vLLM model.
This patch inserts it using the existing DeepSeekCodeInstruct prompt/extraction style.

Usage:
  python scripts/02_patch_deepseek_v2_lite.py /path/to/LiveCodeBench
"""
from __future__ import annotations

import argparse
from pathlib import Path

ENTRY = '''
    # Added by course project run package: DeepSeek-Coder-V2-Lite-Instruct
    LanguageModel(
        "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct",
        "DeepSeek-Coder-V2-Lite-Instruct",
        LMStyle.DeepSeekCodeInstruct,
        datetime(2024, 6, 17),
        link="https://huggingface.co/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct",
    ),
'''


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("repo_root", type=Path, help="Path to the LiveCodeBench repository root")
    args = p.parse_args()

    target = args.repo_root / "lcb_runner" / "lm_styles.py"
    if not target.exists():
        raise SystemExit(f"Could not find {target}")

    text = target.read_text()
    if "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct" in text:
        print("DeepSeek-Coder-V2-Lite-Instruct already present in lm_styles.py; no patch needed.")
        return

    # Prefer to insert before the Deepseek API block, after the older Deepseek-Coder-Instruct entries.
    marker = "    ## Deepseek-Chat Latest API"
    if marker not in text:
        # Fallback: insert before Qwen section if marker changed.
        marker = "    ## Qwen 2"
    if marker not in text:
        raise SystemExit("Could not find an insertion marker in lm_styles.py; patch manually.")

    text = text.replace(marker, ENTRY + "\n" + marker, 1)
    backup = target.with_suffix(".py.bak")
    backup.write_text(target.read_text())
    target.write_text(text)
    print(f"Patched {target}")
    print(f"Backup saved to {backup}")


if __name__ == "__main__":
    main()
