import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_ranking_eval import load_data
from src.evaluation.rating_metrics import mae, rmse
from src.models.svd import SVDRecommender


def evaluate(train, test, movies):
    model = SVDRecommender(train, movies)
    predictions = [
        model.predict_rating(int(uid), int(mid))
        for uid, mid in test[["user_id", "movie_id"]].itertuples(index=False, name=None)
    ]
    if any(not math.isfinite(value) or not 1 <= value <= 5 for value in predictions):
        raise ValueError("SVD predictions must be finite and in [1, 5]")
    result = {
        "model": "svd",
        "rmse": rmse(test.rating.to_numpy(), predictions),
        "mae": mae(test.rating.to_numpy(), predictions),
        "n_test": len(test),
        "train_size": len(train),
        "seed": 42,
        "hyperparameters": {
            "n_factors": 100, "n_epochs": 20, "lr_all": 0.005, "reg_all": 0.02,
        },
    }
    if any(not math.isfinite(result[key]) or result[key] < 0 for key in ("rmse", "mae")):
        raise ValueError("Invalid rating metrics")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data/processed")
    parser.add_argument("--metrics-dir", default="reports/metrics")
    args = parser.parse_args(argv)
    try:
        result = evaluate(*load_data(args.data_dir))
        output = Path(args.metrics_dir) / "svd.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        partial = output.with_suffix(".json.tmp")
        partial.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        partial.replace(output)
    except (OSError, ValueError, RuntimeError, ImportError, KeyError) as exc:
        print(f"SVD evaluation failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, allow_nan=False))
    if not 0.5 <= result["rmse"] <= 1.5:
        print("WARNING: SVD RMSE outside expected [0.5, 1.5]", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
