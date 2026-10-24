from __future__ import annotations

import pandas as pd

from cricketml.features import chase_states, innings_totals, powerplay_summary


def test_innings_totals_matches_the_scorecard(deliveries: pd.DataFrame) -> None:
    totals = innings_totals(deliveries).set_index("innings")
    assert totals.loc[1, "total_runs"] == 15
    assert totals.loc[1, "wickets"] == 2
    assert totals.loc[1, "balls"] == 8  # 9 deliveries, one wide
    assert totals.loc[2, "total_runs"] == 3


def test_powerplay_summary_sees_only_the_powerplay(deliveries: pd.DataFrame) -> None:
    pp = powerplay_summary(deliveries, overs=1).set_index("innings")
    # Over 1 is excluded, so the two runs scored there must not appear.
    assert pp.loc[1, "pp_runs"] == 13
    assert pp.loc[1, "pp_boundaries"] == 2  # a four and a six


def test_chase_states_read_the_scoreboard(deliveries: pd.DataFrame, match_row: dict) -> None:
    states = chase_states(deliveries, pd.DataFrame([match_row]))
    assert len(states) == 1  # one over of the chase was bowled
    state = states.iloc[0]
    assert state["target"] == 16  # first innings made 15
    assert state["runs_needed"] == 16 - state["runs_so_far"]
    assert state["balls_left"] == 120 - state["balls_so_far"]
    assert state["batting_team"] == "Team B"
    assert state["chasing_won"] == 0  # Team A defended
