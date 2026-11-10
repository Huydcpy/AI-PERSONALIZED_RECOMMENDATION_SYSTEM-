import json

import pandas as pd
import pytest

from scripts import run_svd_eval as evaluation


@pytest.fixture
def tables():
    train = pd.DataFrame({"user_id": [1], "movie_id": [1], "rating": [4]})
    test = pd.DataFrame({"user_id": [1, 2], "movie_id": [2, 1], "rating": [5, 2]})
    movies = pd.DataFrame({"movie_id": [1, 2]})
    return train, test, movies


def test_metrics_schema_and_train_only_fit(tables, monkeypatch, tmp_path):
    calls = []

    class Model:
        def __init__(self, train, movies):
            assert train is tables[0] and movies is tables[2]

        def predict_rating(self, uid, mid):
            calls.append((uid, mid))
            return 4.0 if uid == 1 else 3.0

    monkeypatch.setattr(evaluation, "SVDRecommender", Model)
    monkeypatch.setattr(evaluation, "load_data", lambda _: tables)
    assert evaluation.main(["--metrics-dir", str(tmp_path)]) == 0
    report = json.loads((tmp_path / "svd.json").read_text())
    assert report["rmse"] == report["mae"] == 1.0
    assert report["n_test"] == 2 and report["train_size"] == 1
    assert report["seed"] == 42
    assert report["hyperparameters"]["n_factors"] == 100
    assert calls == [(1, 2), (2, 1)]
    assert not (tmp_path / "svd.json.tmp").exists()


@pytest.mark.parametrize("prediction", [float("nan"), float("inf"), 0.9, 5.1])
def test_invalid_prediction_preserves_report(tables, monkeypatch, tmp_path, prediction):
    class Model:
        def __init__(self, *args):
            pass

        def predict_rating(self, *args):
            return prediction

    output = tmp_path / "svd.json"
    output.write_text("existing")
    monkeypatch.setattr(evaluation, "SVDRecommender", Model)
    monkeypatch.setattr(evaluation, "load_data", lambda _: tables)
    assert evaluation.main(["--metrics-dir", str(tmp_path)]) == 1
    assert output.read_text() == "existing"
