#!/usr/bin/env python3
"""Patch LiveCodeBench vllm_runner.py to cap vLLM context/memory use.

Why: Qwen2.5-Coder and DeepSeek-Coder-V2-Lite expose very long context windows.
If vLLM initializes with the full advertised context length, Colab/A100 memory can fail.
This patch adds `max_model_len=int(os.environ.get("LCB_MAX_MODEL_LEN", "8192"))`
and `gpu_memory_utilization=float(os.environ.get("VLLM_GPU_MEMORY_UTILIZATION", "0.90"))`
to the LLM(...) call. You can override them with environment variables.

Usage:
  python scripts/02b_patch_vllm_max_model_len.py /path/to/LiveCodeBench
"""
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("repo_root", type=Path)
    args = p.parse_args()

    target = args.repo_root / "lcb_runner" / "runner" / "vllm_runner.py"
    if not target.exists():
        raise SystemExit(f"Could not find {target}")

    text = target.read_text()
    needs_model_len = "LCB_MAX_MODEL_LEN" not in text
    needs_gpu_util = "VLLM_GPU_MEMORY_UTILIZATION" not in text
    if not needs_model_len and not needs_gpu_util:
        print("vllm_runner.py already has vLLM memory patches; no change needed.")
        return

    backup = target.with_suffix(".py.bak")
    backup.write_text(text)

    # Add os import near the top.
    if "import os" not in text:
        text = text.replace("try:\n", "import os\n\ntry:\n", 1)

    needle = "trust_remote_code=args.trust_remote_code,"
    if needle not in text:
        raise SystemExit("Could not find trust_remote_code argument in vllm_runner.py; patch manually.")

    insertions = []
    if needs_model_len:
        insertions.append("            max_model_len=int(os.environ.get(\"LCB_MAX_MODEL_LEN\", \"8192\")),")
    if needs_gpu_util:
        insertions.append("            gpu_memory_utilization=float(os.environ.get(\"VLLM_GPU_MEMORY_UTILIZATION\", \"0.90\")),")

    replacement = needle + "\n" + "\n".join(insertions)
    text = text.replace(needle, replacement, 1)
    target.write_text(text)
    print(f"Patched {target} to cap vLLM context/memory via environment variables.")
    print(f"Backup saved to {backup}")


if __name__ == "__main__":
    main()
