import numpy as np
import pandas as pd
import pytest

from src.models.content_based import KNOWN_GENRES, ContentBasedRecommender
from src.service.recommender_service import RecommenderService


@pytest.fixture
def inputs():
    movies = pd.DataFrame({"movie_id": [1, 2, 3, 4, 5, 6], "title": list("ABCDEF")})
    for genre in KNOWN_GENRES:
        movies[genre] = 0
    movies.loc[:2, "action"] = 1
    movies.loc[3:4, "comedy"] = 1
    train = pd.DataFrame({"user_id": [1, 1, 2, 2, 3, 3],
                          "movie_id": [1, 4, 2, 5, 3, 6],
                          "rating": [5, 1, 5, 4, 2, 3]})
    return train, movies


def test_similarity_order_and_self_exclusion(inputs):
    model = ContentBasedRecommender(*inputs)
    results = model.similar_items(1, k=2)
    assert [item.movie_id for item in results] == [2, 3]
    assert all(item.method == "content_based" and 0 <= item.score <= 1 for item in results)
    assert all(item.reason == "Cùng thể loại: Action" for item in results)
    np.testing.assert_allclose(model.similarity, model.similarity.T)
    assert model.genre_matrix.shape == (6, 18)


def test_recommend_profile_and_seen(inputs):
    model = ContentBasedRecommender(*inputs)
    assert [item.movie_id for item in model.recommend(1, k=2)] == [2, 3]
    assert model.recommend(1, k=1, exclude_seen=False)[0].movie_id == 1
    results = model.recommend(1, k=5)
    assert len({item.movie_id for item in results}) == len(results)
    assert not {1, 4}.intersection(item.movie_id for item in results)
    assert results[2].method == "popularity"


@pytest.mark.parametrize("user_id", [999999, 3])
def test_cold_start(inputs, user_id):
    results = ContentBasedRecommender(*inputs).recommend(user_id, k=3)
    assert len(results) == 3
    assert all(item.method == "popularity" for item in results)
    assert all(item.reason == "Fallback phổ biến (cold-start)" for item in results)


def test_zero_genre_and_invalid_movie(inputs):
    model = ContentBasedRecommender(*inputs)
    results = model.similar_items(6, k=3)
    assert len(results) == 3
    assert all(item.method == "popularity" and item.movie_id != 6 for item in results)
    with pytest.raises(ValueError, match="999"):
        model.similar_items(999)
    assert model.recommend(1, k=0) == []
    assert model.similar_items(1, k=-1) == []


def test_service_train_only_and_routing(inputs, tmp_path):
    train, movies = inputs
    train.to_parquet(tmp_path / "train.parquet")
    movies.to_parquet(tmp_path / "movies.parquet")
    pd.DataFrame({"user_id": [1], "age": [20], "gender": ["M"],
                  "occupation": ["student"]}).to_parquet(tmp_path / "users.parquet")
    train.assign(rating=1).to_parquet(tmp_path / "ratings.parquet")
    service = RecommenderService(data_dir=tmp_path)
    assert service.get_user_profile(1)["avg_rating"] == 3
    assert service.recommend(1, method="content_based", k=1)[0].movie_id == 2
    assert service.similar_items(1, k=1)[0].movie_id == 2
    with pytest.raises(ValueError, match="Day 4"):
        service.similar_items(1, method="invalid")
    with pytest.raises(ValueError, match="Day 4"):
        service.recommend(1, method="invalid")
