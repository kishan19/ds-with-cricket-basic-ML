"""Innings-level aggregates built from ball-by-ball data."""

from __future__ import annotations

import pandas as pd

from cricketml.config import BALLS_PER_OVER

__all__ = ["chase_states", "innings_totals", "powerplay_summary"]

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


def chase_states(deliveries: pd.DataFrame, matches: pd.DataFrame, overs: int = 20) -> pd.DataFrame:
    """The state of every live chase at the end of each over, one row per over.

    The label table for the win-probability lessons. Each row holds only what
    the scoreboard showed at that moment: the target, runs needed, balls left
    and wickets in hand. ``chasing_won`` is the outcome. A state is kept only
    while the chase is still live, so the over in which it was won, lost all
    out, or ran out of balls does not appear.

    ``result`` and ``method`` are carried through so a lesson can drop ties, no
    results and rain-revised (D/L) targets, and say why.
    """
    targets = (
        innings_totals(deliveries)
        .query("innings == 1")[["match_id", "total_runs"]]
        .assign(target=lambda t: t["total_runs"] + 1)
        .drop(columns="total_runs")
    )
    chase = deliveries.loc[deliveries["innings"] == 2]
    out = chase.groupby(["match_id", "date", "batting_team", "over"], as_index=False).agg(
        runs=("runs_total", "sum"),
        wickets=("is_wicket", "sum"),
        balls=("is_legal_ball", "sum"),
    )
    out = out.sort_values(["match_id", "over"])
    by_match = out.groupby("match_id")
    out["overs_done"] = out["over"] + 1
    out["runs_so_far"] = by_match["runs"].cumsum()
    out["wickets_down"] = by_match["wickets"].cumsum()
    out["balls_so_far"] = by_match["balls"].cumsum()

    context = matches[["match_id", "season", "winner", "result", "method"]]
    out = out.merge(targets, on="match_id").merge(context, on="match_id")
    out["runs_needed"] = out["target"] - out["runs_so_far"]
    out["balls_left"] = overs * BALLS_PER_OVER - out["balls_so_far"]
    out["wickets_left"] = 10 - out["wickets_down"]
    out["required_rate"] = out["runs_needed"] / out["balls_left"].replace(0, pd.NA) * BALLS_PER_OVER
    out["current_rate"] = out["runs_so_far"] / out["balls_so_far"] * BALLS_PER_OVER
    out["chasing_won"] = (out["winner"] == out["batting_team"]).astype(int)

    live = (out["runs_needed"] > 0) & (out["wickets_left"] > 0) & (out["balls_left"] > 0)
    keep = [
        "match_id", "date", "season", "batting_team", "overs_done", "target",
        "runs_so_far", "wickets_down", "balls_so_far", "runs_needed", "balls_left",
        "wickets_left", "required_rate", "current_rate", "winner", "result", "method",
        "chasing_won",
    ]  # fmt: skip
    return out.loc[live, keep].reset_index(drop=True)
