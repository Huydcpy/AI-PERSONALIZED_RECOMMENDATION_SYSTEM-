import argparse
import json
import math
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

K_VALUES = (5, 10, 20)
METHODS = ("popularity", "content_based", "item_cf", "svd", "hybrid")


def load_data(data_dir):
    tables = {}
    for name in ("train", "test", "movies"):
        path = Path(data_dir) / f"{name}.parquet"
        if not path.is_file():
            raise FileNotFoundError(f"Missing {path}. Run the data pipeline first.")
        tables[name] = pd.read_parquet(path)
        if tables[name].empty:
            raise ValueError(f"{name} must be nonempty")
    train, test, movies = (tables[name] for name in ("train", "test", "movies"))
    from src.data.preprocess import validate_ratings

    validate_ratings(train)
    validate_ratings(test)
    catalog = set(movies.movie_id)
    if not catalog or movies.movie_id.duplicated().any():
        raise ValueError("Movie catalog must be nonempty and unique")
    for table in (train, test):
        if not set(table.movie_id).issubset(catalog):
            raise ValueError("Ratings contain movies outside the catalog")
    train_pairs = pd.MultiIndex.from_frame(train[["user_id", "movie_id"]])
    test_pairs = pd.MultiIndex.from_frame(test[["user_id", "movie_id"]])
    if len(train_pairs.intersection(test_pairs)):
        raise ValueError("Train and test overlap")
    return train, test, movies


def load_dependencies():
    try:
        from src.evaluation.ranking_metrics import (
            ndcg_at_k,
            precision_at_k,
            recall_at_k,
        )
        from src.models.content_based import ContentBasedRecommender
        from src.models.hybrid import HybridRecommender
        from src.models.item_cf import ItemCFRecommender
        from src.models.popularity import PopularityRecommender
        from src.models.svd import SVDRecommender
    except ImportError as exc:
        raise RuntimeError(
            "Day 4 dependencies are unavailable. Integrate Huy's "
            "SVD/Hybrid models and service first."
        ) from exc
    return (
        {
            "popularity": PopularityRecommender,
            "content_based": ContentBasedRecommender,
            "item_cf": ItemCFRecommender,
            "svd": SVDRecommender,
            "hybrid": HybridRecommender,
        },
        {"precision": precision_at_k, "recall": recall_at_k, "ndcg": ndcg_at_k},
    )


def evaluate(models, train, test, movies, metrics):
    relevant = {
        int(uid): set(map(int, rows.movie_id))
        for uid, rows in test[test.rating >= 4.0].groupby("user_id")
    }
    if not relevant:
        raise ValueError("No users with relevant test items")
    users = set(train.user_id) | set(test.user_id)
    catalog = set(map(int, movies.movie_id))
    seen = {int(uid): set(map(int, rows.movie_id)) for uid, rows in train.groupby("user_id")}
    report = {
        "config": {
            "k_values": list(K_VALUES), "primary_k": 10,
            "relevance_threshold": 4.0, "seed": 42,
            "n_users_evaluated": len(relevant),
            "n_users_skipped": len(users - set(relevant)),
        },
        "models": {},
    }
    for name, model in models.items():
        totals = {f"{metric}@{k}": 0.0 for k in K_VALUES for metric in metrics}
        covered = set()
        for uid in sorted(relevant):
            results = model.recommend(uid, k=max(K_VALUES), exclude_seen=True)
            ids = list(dict.fromkeys(int(item.movie_id) for item in results))
            if not set(ids).issubset(catalog) or seen.get(uid, set()).intersection(ids):
                raise ValueError(f"{name}: invalid or seen recommendation for user {uid}")
            covered.update(ids[:10])
            for k in K_VALUES:
                for metric, function in metrics.items():
                    value = float(function(ids, relevant[uid], k))
                    if not math.isfinite(value) or not 0 <= value <= 1:
                        raise ValueError(f"{name}: invalid {metric}@{k}: {value}")
                    totals[f"{metric}@{k}"] += value
        report["models"][name] = {key: value / len(relevant) for key, value in totals.items()}
        report["models"][name]["coverage@10"] = len(covered) / len(catalog)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data/processed")
    parser.add_argument("--metrics-dir", default="reports/metrics")
    args = parser.parse_args(argv)
    try:
        train, test, movies = load_data(args.data_dir)
        factories, metrics = load_dependencies()
        popularity = factories["popularity"](train, movies)
        models = {
            "popularity": popularity,
            "content_based": factories["content_based"](
                train, movies, fallback=popularity
            ),
            "item_cf": factories["item_cf"](
                train, movies, fallback=popularity
            ),
            "svd": factories["svd"](train, movies, fallback=popularity),
        }
        models["hybrid"] = factories["hybrid"](
            {
                "svd": models["svd"],
                "item_cf": models["item_cf"],
                "content_based": models["content_based"],
            },
            train,
            fallback=popularity,
        )
        report = evaluate(models, train, test, movies, metrics)
        output = Path(args.metrics_dir) / "ranking.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        partial = output.with_suffix(".json.tmp")
        partial.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        partial.replace(output)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Ranking evaluation failed: {exc}", file=sys.stderr)
        return 1
    print("Model             Precision@10  Recall@10  NDCG@10  Coverage@10")
    for name, values in report["models"].items():
        print(f"{name:18} {values['precision@10']:.6f}      {values['recall@10']:.6f}   "
              f"{values['ndcg@10']:.6f} {values['coverage@10']:.6f}")
    print(json.dumps(report["config"], sort_keys=True))
    print(f"Saved {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
