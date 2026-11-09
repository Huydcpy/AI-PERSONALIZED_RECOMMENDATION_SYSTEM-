import pandas as pd
import pytest

from src.models.base import Recommendation
from src.models.hybrid import HybridRecommender

TRAIN = pd.DataFrame(
    {
        "user_id": [1, 1, 2, 2],
        "movie_id": [1, 2, 1, 3],
        "rating": [5, 4, 4, 3],
    }
)
CATALOG = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4}


class FakeModel:
    def __init__(
        self,
        name,
        recommend_items=None,
        similar_items=None,
        catalog=None,
        extra_recommend=None,
    ):
        self.name = name
        self.recommend_items = recommend_items or []
        self.similar_data = similar_items or {}
        self.movie_id_to_index = catalog or {}
        self.extra_recommend = extra_recommend or []
        self.recommend_calls = []
        self.similar_calls = []

    def recommend(self, user_id, k=10, exclude_seen=True):
        self.recommend_calls.append((user_id, k, exclude_seen))
        results = [
            Recommendation(mid, f"Movie {mid}", score, self.name, "native")
            for mid, score in self.recommend_items
        ]
        results += [
            Recommendation(mid, f"Movie {mid}", score, "popularity", "Fallback")
            for mid, score in self.extra_recommend
        ]
        return results[:k]

    def similar_items(self, movie_id, k=10):
        self.similar_calls.append((movie_id, k))
        return [
            Recommendation(mid, f"Movie {mid}", score, self.name, "native")
            for mid, score in self.similar_data.get(movie_id, [])
        ][:k]


class FakeFallback:
    name = "popularity"

    def __init__(self, start=100):
        self.start = start
        self.recommend_calls = []
        self.similar_calls = []

    def recommend(self, user_id, k=10, exclude_seen=True):
        self.recommend_calls.append((user_id, k, exclude_seen))
        return [
            Recommendation(
                self.start + index,
                f"Movie {self.start + index}",
                4.5,
                "popularity",
                "Phổ biến",
            )
            for index in range(k)
        ]

    def similar_items(self, movie_id, k=10):
        self.similar_calls.append((movie_id, k))
        return [
            Recommendation(
                self.start + index,
                f"Movie {self.start + index}",
                4.5,
                "popularity",
                "Phổ biến",
            )
            for index in range(k)
        ]


def build_models():
    return {
        "svd": FakeModel("svd", [(1, 10.0), (2, 5.0)], catalog=CATALOG),
        "item_cf": FakeModel("item_cf", [(1, 0.9), (3, 0.1)], catalog=CATALOG),
        "content_based": FakeModel("content_based", [(2, 0.2), (3, 0.1)]),
    }


def build_hybrid(models=None, fallback=None, **kwargs):
    return HybridRecommender(
        models or build_models(),
        TRAIN,
        fallback=fallback or FakeFallback(),
        **kwargs,
    )


def test_default_weights_are_normalized():
    model = build_hybrid()
    assert model.recommend_weights == {
        "svd": 0.5,
        "item_cf": 0.3,
        "content_based": 0.2,
    }
    assert model.similar_weights == {
        "svd": 0.3,
        "item_cf": 0.4,
        "content_based": 0.3,
    }


def test_custom_weights_are_normalized():
    model = build_hybrid(
        recommend_weights={"svd": 2, "item_cf": 1, "content_based": 1}
    )
    assert model.recommend_weights == {
        "svd": 0.5,
        "item_cf": 0.25,
        "content_based": 0.25,
    }


@pytest.mark.parametrize(
    "weights",
    [
        {"svd": 1.0, "item_cf": 0.0},
        {"svd": 1.0, "item_cf": 0.0, "content_based": 0.0, "extra": 0.0},
        {"svd": -1.0, "item_cf": 1.0, "content_based": 1.0},
        {"svd": 0.0, "item_cf": 0.0, "content_based": 0.0},
    ],
)
def test_invalid_weights_raise(weights):
    with pytest.raises(ValueError):
        build_hybrid(recommend_weights=weights)


def test_blend_matches_expected_scores():
    results = build_hybrid().recommend(1, k=3, exclude_seen=False)
    assert [item.movie_id for item in results] == [1, 2, 3]
    assert [round(item.score, 8) for item in results] == [0.8, 0.2, 0.0]
    assert all(item.method == "hybrid" for item in results)
    assert all("Kết hợp" in item.reason for item in results)


def test_component_fallback_items_are_not_blended():
    models = build_models()
    models["svd"] = FakeModel(
        "svd",
        [(1, 10.0), (2, 5.0)],
        catalog=CATALOG,
        extra_recommend=[(5, 99.0)],
    )
    results = build_hybrid(models=models).recommend(1, k=3, exclude_seen=False)
    assert 5 not in {item.movie_id for item in results}


def test_single_item_component_normalizes_to_one():
    models = {
        "svd": FakeModel("svd", [(1, 3.0)], catalog=CATALOG),
        "item_cf": FakeModel("item_cf", [(2, 0.1)], catalog=CATALOG),
        "content_based": FakeModel("content_based", [(3, 0.9)]),
    }
    results = build_hybrid(models=models).recommend(1, k=3, exclude_seen=False)
    assert [item.movie_id for item in results] == [1, 2, 3]
    assert [round(item.score, 8) for item in results] == [0.5, 0.3, 0.2]


def test_exclude_seen_and_unknown_user():
    model = build_hybrid()
    results = model.recommend(1, k=5, exclude_seen=True)
    seen = {1, 2}
    assert not seen.intersection(item.movie_id for item in results)
    assert len([item for item in results if item.method == "popularity"]) == 4

    fallback = FakeFallback()
    models = build_models()
    cold = build_hybrid(models=models, fallback=fallback)
    results = cold.recommend(999, k=3)
    assert all(item.method == "popularity" for item in results)
    assert all(item.reason == "Fallback phổ biến (cold-start)" for item in results)
    assert fallback.recommend_calls == [(999, 3, True)]
    assert all(not model.recommend_calls for model in models.values())


def test_insufficient_candidates_fill_popularity():
    models = {
        "svd": FakeModel("svd", [(1, 3.0)], catalog=CATALOG),
        "item_cf": FakeModel("item_cf", [(2, 0.1)], catalog=CATALOG),
        "content_based": FakeModel("content_based", [(3, 0.9)]),
    }
    fallback = FakeFallback()
    results = build_hybrid(models=models, fallback=fallback).recommend(
        1, k=5, exclude_seen=False
    )
    assert len(results) == 5
    native = [item for item in results if item.method == "hybrid"]
    filled = [item for item in results if item.method == "popularity"]
    assert len(native) == 3
    assert len(filled) == 2
    assert all("thiếu tín hiệu" in item.reason for item in filled)


def test_similar_items_blend_and_exclude_self():
    models = {
        "svd": FakeModel(
            "svd",
            similar_items={1: [(1, 100.0), (3, 0.9), (2, 0.1)]},
            catalog=CATALOG,
        ),
        "item_cf": FakeModel(
            "item_cf",
            similar_items={1: [(4, 0.8), (3, 0.2)]},
            catalog=CATALOG,
        ),
        "content_based": FakeModel(
            "content_based",
            similar_items={1: [(2, 0.6), (4, 0.3)]},
        ),
    }
    results = build_hybrid(models=models).similar_items(1, k=3)
    assert [item.movie_id for item in results] == [4, 2, 3]
    assert [round(item.score, 8) for item in results] == [0.4, 0.3, 0.3]
    assert all(item.method == "hybrid" for item in results)
    assert all("tương đồng" in item.reason for item in results)


def test_unknown_movie_raises():
    model = build_hybrid()
    with pytest.raises(ValueError, match="không tồn tại"):
        model.similar_items(999, k=3)


def test_non_positive_k_returns_empty():
    model = build_hybrid()
    assert model.recommend(1, k=0) == []
    assert model.recommend(1, k=-1) == []
    assert model.similar_items(1, k=0) == []
    assert model.similar_items(1, k=-1) == []


def test_missing_models_raise():
    models = build_models()
    del models["content_based"]
    with pytest.raises(ValueError, match="Thiếu model"):
        build_hybrid(models=models)


def test_missing_fallback_raises():
    models = build_models()
    models["svd"].fallback = None
    with pytest.raises(ValueError, match="fallback"):
        HybridRecommender(models, TRAIN, fallback=None)


def test_tie_break_is_deterministic():
    models = {
        "svd": FakeModel("svd", [(1, 10.0), (2, 5.0)], catalog=CATALOG),
        "item_cf": FakeModel("item_cf", [(1, 0.9), (3, 0.1)], catalog=CATALOG),
        "content_based": FakeModel("content_based", [(2, 0.2), (3, 0.1)]),
    }
    first = build_hybrid(models=models).recommend(1, k=4, exclude_seen=False)
    second = build_hybrid(models=models).recommend(1, k=4, exclude_seen=False)
    assert [item.movie_id for item in first] == [item.movie_id for item in second]
    assert [item.score for item in first] == [item.score for item in second]
