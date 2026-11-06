import pandas as pd
import pytest

from src.models.base import Recommendation
from src.models.popularity import PopularityRecommender


def make_model():
    train = pd.DataFrame(
        {
            "user_id": [1, 1, 2, 2, 2],
            "movie_id": [1, 2, 1, 2, 3],
            "rating": [5.0, 2.0, 4.0, 3.0, 5.0],
        }
    )
    movies = pd.DataFrame(
        {
            "movie_id": [1, 2, 3],
            "title": ["A", "B", "C"],
        }
    )
    return PopularityRecommender(train, movies)


def test_predict_rating_falls_back_to_global_mean():
    model = make_model()
    assert model.predict_rating(1, 999) == pytest.approx(3.8)


def test_recommend_excludes_seen_movies():
    model = make_model()
    recs = model.recommend(1, k=10, exclude_seen=True)
    assert {rec.movie_id for rec in recs} == {3}


def test_recommend_unknown_user_does_not_crash():
    model = make_model()
    recs = model.recommend(999, k=2)
    assert len(recs) == 2
    assert all(isinstance(rec, Recommendation) for rec in recs)


def test_recommend_include_seen_movies():
    model = make_model()
    recs = model.recommend(1, k=3, exclude_seen=False)
    assert any(rec.movie_id == 1 for rec in recs)


def test_similar_items_excludes_itself():
    model = make_model()
    recs = model.similar_items(1, k=10)
    assert recs
    assert all(rec.movie_id != 1 for rec in recs)


@pytest.mark.parametrize("k", [0, -1, -10])
def test_nonpositive_k_returns_no_recommendations(k):
    model = make_model()
    assert model.recommend(1, k=k) == []
    assert model.similar_items(1, k=k) == []
