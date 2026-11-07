import math

import pytest

from src.evaluation.ranking_metrics import ndcg_at_k, precision_at_k, recall_at_k


def test_hand_calculated_metrics():
    recommended, relevant = [1, 2, 3, 4, 5], {2, 4, 6}
    assert precision_at_k(recommended, relevant, 5) == 0.4
    assert recall_at_k(recommended, relevant, 5) == pytest.approx(2 / 3)
    expected = (1 / math.log2(3) + 1 / math.log2(5)) / (1 + 1 / math.log2(3) + 0.5)
    assert ndcg_at_k(recommended, relevant, 5) == pytest.approx(expected)


@pytest.mark.parametrize("metric", [precision_at_k, recall_at_k, ndcg_at_k])
def test_empty_duplicate_and_invalid_inputs(metric):
    assert metric([1, 1, 2], {1, 2}, 2) == 1.0
    assert metric([1], set(), 5) == 0.0
    assert metric([], {1}, 5) == 0.0
    assert 0 <= metric([1], {1, 2}, 5) <= 1
    for k in (0, -1):
        with pytest.raises(ValueError, match="k phải > 0"):
            metric([1], {1}, k)


def test_precision_uses_fixed_k():
    assert precision_at_k([1], {1}, 5) == 0.2
