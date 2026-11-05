"""Service layer for movie recommendations.

IMPORTANT: This module MUST NOT import Streamlit (app/ depends on it,
never the reverse). Supported method for Day 1 is "popularity" only;
other methods raise ValueError("Method ... sẽ có từ Day 2/3").
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.models.base import Recommendation
from src.models.popularity import PopularityRecommender

SUPPORTED_METHODS = ("popularity",)


def _read_csv_if_exists(path: Path) -> pd.DataFrame:
    if path.exists() and path.stat().st_size > 0:
        return pd.read_csv(path)
    return pd.DataFrame()


def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename common variants to canonical schema (transparent, no-op if absent)."""
    if df.empty:
        return df
    df = df.copy()
    renames = {}
    if "userID" in df.columns and "user_id" not in df.columns:
        renames["userID"] = "user_id"
    if "itemID" in df.columns and "movie_id" not in df.columns:
        renames["itemID"] = "movie_id"
    if "item_id" in df.columns and "movie_id" not in df.columns:
        renames["item_id"] = "movie_id"
    if "movieId" in df.columns and "movie_id" not in df.columns:
        renames["movieId"] = "movie_id"
    if renames:
        df = df.rename(columns=renames)
    return df


class RecommenderService:
    """Data access + recommendation orchestration (no UI concerns)."""

    def __init__(
        self,
        data_dir: str | Path = "data/processed",
        metrics_dir: str | Path = "reports/metrics",
    ) -> None:
        self.data_dir = Path(data_dir)
        self.metrics_dir = Path(metrics_dir)

        self.ratings: pd.DataFrame = _normalise_columns(
            _read_csv_if_exists(self.data_dir / "ratings.csv")
        )
        self.movies: pd.DataFrame = _normalise_columns(
            _read_csv_if_exists(self.data_dir / "movies.csv")
        )
        self.users: pd.DataFrame = _normalise_columns(
            _read_csv_if_exists(self.data_dir / "users.csv")
        )
        self.train: pd.DataFrame = _normalise_columns(
            _read_csv_if_exists(self.data_dir / "train.csv")
        )
        self.test: pd.DataFrame = _normalise_columns(
            _read_csv_if_exists(self.data_dir / "test.csv")
        )

        # Popularity model trained on ratings (or train split if available).
        self._popularity = PopularityRecommender()
        source = self.train if not self.train.empty else self.ratings
        if not source.empty:
            self._popularity.fit(source, self.movies if not self.movies.empty else None)

        self._movie_index: dict[int, dict] = {}
        if not self.movies.empty and "movie_id" in self.movies.columns:
            for row in self.movies.to_dict(orient="records"):
                self._movie_index[int(row["movie_id"])] = row

        self._seen_by_user: dict[int, set[int]] = {}
        if not self.ratings.empty:
            _u = "user_id" if "user_id" in self.ratings.columns else None
            _m = "movie_id" if "movie_id" in self.ratings.columns else None
            if _u and _m:
                for uid, g in self.ratings.groupby(_u):
                    self._seen_by_user[int(uid)] = set(int(x) for x in g[_m].tolist())

    # ---------- data listing / lookup ----------

    def list_users(self) -> list[int]:
        if not self.users.empty and "user_id" in self.users.columns:
            return sorted(int(x) for x in self.users["user_id"].tolist())
        if not self.ratings.empty and "user_id" in self.ratings.columns:
            return sorted(int(x) for x in self.ratings["user_id"].unique().tolist())
        return []

    def get_user_profile(self, user_id: int) -> dict:
        user_id = int(user_id)
        profile: dict = {}
        if not self.users.empty and "user_id" in self.users.columns:
            match = self.users[self.users["user_id"] == user_id]
            if not match.empty:
                profile = match.iloc[0].to_dict()
        if not self.ratings.empty and "user_id" in self.ratings.columns:
            r = self.ratings[self.ratings["user_id"] == user_id]
            if r.empty:
                raise KeyError(f"User {user_id} not found")
            n_ratings = int(len(r))
            avg = float(r["rating"].mean()) if "rating" in r.columns else 0.0
            # Top genres from this user's rated movies.
            top_genres: list[str] = []
            if (
                not self.movies.empty
                and "movie_id" in self.movies.columns
                and "genres" in self.movies.columns
            ):
                seen_ids = set(int(x) for x in r["movie_id"].tolist()) if "movie_id" in r.columns else set()
                movies = self.movies[self.movies["movie_id"].isin(seen_ids)]
                from collections import Counter

                c: Counter = Counter()
                for g in movies["genres"].tolist():
                    for genre in str(g).split("|"):
                        genre = genre.strip()
                        if genre and genre.lower() not in ("unknown", "n/a"):
                            c[genre] += 1
                top_genres = [g for g, _ in c.most_common(5)]
            profile = {**profile, "user_id": user_id}
            profile.setdefault("n_ratings", n_ratings)
            profile.setdefault("avg_rating", avg)
            profile.setdefault("top_genres", top_genres)
            # Recent ratings (latest first if timestamp exists, else last rows).
            if "timestamp" in r.columns:
                recent = r.sort_values("timestamp", ascending=False).head(10)
            else:
                recent = r.tail(10)
            recent_records = recent.to_dict(orient="records")
            enriched = []
            for rec in recent_records:
                mid = rec.get("movie_id")
                title = None
                if mid is not None and int(mid) in self._movie_index:
                    title = self._movie_index[int(mid)].get("title")
                enriched.append({**rec, "title": title})
            profile["recent_ratings"] = enriched
            return profile
        raise KeyError(f"User {user_id} not found")

    def get_movie(self, movie_id: int) -> dict:
        movie_id = int(movie_id)
        if movie_id in self._movie_index:
            return dict(self._movie_index[movie_id])
        raise KeyError(f"Movie {movie_id} not found")

    def search_movies(self, query: str, limit: int = 20) -> list[dict]:
        if self.movies.empty or "title" not in self.movies.columns:
            return []
        q = (query or "").strip().lower()
        if not q:
            return self.movies.head(limit).to_dict(orient="records")
        mask = self.movies["title"].str.lower().str.contains(q, na=False)
        return self.movies[mask].head(limit).to_dict(orient="records")

    # ---------- recommendation ----------

    def recommend(
        self,
        user_id: int,
        method: str = "popularity",
        k: int = 10,
        exclude_seen: bool = True,
    ) -> list[Recommendation]:
        if method not in SUPPORTED_METHODS:
            raise ValueError(f"Method {method!r} sẽ có từ Day 2/3")
        recs = self._popularity.recommend(int(user_id), k=k, exclude_seen=exclude_seen)
        return [self._enrich(r) for r in recs]

    def similar_items(self, movie_id: int, k: int = 10) -> list[Recommendation]:
        recs = self._popularity.similar_items(int(movie_id), k=k)
        return [self._enrich(r) for r in recs]

    def _enrich(self, rec: Recommendation) -> Recommendation:
        movie = self._movie_index.get(int(rec.movie_id))
        if movie is not None:
            genres = movie.get("genres") or movie.get("genre") or ""
            reason = rec.reason or (str(genres) if genres else None)
            return Recommendation(
                movie_id=rec.movie_id,
                title=str(movie.get("title") or rec.title),
                score=rec.score,
                method=rec.method,
                reason=reason,
            )
        return rec

    # ---------- metrics ----------

    def get_baseline_metrics(self) -> dict:
        path = self.metrics_dir / "baseline.json"
        if not path.exists():
            return {}
        try:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            return {}
