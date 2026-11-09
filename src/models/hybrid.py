from dataclasses import replace

from src.models.base import Recommendation

REQUIRED_MODELS = ("svd", "item_cf", "content_based")
DEFAULT_RECOMMEND_WEIGHTS = {"svd": 0.5, "item_cf": 0.3, "content_based": 0.2}
DEFAULT_SIMILAR_WEIGHTS = {"item_cf": 0.4, "svd": 0.3, "content_based": 0.3}


class HybridRecommender:
    name = "hybrid"

    def __init__(
        self,
        models: dict,
        train_df,
        fallback=None,
        recommend_weights: dict | None = None,
        similar_weights: dict | None = None,
    ):
        missing = [key for key in REQUIRED_MODELS if key not in models]
        if missing:
            raise ValueError(f"Thiếu model: {', '.join(missing)}")
        self.models = {key: models[key] for key in REQUIRED_MODELS}
        self.known_users = set(map(int, train_df.user_id.unique()))
        self.seen = {
            int(user_id): set(map(int, rows.movie_id))
            for user_id, rows in train_df.groupby("user_id")
        }
        if fallback is None:
            fallback = getattr(self.models["svd"], "fallback", None)
        if fallback is None:
            raise ValueError("Hybrid cần fallback Popularity")
        self.fallback = fallback
        self.movie_id_to_index = getattr(
            self.models["item_cf"], "movie_id_to_index", {}
        )
        self.recommend_weights = self._prepare_weights(
            recommend_weights, DEFAULT_RECOMMEND_WEIGHTS
        )
        self.similar_weights = self._prepare_weights(
            similar_weights, DEFAULT_SIMILAR_WEIGHTS
        )

    def _prepare_weights(self, weights, defaults):
        if weights is None:
            weights = defaults
        if set(weights) != set(REQUIRED_MODELS):
            raise ValueError(
                "Trọng số phải có đủ key svd, item_cf, content_based"
            )
        values = [float(weights[key]) for key in REQUIRED_MODELS]
        if any(value < 0 for value in values):
            raise ValueError("Trọng số không được âm")
        total = sum(values)
        if total <= 0:
            raise ValueError("Tổng trọng số phải > 0")
        return {
            key: float(weights[key]) / total for key in REQUIRED_MODELS
        }

    def _normalize(self, values):
        if not values:
            return {}
        low = min(values.values())
        high = max(values.values())
        if high == low:
            return {key: 1.0 for key in values}
        return {
            key: (value - low) / (high - low)
            for key, value in values.items()
        }

    def _collect(self, results_by_model, weights, excluded):
        candidates = {}
        titles = {}
        for name, results in results_by_model.items():
            native = {}
            for item in results:
                movie_id = int(item.movie_id)
                titles.setdefault(movie_id, str(item.title))
                if item.method == name and movie_id not in excluded:
                    native[movie_id] = float(item.score)
            for movie_id, value in self._normalize(native).items():
                candidates[movie_id] = (
                    candidates.get(movie_id, 0.0) + weights[name] * value
                )
        return candidates, titles

    def _fill(self, results, candidates, k, reason):
        used = {item.movie_id for item in results}
        for item in candidates:
            if len(results) >= k:
                break
            if item.movie_id not in used:
                results.append(replace(item, method="popularity", reason=reason))
                used.add(item.movie_id)
        return results

    def recommend(
        self, user_id: int, k: int = 10, exclude_seen: bool = True
    ) -> list[Recommendation]:
        if k <= 0:
            return []
        user_id = int(user_id)
        if user_id not in self.known_users:
            return self.fallback.recommend(
                user_id, k=k, exclude_seen=exclude_seen
            )
        pool = max(50, k * 3)
        excluded = self.seen.get(user_id, set()) if exclude_seen else set()
        results_by_model = {
            name: self.models[name].recommend(
                user_id, k=pool, exclude_seen=exclude_seen
            )
            for name in REQUIRED_MODELS
        }
        candidates, titles = self._collect(
            results_by_model, self.recommend_weights, excluded
        )
        ranked = sorted(candidates.items(), key=lambda pair: (-pair[1], pair[0]))
        results = [
            Recommendation(
                movie_id=mid,
                title=titles.get(mid, str(mid)),
                score=score,
                method=self.name,
                reason="Kết hợp SVD + Item-CF + Content-Based",
            )
            for mid, score in ranked[:k]
        ]
        if len(results) < k:
            results = self._fill(
                results,
                self.fallback.recommend(
                    user_id, k=k + len(results), exclude_seen=exclude_seen
                ),
                k,
                "Fallback phổ biến (thiếu tín hiệu)",
            )
        return results

    def similar_items(self, movie_id: int, k: int = 10) -> list[Recommendation]:
        if self.movie_id_to_index and movie_id not in self.movie_id_to_index:
            raise ValueError(f"Movie {movie_id} không tồn tại")
        if k <= 0:
            return []
        pool = max(50, k * 3)
        results_by_model = {
            name: self.models[name].similar_items(movie_id, k=pool)
            for name in REQUIRED_MODELS
        }
        candidates, titles = self._collect(
            results_by_model, self.similar_weights, {movie_id}
        )
        ranked = sorted(candidates.items(), key=lambda pair: (-pair[1], pair[0]))
        results = [
            Recommendation(
                movie_id=mid,
                title=titles.get(mid, str(mid)),
                score=score,
                method=self.name,
                reason="Kết hợp độ tương đồng SVD + Item-CF + Content-Based",
            )
            for mid, score in ranked[:k]
        ]
        if len(results) < k:
            results = self._fill(
                results,
                self.fallback.similar_items(movie_id, k=k + len(results)),
                k,
                "Fallback phổ biến (thiếu tín hiệu)",
            )
        return results
