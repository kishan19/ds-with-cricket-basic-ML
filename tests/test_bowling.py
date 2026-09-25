from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from cricketml.features.bowling import bowler_profile


@pytest.fixture()
def two_bowlers() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    rows = []
    # Bowler A: 15 overs, all outside the death, tight and wicketless.
    for i in range(90):
        rows.append(
            {
                "bowler": "A",
                "over": i // 6,
                "is_legal_ball": True,
                "runs_total": int(rng.choice([0, 1, 1, 4])),
                "byes": 0,
                "legbyes": 0,
                "runs_batter": int(rng.choice([0, 1, 1, 4])),
                "is_bowler_wicket": False,
            }
        )
    # Bowler B: 20 overs, expensive but strikes, bowls only at the death.
    for i in range(120):
        rows.append(
            {
                "bowler": "B",
                "over": 16 + (i // 6) % 4,
                "is_legal_ball": True,
                "runs_total": int(rng.choice([0, 6, 6, 4])),
                "byes": 0,
                "legbyes": 0,
                "runs_batter": int(rng.choice([0, 6, 6, 4])),
                "is_bowler_wicket": bool(i % 20 == 0),
            }
        )
    # Bowler C: only 5 overs — must be filtered out by the reliability threshold.
    for i in range(30):
        rows.append(
            {
                "bowler": "C",
                "over": i // 6,
                "is_legal_ball": True,
                "runs_total": 0,
                "byes": 0,
                "legbyes": 0,
                "runs_batter": 0,
                "is_bowler_wicket": False,
            }
        )
    return pd.DataFrame(rows)


def test_short_careers_are_dropped(two_bowlers: pd.DataFrame) -> None:
    profile = bowler_profile(two_bowlers, min_overs=10)
    assert set(profile["bowler"]) == {"A", "B"}


def test_byes_and_legbyes_are_not_credited_to_the_bowler() -> None:
    df = pd.DataFrame(
        {
            "bowler": ["A"] * 6,
            "over": [0] * 6,
            "is_legal_ball": [True] * 6,
            "runs_total": [4, 0, 0, 0, 0, 0],
            "byes": [4, 0, 0, 0, 0, 0],
            "legbyes": [0, 0, 0, 0, 0, 0],
            "runs_batter": [0, 0, 0, 0, 0, 0],
            "is_bowler_wicket": [False] * 6,
        }
    )
    profile = bowler_profile(df, min_overs=0)
    # 4 byes off the over, nothing off the bat: the bowler's figures read 0-for-1.
    assert profile.loc[0, "economy"] == 0.0


def test_death_bowler_is_never_in_the_powerplay_share(two_bowlers: pd.DataFrame) -> None:
    profile = bowler_profile(two_bowlers, min_overs=10).set_index("bowler")
    assert profile.loc["B", "powerplay_share"] == 0.0
    assert profile.loc["B", "death_share"] == 1.0
    assert profile.loc["A", "death_share"] == 0.0


def test_wickets_per_over_reflects_the_strike_rate(two_bowlers: pd.DataFrame) -> None:
    profile = bowler_profile(two_bowlers, min_overs=10).set_index("bowler")
    assert profile.loc["A", "wickets_per_over"] == 0.0
    assert profile.loc["B", "wickets_per_over"] > 0.0
