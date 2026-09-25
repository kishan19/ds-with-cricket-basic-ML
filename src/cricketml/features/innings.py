"""Innings-level aggregates built from ball-by-ball data."""

from __future__ import annotations

import pandas as pd

from cricketml.config import BALLS_PER_OVER

__all__ = ["innings_totals", "powerplay_summary"]

_KEYS = ["match_id", "date", "innings", "batting_team"]


def innings_totals(deliveries: pd.DataFrame) -> pd.DataFrame:
    """Final score, wickets and balls faced, one row per innings.

    This is the label table for the regression lessons.
    """
    grouped = deliveries.groupby(_KEYS, as_index=False, observed=True)
    out = grouped.agg(
        total_runs=("runs_total", "sum"),
        wickets=("is_wicket", "sum"),
        balls=("is_legal_ball", "sum"),
    )
    out["run_rate"] = out["total_runs"] / (out["balls"] / BALLS_PER_OVER).replace(0, pd.NA)
    return out


def powerplay_summary(deliveries: pd.DataFrame, overs: int = 6) -> pd.DataFrame:
    """What was known at the end of the powerplay — and only that.

    The classic first regression: predict the final total from these columns.
    Because the cut is on ``over < overs``, no post-powerplay information can
    reach the features.
    """
    pp = deliveries.loc[deliveries["over"] < overs]
    grouped = pp.groupby(_KEYS, as_index=False, observed=True)
    out = grouped.agg(
        pp_runs=("runs_total", "sum"),
        pp_wickets=("is_wicket", "sum"),
        pp_balls=("is_legal_ball", "sum"),
        pp_boundaries=("runs_batter", lambda s: int((s >= 4).sum())),
        pp_dots=("runs_total", lambda s: int((s == 0).sum())),
    )
    out["pp_run_rate"] = out["pp_runs"] / (out["pp_balls"] / BALLS_PER_OVER).replace(0, pd.NA)
    return out
