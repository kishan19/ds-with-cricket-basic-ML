"""Splits are the guardrail. These tests exist so the guardrail cannot rot."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from cricketml.evaluation.splits import match_group_cv, season_split, temporal_split


@pytest.fixture()
def frame() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    dates = pd.date_range("2020-01-01", periods=10, freq="365D")
    rows = []
    for i, d in enumerate(dates):
        for ball in range(5):
            rows.append(
                {
                    "match_id": f"m{i}",
                    "date": d,
                    "season": str(d.year),
                    "ball": ball,
                    "y": rng.normal(),
                }
            )
    return pd.DataFrame(rows)


def test_temporal_split_never_puts_the_future_in_train(frame: pd.DataFrame) -> None:
    train, test = temporal_split(frame, test_size=0.3)
    assert train["date"].max() < test["date"].min()
    assert len(train) + len(test) == len(frame)


def test_temporal_split_keeps_matches_whole(frame: pd.DataFrame) -> None:
    train, test = temporal_split(frame, test_size=0.3)
    assert set(train["match_id"]).isdisjoint(set(test["match_id"]))


def test_temporal_split_rejects_silly_sizes(frame: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="test_size"):
        temporal_split(frame, test_size=1.5)


def test_season_split_holds_out_whole_seasons(frame: pd.DataFrame) -> None:
    train, test = season_split(frame, test_seasons=2)
    assert test["season"].nunique() == 2
    assert set(train["season"]).isdisjoint(set(test["season"]))


def test_match_group_cv_keeps_a_match_inside_one_fold(frame: pd.DataFrame) -> None:
    cv, groups = match_group_cv(frame, n_splits=5)
    for train_idx, test_idx in cv.split(frame, groups=groups):
        assert set(groups[train_idx]).isdisjoint(set(groups[test_idx]))


def test_match_group_cv_refuses_to_guess_the_group(frame: pd.DataFrame) -> None:
    with pytest.raises(KeyError, match="leak"):
        match_group_cv(frame.drop(columns=["match_id"]))
