from __future__ import annotations

import numpy as np

from cricketml.evaluation.metrics import classification_report_row, regression_report_row


def test_regression_row_reports_against_a_baseline() -> None:
    y = np.array([150.0, 160.0, 170.0])
    row = regression_report_row(y, y + 5, model="toy", baseline=10.0)
    assert row["model"] == "toy"
    assert np.isclose(row["rmse"], 5.0)
    assert np.isclose(row["vs_baseline_%"], 50.0)
    assert row["n"] == 3


def test_classification_row_exposes_the_imbalance() -> None:
    y = np.array([0] * 39 + [1])
    proba = np.full(40, 0.025)
    row = classification_report_row(y, proba, model="base rate")
    # 97.5% accurate and utterly useless — the lesson in one row.
    assert np.isclose(row["accuracy"], 0.975)
    assert row["recall"] == 0.0
    assert np.isclose(row["positive_rate"], 0.025)
