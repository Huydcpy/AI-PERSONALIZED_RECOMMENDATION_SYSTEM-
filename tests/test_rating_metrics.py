import pytest

from src.evaluation.rating_metrics import mae, rmse


def test_rmse_and_mae_hand_calculated():
    assert rmse([3, 5], [2, 5]) == pytest.approx(0.7071, abs=1e-4)
    assert mae([3, 5], [2, 5]) == pytest.approx(0.5)


def test_length_mismatch_raises():
    with pytest.raises(ValueError):
        rmse([1, 2], [1])


def test_empty_input_raises():
    with pytest.raises(ValueError):
        mae([], [])