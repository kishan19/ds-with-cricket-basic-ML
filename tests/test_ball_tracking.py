"""The loader is the seam between "whatever proprietary export you have today"
and "whatever replaces it tomorrow" — so it is tested against a synthetic
fixture, never against real (and never-committed) tracking data.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from cricketml.data.ball_tracking import PHYSICS_COLUMNS, load_ball_tracking

FIXTURE = Path(__file__).parent / "fixtures" / "ball_tracking_sample.csv"


def test_loads_the_fixture() -> None:
    df = load_ball_tracking(FIXTURE, dropna=False)
    assert len(df) == 40
    assert set(PHYSICS_COLUMNS) <= set(df.columns)


def test_dropna_removes_sensor_dropout_rows() -> None:
    full = load_ball_tracking(FIXTURE, dropna=False)
    clean = load_ball_tracking(FIXTURE, dropna=True)
    assert clean.shape[0] < full.shape[0]
    assert clean[list(PHYSICS_COLUMNS)].isna().sum().sum() == 0


def test_missing_file_fails_loudly(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="no public source"):
        load_ball_tracking(tmp_path / "nope.csv")


def test_missing_column_fails_loudly(tmp_path: Path) -> None:
    bad = tmp_path / "bad.csv"
    pd.DataFrame({"release_speed_kph": [130.0]}).to_csv(bad, index=False)
    with pytest.raises(KeyError, match="missing required columns"):
        load_ball_tracking(bad)
