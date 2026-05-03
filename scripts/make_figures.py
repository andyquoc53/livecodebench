#!/usr/bin/env python3
"""Recreate the figures for the LiveCodeBench progress survey report."""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def save(fig, out_dir: Path, stem: str) -> None:
    fig.tight_layout(pad=0.3)
    fig.savefig(out_dir / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(out_dir / f"{stem}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=Path, default=Path("data"))
    parser.add_argument("--out_dir", type=Path, default=Path("figures"))
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    releases = pd.read_csv(args.data_dir / "lcb_releases.csv")
    fig, ax = plt.subplots(figsize=(3.35, 2.25))
    ax.plot(releases["release"], releases["problems"], marker="o")
    for i, row in releases.iterrows():
        ax.text(i, row["problems"] + 25, str(row["problems"]), ha="center", fontsize=7)
    ax.set_ylim(300, 1125)
    ax.set_xlabel("LiveCodeBench release")
    ax.set_ylabel("Problems")
    ax.set_title("Benchmark growth across releases")
    ax.grid(axis="y", linewidth=0.3)
    save(fig, args.out_dir, "release_growth")

    open_models = pd.read_csv(args.data_dir / "open_model_scores_qwen_report.csv")
    fig, ax = plt.subplots(figsize=(3.35, 2.35))
    ax.bar(open_models["model"], open_models["lcb_pass1"])
    for i, row in open_models.iterrows():
        ax.text(i, row["lcb_pass1"] + 0.9, f"{row['lcb_pass1']:.1f}", ha="center", fontsize=7)
    ax.set_ylabel("LiveCodeBench pass@1 (%)")
    ax.set_title("Open coding models in Qwen report")
    ax.set_xticks(range(len(open_models)))
    ax.set_xticklabels(open_models["model"], rotation=28, ha="right", fontsize=7)
    ax.grid(axis="y", linewidth=0.3)
    save(fig, args.out_dir, "open_model_lcb")

    diff = pd.read_csv(args.data_dir / "difficulty_split_lcb_paper.csv")
    fig, ax = plt.subplots(figsize=(3.35, 2.55))
    x = list(range(len(diff)))
    width = 0.25
    for idx, col in enumerate(["Easy", "Medium", "Hard"]):
        ax.bar([i + (idx - 1) * width for i in x], diff[col], width=width, label=col)
    ax.set_xticks(x)
    ax.set_xticklabels(diff["model"], rotation=28, ha="right", fontsize=7)
    ax.set_ylabel("pass@1 (%)")
    ax.set_title("Difficulty stratification")
    ax.legend(fontsize=7, frameon=False, ncol=3, loc="upper right")
    ax.grid(axis="y", linewidth=0.3)
    save(fig, args.out_dir, "difficulty_split")

    repair = pd.read_csv(args.data_dir / "self_repair_lcb_paper.csv")
    if "gain" not in repair.columns:
        repair["gain"] = repair["self_repair"] - repair["codegen"]
    fig, ax = plt.subplots(figsize=(3.35, 2.35))
    ax.bar(repair["model"], repair["gain"])
    for i, row in repair.iterrows():
        ax.text(i, row["gain"] + 0.15, f"{row['gain']:.1f}", ha="center", fontsize=7)
    ax.set_ylabel("pass@1 gain (%)")
    ax.set_title("Self-repair adds limited margin")
    ax.set_xticks(range(len(repair)))
    ax.set_xticklabels(repair["model"], rotation=28, ha="right", fontsize=7)
    ax.grid(axis="y", linewidth=0.3)
    save(fig, args.out_dir, "repair_gain")


if __name__ == "__main__":
    main()
