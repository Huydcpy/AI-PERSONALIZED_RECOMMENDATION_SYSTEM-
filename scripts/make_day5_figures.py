import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / "reports" / "metrics"
FIGURES = ROOT / "reports" / "figures"
MODELS = [
    ("popularity", "Popularity"),
    ("content_based", "Content-Based"),
    ("item_cf", "Item-CF"),
    ("svd", "SVD"),
    ("hybrid", "Hybrid"),
]
COLORS = ["#4c72b0", "#dd8452", "#55a868", "#c44e52", "#8172b3"]


def load_json(path):
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_metrics():
    for name, model in (("baseline", "popularity"), ("svd", "svd")):
        data = load_json(METRICS / f"{name}.json")
        if data.get("model") != model:
            raise ValueError(f"Invalid model in {name}.json")
        for metric in ("rmse", "mae"):
            value = data.get(metric)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError(f"Invalid {metric} in {name}.json")
    ranking = load_json(METRICS / "ranking.json")
    if set(ranking.get("models", {})) != {key for key, _ in MODELS}:
        raise ValueError("Ranking must contain exactly five expected models")
    for key, _ in MODELS:
        for metric in ("precision@5", "precision@10", "recall@10", "ndcg@10", "coverage@10"):
            value = ranking["models"][key].get(metric)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"Invalid {key}: {metric}")


def save(fig, name):
    FIGURES.mkdir(parents=True, exist_ok=True)
    path = FIGURES / name
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(path)


def plot_rating():
    baseline = load_json(METRICS / "baseline.json")
    svd = load_json(METRICS / "svd.json")
    labels = ["Popularity", "SVD"]
    rmse = [baseline["rmse"], svd["rmse"]]
    mae = [baseline["mae"], svd["mae"]]

    x = range(len(labels))
    width = 0.36
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    bars_rmse = ax.bar([i - width / 2 for i in x], rmse, width, label="RMSE", color="#4c72b0")
    bars_mae = ax.bar([i + width / 2 for i in x], mae, width, label="MAE", color="#dd8452")
    for bars in (bars_rmse, bars_mae):
        for bar in bars:
            ax.annotate(
                f"{bar.get_height():.4f}",
                xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
            )
    ax.set_xticks(list(x), labels)
    ax.set_ylabel("Error (lower is better)")
    ax.set_title("Rating Prediction: Popularity vs SVD")
    ax.set_ylim(0, 1.25)
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    save(fig, "day5_rating_rmse_mae.png")


def plot_ranking_metric(metric, title, ylabel, name):
    ranking = load_json(METRICS / "ranking.json")
    labels = [label for _, label in MODELS]
    values = [ranking["models"][key][metric] for key, _ in MODELS]

    fig, ax = plt.subplots(figsize=(9, 4.8))
    bars = ax.bar(labels, values, color=COLORS)
    for bar, value in zip(bars, values):
        ax.annotate(
            f"{value:.4f}",
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_ylim(0, max(values) * 1.25)
    ax.grid(axis="y", alpha=0.25)
    save(fig, name)


def plot_tradeoff():
    ranking = load_json(METRICS / "ranking.json")
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    for (key, label), color in zip(MODELS, COLORS):
        ndcg = ranking["models"][key]["ndcg@10"]
        coverage = ranking["models"][key]["coverage@10"]
        ax.scatter(ndcg, coverage, s=90, color=color, label=label)
        ax.annotate(
            f"{label}\n({ndcg:.4f}, {coverage:.4f})",
            xy=(ndcg, coverage),
            xytext=(6, 6),
            textcoords="offset points",
            fontsize=9,
        )
    ax.set_xlabel("NDCG@10")
    ax.set_ylabel("Coverage@10")
    ax.set_title("NDCG@10 vs Coverage@10")
    ax.margins(x=0.3, y=0.2)
    ax.grid(alpha=0.25)
    ax.legend()
    save(fig, "day5_ndcg_vs_coverage.png")


def main():
    validate_metrics()
    plot_rating()
    plot_ranking_metric(
        "ndcg@10",
        "Ranking Accuracy: NDCG@10",
        "NDCG@10",
        "day5_ranking_ndcg10.png",
    )
    plot_ranking_metric(
        "coverage@10",
        "Catalog Coverage: Coverage@10",
        "Coverage@10",
        "day5_ranking_coverage10.png",
    )
    plot_tradeoff()


if __name__ == "__main__":
    main()
