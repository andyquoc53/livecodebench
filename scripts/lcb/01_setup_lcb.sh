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

if ! command -v uv >/dev/null 2>&1; then
  python3 -m pip install --user -U uv || python3 -m pip install --user -U --break-system-packages uv
  USER_BIN="$(python3 - <<'PY'
import site
print(site.USER_BASE + "/bin")
PY
)"
  export PATH="$USER_BIN:$PATH"
fi

UV_BIN="${UV_BIN:-$(command -v uv)}"
"$UV_BIN" --version
VLLM_VERSION="${VLLM_VERSION:-0.10.0}"
VLLM_CUDA_VERSION="${VLLM_CUDA_VERSION:-126}"
VLLM_WHEEL_URL="${VLLM_WHEEL_URL:-https://github.com/vllm-project/vllm/releases/download/v${VLLM_VERSION}/vllm-${VLLM_VERSION}+cu${VLLM_CUDA_VERSION}-cp38-abi3-manylinux1_x86_64.whl}"
PYTORCH_CUDA_INDEX_URL="${PYTORCH_CUDA_INDEX_URL:-https://download.pytorch.org/whl/cu${VLLM_CUDA_VERSION}}"

# Official LiveCodeBench setup.
if [[ "${RESET_VENV:-0}" == "1" ]]; then
  "$UV_BIN" venv --python 3.11 --clear
elif [[ -d ".venv" ]]; then
  echo "Using existing .venv; rerun with RESET_VENV=1 to recreate it."
else
  "$UV_BIN" venv --python 3.11
fi
# shellcheck disable=SC1091
source .venv/bin/activate
"$UV_BIN" pip install -e .

# Extra dependencies commonly needed for open HF/vLLM model inference.
# LiveCodeBench's HF dataset still uses a dataset script, which datasets 4.x no longer supports.
"$UV_BIN" pip install -U "numpy<2.3" "transformers==4.57.3" accelerate "datasets==3.6.0" huggingface_hub hf_transfer safetensors sentencepiece protobuf
"$UV_BIN" pip install -U "$VLLM_WHEEL_URL" --extra-index-url "$PYTORCH_CUDA_INDEX_URL"
"$UV_BIN" pip install -U "numpy<2.3" "datasets==3.6.0" "transformers==4.57.3"

python - <<'PY'
from vllm import LLM, SamplingParams
import numpy
print("vLLM import OK")
print("NumPy:", numpy.__version__)
PY

# Reduce vLLM memory pressure from long-context model configs and keep self-repair on the same date window.
python "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/02b_patch_vllm_max_model_len.py" . || true
python "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/02c_patch_selfrepair_date_filter.py" . || true
python "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/02d_patch_claude_sonnet_4_6.py" . || true
python "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/02e_patch_debug_sample_limit.py" . || true
python "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/02f_patch_datasets_trust_remote_code.py" . || true
python "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/02g_patch_selfrepair_styles.py" . || true

python - <<'PY'
import torch, sys
print('Python:', sys.version)
print('Torch:', torch.__version__)
print('CUDA available:', torch.cuda.is_available())
print('GPU count:', torch.cuda.device_count())
for i in range(torch.cuda.device_count()):
    print(i, torch.cuda.get_device_name(i))
PY
