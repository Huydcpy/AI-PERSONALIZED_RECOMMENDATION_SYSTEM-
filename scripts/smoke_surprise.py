"""Smoke test môi trường Surprise, không phải kết quả chính thức."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import _bootstrap  # noqa: F401
import pandas as pd
from surprise import KNNWithMeans, accuracy

from src.data.surprise_dataset import build_surprise_trainset, build_testset


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data/processed")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_dir = Path(args.data_dir)

    train_df = pd.read_parquet(data_dir / "train.parquet")
    test_df = pd.read_parquet(data_dir / "test.parquet")

    trainset = build_surprise_trainset(train_df)
    testset = build_testset(test_df)

    algo = KNNWithMeans(
        k=40,
        sim_options={"name": "cosine", "user_based": False},
    )

    start = time.perf_counter()
    algo.fit(trainset)
    predictions = algo.test(testset)
    elapsed = time.perf_counter() - start

    score = accuracy.rmse(predictions, verbose=False)
    print(f"RMSE: {score:.4f}")
    print(f"Thời gian: {elapsed:.1f} giây")


if __name__ == "__main__":
    main()
