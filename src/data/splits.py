"""Export the fixed u1 split; never randomly resplit or fit on test data."""

from pathlib import Path

import pandas as pd

from src.data.preprocess import RATING_COLUMNS, read_ratings, validate_ratings


def validate_split(train: pd.DataFrame, test: pd.DataFrame) -> None:
    validate_ratings(train)
    validate_ratings(test)
    if (len(train), len(test)) != (80000, 20000):
        raise ValueError("Expected 80000 train / 20000 test ratings")
    train_pairs = pd.MultiIndex.from_frame(train[["user_id", "movie_id"]])
    test_pairs = pd.MultiIndex.from_frame(test[["user_id", "movie_id"]])
    if len(train_pairs.intersection(test_pairs)):
        raise ValueError("Train and test overlap on (user_id, movie_id)")


def main() -> None:
    raw = Path("data/raw/ml-100k")
    train, test = (read_ratings(raw / name) for name in ("u1.base", "u1.test"))
    validate_split(train, test)
    original = read_ratings(raw / "u.data")
    combined = pd.concat([train, test], ignore_index=True)
    order = ["user_id", "movie_id"]
    if not combined.sort_values(order).reset_index(drop=True).equals(
        original[RATING_COLUMNS].sort_values(order).reset_index(drop=True)
    ):
        raise ValueError("Split union differs from u.data")
    output = Path("data/processed")
    output.mkdir(parents=True, exist_ok=True)
    train.to_parquet(output / "train.parquet", index=False)
    test.to_parquet(output / "test.parquet", index=False)
    print(f"Train: {len(train)} / test: {len(test)}; disjoint, union matches u.data")


if __name__ == "__main__":
    main()
