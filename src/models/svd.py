from dataclasses import replace

import numpy as np
from sklearn.preprocessing import normalize
from surprise import SVD

from src.data.surprise_dataset import build_surprise_trainset
from src.models.base import Recommendation
from src.models.popularity import PopularityRecommender


class SVDRecommender:
    name = "svd"

    def __init__(
        self,
        train_df,
        movies_df,
        fallback=None,
        n_factors: int = 100,
        n_epochs: int = 20,
        lr_all: float = 0.005,
        reg_all: float = 0.02,
        random_state: int = 42,
    ):
        self.movies_df = movies_df.sort_values("movie_id").reset_index(drop=True)
        self.movie_ids = self.movies_df.movie_id.to_numpy()
        self.movie_id_to_index = {int(mid): i for i, mid in enumerate(self.movie_ids)}
        self.index_to_movie_id = dict(enumerate(map(int, self.movie_ids)))
        self.titles = self.movies_df.title.astype(str).to_numpy()
        self.fallback = fallback if fallback is not None else PopularityRecommender(
            train_df, movies_df
        )
        self.known_users = set(map(int, train_df.user_id.unique()))
        self.seen = {
            int(user_id): set(map(int, rows.movie_id))
            for user_id, rows in train_df.groupby("user_id")
        }
        self.trainset = build_surprise_trainset(train_df)
        self.algo = SVD(
            n_factors=n_factors,
            n_epochs=n_epochs,
            lr_all=lr_all,
            reg_all=reg_all,
            random_state=random_state,
        )
        self.algo.fit(self.trainset)
        self.global_mean = float(self.trainset.global_mean)

        n_movies = len(self.movie_ids)
        n_latent = self.algo.qi.shape[1]
        self.item_factors = np.zeros((n_movies, n_latent), dtype=float)
        self.item_bias = np.zeros(n_movies, dtype=float)
        self.has_factors = np.zeros(n_movies, dtype=bool)
        for inner_id in range(self.trainset.n_items):
            raw_id = int(self.trainset.to_raw_iid(inner_id))
            index = self.movie_id_to_index.get(raw_id)
            if index is None:
                continue
            self.item_factors[index] = self.algo.qi[inner_id]
            self.item_bias[index] = self.algo.bi[inner_id]
            self.has_factors[index] = True

        self.user_factors = {}
        self.user_bias = {}
        for user_id in self.known_users:
            inner_id = self.trainset.to_inner_uid(user_id)
            self.user_factors[user_id] = self.algo.pu[inner_id].copy()
            self.user_bias[user_id] = float(self.algo.bu[inner_id])

        normalized = normalize(self.item_factors)
        self.similarity = np.clip(normalized @ normalized.T, 0, 1)
        np.fill_diagonal(self.similarity, 0)

    def _score_user(self, user_id: int) -> np.ndarray:
        scores = (
            self.global_mean
            + self.user_bias[user_id]
            + self.item_bias
            + self.item_factors @ self.user_factors[user_id]
        )
        return np.clip(scores, 1, 5)

    def _rank(self, scores, valid, excluded, k, reason):
        indices = [
            i for i in np.flatnonzero(valid) if int(self.movie_ids[i]) not in excluded
        ]
        indices.sort(key=lambda i: (-float(scores[i]), int(self.movie_ids[i])))
        return [
            Recommendation(
                movie_id=int(self.movie_ids[i]),
                title=self.titles[i],
                score=float(scores[i]),
                method=self.name,
                reason=reason,
            )
            for i in indices[:k]
        ]

    def _fill(self, results, candidates, k, reason):
        used = {item.movie_id for item in results}
        for item in candidates:
            if len(results) >= k:
                break
            if item.movie_id not in used:
                results.append(replace(item, method="popularity", reason=reason))
                used.add(item.movie_id)
        return results

    def predict_rating(self, user_id: int, movie_id: int) -> float:
        prediction = self.algo.predict(int(user_id), int(movie_id))
        return float(np.clip(prediction.est, 1, 5))

    def recommend(
        self, user_id: int, k: int = 10, exclude_seen: bool = True
    ) -> list[Recommendation]:
        if k <= 0:
            return []
        user_id = int(user_id)
        results = []
        if user_id in self.known_users:
            scores = self._score_user(user_id)
            excluded = self.seen.get(user_id, set()) if exclude_seen else set()
            results = self._rank(
                scores,
                self.has_factors,
                excluded,
                k,
                "Dự đoán theo sở thích cá nhân (SVD)",
            )
            reason = "Fallback phổ biến (thiếu tín hiệu)"
        else:
            reason = "Fallback phổ biến (cold-start)"
        if len(results) < k:
            candidates = self.fallback.recommend(
                user_id, k=k + len(results), exclude_seen=exclude_seen
            )
            results = self._fill(results, candidates, k, reason)
        return results

    def similar_items(self, movie_id: int, k: int = 10) -> list[Recommendation]:
        if movie_id not in self.movie_id_to_index:
            raise ValueError(f"Movie {movie_id} không tồn tại")
        if k <= 0:
            return []
        scores = self.similarity[self.movie_id_to_index[movie_id]]
        results = self._rank(
            scores, scores > 0, {movie_id}, k, "Cùng gu người dùng (SVD)"
        )
        if len(results) < k:
            results = self._fill(
                results,
                self.fallback.similar_items(movie_id, k=k + len(results)),
                k,
                "Fallback phổ biến (thiếu tín hiệu)",
            )
        return results
