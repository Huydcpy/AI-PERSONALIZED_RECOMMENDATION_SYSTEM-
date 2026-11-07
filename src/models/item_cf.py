from dataclasses import replace

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.preprocessing import normalize

from src.models.base import Recommendation
from src.models.popularity import PopularityRecommender


class ItemCFRecommender:
    name = "item_cf"

    def __init__(self, train_df, movies_df, fallback=None, k_neighbors: int = 50):
        if k_neighbors <= 0:
            raise ValueError("k_neighbors phải > 0")
        self.movies_df = movies_df.sort_values("movie_id").reset_index(drop=True)
        self.movie_ids = self.movies_df.movie_id.to_numpy()
        self.movie_id_to_index = {int(mid): i for i, mid in enumerate(self.movie_ids)}
        self.index_to_movie_id = dict(enumerate(map(int, self.movie_ids)))
        self.user_ids = np.sort(train_df.user_id.unique())
        self.user_id_to_index = {int(uid): i for i, uid in enumerate(self.user_ids)}
        self.global_mean = float(train_df.rating.mean()) if len(train_df) else 3.0
        self.user_mean = train_df.groupby("user_id").rating.mean().to_dict()
        self.fallback = fallback if fallback is not None else PopularityRecommender(train_df, movies_df)
        rows = train_df.user_id.map(self.user_id_to_index).to_numpy(dtype=int)
        columns = train_df.movie_id.map(self.movie_id_to_index).to_numpy(dtype=int)
        centered = train_df.rating.to_numpy(dtype=float) - train_df.user_id.map(self.user_mean).to_numpy(dtype=float)
        shape = (len(self.user_ids), len(self.movie_ids))
        self.centered_ratings = csr_matrix((centered, (rows, columns)), shape=shape)
        self.observed = csr_matrix((np.ones(len(rows)), (rows, columns)), shape=shape)
        normalized = normalize(self.centered_ratings.T) if len(rows) else self.centered_ratings.T
        self.similarity = np.clip((normalized @ normalized.T).toarray(), 0, 1)
        np.fill_diagonal(self.similarity, 0)
        for scores in self.similarity:
            order = np.lexsort((self.movie_ids, -scores))
            scores[order[k_neighbors:]] = 0
        self.titles = self.movies_df.title.astype(str).to_numpy()

    def _rank(self, scores, valid, excluded, k, reason):
        indices = [i for i in np.flatnonzero(valid) if int(self.movie_ids[i]) not in excluded]
        indices.sort(key=lambda i: (-float(scores[i]), int(self.movie_ids[i])))
        return [Recommendation(movie_id=int(self.movie_ids[i]), title=self.titles[i],
                               score=float(scores[i]), method=self.name, reason=reason)
                for i in indices[:k]]

    def _fill(self, results, candidates, k, reason):
        used = {item.movie_id for item in results}
        for item in candidates:
            if len(results) >= k:
                break
            if item.movie_id not in used:
                results.append(replace(item, method="popularity", reason=reason))
                used.add(item.movie_id)
        return results

    def recommend(self, user_id: int, k: int = 10, exclude_seen: bool = True) -> list[Recommendation]:
        if k <= 0:
            return []
        index = self.user_id_to_index.get(user_id)
        results = []
        reason = "Fallback phổ biến (cold-start)"
        if index is not None:
            observed = self.observed.getrow(index).indices
            centered = self.centered_ratings.getrow(index).toarray().ravel()
            weights = self.similarity[:, observed]
            denominator = np.abs(weights).sum(axis=1)
            numerator = weights @ centered[observed]
            scores = np.divide(numerator, denominator, out=np.zeros_like(numerator), where=denominator > 0)
            predicted = np.clip(self.user_mean.get(user_id, self.global_mean) + scores, 1, 5)
            excluded = set(map(int, self.movie_ids[observed])) if exclude_seen else set()
            results = self._rank(predicted, scores > 0, excluded, k,
                                 "Dựa trên phim tương tự bạn đã rating")
            reason = "Fallback phổ biến (thiếu tín hiệu)"
        if len(results) < k:
            candidates = self.fallback.recommend(user_id, k=k + len(results), exclude_seen=exclude_seen)
            self._fill(results, candidates, k, reason)
        return results

    def similar_items(self, movie_id: int, k: int = 10) -> list[Recommendation]:
        if movie_id not in self.movie_id_to_index:
            raise ValueError(f"Movie {movie_id} không tồn tại")
        if k <= 0:
            return []
        scores = self.similarity[self.movie_id_to_index[movie_id]]
        results = self._rank(scores, scores > 0, {movie_id}, k, "Cùng gu người dùng")
        if len(results) < k:
            self._fill(results, self.fallback.similar_items(movie_id, k=k + len(results)),
                       k, "Fallback phổ biến (thiếu tín hiệu)")
        return results
