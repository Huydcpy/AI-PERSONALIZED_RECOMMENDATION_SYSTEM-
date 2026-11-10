import argparse
import json
import math
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.service.recommender_service import RecommenderService


def check(condition, message):
    if not condition:
        raise ValueError(message)


def check_results(service, results, k, method, excluded=(), fallback=False, similar=False):
    ids = [item.movie_id for item in results]
    check(len(ids) == k and len(set(ids)) == len(ids), "Wrong result count or duplicates")
    check(not set(ids).intersection(excluded), "Excluded movie returned")
    for item in results:
        service.get_movie(item.movie_id)
        check(math.isfinite(item.score), "Non-finite score")
        check(item.method in (method, "popularity"), "Unexpected method")
        check(bool(item.reason), "Missing reason")
        if item.method == "popularity":
            check("Fallback" in item.reason, "Missing fallback explanation")
        if fallback:
            check(item.method == "popularity", "Expected Popularity fallback")
        if item.method == "popularity":
            check(1 <= item.score <= 5, "Fallback rating outside [1, 5]")
        elif method == "hybrid":
            check(0 <= item.score <= 1, "Hybrid score outside [0, 1]")
        elif similar:
            check(0 < item.score <= 1, "Similarity outside (0, 1]")
        else:
            check(1 <= item.score <= 5, "Rating score outside [1, 5]")


def smoke(data_dir):
    service = RecommenderService(data_dir=data_dir)
    check(all(name in service.models for name in ("svd", "hybrid")), "SVD/Hybrid not registered")
    train, movies = service.train_df, service.movies_df
    check(train is not None and movies is not None, "Run the data pipeline first")
    report = {"users": {}, "similar": {}}
    for method in ("svd", "hybrid"):
        report["users"][method] = {}
        report["similar"][method] = {}
        for uid in (1, 196, 405):
            seen = set(train.loc[train.user_id == uid, "movie_id"])
            results = service.recommend(uid, method=method, k=10, exclude_seen=True)
            check_results(service, results, 10, method, excluded=seen)
            check(any(item.method == method for item in results), "All results are fallback")
            check(results == service.recommend(uid, method=method, k=10), "Unstable recommendations")
            report["users"][method][str(uid)] = [vars(item) for item in results[:5]]
        for mid in (1, 50, 56):
            results = service.similar_items(mid, k=5, method=method)
            check_results(service, results, 5, method, excluded={mid}, similar=True)
            check(any(item.method == method for item in results), "All similar items are fallback")
            check(results == service.similar_items(mid, k=5, method=method), "Unstable similarity")
            report["similar"][method][str(mid)] = [vars(item) for item in results]
        check_results(service, service.recommend(999999, method=method, k=5), 5, method, fallback=True)
        try:
            service.similar_items(int(movies.movie_id.max()) + 1, method=method)
        except ValueError:
            pass
        else:
            raise ValueError("Unknown movie must raise ValueError")
    svd = service.models["svd"]
    errors = []
    for uid in (1, 196, 405):
        scores = svd._score_user(uid)
        for mid in (1, 50, 56):
            errors.append(abs(float(scores[svd.movie_id_to_index[mid]]) - svd.predict_rating(uid, mid)))
    check(max(errors) <= 1e-6, "Vectorized SVD differs from Surprise")
    with TemporaryDirectory(prefix="svd_hybrid_smoke_") as temporary:
        root = Path(temporary)
        user_id, movie_id = 196, 1
        reduced = train[(train.user_id != user_id) & (train.movie_id != movie_id)]
        reduced.to_parquet(root / "train.parquet", index=False)
        movies.to_parquet(root / "movies.parquet", index=False)
        check(service.users_df is not None, "Missing users metadata")
        service.users_df.to_parquet(root / "users.parquet", index=False)
        isolated = RecommenderService(data_dir=str(root))
        check(user_id in isolated.list_users(), "Cold-start user must exist in metadata")
        for method in ("svd", "hybrid"):
            check_results(isolated, isolated.recommend(user_id, method=method, k=5),
                          5, method, fallback=True)
        check_results(isolated, isolated.similar_items(movie_id, method="svd", k=5),
                      5, "svd", excluded={movie_id}, fallback=True, similar=True)
    report["fallback_checks"] = "passed: unknown user, metadata-only user, SVD zero-interaction movie"
    report["invalid_movie_check"] = "passed for SVD and Hybrid"
    report["max_vectorized_prediction_error"] = max(errors)
    report["repeatability_checks"] = "passed on three users and three movies per method"
    return report


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data/processed")
    args = parser.parse_args(argv)
    try:
        report = smoke(args.data_dir)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"SVD/Hybrid smoke failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=True, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
