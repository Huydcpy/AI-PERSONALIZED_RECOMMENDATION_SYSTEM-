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


def check_results(service, results, k, excluded=(), fallback=False, similar=False):
    ids = [item.movie_id for item in results]
    check(len(ids) == k and len(set(ids)) == len(ids), "Wrong result count or duplicates")
    check(not set(ids).intersection(excluded), "Excluded movie returned")
    for item in results:
        service.get_movie(item.movie_id)
        check(math.isfinite(item.score), "Non-finite score")
        check(item.method in ("item_cf", "popularity"), "Unexpected method")
        check(bool(item.reason), "Missing reason")
        if item.method == "popularity":
            check("Fallback" in item.reason, "Missing fallback explanation")
        if fallback:
            check(item.method == "popularity", "Expected Popularity fallback")
        if similar and item.method == "item_cf":
            check(0 < item.score <= 1, "Similarity outside (0, 1]")
        else:
            check(1 <= item.score <= 5, "Rating score outside [1, 5]")


def smoke(data_dir):
    service = RecommenderService(data_dir=data_dir)
    check("item_cf" in service.models, "Item-CF is not registered; integrate Huy's model/service first")
    train, movies = service.train_df, service.movies_df
    check(train is not None and movies is not None, "Run the data pipeline first")
    report = {"users": {}, "similar": {}}
    for uid in (1, 196, 405):
        seen = set(train.loc[train.user_id == uid, "movie_id"])
        results = service.recommend(uid, method="item_cf", k=10, exclude_seen=True)
        check_results(service, results, 10, excluded=seen)
        check(any(item.method == "item_cf" for item in results), "All results are fallback")
        report["users"][str(uid)] = [vars(item) for item in results[:5]]
    for mid in (1, 50, 56):
        results = service.similar_items(mid, k=5, method="item_cf")
        check_results(service, results, 5, excluded={mid}, similar=True)
        check(any(item.method == "item_cf" for item in results), "All similar items are fallback")
        report["similar"][str(mid)] = [vars(item) for item in results]
    unknown_user = max(999999, int(train.user_id.max()) + 1)
    check_results(service, service.recommend(unknown_user, method="item_cf", k=5), 5, fallback=True)
    invalid_movie = int(movies.movie_id.max()) + 1
    try:
        service.similar_items(invalid_movie, method="item_cf")
    except ValueError:
        pass
    else:
        raise ValueError("Unknown movie must raise ValueError")
    with TemporaryDirectory(prefix="item_cf_smoke_") as temporary:
        root = Path(temporary)
        user_id, movie_id = 196, 1
        reduced = train[(train.user_id != user_id) & (train.movie_id != movie_id)]
        reduced.to_parquet(root / "train.parquet", index=False)
        movies.to_parquet(root / "movies.parquet", index=False)
        check(service.users_df is not None, "Missing users metadata")
        service.users_df.to_parquet(root / "users.parquet", index=False)
        isolated = RecommenderService(data_dir=str(root))
        check("item_cf" in isolated.models, "Item-CF missing in isolated service")
        check(user_id in isolated.list_users(), "Cold-start user must exist in metadata")
        check_results(isolated, isolated.recommend(user_id, method="item_cf", k=5), 5, fallback=True)
        check_results(isolated, isolated.similar_items(movie_id, method="item_cf", k=5),
                      5, excluded={movie_id}, fallback=True, similar=True)
    report["fallback_checks"] = "passed: unknown user, metadata-only user, zero-interaction movie"
    report["invalid_movie_check"] = "passed"
    return report


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data/processed")
    args = parser.parse_args(argv)
    try:
        report = smoke(args.data_dir)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Item-CF smoke failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=True, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
