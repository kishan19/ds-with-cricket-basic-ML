"""Hawk-Eye ball tracking for the IPL: one row per delivery, measured rather than scored.

Source: **HawkeyeStats** by alittlefitness —
https://github.com/alittlefitness/HawkeyeStats — a tidy CSV of the Hawk-Eye
numbers the ICC's Pulselive API publishes per delivery. That repo did the
scraping and tidying; this module only downloads its ``mensIPLHawkeyeStats.csv``
and cleans it for modelling.

The upstream repo carries **no licence**, so the CSV is downloaded on demand
into ``data/raw/`` and never committed or redistributed here. Credit the repo
(``ATTRIBUTION``) on anything derived from it.

Units, per the upstream README:

* ``ballSpeed`` — metres per second (``-1`` when the tracker failed)
* ``pitchX`` / ``pitchY`` — where the ball bounced, metres; ``pitchY`` is
  distance from the batter's stumps (length), ``pitchX`` is across the pitch (line)
* ``stumpsX`` / ``stumpsY`` — where the ball passed (or would have passed) the
  stumps, metres; across and height
"""

from __future__ import annotations

from pathlib import Path
from urllib.request import urlopen

import numpy as np
import pandas as pd

from cricketml.config import PATHS

__all__ = [
    "ATTRIBUTION",
    "FEATURE_COLUMNS",
    "LABEL_COLUMNS",
    "PACE_STYLES",
    "PLAUSIBLE_RANGES",
    "SOURCE_REPO",
    "bowler_type",
    "download",
    "load_hawkeye",
]

SOURCE_REPO = "https://github.com/alittlefitness/HawkeyeStats"
_URL = "https://raw.githubusercontent.com/alittlefitness/HawkeyeStats/main/mensIPLHawkeyeStats.csv"
_FILENAME = "mensIPLHawkeyeStats.csv"

#: For chart footers — ``annotate_source(ax, text=ATTRIBUTION)``.
ATTRIBUTION = "Data: Hawk-Eye via github.com/alittlefitness/HawkeyeStats"

#: The ball's physics. Clustering features — nothing else goes in.
FEATURE_COLUMNS: tuple[str, ...] = ("ballSpeed", "pitchX", "pitchY", "stumpsX", "stumpsY")

#: Who bowled it. Held out, used only afterwards to interpret clusters.
LABEL_COLUMNS: tuple[str, ...] = ("bowler", "rightArmedBowl", "bowlingStyle")

#: Anything outside these is a tracker glitch, not a delivery. Speeds of
#: 15-45 m/s are 54-162 kph (the fastest ball ever recorded is 161.3 kph);
#: the pitch is 20.12 m long and 3.05 m wide, with slack for wides and for
#: full tosses whose projected bounce lands behind the batter.
PLAUSIBLE_RANGES: dict[str, tuple[float, float]] = {
    "ballSpeed": (15.0, 45.0),
    "pitchX": (-2.0, 2.0),
    "pitchY": (-5.0, 20.12),
    "stumpsX": (-2.0, 2.0),
    "stumpsY": (0.0, 3.0),
}

#: ``bowlingStyle`` values that are pace. The other four are spin.
PACE_STYLES: frozenset[str] = frozenset({"FAST_SEAM", "MEDIUM_SEAM", "SEAM"})


def download(*, force: bool = False) -> Path:
    """Fetch the men's IPL CSV into ``data/raw``. Cached unless ``force``."""
    PATHS.ensure()
    dest = PATHS.raw / _FILENAME
    if dest.exists() and not force:
        return dest
    with urlopen(_URL) as response, dest.open("wb") as fh:
        fh.write(response.read())
    return dest


def bowler_type(df: pd.DataFrame) -> pd.Series:
    """Arm and style in one label: ``RIGHT_FAST_SEAM``, ``LEFT_ORTHODOX``, ...

    Caveat: ``SEAM`` is upstream's fallback style, and its arm flag is
    unreliable — ``LEFT_SEAM`` includes plenty of right-arm bowlers.
    """
    arm = np.where(df["rightArmedBowl"], "RIGHT_", "LEFT_")
    return pd.Series(arm, index=df.index) + df["bowlingStyle"]


def load_hawkeye(path: Path | None = None, *, clean: bool = True) -> pd.DataFrame:
    """Load the delivery-level Hawk-Eye table, with a ``bowler_type`` column added.

    Args:
        path: Defaults to ``data/raw/mensIPLHawkeyeStats.csv``.
        clean: Drop rows the tracker did not measure (missing coordinates,
            ``ballSpeed == -1``) or measured impossibly (``PLAUSIBLE_RANGES``).
            Dropping is right for clustering: an imputed measurement would be
            a delivery nobody bowled.

    Raises:
        FileNotFoundError: If the CSV isn't there — run ``make hawkeye``.
        KeyError: If a feature or label column is missing.
    """
    path = path or (PATHS.raw / _FILENAME)
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run:  make hawkeye")

    df = pd.read_csv(path)
    missing = set(FEATURE_COLUMNS + LABEL_COLUMNS) - set(df.columns)
    if missing:
        raise KeyError(f"{path.name} is missing required columns: {sorted(missing)}")

    if clean:
        keep = df[list(FEATURE_COLUMNS)].notna().all(axis=1)
        for col, (lo, hi) in PLAUSIBLE_RANGES.items():
            keep &= df[col].between(lo, hi)
        df = df.loc[keep].reset_index(drop=True)

    return df.assign(bowler_type=bowler_type(df))
