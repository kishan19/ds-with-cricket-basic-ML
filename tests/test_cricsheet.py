"""The flattener is the foundation. If it is wrong, every lesson is wrong."""

from __future__ import annotations

import pandas as pd


def test_match_row_captures_context(match_row: dict) -> None:
    assert match_row["match_id"] == "fixture-001"
    assert match_row["date"] == pd.Timestamp("2024-04-15")
    assert match_row["season"] == "2024"
    assert match_row["venue"] == "M Chinnaswamy Stadium"
    assert match_row["toss_winner"] == "Team A"
    assert match_row["winner"] == "Team A"
    assert match_row["win_by_runs"] == 12


def test_every_delivery_is_a_row(deliveries: pd.DataFrame) -> None:
    # 7 + 2 in the first innings, 2 in the second.
    assert len(deliveries) == 11
    assert deliveries["innings"].tolist().count(1) == 9


def test_wides_do_not_count_as_a_ball_faced(deliveries: pd.DataFrame) -> None:
    first_over = deliveries[(deliveries["innings"] == 1) & (deliveries["over"] == 0)]
    assert first_over["is_legal_ball"].sum() == 6  # seven deliveries, one wide
    assert first_over["ball_in_innings"].max() == 6


def test_run_out_is_not_credited_to_the_bowler(deliveries: pd.DataFrame) -> None:
    run_out = deliveries[deliveries["wicket_kind"] == "run out"].iloc[0]
    assert run_out["is_wicket"]
    assert not run_out["is_bowler_wicket"]

    caught = deliveries[deliveries["wicket_kind"] == "caught"].iloc[0]
    assert caught["is_bowler_wicket"]


def test_runs_add_up(deliveries: pd.DataFrame) -> None:
    first = deliveries[deliveries["innings"] == 1]
    assert first["runs_total"].sum() == 15
    assert first["runs_batter"].sum() == 13
    assert first["runs_extras"].sum() == 2
