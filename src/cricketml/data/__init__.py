"""Data access. Lessons call :func:`load_deliveries` / :func:`load_matches` and
nothing else — the JSON parsing lives in :mod:`cricketml.data.cricsheet` and
runs once, via ``make data``.
"""

from __future__ import annotations

import pandas as pd

from cricketml.config import PATHS

__all__ = ["load_deliveries", "load_matches"]

_HINT = "Table {name!r} not built yet. Run:  make data SOURCE={source}"


def _load(table: str, source: str) -> pd.DataFrame:
    path = PATHS.processed / f"{source}_{table}.parquet"
    if not path.exists():
        raise FileNotFoundError(_HINT.format(name=path.name, source=source))
    return pd.read_parquet(path)


def load_matches(source: str = "ipl") -> pd.DataFrame:
    """One row per match: venue, toss, season, result."""
    return _load("matches", source)


def load_deliveries(source: str = "ipl", *, drop_super_overs: bool = True) -> pd.DataFrame:
    """One row per ball bowled.

    Super overs are dropped by default: they are three-ball-innings oddities
    that quietly wreck any per-innings aggregate.
    """
    df = _load("deliveries", source)
    if drop_super_overs and "is_super_over" in df.columns:
        df = df.loc[~df["is_super_over"]].copy()
    return df
