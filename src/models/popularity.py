"""Popularity-based recommender (Day 1 baseline).

Score = bayesian weighted mean of ratings, shrunk toward global mean.
similar_items falls back to popularity (Day 1 scope).
"""
from __future__ import annotations

import pandas as pd

from .base import Recommendation


class PopularityRecommender:
    """Baseline recommender ranked by Bayesian average rating."""

    name = "popularity"

    def __init__(self, min_votes: int = 5) -> None:
        self.min_votes = min_votes
        self._stats: pd.DataFrame | None = None
        self._global_mean: float = 0.0
        self._user_seen: dict[int, set[int]] = {}

    def fit(
        self, ratings_df: pd.DataFrame, items_df: pd.DataFrame | None = None
    ) -> None:
        if ratings_df is None or ratings_df.empty:
            self._stats = pd.DataFrame(
                columns=["movie_id", "n_ratings", "mean_rating", "score"]
            )
            return

        df = ratings_df.copy()
        # Normalise column names used internally.
        if "item_id" in df.columns and "movie_id" not in df.columns:
            df["movie_id"] = df["item_id"]
        if "userID" in df.columns and "user_id" not in df.columns:
            df["user_id"] = df["userID"]

        self._global_mean = float(df["rating"].mean()) if "rating" in df else 0.0

        grp = df.groupby("movie_id")["rating"].agg(["count", "mean"]).rename(
            columns={"count": "n_ratings", "mean": "mean_rating"}
        ).reset_index()
        m = float(self.min_votes)
        grp["score"] = (
            (grp["n_ratings"] * grp["mean_rating"] + m * self._global_mean)
            / (grp["n_ratings"] + m)
        )
        self._stats = grp.sort_values("score", ascending=False).reset_index(drop=True)

        if "user_id" in df.columns and "movie_id" in df.columns:
            seen: dict[int, set[int]] = {}
            for uid, g in df.groupby("user_id"):
                seen[int(uid)] = {int(x) for x in g["movie_id"].tolist()}
            self._user_seen = seen

    def recommend(
        self, user_id: int, k: int = 10, exclude_seen: bool = True
    ) -> list[Recommendation]:
        if self._stats is None or self._stats.empty:
            return []
        stats = self._stats
        if exclude_seen:
            seen = self._user_seen.get(int(user_id), set())
            if seen:
                stats = stats[~stats["movie_id"].isin(seen)]
        top = stats.head(k)
        return [
            Recommendation(
                movie_id=int(r.movie_id),
                title="",  # title enriched by service layer if available
                score=float(r.score),
                method=self.name,
                reason=None,
            )
            for r in top.itertuples()
        ]

    def similar_items(self, movie_id: int, k: int = 10) -> list[Recommendation]:
        """Day 1 fallback: popularity ignoring the query movie itself."""
        if self._stats is None or self._stats.empty:
            return []
        stats = self._stats[self._stats["movie_id"] != int(movie_id)]
        top = stats.head(k)
        return [
            Recommendation(
                movie_id=int(r.movie_id),
                title="",
                score=float(r.score),
                method=self.name,
                reason="Fallback to popularity (Day 1)",
            )
            for r in top.itertuples()
        ]
