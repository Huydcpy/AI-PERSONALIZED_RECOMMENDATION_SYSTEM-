import numpy as np
import pandas as pd
import pytest

from src.models.item_cf import ItemCFRecommender


@pytest.fixture
def model():
    train = pd.DataFrame([
        (1, 1, 5), (1, 2, 5), (1, 3, 1),
        (2, 1, 4), (2, 2, 4), (2, 3, 2),
        (3, 1, 5), (3, 3, 1),
        (4, 4, 3), (4, 3, 3),
    ], columns=["user_id", "movie_id", "rating"])
    movies = pd.DataFrame({"movie_id": [1, 2, 3, 4, 5], "title": list("ABCDE")})
    return ItemCFRecommender(train, movies)


def test_adjusted_cosine_and_neighbor_limit(model):
    assert model.similarity[0, 1] == pytest.approx(np.sqrt(5 / 14))
    assert model.similarity[0, 2] == 0
    assert np.all(np.diag(model.similarity) == 0)
    assert np.all(model.similarity[4] == 0)
    assert model.user_mean[1] == pytest.approx(11 / 3)
    limited = ItemCFRecommender(model.fallback.train_df, model.movies_df, k_neighbors=1)
    assert np.all(np.count_nonzero(limited.similarity, axis=1) <= 1)


def test_similar_items_and_invalid_inputs(model):
    result = model.similar_items(1, k=1)
    assert result[0].movie_id == 2
    assert result[0].method == "item_cf"
    assert 0 < result[0].score <= 1
    assert all(item.movie_id != 1 for item in model.similar_items(1))
    assert model.similar_items(1, k=0) == []
    with pytest.raises(ValueError, match="không tồn tại"):
        model.similar_items(999)


def test_recommendation_prediction_and_exclusion(model):
    result = model.recommend(3, k=1)
    assert result[0].movie_id == 2
    assert result[0].method == "item_cf"
    assert result[0].score == pytest.approx(5)
    assert all(item.movie_id not in {1, 3} for item in model.recommend(3))
    assert all(1 <= item.score <= 5 for item in model.recommend(3))
    assert model.recommend(3) == model.recommend(3)
    assert model.recommend(3, k=-1) == []
    assert any(item.movie_id in {1, 3} for item in model.recommend(3, exclude_seen=False))


def test_fallback_reasons(model):
    assert all(item.method == "popularity" and "cold-start" in item.reason
               for item in model.recommend(999, k=3))
    assert all(item.method == "popularity" and "thiếu tín hiệu" in item.reason
               for item in model.similar_items(5, k=3))
    assert all(item.method == "popularity" for item in model.recommend(4, k=2))


def test_ties_use_movie_id(model):
    model.similarity[0] = [0, 0.5, 0.5, 0, 0]
    assert [item.movie_id for item in model.similar_items(1, k=2)] == [2, 3]


def test_empty_train_and_catalog_only_movie(model):
    empty = model.fallback.train_df.iloc[:0]
    cold = ItemCFRecommender(empty, model.movies_df)
    assert cold.global_mean == 3.0
    assert cold.recommend(1) == []
    assert cold.similar_items(1) == []


def test_fit_and_scores_do_not_depend_on_input_order(model):
    shuffled = ItemCFRecommender(
        model.fallback.train_df.sample(frac=1, random_state=42),
        model.movies_df.sample(frac=1, random_state=42),
    )
    np.testing.assert_allclose(model.similarity, shuffled.similarity)
    assert shuffled.recommend(3) == model.recommend(3)
