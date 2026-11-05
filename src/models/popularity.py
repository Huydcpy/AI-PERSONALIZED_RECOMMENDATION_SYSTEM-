"""Baseline gợi ý phim theo độ phổ biến."""

from __future__ import annotations

from src.models.base import Recommendation


class PopularityRecommender:
    """Gợi ý phim bằng Bayesian average của rating."""

    name = "popularity"

    def __init__(self, train_df, movies_df, m: int = 50):
        self.train_df = train_df
        self.movies_df = movies_df
        self.m = m
        self.global_mean = float(train_df["rating"].mean())

        stats = train_df.groupby("movie_id")["rating"].agg(["count", "mean"])
        v = stats["count"].astype(float)
        r = stats["mean"].astype(float)
        stats["score"] = (v / (v + m)) * r + (m / (v + m)) * self.global_mean

        self.scores = {int(key): float(value) for key, value in stats["score"].items()}
        self.titles = {
            int(key): str(value)
            for key, value in movies_df.set_index("movie_id")["title"].items()
        }

    def predict_rating(self, user_id: int, movie_id: int) -> float:
        """Dự đoán rating của user cho phim, fallback global mean."""
        return float(self.scores.get(movie_id, self.global_mean))

    def recommend(
        self, user_id: int, k: int = 10, exclude_seen: bool = True
    ) -> list[Recommendation]:
        """Trả về top-k phim phổ biến, loại phim user đã xem nếu cần."""
        seen = {
            int(movie_id)
            for movie_id in self.train_df.loc[
                self.train_df["user_id"] == user_id, "movie_id"
            ]
        }
        candidates = [
            (movie_id, score)
            for movie_id, score in self.scores.items()
            if not (exclude_seen and movie_id in seen)
        ]
        candidates.sort(key=lambda item: (-item[1], item[0]))

        return [
            Recommendation(
                movie_id=movie_id,
                title=self.titles.get(movie_id, f"Movie {movie_id}"),
                score=score,
                method=self.name,
                reason="Phổ biến toàn hệ thống",
            )
            for movie_id, score in candidates[:k]
        ]

    def similar_items(
        self, movie_id: int, k: int = 10
    ) -> list[Recommendation]:
        """Fallback Day 1: trả về các phim phổ biến khác."""
        candidates = [
            (mid, score)
            for mid, score in self.scores.items()
            if mid != movie_id
        ]
        candidates.sort(key=lambda item: (-item[1], item[0]))

        return [
            Recommendation(
                movie_id=mid,
                title=self.titles.get(mid, f"Movie {mid}"),
                score=score,
                method=self.name,
                reason="Fallback phổ biến (Day 1)",
            )
            for mid, score in candidates[:k]
        ]
