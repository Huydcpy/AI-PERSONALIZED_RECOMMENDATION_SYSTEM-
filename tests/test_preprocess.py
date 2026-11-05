"""Data checks plus synthetic regression tests that run without downloads."""

from pathlib import Path

import pandas as pd
import pytest

from src.data.preprocess import load_processed_data, validate_data, validate_ratings
from src.data.splits import validate_split

DATA = Path("data/processed")


def test_processed_data():
    if not all((DATA / f"{name}.parquet").exists()
               for name in ("ratings", "movies", "users")):
        pytest.skip("Run src.data.download and src.data.preprocess first")
    validate_data(*load_processed_data())


def test_official_split():
    if not all((DATA / f"{name}.parquet").exists() for name in ("train", "test")):
        pytest.skip("Run src.data.splits first")
    train = pd.read_parquet(DATA / "train.parquet")
    test = pd.read_parquet(DATA / "test.parquet")
    validate_split(train, test)
    if (DATA / "ratings.parquet").exists():
        ratings = pd.read_parquet(DATA / "ratings.parquet")
        order = ["user_id", "movie_id"]
        pd.testing.assert_frame_equal(
            pd.concat([train, test]).sort_values(order).reset_index(drop=True),
            ratings.sort_values(order).reset_index(drop=True),
        )


@pytest.mark.parametrize("rating", [0, 6, None])
def test_invalid_rating_rejected(rating):
    frame = pd.DataFrame({"user_id": [1], "movie_id": [1],
                          "rating": [rating], "timestamp": [1]})
    with pytest.raises(ValueError):
        validate_ratings(frame)


def test_overlap_rejected_at_official_sizes():
    train = pd.DataFrame({"user_id": 1, "movie_id": range(80000),
                          "rating": 4, "timestamp": 1})
    test = pd.DataFrame({"user_id": 1, "movie_id": range(79999, 99999),
                         "rating": 4, "timestamp": 1})
    with pytest.raises(ValueError, match="overlap"):
        validate_split(train, test)


def test_duplicate_pair_rejected():
    frame = pd.DataFrame({"user_id": [1, 1], "movie_id": [2, 2],
                          "rating": [3, 4], "timestamp": [1, 2]})
    with pytest.raises(ValueError, match="Duplicate"):
        validate_ratings(frame)
