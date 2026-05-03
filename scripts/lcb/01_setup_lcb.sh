#!/usr/bin/env bash
set -euo pipefail

# Run this from inside the LiveCodeBench repository root.
# Example:
#   git clone https://github.com/LiveCodeBench/LiveCodeBench.git
#   cd LiveCodeBench
#   bash /path/to/scripts/01_setup_lcb.sh

if [[ ! -f "pyproject.toml" || ! -d "lcb_runner" ]]; then
  echo "ERROR: Run this from the root of the official LiveCodeBench repository." >&2
  exit 1
fi

python3 -m pip install -U pip
python3 -m pip install -U uv
uv --version

# Official LiveCodeBench setup.
uv venv --python 3.11
# shellcheck disable=SC1091
source .venv/bin/activate
uv pip install -e .

# Extra dependencies commonly needed for open HF/vLLM model inference.
# The exact versions are intentionally not pinned so Colab/CUDA can resolve compatible wheels.
uv pip install -U "transformers>=4.37.0" accelerate datasets huggingface_hub hf_transfer safetensors sentencepiece protobuf
uv pip install -U vllm || echo "vLLM install failed; check CUDA/PyTorch compatibility for your runtime."

# Reduce vLLM memory pressure from long-context model configs and keep self-repair on the same date window.
python "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/02b_patch_vllm_max_model_len.py" . || true
python "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/02c_patch_selfrepair_date_filter.py" . || true
python "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/02d_patch_claude_sonnet_4_6.py" . || true
python "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/02e_patch_debug_sample_limit.py" . || true

python - <<'PY'
import torch, sys
print('Python:', sys.version)
print('Torch:', torch.__version__)
print('CUDA available:', torch.cuda.is_available())
print('GPU count:', torch.cuda.device_count())
for i in range(torch.cuda.device_count()):
    print(i, torch.cuda.get_device_name(i))
PY
