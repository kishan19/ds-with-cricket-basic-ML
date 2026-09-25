"""Career-level bowling profiles, built for clustering rather than a scorecard.

Cricsheet has no ball-tracking data — no pace, no line and length, no seam
position. So "what kind of bowler is this?" cannot be answered the way a
broadcast graphic answers it. It can still be answered from what the outcome of
each ball reveals: how many runs it cost, how often it took a wicket, how often
it went for nothing, how often it went for a boundary, and which part of the
innings the captain trusted the bowler with. Five outcome-based numbers stand
in for six ball-tracking ones.
"""

from __future__ import annotations

import pandas as pd

__all__ = ["bowler_profile"]

#: T20 phase boundaries (0-indexed overs): powerplay is overs 0-5, death is 16-19.
_POWERPLAY_LAST_OVER = 6
_DEATH_FIRST_OVER = 16


def bowler_profile(deliveries: pd.DataFrame, min_overs: float = 100.0) -> pd.DataFrame:
    """One row per bowler with enough overs to trust a rate statistic.

    Args:
        deliveries: Ball-by-ball frame from :func:`cricketml.data.load_deliveries`.
        min_overs: Minimum career overs to be included. Below this, economy
            rate and dot-ball percentage are noise, not signal — a part-timer's
            three overs will not survive a temporal split, let alone a cluster.

    Returns:
        One row per bowler: ``overs``, ``economy``, ``wickets_per_over``,
        ``dot_pct``, ``boundary_pct``, ``powerplay_share``, ``death_share``.
    """
    legal = deliveries.loc[deliveries["is_legal_ball"]].copy()
    # Byes and leg-byes are extras the *wicketkeeper* let through, not runs the
    # bowler conceded — cricket's other "credit it to the wrong person" trap,
    # alongside the run-out one in cricketml.config.BOWLER_WICKET_KINDS.
    legal["runs_conceded"] = legal["runs_total"] - legal["byes"] - legal["legbyes"]
    legal["is_dot"] = legal["runs_total"] == 0
    legal["is_boundary"] = legal["runs_batter"].isin((4, 6))
    legal["is_powerplay"] = legal["over"] < _POWERPLAY_LAST_OVER
    legal["is_death"] = legal["over"] >= _DEATH_FIRST_OVER

    g = legal.groupby("bowler", observed=True)
    balls = g.size()
    overs = balls / 6

    profile = pd.DataFrame(
        {
            "overs": overs,
            "economy": g["runs_conceded"].sum() / overs,
            "wickets_per_over": g["is_bowler_wicket"].sum() / overs,
            "dot_pct": g["is_dot"].sum() / balls,
            "boundary_pct": g["is_boundary"].sum() / balls,
            "powerplay_share": g["is_powerplay"].sum() / balls,
            "death_share": g["is_death"].sum() / balls,
        }
    )

    return (
        profile.loc[profile["overs"] >= min_overs]
        .sort_values("overs", ascending=False)
        .rename_axis("bowler")
        .reset_index()
    )
