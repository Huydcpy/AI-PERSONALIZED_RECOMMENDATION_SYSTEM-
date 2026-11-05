"""Chạy baseline Popularity và ghi kết quả đánh giá."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import _bootstrap  # noqa: F401
import pandas as pd

from src.evaluation.rating_metrics import mae, rmse
from src.models.popularity import PopularityRecommender

SEED = 42


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data/processed")
    parser.add_argument("--metrics-dir", default="reports/metrics")
    return parser.parse_args()


def load_parquet(data_dir: Path, name: str) -> pd.DataFrame:
    path = data_dir / f"{name}.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy {path}. Hãy chạy data pipeline trước."
        )
    return pd.read_parquet(path)


def main() -> None:
    args = parse_args()
    data_dir = Path(args.data_dir)
    metrics_dir = Path(args.metrics_dir)

    train_df = load_parquet(data_dir, "train")
    test_df = load_parquet(data_dir, "test")
    movies_df = load_parquet(data_dir, "movies")

    model = PopularityRecommender(train_df, movies_df)

    y_true = []
    y_pred = []
    for user_id, movie_id, rating in test_df[
        ["user_id", "movie_id", "rating"]
    ].itertuples(index=False, name=None):
        y_true.append(float(rating))
        y_pred.append(model.predict_rating(user_id, movie_id))

    result = {
        "model": model.name,
        "rmse": rmse(y_true, y_pred),
        "mae": mae(y_true, y_pred),
        "n_test": len(test_df),
        "train_size": len(train_df),
        "seed": SEED,
    }

    metrics_dir.mkdir(parents=True, exist_ok=True)
    output = metrics_dir / "baseline.json"
    with output.open("w", encoding="utf-8") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)

    print(json.dumps(result, indent=2))

    if not 0.95 <= result["rmse"] <= 1.10:
        print(
            "CẢNH BÁO: RMSE ngoài khoảng kỳ vọng 0.95–1.10. "
            "Kiểm tra lại split và fallback global_mean."
        )


if __name__ == "__main__":
    main()
