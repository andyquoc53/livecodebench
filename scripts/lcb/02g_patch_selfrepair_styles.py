#!/usr/bin/env python3
"""Patch LiveCodeBench self-repair prompt style compatibility.

The current LMStyle enum removed several legacy members that older prompt
formatters still reference. It also lacks a self-repair branch for
CodeQwenInstruct. This patch keeps those references from crashing and routes
Qwen self-repair through the generic instruction prompt.

Usage:
  python scripts/02g_patch_selfrepair_styles.py /path/to/LiveCodeBench
"""
from __future__ import annotations

import argparse
from pathlib import Path


ENUM_ANCHOR = "    TogetherAI = \"TogetherAI\"\n"
ENUM_PATCH = """    MagiCoder = "MagiCoder"
    WizardCoder = "WizardCoder"
    Phind = "Phind"
    DracarysQwen = "DracarysQwen"
    DracarysLlama = "DracarysLlama"
    Eurusx = "Eurusx"
    CodeLLaMa = "CodeLLaMa"

"""

SELF_REPAIR_ANCHOR = """    elif LanguageModelStyle == LMStyle.StarCoderInstruct:
        prompt = f"{PromptConstants.SYSTEM_MESSAGE_GENERIC}\\n{get_generic_question_template_answer(question, code, result,metadata)}"
        return prompt

"""
SELF_REPAIR_PATCH = """    elif LanguageModelStyle == LMStyle.CodeQwenInstruct:
        prompt = f"{PromptConstants.SYSTEM_MESSAGE_GENERIC}\\n{get_generic_question_template_answer(question, code, result,metadata)}"
        return prompt

"""


def patch_file(path: Path, old: str, new: str, marker: str) -> bool:
    text = path.read_text()
    if marker in text:
        print(f"{path.name} already has self-repair style compatibility; no change needed.")
        return False
    if old not in text:
        raise SystemExit(f"Could not find expected block in {path}; patch manually.")
    backup = path.with_suffix(".py.bak")
    backup.write_text(text)
    path.write_text(text.replace(old, old + new, 1))
    print(f"Patched {path}")
    print(f"Backup saved to {backup}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_root", type=Path, help="Path to the LiveCodeBench repository root")
    args = parser.parse_args()

    lm_styles = args.repo_root / "lcb_runner" / "lm_styles.py"
    self_repair = args.repo_root / "lcb_runner" / "prompts" / "self_repair.py"

    if not lm_styles.exists():
        raise SystemExit(f"Could not find {lm_styles}")
    if not self_repair.exists():
        raise SystemExit(f"Could not find {self_repair}")

    patch_file(lm_styles, ENUM_ANCHOR, ENUM_PATCH, '    MagiCoder = "MagiCoder"')
    patch_file(self_repair, SELF_REPAIR_ANCHOR, SELF_REPAIR_PATCH, "LMStyle.CodeQwenInstruct")


if __name__ == "__main__":
    main()
