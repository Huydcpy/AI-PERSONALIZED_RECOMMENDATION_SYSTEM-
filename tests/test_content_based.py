import pandas as pd
import pytest

from src.models.base import Recommendation
from src.models.content_based import GENRES, ContentBasedRecommender
from src.models.popularity import PopularityRecommender

MOVIE_SPECS = [
    (1, "Action One", ("action",)),
    (2, "Action Two", ("action",)),
    (3, "Comedy One", ("comedy",)),
    (4, "Romantic Comedy", ("comedy", "romance")),
    (5, "No Genre", ()),
    (6, "Drama One", ("drama",)),
    (7, "Horror One", ("horror",)),
    (8, "Action Adventure", ("action", "adventure")),
]


def make_movies() -> pd.DataFrame:
    data = {"movie_id": [], "title": []}
    for genre in GENRES:
        data[genre] = []

    for movie_id, title, genres in MOVIE_SPECS:
        data["movie_id"].append(movie_id)
        data["title"].append(title)
        for genre in GENRES:
            data[genre].append(1 if genre in genres else 0)

    return pd.DataFrame(data)


def make_train() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "user_id": [1, 1, 2, 3, 4, 5, 6],
            "movie_id": [1, 3, 3, 5, 7, 1, 4],
            "rating": [5.0, 2.0, 5.0, 5.0, 5.0, 3.0, 4.0],
        }
    )


def make_model() -> ContentBasedRecommender:
    train = make_train()
    movies = make_movies()
    fallback = PopularityRecommender(train, movies)
    return ContentBasedRecommender(train, movies, fallback=fallback)


def test_similar_items_returns_same_genre_first():
    model = make_model()
    recs = model.similar_items(1, k=2)

    assert [rec.movie_id for rec in recs] == [2, 8]
    assert all(rec.method == "content_based" for rec in recs)
    assert all("Cùng thể loại: Action" in rec.reason for rec in recs)


def test_similar_items_excludes_itself_and_respects_k():
    model = make_model()
    recs = model.similar_items(8, k=1)

    assert len(recs) == 1
    assert recs[0].movie_id != 8


def test_similar_items_unknown_movie_raises():
    model = make_model()
    with pytest.raises(ValueError, match="không tồn tại"):
        model.similar_items(999, k=5)


def test_similar_items_without_genre_falls_back():
    model = make_model()
    recs = model.similar_items(5, k=3)

    assert recs
    assert all(rec.method == "popularity" for rec in recs)
    assert all("Fallback phổ biến" in rec.reason for rec in recs)


def test_recommend_excludes_seen_movies():
    model = make_model()
    recs = model.recommend(1, k=2, exclude_seen=True)

    assert {rec.movie_id for rec in recs} == {2, 8}
    assert 1 not in {rec.movie_id for rec in recs}
    assert 3 not in {rec.movie_id for rec in recs}


def test_recommend_can_include_seen_movies():
    model = make_model()
    recs = model.recommend(1, k=10, exclude_seen=False)

    assert 1 in {rec.movie_id for rec in recs}


def test_recommend_unknown_user_falls_back():
    model = make_model()
    recs = model.recommend(999, k=3)

    assert len(recs) == 3
    assert all(isinstance(rec, Recommendation) for rec in recs)
    assert all(rec.method == "popularity" for rec in recs)
    assert all(rec.reason == "Fallback phổ biến (cold-start)" for rec in recs)


def test_recommend_low_ratings_fall_back():
    model = make_model()
    recs = model.recommend(5, k=3)

    assert recs
    assert all(rec.method == "popularity" for rec in recs)


def test_recommend_user_without_genre_falls_back():
    model = make_model()
    recs = model.recommend(3, k=3)

    assert recs
    assert all(rec.method == "popularity" for rec in recs)


def test_recommend_is_deterministic_for_equal_scores():
    model = make_model()
    first = model.recommend(1, k=2)
    second = model.recommend(1, k=2)

    assert [rec.movie_id for rec in first] == [rec.movie_id for rec in second]
    assert [rec.movie_id for rec in first] == [2, 8]


def test_scores_are_within_unit_interval():
    model = make_model()
    recs = model.recommend(1, k=2) + model.similar_items(4, k=10)

    assert recs
    assert all(0.0 <= rec.score <= 1.0 for rec in recs if rec.method == "content_based")


def test_content_based_method_and_reason():
    model = make_model()
    recs = model.recommend(1, k=1)

    assert recs[0].method == "content_based"
    assert recs[0].reason.startswith("Khớp thể loại:")
