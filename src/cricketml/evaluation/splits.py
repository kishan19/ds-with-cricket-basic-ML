"""Leakage-safe splitting for cricket data.

Cricket data breaks the i.i.d. assumption in two ways at once:

1. **Time.** A model that trained on the 2024 season and is tested on 2019 has
   read tomorrow's newspaper. Every split here is ordered by date.
2. **Grouping.** Deliveries within one match share a pitch, a toss, a dew
   factor and two teams. Put some balls of a match in train and the rest in
   test, and the test score is fiction.

So: never `train_test_split(shuffle=True)` on ball-by-ball data. Use these.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold

__all__ = ["match_group_cv", "season_split", "temporal_split"]


def temporal_split(
    df: pd.DataFrame,
    date_col: str = "date",
    test_size: float = 0.2,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split chronologically: the oldest ``1 - test_size`` trains, the newest tests.

    The cut is placed on a *date* boundary, not a row boundary, so a single
    match is never torn in half.

    Args:
        df: Any frame with a date column.
        date_col: Name of that column (parsed to datetime if it is not already).
        test_size: Fraction of *matches* held out, taken from the end.

    Returns:
        ``(train, test)``, each preserving the original row order.
    """
    if not 0 < test_size < 1:
        raise ValueError(f"test_size must be in (0, 1), got {test_size}")

    dates = pd.to_datetime(df[date_col])
    unique_dates = np.sort(dates.unique())
    if len(unique_dates) < 2:
        raise ValueError("Need at least two distinct dates to split chronologically.")

    cut_idx = int(len(unique_dates) * (1 - test_size))
    cut_idx = min(max(cut_idx, 1), len(unique_dates) - 1)
    cutoff = unique_dates[cut_idx]

    is_train = (dates < cutoff).to_numpy()
    return df.loc[is_train].copy(), df.loc[~is_train].copy()


def season_split(
    df: pd.DataFrame,
    season_col: str = "season",
    test_seasons: int = 1,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Hold out the last ``test_seasons`` whole seasons.

    Preferred over :func:`temporal_split` whenever the data has a natural
    season, because it matches how the model would really be used: you fit on
    everything played so far and predict the tournament that hasn't started.
    """
    seasons = np.sort(df[season_col].unique())
    if len(seasons) <= test_seasons:
        raise ValueError(
            f"Need more than {test_seasons} season(s) to hold out; found {len(seasons)}."
        )
    held_out = set(seasons[-test_seasons:])
    is_test = df[season_col].isin(held_out).to_numpy()
    return df.loc[~is_test].copy(), df.loc[is_test].copy()


def match_group_cv(
    df: pd.DataFrame,
    n_splits: int = 5,
    group_col: str = "match_id",
) -> tuple[GroupKFold, np.ndarray]:
    """Cross-validation that keeps every match wholly inside one fold.

    Returns the splitter and the group vector, ready for
    ``cross_val_score(..., cv=cv, groups=groups)``. ``GroupKFold`` is
    deterministic, so no seed is needed.
    """
    if group_col not in df.columns:
        raise KeyError(
            f"{group_col!r} not in frame. Grouping by match is not optional — "
            "without it, deliveries from the same game leak across folds."
        )
    n_groups = df[group_col].nunique()
    if n_groups < n_splits:
        raise ValueError(f"{n_splits} folds requested but only {n_groups} matches available.")

    return GroupKFold(n_splits=n_splits), df[group_col].to_numpy()
