from dataclasses import replace

import numpy as np
from sklearn.preprocessing import normalize

from src.data.preprocess import GENRES as DATA_GENRES
from src.models.base import Recommendation
from src.models.popularity import PopularityRecommender

KNOWN_GENRES = [genre for genre in DATA_GENRES if genre != "unknown"]
GENRES = tuple(KNOWN_GENRES)


class ContentBasedRecommender:
    name = "content_based"

    def __init__(self, train_df, movies_df, fallback=None):
        self.train_df = train_df.copy()
        self.movies_df = movies_df.sort_values("movie_id").reset_index(drop=True)
        self.fallback = fallback if fallback is not None else PopularityRecommender(
            train_df, movies_df
        )
        self.movie_ids = self.movies_df.movie_id.to_numpy()
        self.movie_id_to_index = {int(mid): i for i, mid in enumerate(self.movie_ids)}
        self.index_to_movie_id = dict(enumerate(map(int, self.movie_ids)))
        self.genre_matrix = normalize(self.movies_df[KNOWN_GENRES].to_numpy(dtype=float))
        self.similarity = np.clip(self.genre_matrix @ self.genre_matrix.T, 0, 1)

    def _reason(self, index, vector, prefix):
        shared = (self.genre_matrix[index] > 0) & (vector > 0)
        labels = [
            "Sci-Fi" if genre == "sci_fi" else genre.replace("_", " ").title()
            for genre, match in zip(KNOWN_GENRES, shared) if match
        ]
        return prefix + ", ".join(labels) if labels else "Nội dung tương tự"

    def _rank(self, scores, vector, excluded, k, prefix):
        indices = [
            i for i, score in enumerate(scores)
            if score > 0 and int(self.movie_ids[i]) not in excluded
        ]
        indices.sort(key=lambda i: (-float(scores[i]), int(self.movie_ids[i])))
        return [
            Recommendation(
                movie_id=int(self.movie_ids[i]), title=str(self.movies_df.iloc[i].title),
                score=float(scores[i]), method=self.name,
                reason=self._reason(i, vector, prefix),
            ) for i in indices[:k]
        ]

    def _fill(self, results, candidates, k):
        used = {item.movie_id for item in results}
        for item in candidates:
            if len(results) >= k:
                break
            if item.movie_id not in used:
                results.append(replace(
                    item, method="popularity", reason="Fallback phổ biến (cold-start)"
                ))
                used.add(item.movie_id)
        return results

    def recommend(self, user_id: int, k: int = 10, exclude_seen: bool = True):
        if k <= 0:
            return []
        ratings = self.train_df[self.train_df.user_id == user_id]
        seen = set(map(int, ratings.movie_id)) if exclude_seen else set()
        profile = np.zeros(len(KNOWN_GENRES))
        for row in ratings.itertuples():
            index = self.movie_id_to_index.get(row.movie_id)
            if index is not None:
                profile += max(float(row.rating) - 3, 0) * self.genre_matrix[index]
        profile = normalize(profile.reshape(1, -1))[0]
        scores = np.clip(self.genre_matrix @ profile, 0, 1)
        results = self._rank(scores, profile, seen, k, "Khớp thể loại: ")
        if len(results) < k:
            results = self._fill(results, self.fallback.recommend(
                user_id, k=k + len(results), exclude_seen=exclude_seen
            ), k)
        return results

    def similar_items(self, movie_id: int, k: int = 10):
        if movie_id not in self.movie_id_to_index:
            raise ValueError(f"Movie {movie_id} không tồn tại")
        if k <= 0:
            return []
        index = self.movie_id_to_index[movie_id]
        results = self._rank(
            self.similarity[index], self.genre_matrix[index], {movie_id}, k,
            "Cùng thể loại: ",
        )
        if len(results) < k:
            results = self._fill(results, self.fallback.similar_items(
                movie_id, k=k + len(results)
            ), k)
        return results
