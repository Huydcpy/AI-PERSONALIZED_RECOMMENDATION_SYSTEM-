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
