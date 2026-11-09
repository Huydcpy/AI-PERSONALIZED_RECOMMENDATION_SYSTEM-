import numpy as np
import pandas as pd
import pytest

from src.models.popularity import PopularityRecommender
from src.models.svd import SVDRecommender

TRAIN = pd.DataFrame(
    {
        "user_id": [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6],
        "movie_id": [1, 2, 3, 4, 1, 2, 5, 6, 1, 3, 5, 7, 2, 4, 6, 8, 3, 4, 7, 9, 1, 2, 8, 9],
        "rating": [5, 4, 3, 5, 4, 5, 2, 3, 3, 4, 5, 2, 2, 3, 4, 5, 4, 5, 3, 4, 5, 2, 4, 3],
    }
)
MOVIES = pd.DataFrame(
    {
        "movie_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "title": [f"Movie {index}" for index in range(1, 11)],
    }
)


def build_model(**kwargs):
    fallback = PopularityRecommender(TRAIN, MOVIES)
    params = {"n_factors": 2, "n_epochs": 2, "random_state": 42}
    params.update(kwargs)
    return SVDRecommender(TRAIN, MOVIES, fallback=fallback, **params)


def test_recommend_returns_native_results_and_excludes_seen():
    model = build_model()
    results = model.recommend(1, k=3, exclude_seen=True)
    assert len(results) == 3
    seen = {1, 2, 3, 4}
    assert not seen.intersection(item.movie_id for item in results)
    assert any(item.method == "svd" for item in results)
    for item in results:
        assert item.method in {"svd", "popularity"}
        assert 1 <= item.score <= 5
        assert item.reason


def test_recommend_include_seen_when_disabled():
    model = build_model()
    results = model.recommend(1, k=9, exclude_seen=False)
    assert {1, 2, 3, 4}.intersection(item.movie_id for item in results)


def test_unknown_user_falls_back_to_popularity():
    model = build_model()
    results = model.recommend(999, k=3)
    assert len(results) == 3
    assert all(item.method == "popularity" for item in results)
    assert all("Fallback" in item.reason for item in results)


def test_similar_items_excludes_self_and_respects_k():
    model = build_model()
    results = model.similar_items(1, k=3)
    assert len(results) == 3
    assert all(item.movie_id != 1 for item in results)
    assert all(item.reason for item in results)
    for item in results:
        if item.method == "svd":
            assert 0 < item.score <= 1
        else:
            assert item.method == "popularity"


def test_zero_interaction_movie_falls_back():
    model = build_model()
    results = model.similar_items(10, k=3)
    assert len(results) == 3
    assert all(item.method == "popularity" for item in results)
    assert all("Fallback" in item.reason for item in results)


def test_unknown_movie_raises():
    model = build_model()
    with pytest.raises(ValueError, match="không tồn tại"):
        model.similar_items(999, k=3)


def test_non_positive_k_returns_empty():
    model = build_model()
    assert model.recommend(1, k=0) == []
    assert model.recommend(1, k=-1) == []
    assert model.similar_items(1, k=0) == []
    assert model.similar_items(1, k=-1) == []


def test_predict_rating_is_clipped():
    model = build_model()
    for user_id, movie_id in ((1, 1), (1, 5), (999, 1), (1, 999)):
        value = model.predict_rating(user_id, movie_id)
        assert isinstance(value, float)
        assert 1 <= value <= 5


def test_scores_are_deterministic():
    first = build_model().recommend(2, k=3)
    second = build_model().recommend(2, k=3)
    assert [(item.movie_id, round(item.score, 8)) for item in first] == [
        (item.movie_id, round(item.score, 8)) for item in second
    ]


def test_vectorized_scores_match_surprise():
    model = build_model()
    for user_id, movie_id in ((1, 5), (2, 6), (3, 7), (4, 8), (5, 9)):
        index = model.movie_id_to_index[movie_id]
        vectorized = float(np.clip(model._score_user(user_id)[index], 1, 5))
        expected = float(np.clip(model.algo.predict(user_id, movie_id).est, 1, 5))
        assert vectorized == pytest.approx(expected, abs=1e-6)


def test_similar_items_native_results_sorted_by_score_then_movie_id():
    model = build_model()
    results = model.similar_items(1, k=9)
    native = [
        (item.score, item.movie_id)
        for item in results
        if item.method == "svd"
    ]
    assert native == sorted(native, key=lambda pair: (-pair[0], pair[1]))
    assert len({item.movie_id for item in results}) == len(results)
