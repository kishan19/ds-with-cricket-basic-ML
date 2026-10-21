"""The Hawk-Eye loader is tested on a handful of synthetic rows, never on the
real (unlicensed, never-committed) CSV — so CI and a fresh clone need no download.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from cricketml.data.hawkeye import FEATURE_COLUMNS, bowler_type, load_hawkeye


@pytest.fixture()
def csv(tmp_path: Path) -> Path:
    df = pd.DataFrame(
        {
            "bowler": ["A", "B", "C", "D", "E", "F"],
            "rightArmedBowl": [True, False, False, True, True, True],
            "bowlingStyle": ["FAST_SEAM", "FAST_SEAM", "ORTHODOX", "LEG_SPIN", "SEAM", "SEAM"],
            "ballSpeed": [38.0, 37.5, 25.0, -1.0, 36.0, 35.0],  # D: tracker failed
            "pitchX": [-0.2, 0.1, 0.0, 0.0, None, 0.3],  # E: no coordinates
            "pitchY": [7.0, 5.0, 4.5, 5.0, None, 897.8],  # F: impossible length
            "stumpsX": [-0.1, 0.2, 0.0, 0.0, None, 0.1],
            "stumpsY": [0.8, 0.5, 0.6, 0.6, None, 0.7],
        }
    )
    path = tmp_path / "hawkeye.csv"
    df.to_csv(path, index=False)
    return path


def test_bowler_type_combines_arm_and_style(csv: Path) -> None:
    raw = pd.read_csv(csv)
    assert bowler_type(raw).tolist() == [
        "RIGHT_FAST_SEAM",
        "LEFT_FAST_SEAM",
        "LEFT_ORTHODOX",
        "RIGHT_LEG_SPIN",
        "RIGHT_SEAM",
        "RIGHT_SEAM",
    ]


def test_clean_drops_failed_and_impossible_readings(csv: Path) -> None:
    df = load_hawkeye(csv)
    assert df["bowler"].tolist() == ["A", "B", "C"]
    assert df[list(FEATURE_COLUMNS)].notna().all().all()
    assert "bowler_type" in df.columns


def test_unclean_keeps_every_row(csv: Path) -> None:
    assert len(load_hawkeye(csv, clean=False)) == 6


def test_missing_file_points_at_make(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="make hawkeye"):
        load_hawkeye(tmp_path / "nope.csv")


def test_missing_column_fails_loudly(tmp_path: Path) -> None:
    bad = tmp_path / "bad.csv"
    pd.DataFrame({"ballSpeed": [38.0]}).to_csv(bad, index=False)
    with pytest.raises(KeyError, match="missing required columns"):
        load_hawkeye(bad)
