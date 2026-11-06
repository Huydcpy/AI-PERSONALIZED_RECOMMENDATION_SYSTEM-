"""Content-Based Filtering dựa trên thể loại phim."""

from __future__ import annotations

import numpy as np

from src.models.base import Recommendation
from src.models.popularity import PopularityRecommender

GENRES = (
    "action",
    "adventure",
    "animation",
    "children",
    "comedy",
    "crime",
    "documentary",
    "drama",
    "fantasy",
    "film_noir",
    "horror",
    "musical",
    "mystery",
    "romance",
    "sci_fi",
    "thriller",
    "war",
    "western",
)

GENRE_LABELS = {
    "action": "Action",
    "adventure": "Adventure",
    "animation": "Animation",
    "children": "Children",
    "comedy": "Comedy",
    "crime": "Crime",
    "documentary": "Documentary",
    "drama": "Drama",
    "fantasy": "Fantasy",
    "film_noir": "Film-Noir",
    "horror": "Horror",
    "musical": "Musical",
    "mystery": "Mystery",
    "romance": "Romance",
    "sci_fi": "Sci-Fi",
    "thriller": "Thriller",
    "war": "War",
    "western": "Western",
}


class ContentBasedRecommender:
    """Gợi ý phim theo độ tương đồng vector thể loại."""

    name = "content_based"

    def __init__(self, train_df, movies_df, fallback=None):
        self.train_df = train_df
        self.movies_df = movies_df.sort_values("movie_id").reset_index(drop=True)
        self.fallback = fallback or PopularityRecommender(train_df, movies_df)

        self.genre_columns = [
            genre for genre in GENRES if genre in self.movies_df.columns
        ]
        self.movie_ids = [
            int(movie_id) for movie_id in self.movies_df["movie_id"]
        ]
        self.movie_id_to_index = {
            movie_id: index for index, movie_id in enumerate(self.movie_ids)
        }
        self.index_to_movie_id = {
            index: movie_id for index, movie_id in enumerate(self.movie_ids)
        }
        self.titles = {
            int(row.movie_id): str(row.title)
            for row in self.movies_df.itertuples(index=False)
        }

        if self.genre_columns:
            raw_matrix = self.movies_df[self.genre_columns].to_numpy(
                dtype=np.float32
            )
            self.genre_matrix = self._normalize_rows(raw_matrix)
        else:
            self.genre_matrix = np.zeros(
                (len(self.movies_df), 0), dtype=np.float32
            )

        self.similarity = self.genre_matrix @ self.genre_matrix.T
        np.clip(self.similarity, 0.0, 1.0, out=self.similarity)

    @staticmethod
    def _normalize_rows(matrix: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return matrix / norms

    def _profile(self, user_id: int) -> np.ndarray | None:
        rows = self.train_df[self.train_df["user_id"] == user_id]
        if rows.empty:
            return None

        weights = rows["rating"].astype(float).sub(3.0).clip(lower=0.0)
        if float(weights.sum()) <= 0:
            return None

        vector = np.zeros(len(self.genre_columns), dtype=np.float64)
        total_weight = 0.0
        for movie_id, weight in zip(rows["movie_id"], weights):
            index = self.movie_id_to_index.get(int(movie_id))
            if index is None:
                continue
            vector += weight * self.genre_matrix[index]
            total_weight += float(weight)

        if total_weight <= 0:
            return None

        vector /= total_weight
        norm = float(np.linalg.norm(vector))
        if norm <= 0:
            return None
        return vector / norm

    def _seen_movie_ids(self, user_id: int) -> set[int]:
        rows = self.train_df.loc[
            self.train_df["user_id"] == user_id, "movie_id"
        ]
        return {int(movie_id) for movie_id in rows}

    def _genre_labels(self, indices) -> list[str]:
        return [GENRE_LABELS[self.genre_columns[index]] for index in indices]

    def _recommend_fallback(
        self, user_id: int, k: int, exclude_seen: bool
    ) -> list[Recommendation]:
        recommendations = self.fallback.recommend(
            user_id=user_id, k=k, exclude_seen=exclude_seen
        )
        return [
            Recommendation(
                movie_id=rec.movie_id,
                title=rec.title,
                score=float(rec.score),
                method="popularity",
                reason="Fallback phổ biến (cold-start)",
            )
            for rec in recommendations
        ]

    def _similar_fallback(self, movie_id: int, k: int) -> list[Recommendation]:
        recommendations = self.fallback.similar_items(movie_id=movie_id, k=k)
        return [
            Recommendation(
                movie_id=rec.movie_id,
                title=rec.title,
                score=float(rec.score),
                method="popularity",
                reason="Fallback phổ biến (thiếu thể loại)",
            )
            for rec in recommendations
        ]

    def recommend(
        self, user_id: int, k: int = 10, exclude_seen: bool = True
    ) -> list[Recommendation]:
        """Trả về tối đa k phim khớp thể loại với hồ sơ người dùng."""
        profile = self._profile(user_id)
        if profile is None or not self.genre_columns:
            return self._recommend_fallback(user_id, k, exclude_seen)

        scores = self.genre_matrix @ profile.astype(np.float32)
        seen = self._seen_movie_ids(user_id) if exclude_seen else set()

        candidates = [
            index
            for index, movie_id in enumerate(self.movie_ids)
            if scores[index] > 0 and movie_id not in seen
        ]
        if not candidates:
            return self._recommend_fallback(user_id, k, exclude_seen)

        candidates.sort(
            key=lambda index: (-float(scores[index]), self.movie_ids[index])
        )

        recommendations = []
        for index in candidates[:k]:
            genres = self._genre_labels(
                [
                    genre_index
                    for genre_index, column in enumerate(self.genre_columns)
                    if self.genre_matrix[index, genre_index] > 0
                    and profile[genre_index] > 0
                ]
            )
            reason = (
                f"Khớp thể loại: {', '.join(genres)}"
                if genres
                else "Nội dung tương tự"
            )
            movie_id = self.movie_ids[index]
            recommendations.append(
                Recommendation(
                    movie_id=movie_id,
                    title=self.titles.get(movie_id, f"Movie {movie_id}"),
                    score=min(1.0, max(0.0, float(scores[index]))),
                    method=self.name,
                    reason=reason,
                )
            )
        return recommendations

    def similar_items(
        self, movie_id: int, k: int = 10
    ) -> list[Recommendation]:
        """Trả về tối đa k phim cùng thể loại với phim gốc."""
        index = self.movie_id_to_index.get(int(movie_id))
        if index is None:
            raise ValueError(f"Movie {movie_id} không tồn tại")

        if not self.genre_columns or not self.genre_matrix[index].any():
            return self._similar_fallback(movie_id, k)

        scores = self.similarity[index]
        candidates = [
            candidate
            for candidate in range(len(self.movie_ids))
            if candidate != index and scores[candidate] > 0
        ]
        if not candidates:
            return self._similar_fallback(movie_id, k)

        candidates.sort(
            key=lambda candidate: (
                -float(scores[candidate]),
                self.movie_ids[candidate],
            )
        )

        recommendations = []
        source_genres = self.genre_matrix[index] > 0
        for candidate in candidates[:k]:
            genres = self._genre_labels(
                [
                    genre_index
                    for genre_index, column in enumerate(self.genre_columns)
                    if source_genres[genre_index]
                    and self.genre_matrix[candidate, genre_index] > 0
                ]
            )
            reason = (
                f"Cùng thể loại: {', '.join(genres)}"
                if genres
                else "Nội dung tương tự"
            )
            candidate_id = self.movie_ids[candidate]
            recommendations.append(
                Recommendation(
                    movie_id=candidate_id,
                    title=self.titles.get(
                        candidate_id, f"Movie {candidate_id}"
                    ),
                    score=min(1.0, max(0.0, float(scores[candidate]))),
                    method=self.name,
                    reason=reason,
                )
            )
        return recommendations
