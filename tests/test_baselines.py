from __future__ import annotations

import numpy as np
import pandas as pd

from cricketml.models import CurrentRunRateProjection, MajorityClass, TeamMeanScore


def test_run_rate_projection_matches_the_commentator() -> None:
    X = pd.DataFrame({"runs_so_far": [60.0], "balls_so_far": [36.0], "total_overs": [20.0]})
    pred = CurrentRunRateProjection().fit(X).predict(X)
    # 10 an over for 6 overs -> 200 at the same rate.
    assert np.isclose(pred[0], 200.0)


def test_team_mean_falls_back_to_the_global_mean() -> None:
    X = pd.DataFrame({"batting_team": ["A", "A", "B"]})
    model = TeamMeanScore().fit(X, np.array([100.0, 200.0, 300.0]))
    unseen = pd.DataFrame({"batting_team": ["A", "C"]})
    assert np.allclose(model.predict(unseen), [150.0, 200.0])


def test_majority_class_predicts_the_base_rate() -> None:
    y = np.array([0] * 9 + [1])
    model = MajorityClass().fit(np.zeros((10, 1)), y)
    assert np.isclose(model.predict_proba(np.zeros((3, 1)))[:, 1], 0.1).all()
