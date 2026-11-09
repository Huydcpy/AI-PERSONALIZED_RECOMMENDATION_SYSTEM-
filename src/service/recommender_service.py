"""Service layer cho ứng dụng gợi ý phim."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.models.base import Recommendation

GENRES = (
    "unknown",
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


def _to_python(value):
    return value.item() if hasattr(value, "item") else value


class RecommenderService:
    """Điểm truy cập duy nhất cho UI, không phụ thuộc Streamlit."""

    def __init__(
        self,
        data_dir: str = "data/processed",
        metrics_dir: str = "reports/metrics",
    ):
        self.data_dir = Path(data_dir)
        self.metrics_dir = Path(metrics_dir)

        self.ratings_df = self._load_parquet("ratings")
        self.movies_df = self._load_parquet("movies")
        self.users_df = self._load_parquet("users")
        self.train_df = self._load_parquet("train")
        self.test_df = self._load_parquet("test")

        self.models: dict[str, object] = {}
        self._init_models()

    def _load_parquet(self, name: str) -> pd.DataFrame | None:
        path = self.data_dir / f"{name}.parquet"
        if not path.exists():
            return None
        return pd.read_parquet(path)

    def _init_models(self) -> None:
        if self.train_df is None or self.movies_df is None:
            return

        popularity = None
        try:
            from src.models.popularity import PopularityRecommender

            popularity = PopularityRecommender(self.train_df, self.movies_df)
            self.models["popularity"] = popularity
        except ImportError:
            pass

        try:
            from src.models.content_based import ContentBasedRecommender

            self.models["content_based"] = ContentBasedRecommender(
                self.train_df, self.movies_df, fallback=popularity
            )
        except ImportError:
            pass

        from src.models.item_cf import ItemCFRecommender

        self.models["item_cf"] = ItemCFRecommender(
            self.train_df, self.movies_df, fallback=popularity
        )

        svd = None
        try:
            from src.models.svd import SVDRecommender

            svd = SVDRecommender(
                self.train_df, self.movies_df, fallback=popularity
            )
            self.models["svd"] = svd
        except ImportError:
            pass

        if svd is not None:
            components = {
                key: self.models.get(key)
                for key in ("svd", "item_cf", "content_based")
            }
            if all(components.values()):
                try:
                    from src.models.hybrid import HybridRecommender

                    self.models["hybrid"] = HybridRecommender(
                        components,
                        self.train_df,
                        fallback=popularity,
                    )
                except ImportError:
                    pass

    def list_users(self) -> list[int]:
        """Trả về danh sách user_id có trong dữ liệu."""
        if self.users_df is None:
            return []
        return sorted(int(uid) for uid in self.users_df["user_id"].unique())

    def get_user_profile(self, user_id: int) -> dict:
        """Trả về thông tin nhân khẩu học và sở thích của người dùng."""
        if self.users_df is None:
            raise RuntimeError("Dữ liệu người dùng chưa được xử lý")
        user_rows = self.users_df[self.users_df["user_id"] == user_id]
        if user_rows.empty:
            raise ValueError(f"User {user_id} không tồn tại")
        user = user_rows.iloc[0]

        user_ratings = pd.DataFrame()
        if self.train_df is not None:
            user_ratings = self.train_df[
                self.train_df["user_id"] == user_id
            ]

        return {
            "user_id": int(user_id),
            "age": int(user["age"]),
            "gender": str(user["gender"]),
            "occupation": str(user["occupation"]),
            "n_ratings": len(user_ratings),
            "avg_rating": (
                float(user_ratings["rating"].mean())
                if not user_ratings.empty
                else None
            ),
            "top_genres": self._top_genres(user_ratings),
            "recent_ratings": self._recent_ratings(user_ratings),
        }

    def _top_genres(self, user_ratings: pd.DataFrame) -> list[dict]:
        if user_ratings.empty or self.movies_df is None:
            return []
        genre_cols = [g for g in GENRES if g in self.movies_df.columns]
        if not genre_cols:
            return []

        merged = user_ratings.merge(
            self.movies_df[["movie_id", *genre_cols]],
            on="movie_id",
            how="inner",
        )
        stats = []
        for genre in genre_cols:
            subset = merged[merged[genre] == 1]
            if subset.empty:
                continue
            stats.append(
                {
                    "genre": genre,
                    "count": len(subset),
                    "avg_rating": float(subset["rating"].mean()),
                }
            )
        stats.sort(
            key=lambda item: (
                -item["count"],
                -item["avg_rating"],
                item["genre"],
            )
        )
        return stats[:5]

    def _recent_ratings(self, user_ratings: pd.DataFrame) -> list[dict]:
        if user_ratings.empty:
            return []

        recent = user_ratings
        if "timestamp" in recent.columns:
            recent = recent.sort_values("timestamp", ascending=False)
        recent = recent.head(10)

        if self.movies_df is not None:
            recent = recent.merge(
                self.movies_df[["movie_id", "title"]],
                on="movie_id",
                how="left",
            )

        columns = [
            column
            for column in ("movie_id", "title", "rating", "timestamp")
            if column in recent.columns
        ]
        return [
            {key: _to_python(value) for key, value in row.items()}
            for row in recent[columns].to_dict("records")
        ]

    def get_movie(self, movie_id: int) -> dict:
        """Trả về thông tin của một bộ phim."""
        if self.movies_df is None:
            raise RuntimeError("Dữ liệu phim chưa được xử lý")
        rows = self.movies_df[self.movies_df["movie_id"] == movie_id]
        if rows.empty:
            raise ValueError(f"Movie {movie_id} không tồn tại")
        return {
            key: _to_python(value)
            for key, value in rows.iloc[0].to_dict().items()
        }

    def search_movies(self, query: str, limit: int = 20) -> list[dict]:
        """Tìm phim theo tiêu đề, không phân biệt hoa thường."""
        if self.movies_df is None or not query or not query.strip():
            return []

        mask = self.movies_df["title"].str.contains(
            query.strip(), case=False, na=False, regex=False
        )
        rows = self.movies_df[mask].head(limit)
        return [
            {key: _to_python(value) for key, value in row.items()}
            for row in rows.to_dict("records")
        ]

    def _resolve_model(self, method: str):
        model = self.models.get(method)
        if model is not None:
            return model
        if method == "content_based":
            model = self.models.get("popularity")
            if model is None:
                raise RuntimeError(
                    "ContentBasedRecommender chưa sẵn sàng: "
                    "thiếu model hoặc dữ liệu train/movies"
                )
            return model
        if method == "popularity":
            raise RuntimeError(
                "PopularityRecommender chưa sẵn sàng: "
                "thiếu model hoặc dữ liệu train/movies"
            )
        if method == "item_cf":
            raise RuntimeError(
                "ItemCFRecommender chưa sẵn sàng: "
                "thiếu dữ liệu train/movies"
            )
        if method == "svd":
            raise RuntimeError(
                "SVDRecommender chưa sẵn sàng: "
                "thiếu model hoặc dữ liệu train/movies"
            )
        if method == "hybrid":
            raise RuntimeError(
                "HybridRecommender chưa sẵn sàng: "
                "thiếu model hoặc dữ liệu train/movies"
            )
        raise ValueError(f"Method {method} không được hỗ trợ")

    def recommend(
        self,
        user_id: int,
        method: str = "popularity",
        k: int = 10,
        exclude_seen: bool = True,
    ) -> list[Recommendation]:
        """Gợi ý top-k phim cho người dùng bằng phương pháp đã chọn."""
        model = self._resolve_model(method)
        return model.recommend(
            user_id=user_id, k=k, exclude_seen=exclude_seen
        )

    def similar_items(
        self,
        movie_id: int,
        k: int = 10,
        method: str = "content_based",
    ) -> list[Recommendation]:
        """Gợi ý các phim tương tự với một bộ phim."""
        model = self._resolve_model(method)
        self.get_movie(movie_id)
        return model.similar_items(movie_id=movie_id, k=k)

    def get_baseline_metrics(self) -> dict:
        """Đọc kết quả đánh giá baseline, trả về {} nếu chưa có."""
        path = self.metrics_dir / "baseline.json"
        if not path.exists():
            return {}
        with path.open(encoding="utf-8") as file:
            return json.load(file)

    def get_ranking_metrics(self) -> dict:
        path = self.metrics_dir / "ranking.json"
        if not path.exists():
            return {}
        with path.open(encoding="utf-8") as file:
            return json.load(file)

    def get_svd_metrics(self) -> dict:
        path = self.metrics_dir / "svd.json"
        if not path.exists():
            return {}
        with path.open(encoding="utf-8") as file:
            return json.load(file)
