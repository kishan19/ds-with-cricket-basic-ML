"""The rules a real model has to beat.

A lesson that opens with `RandomForestRegressor` has skipped the only question
that matters: is this better than what a commentator says out loud? Each
baseline here is scikit-learn compatible, so it drops into the same
cross-validation loop as the real model and lands in the same results table.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin

from cricketml.config import BALLS_PER_OVER

__all__ = ["CurrentRunRateProjection", "MajorityClass", "TeamMeanScore"]


class CurrentRunRateProjection(BaseEstimator, RegressorMixin):
    """ "They're on course for about 180." Runs so far + run rate * overs left.

    The commentator's baseline for predicting a final innings total. It is
    stateless — ``fit`` only records the format — and it is surprisingly hard to
    beat before the 12th over.

    Expects a frame with ``runs_so_far``, ``balls_so_far`` and ``total_overs``.
    """

    def __init__(
        self,
        runs_col: str = "runs_so_far",
        balls_col: str = "balls_so_far",
        overs_col: str = "total_overs",
    ) -> None:
        self.runs_col = runs_col
        self.balls_col = balls_col
        self.overs_col = overs_col

    def fit(self, X: pd.DataFrame, y: np.ndarray | None = None) -> CurrentRunRateProjection:
        missing = {self.runs_col, self.balls_col, self.overs_col} - set(X.columns)
        if missing:
            raise KeyError(f"Missing columns for the run-rate baseline: {sorted(missing)}")
        self.is_fitted_ = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        runs = X[self.runs_col].to_numpy(float)
        balls = X[self.balls_col].to_numpy(float)
        total_balls = X[self.overs_col].to_numpy(float) * BALLS_PER_OVER
        with np.errstate(divide="ignore", invalid="ignore"):
            rate = np.where(balls > 0, runs / balls, 0.0)
        return runs + rate * np.maximum(total_balls - balls, 0.0)


class TeamMeanScore(BaseEstimator, RegressorMixin):
    """Predict each team's historical mean score; fall back to the global mean.

    The "look it up in the record book" baseline. Any model that cannot beat it
    has learnt nothing the scorecard did not already say.
    """

    def __init__(self, group_col: str = "batting_team") -> None:
        self.group_col = group_col

    def fit(self, X: pd.DataFrame, y: np.ndarray) -> TeamMeanScore:
        y = np.asarray(y, float)
        self.global_mean_ = float(y.mean())
        self.group_means_ = pd.Series(y, index=X[self.group_col].to_numpy()).groupby(level=0).mean()
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return X[self.group_col].map(self.group_means_).fillna(self.global_mean_).to_numpy(float)


class MajorityClass(BaseEstimator, ClassifierMixin):
    """Always predict the base rate.

    For rare events — a wicket on any given ball — this scores ~95% accuracy and
    is completely useless. That is the point: it is the exhibit in the lesson on
    why accuracy is the wrong metric.
    """

    def fit(self, X, y) -> MajorityClass:
        y = np.asarray(y, int)
        self.classes_ = np.unique(y)
        self.base_rate_ = float(y.mean())
        return self

    def predict_proba(self, X) -> np.ndarray:
        p = np.full(len(X), self.base_rate_)
        return np.column_stack([1 - p, p])

    def predict(self, X) -> np.ndarray:
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)
