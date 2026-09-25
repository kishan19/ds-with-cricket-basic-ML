"""Ball-tracking data: one row per delivery, measured rather than scored.

Unlike Cricsheet, there is no public source for this. It is a proprietary
per-delivery tracking export — release speed, swing, seam deviation, and where
the ball pitched and passed the stumps — supplied by the user as
``data/raw/data.csv``. **This file is never committed**; only the code that
reads it is. Swap the CSV for a different provider's export and everything
downstream keeps working, provided the column names below are preserved.

No player identity is present — a row is a delivery, not "a ball Bumrah
bowled" — so this is a dataset for clustering *deliveries*, not bowlers.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from cricketml.config import PATHS

__all__ = ["PHYSICS_COLUMNS", "REQUIRED_COLUMNS", "load_ball_tracking"]

#: The physical measurements of a delivery. Used as clustering features.
PHYSICS_COLUMNS: tuple[str, ...] = (
    "release_speed_kph",
    "swing_angle",
    "deviation",
    "bounce_position_x",  # how far down the pitch it landed — length
    "stumps_position_y",  # how far off the stumps it passed — line
    "bounce_angle",
    "drop_angle",
)

#: What a replacement file must provide. Everything else is optional extras.
REQUIRED_COLUMNS: tuple[str, ...] = (
    *PHYSICS_COLUMNS,
    "batting_hand",
    "bowling_hand",
    "bowling_type",  # pace / spin — held out as a label, never a feature
    "runs",
    "wicket",
)


def load_ball_tracking(path: Path | None = None, *, dropna: bool = True) -> pd.DataFrame:
    """Load the delivery-level tracking export.

    Args:
        path: Defaults to ``data/raw/data.csv``.
        dropna: Drop rows missing any physics column. The export has a small
            fraction of sensor dropout (under 3% per column in the supplied
            data) — dropping is simpler than imputing a *measurement* and
            does not bias a clustering exercise the way imputing a *label*
            would.

    Raises:
        FileNotFoundError: If no file is at ``path``. This data has no
            ``make data`` step — there is nowhere to download it from.
        KeyError: If the file is missing a required column, so a swapped-in
            replacement fails loudly rather than clustering the wrong thing.
    """
    path = path or (PATHS.raw / "data.csv")
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. This dataset has no public source — place a "
            f"delivery-tracking export there with columns: {REQUIRED_COLUMNS}"
        )

    df = pd.read_csv(path)
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise KeyError(f"{path.name} is missing required columns: {sorted(missing)}")

    if dropna:
        df = df.dropna(subset=list(PHYSICS_COLUMNS)).reset_index(drop=True)

    return df
