"""Base contract for recommenders."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import pandas as pd


@dataclass
class Recommendation:
    movie_id: int
    title: str
    score: float
    method: str
    reason: str | None = None


@runtime_checkable
class Recommender(Protocol):
    """Protocol for recommender models.

    Implementations must provide:
    - name: str
    - recommend(user_id, k=10, exclude_seen=True) -> list[Recommendation]
    - similar_items(movie_id, k=10) -> list[Recommendation]
    """

    name: str

    def recommend(
        self, user_id: int, k: int = 10, exclude_seen: bool = True
    ) -> list[Recommendation]: ...

    def similar_items(self, movie_id: int, k: int = 10) -> list[Recommendation]: ...

    def fit(self, ratings_df: pd.DataFrame, items_df: pd.DataFrame | None = None) -> None: ...
