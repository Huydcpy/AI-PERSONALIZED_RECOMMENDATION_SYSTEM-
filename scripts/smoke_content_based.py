import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.preprocess import GENRES
from src.service.recommender_service import RecommenderService


def main():
    service = RecommenderService()
    movies, train = service.movies_df, service.train_df
    assert movies is not None and train is not None, "Run the data pipeline first"
    assert len(movies) == 1682
    assert set(GENRES).issubset(movies.columns)
    assert movies[GENRES].isin([0, 1]).all().all()
    known = [genre for genre in GENRES if genre != "unknown"]
    zero = movies[movies[known].sum(axis=1) == 0]
    report = {
        "movie_count": len(movies),
        "genre_counts": {g: int(movies[g].sum()) for g in GENRES},
        "unknown_ratio": float(movies.unknown.mean()),
        "zero_genre_movies": zero[["movie_id", "title"]].to_dict("records"),
        "users": {}, "similar": {},
    }
    for uid in (1, 196, 405):
        results = service.recommend(uid, method="content_based", k=10)
        seen = set(train.loc[train.user_id == uid, "movie_id"])
        assert len(results) == 10
        assert not seen.intersection(item.movie_id for item in results)
        assert all(item.method == "content_based" and 0 < item.score <= 1 for item in results)
        report["users"][str(uid)] = [vars(item) for item in results[:5]]
    for title in ("Toy Story (1995)", "Star Wars (1977)", "Pulp Fiction (1994)"):
        source = movies[movies.title == title].iloc[0]
        results = service.similar_items(int(source.movie_id), k=5)
        assert len(results) == 5
        for item in results:
            target = service.get_movie(item.movie_id)
            assert item.movie_id != int(source.movie_id)
            assert item.method == "content_based" and 0 < item.score <= 1
            assert any(source[g] == 1 and target[g] == 1 for g in known)
        report["similar"][title] = {
            "movie_id": int(source.movie_id),
            "genres": [g for g in known if source[g] == 1],
            "results": [vars(item) for item in results],
        }
    fallback = service.recommend(999999, method="content_based", k=5)
    assert len(fallback) == 5
    assert all(item.method == "popularity" and "Fallback" in item.reason for item in fallback)
    for mid in zero.movie_id:
        results = service.similar_items(int(mid), k=5)
        assert len(results) == 5
        assert all(item.method == "popularity" and item.movie_id != mid for item in results)
    report["fallback_checks"] = "passed"
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
