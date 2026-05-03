#!/usr/bin/env python3
"""Patch LiveCodeBench lm_styles.py to add Claude Sonnet 4.6 if missing.

LiveCodeBench may lag newer Anthropic model aliases. This inserts the
cost-controlled, non-thinking Sonnet 4.6 API model so the regular Claude3 runner
uses --max_tokens/--temperature instead of the expensive thinking defaults.

Usage:
  python scripts/02d_patch_claude_sonnet_4_6.py /path/to/LiveCodeBench
"""
from __future__ import annotations

import argparse
from pathlib import Path

ENTRY = '''
    # Added by course project run package: Claude Sonnet 4.6 safe 100-problem API run
    LanguageModel(
        "claude-sonnet-4-6",
        "Claude-Sonnet-4.6",
        LMStyle.Claude3,
        datetime(2026, 2, 17),
        link="https://www.anthropic.com/claude/sonnet",
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
    if '"claude-sonnet-4-6"' in text:
        print("Claude Sonnet 4.6 already present in lm_styles.py; no patch needed.")
        return

    marker = "    ## Claude 3 and Claude 3.5"
    if marker not in text:
        marker = "    ## Gemini"
    if marker not in text:
        raise SystemExit("Could not find a Claude/Gemini insertion marker in lm_styles.py; patch manually.")

    backup = target.with_suffix(".py.bak")
    backup.write_text(text)

    if marker == "    ## Claude 3 and Claude 3.5":
        insert_after = '        link="https://www.anthropic.com/claude/sonnet",\n    ),'
        pos = text.find(insert_after, text.find(marker))
        if pos != -1:
            pos += len(insert_after)
            text = text[:pos] + "\n" + ENTRY + text[pos:]
        else:
            text = text.replace(marker, marker + "\n" + ENTRY, 1)
    else:
        text = text.replace(marker, ENTRY + "\n" + marker, 1)

    target.write_text(text)
    print(f"Patched {target} with Claude Sonnet 4.6.")
    print(f"Backup saved to {backup}")


if __name__ == "__main__":
    main()
