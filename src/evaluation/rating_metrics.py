"""Các metric đánh giá dự đoán rating."""

from __future__ import annotations

import numpy as np


def _check(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_pred = np.asarray(y_pred, dtype=float).ravel()
    if y_true.size != y_pred.size:
        raise ValueError("y_true và y_pred phải cùng độ dài")
    if y_true.size == 0:
        raise ValueError("Không có dữ liệu để đánh giá")
    return y_true, y_pred


def rmse(y_true, y_pred) -> float:
    """Root Mean Squared Error.

    Args:
        y_true: Rating thực tế.
        y_pred: Rating dự đoán.

    Returns:
        RMSE = sqrt(mean((y_true - y_pred) ** 2)).
    """
    y_true, y_pred = _check(y_true, y_pred)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mae(y_true, y_pred) -> float:
    """Mean Absolute Error.

    Args:
        y_true: Rating thực tế.
        y_pred: Rating dự đoán.

    Returns:
        MAE = mean(|y_true - y_pred|).
    """
    y_true, y_pred = _check(y_true, y_pred)
    return float(np.mean(np.abs(y_true - y_pred)))
