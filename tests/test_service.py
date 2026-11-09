import json

import pytest

from src.service.recommender_service import RecommenderService


def test_service_initialization():
    service = RecommenderService()
    assert service is not None

def test_recommend_returns_list():
    service = RecommenderService()
    recs = service.recommend(196, method="popularity", k=5)
    assert isinstance(recs, list)

def test_similar_items_returns_list():
    service = RecommenderService()
    recs = service.similar_items(1, k=5)
    assert isinstance(recs, list)


def test_item_cf_registered_and_dispatch():
    service = RecommenderService()
    assert "item_cf" in service.models
    assert any(item.method == "item_cf" for item in service.recommend(196, method="item_cf", k=5))
    assert any(item.method == "item_cf" for item in service.similar_items(1, method="item_cf", k=5))
    for operation in (service.recommend, service.similar_items):
        with pytest.raises(ValueError, match="không được hỗ trợ"):
            operation(1, method="invalid")


def test_svd_and_hybrid_registered_and_dispatch():
    service = RecommenderService()
    for method in ("svd", "hybrid"):
        assert method in service.models
        assert isinstance(service.recommend(196, method=method, k=5), list)
        assert isinstance(service.similar_items(1, method=method, k=5), list)


def test_svd_metrics_file(tmp_path):
    service = RecommenderService(data_dir=str(tmp_path), metrics_dir=str(tmp_path))
    assert service.get_svd_metrics() == {}
    report = {"model": "svd", "rmse": 0.9, "mae": 0.7}
    (tmp_path / "svd.json").write_text(json.dumps(report), encoding="utf-8")
    assert service.get_svd_metrics() == report
    for method in ("svd", "hybrid"):
        with pytest.raises(RuntimeError, match="chưa sẵn sàng"):
            service.recommend(1, method=method)


def test_ranking_metrics_file(tmp_path):
    service = RecommenderService(data_dir=str(tmp_path), metrics_dir=str(tmp_path))
    assert service.get_ranking_metrics() == {}
    report = {"config": {"primary_k": 10}, "models": {"item_cf": {"ndcg@10": 0.2}}}
    (tmp_path / "ranking.json").write_text(json.dumps(report), encoding="utf-8")
    assert service.get_ranking_metrics() == report
    with pytest.raises(RuntimeError, match="chưa sẵn sàng"):
        service.recommend(1, method="item_cf")
