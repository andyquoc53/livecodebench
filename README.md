# LCB Progress Survey Code Package

This repository accompanies the report:

**Survey: Measuring Algorithmic Progress in Modern LLMs on Competitive Programming via LiveCodeBench**

It is intentionally separate from the original LiveCodeBench repository. It contains:

- `data/`: CSV files used for the secondary analysis in the report.
- `scripts/make_figures.py`: recreates the report figures from the CSV files.
- `scripts/run_lcb_experiments.sh`: a Vast.ai/A100-ready wrapper for running LiveCodeBench code generation and self-repair.
- `scripts/lcb/`: patched helper scripts for Qwen2.5-Coder-7B-Instruct, DeepSeek-Coder-V2-Lite-Instruct, and a safe Claude Sonnet 4.6 API sample.
- `notebooks/LiveCodeBench_Qwen_DeepSeek_Run.ipynb`: the notebook workflow for Vast.ai, Colab, or plain Jupyter.
- `requirements.txt`: Python packages for the lightweight analysis scripts.

## What was actually executed

The final report uses a legitimate secondary analysis of published measurements from LiveCodeBench and model technical reports. The included plotting script was executed locally to generate the figures in the PDF.

A full controlled benchmark run over Claude Sonnet 4.6, Qwen2.5-Coder-7B-Instruct, and DeepSeek-Coder-V2-Lite-Instruct was **not** executed in this local environment because it requires GPU resources and/or API credentials. The included `scripts/lcb/` and notebook are the prepared execution path for the two open models on a rented A100, plus a small API-only Sonnet sample.

Qwen and DeepSeek are run as regular instruct/code models through vLLM. They are not QwQ/DeepSeek-R1-style reasoning models, and the scripts do not enable any extended-thinking mode.

## Recreate the report figures

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/make_figures.py --data_dir data --out_dir figures
```

The script creates the following figures:

- `release_growth.pdf`
- `open_model_lcb.pdf`
- `difficulty_split.pdf`
- `repair_gain.pdf`

## Prospective LiveCodeBench execution

Clone and install the official LiveCodeBench runner:

```bash
git clone https://github.com/LiveCodeBench/LiveCodeBench.git
cd LiveCodeBench
uv venv --python 3.11
source .venv/bin/activate
uv pip install -e .
```

Then run the wrapper from inside the cloned LiveCodeBench repository:

```bash
bash /path/to/this_repo/scripts/run_lcb_experiments.sh
```

Recommended controlled window for the proposal:

- `--release_version release_v5`
- `--start_date 2024-08-01`
- `--end_date 2025-01-31`

For a 2026 final run, `release_v6` can also be used if every model is evaluated on the same date window.

For a quick smoke test before spending full GPU time:

```bash
SMOKE=1 bash /path/to/this_repo/scripts/run_lcb_experiments.sh
```

## Safe Claude Sonnet 4.6 sample

The Sonnet path is intentionally separate from the full open-model runner so it cannot accidentally evaluate the full set. It uses the non-thinking Claude style in LiveCodeBench and defaults to three problems.

```bash
export ANTHROPIC_KEY="sk-ant-..."
# or export ANTHROPIC_API_KEY="sk-ant-..."

cd /path/to/LiveCodeBench
bash /path/to/this_repo/scripts/lcb/01_setup_lcb.sh
API_SAMPLE_SIZE=3 SONNET_MAX_TOKENS=2048 bash /path/to/this_repo/scripts/lcb/10_run_codegen_sonnet_sample.sh
```

Optional self-repair sample, after the code-generation sample:

```bash
API_SAMPLE_SIZE=3 SONNET_MAX_TOKENS=2048 bash /path/to/this_repo/scripts/lcb/11_run_selfrepair_sonnet_sample.sh
```

The wrapper applies three compatibility patches to the official LiveCodeBench checkout:

- adds `deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct` and `claude-sonnet-4-6` to `lm_styles.py` when missing;
- caps vLLM context and GPU memory usage through `LCB_MAX_MODEL_LEN` and `VLLM_GPU_MEMORY_UTILIZATION`;
- makes self-repair respect the same `--start_date` and `--end_date` filter as code generation.
- makes LiveCodeBench `--debug` respect `LCB_DEBUG_LIMIT` for safe API sampling.

## GitHub submission step

Before submitting the final report, push this folder to a GitHub repository and update the placeholder URL in the report's Code section:

```bash
git init
git add .
git commit -m "Add LiveCodeBench progress survey code"
git branch -M main
git remote add origin https://github.com/<your-username>/lcb-progress-survey.git
git push -u origin main
```
