"""One-row scorecards.

Every lesson reports its model the same way, so results can be stacked into a
single table across the whole curriculum and compared honestly.
"""

from __future__ import annotations

import numpy as np
from sklearn import metrics as skm

__all__ = ["classification_report_row", "regression_report_row"]


def regression_report_row(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    model: str,
    baseline: float | None = None,
) -> dict[str, float | str]:
    """Score a regression model (e.g. predicting a first-innings total).

    Args:
        y_true: Observed values.
        y_pred: Model predictions.
        model: Label for the row.
        baseline: Optional RMSE of the naive rule the lesson opened with. A
            model that cannot beat it has not earned its complexity.
    """
    y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
    rmse = float(np.sqrt(skm.mean_squared_error(y_true, y_pred)))
    row: dict[str, float | str] = {
        "model": model,
        "rmse": rmse,
        "mae": float(skm.mean_absolute_error(y_true, y_pred)),
        "r2": float(skm.r2_score(y_true, y_pred)),
        "n": len(y_true),
    }
    if baseline is not None:
        row["vs_baseline_%"] = float((baseline - rmse) / baseline * 100)
    return row


def classification_report_row(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    *,
    model: str,
    threshold: float = 0.5,
) -> dict[str, float | str]:
    """Score a binary classifier (e.g. win probability, wicket next ball).

    Takes *probabilities*, not labels. Cricket's interesting targets are rare —
    in the IPL a wicket falls on roughly one legal ball in twenty — so accuracy is meaningless and
    the threshold is a decision, not a default. Average precision and Brier
    score are reported because they survive imbalance; accuracy is included only
    as the cautionary number.
    """
    y_true = np.asarray(y_true, int)
    y_proba = np.asarray(y_proba, float)
    y_pred = (y_proba >= threshold).astype(int)
    return {
        "model": model,
        "roc_auc": float(skm.roc_auc_score(y_true, y_proba)),
        "avg_precision": float(skm.average_precision_score(y_true, y_proba)),
        "brier": float(skm.brier_score_loss(y_true, y_proba)),
        "precision": float(skm.precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(skm.recall_score(y_true, y_pred, zero_division=0)),
        "accuracy": float(skm.accuracy_score(y_true, y_pred)),
        "positive_rate": float(y_true.mean()),
        "n": len(y_true),
    }
