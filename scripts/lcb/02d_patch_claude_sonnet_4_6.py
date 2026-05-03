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


def patch_lm_styles(repo_root: Path) -> None:
    target = repo_root / "lcb_runner" / "lm_styles.py"
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


def patch_claude3_runner(repo_root: Path) -> None:
    target = repo_root / "lcb_runner" / "runner" / "claude3_runner.py"
    if not target.exists():
        raise SystemExit(f"Could not find {target}")

    text = target.read_text()
    marker = 'if args.model == "claude-sonnet-4-6":'
    if marker in text:
        print("claude3_runner.py already omits top_p for Claude Sonnet 4.6; no change needed.")
        return

    old = '''            self.client_kwargs: dict[str | str] = {
                "model": args.model,
                "temperature": args.temperature,
                "max_tokens": args.max_tokens,
                "top_p": args.top_p,
            }
'''
    new = '''            self.client_kwargs: dict[str | str] = {
                "model": args.model,
                "temperature": args.temperature,
                "max_tokens": args.max_tokens,
                "top_p": args.top_p,
            }
            if args.model == "claude-sonnet-4-6":
                self.client_kwargs.pop("top_p", None)
'''
    if old not in text:
        raise SystemExit("Could not find Claude3 non-thinking kwargs block; patch manually.")

    backup = target.with_suffix(".py.bak")
    backup.write_text(text)
    target.write_text(text.replace(old, new, 1))
    print(f"Patched {target} to omit top_p for Claude Sonnet 4.6.")
    print(f"Backup saved to {backup}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("repo_root", type=Path, help="Path to the LiveCodeBench repository root")
    args = p.parse_args()

    patch_lm_styles(args.repo_root)
    patch_claude3_runner(args.repo_root)


if __name__ == "__main__":
    main()
