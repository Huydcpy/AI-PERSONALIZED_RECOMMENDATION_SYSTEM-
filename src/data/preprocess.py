"""Read, validate and export the official MovieLens 100K tables."""

from pathlib import Path

import pandas as pd

RATING_COLUMNS = ["user_id", "movie_id", "rating", "timestamp"]
GENRES = [
    "unknown", "action", "adventure", "animation", "children", "comedy",
    "crime", "documentary", "drama", "fantasy", "film_noir", "horror",
    "musical", "mystery", "romance", "sci_fi", "thriller", "war", "western",
]
MOVIE_COLUMNS = [
    "movie_id", "title", "release_date", "video_release_date", "imdb_url", *GENRES,
]
USER_COLUMNS = ["user_id", "age", "gender", "occupation", "zip_code"]


def read_ratings(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t", names=RATING_COLUMNS, dtype="int64")


def validate_ratings(ratings: pd.DataFrame) -> None:
    if ratings[RATING_COLUMNS].isna().any().any():
        raise ValueError("Ratings contain missing values")
    if not ratings["rating"].between(1, 5).all():
        raise ValueError("Ratings must be in [1, 5]")
    if ratings.duplicated(["user_id", "movie_id"]).any():
        raise ValueError("Duplicate (user_id, movie_id) pairs")


def validate_data(
    ratings: pd.DataFrame, movies: pd.DataFrame, users: pd.DataFrame,
) -> None:
    validate_ratings(ratings)
    if (len(ratings), ratings.user_id.nunique(), ratings.movie_id.nunique()) != (
        100000, 943, 1682,
    ):
        raise ValueError("Expected 100000 ratings, 943 users and 1682 movies")
    for table, key, expected, required in (
        (movies, "movie_id", 1682, ["movie_id", "title", *GENRES]),
        (users, "user_id", 943, USER_COLUMNS),
    ):
        if len(table) != expected or table[key].nunique() != expected:
            raise ValueError(f"Invalid metadata count or duplicate {key}")
        if table[required].isna().any().any():
            raise ValueError(f"Missing required metadata for {key}")
        if set(ratings[key]) != set(table[key]):
            raise ValueError(f"Ratings and metadata {key} do not match")
    if not movies[GENRES].isin([0, 1]).all().all():
        raise ValueError("Genre flags must be binary")


def load_processed_data(
    data_dir: str = "data/processed",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return (ratings, movies, users), in that order."""
    root = Path(data_dir)
    return tuple(pd.read_parquet(root / f"{name}.parquet")
                 for name in ("ratings", "movies", "users"))


def main() -> None:
    raw = Path("data/raw/ml-100k")
    ratings = read_ratings(raw / "u.data")
    movies = pd.read_csv(raw / "u.item", sep="|", encoding="latin-1",
                         names=MOVIE_COLUMNS)
    users = pd.read_csv(raw / "u.user", sep="|", names=USER_COLUMNS,
                        dtype={"zip_code": "string"}, keep_default_na=False)
    validate_data(ratings, movies, users)
    output = Path("data/processed")
    output.mkdir(parents=True, exist_ok=True)
    for name, table in (("ratings", ratings), ("movies", movies), ("users", users)):
        table.to_parquet(output / f"{name}.parquet", index=False)
    print("Validated and saved: 100000 ratings / 943 users / 1682 movies")


if __name__ == "__main__":
    main()
