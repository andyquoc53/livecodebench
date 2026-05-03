from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "livecodebench"
FIGURES = Path(__file__).resolve().parent / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

MODEL_LABELS = {
    "Claude-Sonnet-4.6": "Claude\nSonnet 4.6",
    "Qwen2.5-Coder-Ins-7B": "Qwen2.5\nCoder 7B",
    "DeepSeek-Coder-V2-Lite-Instruct": "DeepSeek\nV2 Lite",
}


def savefig(name: str) -> None:
    for ext in ("pdf", "png"):
        plt.savefig(FIGURES / f"{name}.{ext}", bbox_inches="tight", dpi=220)
    plt.close()


def percent(x: float) -> float:
    return 100 * x


def plot_release_growth() -> None:
    releases = pd.DataFrame(
        {
            "release": ["v1", "v2", "v3", "v4", "v5", "v6"],
            "problems": [400, 511, 612, 713, 880, 1055],
        }
    )
    plt.figure(figsize=(5.4, 3.2))
    plt.plot(releases["release"], releases["problems"], marker="o", color="#2563eb", linewidth=2.2)
    for x, y in zip(releases["release"], releases["problems"]):
        plt.text(x, y + 18, str(y), ha="center", va="bottom", fontsize=8)
    plt.ylabel("Problems")
    plt.xlabel("LiveCodeBench release")
    plt.title("LiveCodeBench release growth")
    plt.grid(axis="y", alpha=0.25)
    savefig("release_growth")


def plot_overall() -> None:
    summary = pd.read_csv(RESULTS / "lcb_summary.csv")
    subset = summary[["model_dir", "scenario", "computed_first_sample_pass_rate"]].copy()
    subset["scenario"] = subset["scenario"].str.replace("Scenario.", "", regex=False)
    subset["model"] = subset["model_dir"].map(MODEL_LABELS)
    pivot = subset.pivot(index="model", columns="scenario", values="computed_first_sample_pass_rate")
    pivot = pivot.loc[[MODEL_LABELS[k] for k in MODEL_LABELS]]
    pivot = pivot[["codegeneration", "selfrepair"]].rename(
        columns={"codegeneration": "Code generation", "selfrepair": "Self-repair"}
    )
    ax = (pivot * 100).plot(kind="bar", figsize=(6.1, 3.35), width=0.74, color=["#2563eb", "#16a34a"])
    ax.set_ylabel("Pass@1 (%)")
    ax.set_xlabel("")
    ax.set_ylim(0, 78)
    ax.set_title("Controlled release_v5 results (279 problems)")
    ax.legend(frameon=False, loc="upper right")
    ax.grid(axis="y", alpha=0.25)
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f", fontsize=8, padding=2)
    plt.xticks(rotation=0)
    savefig("open_model_lcb")


def plot_difficulty() -> None:
    breakdown = pd.read_csv(RESULTS / "lcb_breakdown.csv")
    df = breakdown[
        (breakdown["group_type"] == "difficulty")
        & (breakdown["scenario"] == "Scenario.codegeneration")
    ].copy()
    df["model"] = df["model_dir"].map(MODEL_LABELS)
    order = ["easy", "medium", "hard"]
    pivot = df.pivot(index="model", columns="group_value", values="pass_at_1")
    pivot = pivot.loc[[MODEL_LABELS[k] for k in MODEL_LABELS], order]
    pivot = pivot.rename(columns={"easy": "Easy", "medium": "Medium", "hard": "Hard"})
    ax = (pivot * 100).plot(kind="bar", figsize=(6.35, 3.35), width=0.78, color=["#22c55e", "#f59e0b", "#ef4444"])
    ax.set_ylabel("Pass@1 (%)")
    ax.set_xlabel("")
    ax.set_ylim(0, 106)
    ax.set_title("Difficulty split for code generation")
    ax.legend(frameon=False, ncol=3, loc="upper right")
    ax.grid(axis="y", alpha=0.25)
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f", fontsize=7, padding=1)
    plt.xticks(rotation=0)
    savefig("difficulty_split")


def plot_repair_gain() -> None:
    summary = pd.read_csv(RESULTS / "lcb_summary.csv")
    wide = summary.pivot(
        index="model_dir", columns="scenario", values="computed_first_sample_pass_rate"
    )
    gains = (
        wide["Scenario.selfrepair"] - wide["Scenario.codegeneration"]
    ).rename("gain").reset_index()
    gains["model"] = gains["model_dir"].map(MODEL_LABELS)
    gains = gains.set_index("model").loc[[MODEL_LABELS[k] for k in MODEL_LABELS]]
    ax = (gains["gain"] * 100).plot(kind="bar", figsize=(5.7, 3.2), color="#7c3aed", width=0.58)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("Self-repair gain (points)")
    ax.set_xlabel("")
    ax.set_ylim(0, 4.4)
    ax.set_title("Self-repair improvement")
    ax.grid(axis="y", alpha=0.25)
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f", fontsize=8, padding=2)
    plt.xticks(rotation=0)
    savefig("repair_gain")


if __name__ == "__main__":
    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )
    plot_release_growth()
    plot_overall()
    plot_difficulty()
    plot_repair_gain()
