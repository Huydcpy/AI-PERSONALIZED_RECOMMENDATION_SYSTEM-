import importlib.util
import json
import math
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

SPEC = importlib.util.spec_from_file_location(
    "run_ranking_eval", Path(__file__).resolve().parents[1] / "scripts/run_ranking_eval.py"
)
evaluation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluation)


def reference_metrics():
    def precision(ids, relevant, k):
        return len(set(ids[:k]) & relevant) / k

    def recall(ids, relevant, k):
        return len(set(ids[:k]) & relevant) / len(relevant)

    def ndcg(ids, relevant, k):
        gain = sum(1 / math.log2(rank + 2) for rank, mid in enumerate(ids[:k]) if mid in relevant)
        ideal = sum(1 / math.log2(rank + 2) for rank in range(min(len(relevant), k)))
        return gain / ideal

    return {"precision": precision, "recall": recall, "ndcg": ndcg}


@pytest.fixture
def tables():
    train = pd.DataFrame({"user_id": [1, 2, 3], "movie_id": [1, 1, 1],
                          "rating": [5, 4, 2], "timestamp": [1, 2, 3]})
    test = pd.DataFrame({"user_id": [1, 2, 3], "movie_id": [2, 3, 2],
                         "rating": [4, 5, 3], "timestamp": [4, 5, 6]})
    movies = pd.DataFrame({"movie_id": [1, 2, 3, 4]})
    return train, test, movies


class FixedModel:
    def __init__(self, ids):
        self.ids = ids
        self.calls = []

    def recommend(self, uid, k, exclude_seen):
        self.calls.append((uid, k, exclude_seen))
        return [SimpleNamespace(movie_id=mid) for mid in self.ids]


def test_macro_average_duplicates_threshold_and_coverage(tables):
    model = FixedModel([2, 2, 4])
    report = evaluation.evaluate({"example": model}, *tables, reference_metrics())
    assert model.calls == [(1, 20, True), (2, 20, True)]
    assert report["config"]["n_users_evaluated"] == 2
    assert report["config"]["n_users_skipped"] == 1
    values = report["models"]["example"]
    assert values["precision@5"] == pytest.approx(0.1)
    assert values["precision@10"] == pytest.approx(0.05)
    assert values["recall@20"] == pytest.approx(0.5)
    assert values["ndcg@10"] == pytest.approx(0.5)
    assert values["coverage@10"] == pytest.approx(0.5)
    assert len(values) == 10


@pytest.mark.parametrize("ids", [[1], [999]])
def test_invalid_recommendations_rejected(tables, ids):
    with pytest.raises(ValueError, match="invalid or seen"):
        evaluation.evaluate({"example": FixedModel(ids)}, *tables, reference_metrics())


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -0.1, 1.1])
def test_invalid_metric_rejected(tables, value):
    with pytest.raises(ValueError, match="invalid precision"):
        evaluation.evaluate({"example": FixedModel([2])}, *tables,
                            {"precision": lambda *args: value})


def test_no_relevant_users_rejected(tables):
    train, test, movies = tables
    test = test.assign(rating=3)
    with pytest.raises(ValueError, match="No users"):
        evaluation.evaluate({"example": FixedModel([2])}, train, test, movies, reference_metrics())


def test_failed_cli_preserves_existing_report(tmp_path, monkeypatch):
    output = tmp_path / "ranking.json"
    output.write_text("existing", encoding="utf-8")
    def unavailable(*args):
        raise RuntimeError("missing dependency")
    monkeypatch.setattr(evaluation, "load_data", unavailable)
    assert evaluation.main(["--metrics-dir", str(tmp_path)]) == 1
    assert output.read_text(encoding="utf-8") == "existing"


def test_overlap_rejected(tmp_path, tables):
    train, _test, movies = tables
    for name, table in (("train", train), ("test", train), ("movies", movies)):
        table.to_parquet(tmp_path / f"{name}.parquet", index=False)
    with pytest.raises(ValueError, match="overlap"):
        evaluation.load_data(tmp_path)


@pytest.mark.parametrize("empty_name", ["train", "test", "movies"])
def test_empty_input_rejected(tmp_path, tables, empty_name):
    for name, table in zip(("train", "test", "movies"), tables):
        if name == empty_name:
            table = table.iloc[:0]
        table.to_parquet(tmp_path / f"{name}.parquet", index=False)
    with pytest.raises(ValueError, match="nonempty"):
        evaluation.load_data(tmp_path)


def test_successful_cli_schema_and_train_only_fit(tmp_path, tables, monkeypatch):
    train, _test, movies = tables
    fitted = []

    def factory(fit_train, fit_movies, fallback=None):
        assert fit_train is train
        assert fit_movies is movies
        fitted.append(fallback)
        return FixedModel([2, 4])

    def hybrid_factory(components, fit_train, fallback=None):
        assert set(components) == {"svd", "item_cf", "content_based"}
        assert fit_train is train
        fitted.append(fallback)
        return FixedModel([2, 4])

    factories = {
        "popularity": factory,
        "content_based": factory,
        "item_cf": factory,
        "svd": factory,
        "hybrid": hybrid_factory,
    }
    monkeypatch.setattr(evaluation, "load_data", lambda _: tables)
    monkeypatch.setattr(evaluation, "load_dependencies",
                        lambda: (factories, reference_metrics()))
    assert evaluation.main(["--metrics-dir", str(tmp_path)]) == 0
    report = json.loads((tmp_path / "ranking.json").read_text(encoding="utf-8"))
    assert list(report["models"]) == list(evaluation.METHODS)
    assert fitted[0] is None
    assert fitted[1] is fitted[2] is fitted[3] is fitted[4]
    for values in report["models"].values():
        assert len(values) == 10
        assert all(0 <= value <= 1 for value in values.values())
    assert not (tmp_path / "ranking.json.tmp").exists()
