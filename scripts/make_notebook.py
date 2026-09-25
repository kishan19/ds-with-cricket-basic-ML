"""Build a lesson notebook from a list of (kind, source) cells.

Notebooks are generated rather than hand-edited so that the seven-section
skeleton is identical in every lesson. Run via `python scripts/make_notebook.py`.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SETUP = """\
import pandas as pd

from cricketml import SEED
from cricketml.data import load_deliveries, load_matches
from cricketml.evaluation import regression_report_row, temporal_split
from cricketml.features import innings_totals, powerplay_summary
from cricketml.models import CurrentRunRateProjection, TeamMeanScore
from cricketml.viz import use_theme

use_theme()
pd.set_option("display.precision", 3)
SEED"""


def notebook(cells: list[tuple[str, str]]) -> dict:
    return {
        "cells": [
            {
                "id": f"c{i:02d}",
                "cell_type": kind,
                "metadata": {},
                "source": src.splitlines(keepends=True),
                **({"outputs": [], "execution_count": None} if kind == "code" else {}),
            }
            for i, (kind, src) in enumerate(cells)
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python (cricketml)",
                "language": "python",
                "name": "cricketml",
            },
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def write(path: Path, cells: list[tuple[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(notebook(cells), indent=1) + "\n")
    print(f"wrote {path.relative_to(ROOT)}")


SECTIONS = [
    ("1. The cricket question", "One sentence a fan would ask. No ML words."),
    ("2. The data", "Which table, what grain, what is excluded — and why."),
    ("3. The naive answer", "The commentator's rule, scored on the test set."),
    ("4. The idea", "Cricket paragraph first. Then the maths. Then the assumption."),
    ("5. Build it", "Short. Split with `cricketml.evaluation.splits`. Seed is `SEED`."),
    ("6. Judge it", "One results table, baseline included. Then say it in prose."),
    ("7. What it gets wrong", "Failure modes, and the concept that fixes them next."),
]


def template_cells() -> list[tuple[str, str]]:
    cells: list[tuple[str, str]] = [
        (
            "markdown",
            "# Lesson NN — <cricket question as a title>\n\n"
            "**Concept:** <the ML idea>  \n"
            "**Cricket question:** <the fan's question>  \n"
            "**Data:** <source, format, period>\n\n"
            "> Sections below are fixed by `docs/lesson-contract.md`. "
            "Do not add, remove or reorder them.",
        ),
        ("code", SETUP),
    ]
    for title, hint in SECTIONS:
        cells.append(("markdown", f"## {title}\n\n_{hint}_"))
        if title != "1. The cricket question":
            cells.append(("code", "# TODO"))
    return cells


LESSON_01 = [
    (
        "markdown",
        """# Lesson 01 — How many will they get from here?

**Concept:** linear regression, and the baseline it has to beat
**Cricket question:** six overs are gone. What will the first-innings total be?
**Data:** IPL ball-by-ball, Cricsheet, 2008–present

> Sections are fixed by `docs/lesson-contract.md`. Do not add, remove or reorder them.""",
    ),
    (
        "code",
        """import pandas as pd
from sklearn.linear_model import LinearRegression

from cricketml import SEED
from cricketml.data import load_deliveries
from cricketml.evaluation import regression_report_row, temporal_split
from cricketml.features import innings_totals, powerplay_summary
from cricketml.models import CurrentRunRateProjection, TeamMeanScore
from cricketml.viz import annotate_source, use_theme

use_theme()
pd.set_option("display.precision", 3)
SEED""",
    ),
    (
        "markdown",
        """## 1. The cricket question

The powerplay is over. The score is 58 for 1. Every commentator in the world now
says a number out loud — *"they'll fancy 190 from here"* — and every viewer has
an opinion about it.

That guess is a prediction from data. This lesson makes it one explicitly, and
then asks the only question that matters: **is the machine's guess better than
the commentator's?**""",
    ),
    (
        "markdown",
        """## 2. The data

**Grain:** one row per innings. Features come from the first 6 overs; the target
is the final total.

**Exclusions, and why:**

- **Second innings dropped.** A team chasing 140 stops at 141. The target is
  censored by the chase, so it is not the same quantity as a first-innings
  total. Mixing them teaches the model that chases are low-scoring.
- **Innings under 100 balls dropped.** Rain-shortened games have a different
  target entirely.
- **Innings with fewer than 30 powerplay balls dropped.** No powerplay, no
  features.
- **Super overs dropped** by `load_deliveries` — three-ball innings wreck
  per-innings aggregates.""",
    ),
    (
        "code",
        """deliveries = load_deliveries("ipl")

totals = innings_totals(deliveries)
powerplay = powerplay_summary(deliveries, overs=6)

KEYS = ["match_id", "date", "innings", "batting_team"]
df = (
    powerplay.merge(totals, on=KEYS)
    .query("innings == 1 and balls >= 100 and pp_balls >= 30")
    .reset_index(drop=True)
)

print(f"{len(df):,} first innings, {df.date.min():%Y} to {df.date.max():%Y}")
df.head()""",
    ),
    (
        "markdown",
        """A temporal split, not a random one. Predicting 2019 with a model that has read
2024 is not a forecast, it is a memory — and it is the single most common way a
cricket model flatters itself.""",
    ),
    (
        "code",
        """train, test = temporal_split(df, test_size=0.2)
print(f"train {len(train):,} innings, up to {train.date.max():%d %b %Y}")
print(f"test  {len(test):,} innings, from  {test.date.min():%d %b %Y}")""",
    ),
    (
        "markdown",
        """## 3. The naive answer

Two rules that need no machine learning at all:

1. **Current run rate.** Score so far, extended at the same rate to 20 overs.
   This is literally what the commentator says.
2. **Team mean.** Look up what this team usually scores.

Both are scored on the same test set, with the same metric, before any model is
fitted.""",
    ),
    (
        "code",
        """FEATURES = ["pp_runs", "pp_wickets", "pp_boundaries", "pp_dots"]

def as_projection_input(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.assign(
        runs_so_far=frame.pp_runs, balls_so_far=frame.pp_balls, total_overs=20
    )

crr = CurrentRunRateProjection().fit(as_projection_input(train))
pred_crr = crr.predict(as_projection_input(test))

baseline = regression_report_row(test.total_runs, pred_crr, model="Current run rate")
BASELINE_RMSE = baseline["rmse"]

pred_team = TeamMeanScore().fit(train, train.total_runs).predict(test)
team_row = regression_report_row(
    test.total_runs, pred_team, model="Team mean", baseline=BASELINE_RMSE
)

pd.DataFrame([baseline, team_row])""",
    ),
    (
        "markdown",
        """Worth pausing on. **The commentator beats the record book.** Knowing how this
team is going right now is more use than knowing how they usually go. That is
already a real finding, and it came from two lines of arithmetic.

Note also the negative R². Both baselines are *worse than predicting the overall
mean every time*. R² is a comparison against a constant, and a rule that
extrapolates a six-over run rate to twenty overs overshoots badly — teams do not
score at the powerplay rate throughout.""",
    ),
    (
        "markdown",
        """## 4. The idea

**In cricket.** The commentator uses one number — the run rate — and multiplies
it. But he *knows* more than that. He knows two down is worse than none down. He
knows 58 off boundaries is different from 58 in ones and twos. Linear regression
is the machinery for using all of those at once, each with a weight the data
chooses rather than a weight you assert.

**In maths.** We assume the final total is a weighted sum of what we observed,
plus noise:

$$\\hat{y} = \\beta_0 + \\beta_1 x_1 + \\dots + \\beta_k x_k$$

and pick the $\\beta$ that minimise the squared error on the training innings.
Closed form, no tuning, no seed sensitivity.

**The assumption, and whether cricket satisfies it.** Linearity says each extra
powerplay run is worth the same number of final runs, whether the score is 30
or 80. Cricket only roughly agrees: a flying start changes the batting team's
intent, not just its arithmetic. That the assumption is imperfect is exactly why
section 7 exists.""",
    ),
    (
        "markdown",
        """## 5. Build it

First, a check that takes one line and saves an hour of nonsense. `pp_run_rate`
looks like a sensible feature, so why is it not in `FEATURES`?""",
    ),
    ("code", """df[["pp_runs", "pp_run_rate"]].corr().iloc[0, 1]"""),
    (
        "markdown",
        """A correlation of **0.999997**. Not "high" — identical to rounding error. The
powerplay is six overs, so
`pp_balls` is 36 in all but one innings of the whole dataset, which makes run
rate a rescaling of runs and nothing else.

Two perfectly collinear features do not break the fit — it still scores the same
— but they destroy the coefficients: least squares splits the credit between them
arbitrarily, and you get `pp_runs = +18.7` alongside `pp_run_rate = -106.2`,
two large numbers that cancel and mean nothing. Anyone reading those coefficients
as cricket would conclude that scoring faster lowers your score.

**Drop the redundant one.** Regularisation handles this more gracefully, and that
is lesson 05 — but noticing it is free, and noticing beats patching.""",
    ),
    (
        "code",
        """model = LinearRegression().fit(train[FEATURES], train.total_runs)
pred_lr = model.predict(test[FEATURES])

pd.Series(model.coef_, index=FEATURES, name="runs per unit").sort_values()""",
    ),
    (
        "markdown",
        """Now read them as cricket:

| feature | coefficient | what it says |
|---|---|---|
| `pp_runs` | **+1.0** | A powerplay run is worth almost exactly one final run — no more, no less |
| `pp_wickets` | **-7.6** | A wicket inside the first six overs costs nearly eight runs off the final total |
| `pp_boundaries` | **+1.1** | A boundary is worth its runs *plus another*, because it is evidence about the batter and the pitch, not just an addition to the score |
| `pp_dots` | **+0.5** | Positive?! |

That last one looks wrong until you remember every coefficient is *conditional on
the others*. Holding powerplay runs fixed, more dot balls means the same runs
arrived in fewer, bigger hits — the boundary-hitting template, which keeps
scoring. Dots are not good; dots **alongside the same score** are a signal about
how that score was made.

This is the habit the rest of the curriculum is built on: a coefficient is never
read alone.""",
    ),
    ("markdown", """## 6. Judge it"""),
    (
        "code",
        """results = pd.DataFrame([
    baseline,
    team_row,
    regression_report_row(
        test.total_runs, pred_lr, model="Linear regression", baseline=BASELINE_RMSE
    ),
])
results""",
    ),
    (
        "code",
        """ax = (
    results.set_index("model")["rmse"]
    .sort_values()
    .plot.barh(title="Error predicting the first-innings total (RMSE, runs)")
)
ax.bar_label(ax.containers[0], fmt="%.1f", padding=4)
ax.set_xlabel("RMSE (runs) — lower is better")
ax.set_ylabel("")
annotate_source(ax)""",
    ),
    (
        "markdown",
        """**In prose.** Linear regression cuts the commentator's error by about a fifth —
from roughly 39 runs to roughly 31. R² turns positive, so unlike the baselines
it is at least better than always guessing the average.

But state the size honestly. An RMSE near 30 runs means a typical prediction of
"175" is really "somewhere between 145 and 205". That is a wide enough band to
contain a comfortable win and a collapse. After six overs, a T20 innings is
genuinely uncertain, and the right output of this model is a range, not a
number. Any single-figure projection on a broadcast is theatre.""",
    ),
    (
        "markdown",
        """## 7. What it gets wrong

- **It ignores the pitch.** A venue feature is missing, and Chinnaswamy is not
  Chepauk. → *feature engineering*
- **It ignores the opposition.** Facing the best death bowling attack in the
  league is not the same as facing the worst. → *feature engineering*
- **It assumes linearity.** The 80-for-0 innings and the 30-for-3 innings are not
  two points on the same straight line; intent changes. → *trees and non-linear
  models*
- **It has no error bars**, and we just established that the error bar is the
  most important part of the answer. → *prediction intervals, quantile
  regression*
- **It was trained on eighteen seasons of a changing game.** A 2010 par score is
  not a 2026 par score. → *distribution shift*

**Next:** lesson 02 adds venue and opposition, and shows how fast a
feature-engineering idea can turn into leakage if you compute it carelessly.""",
    ),
]


if __name__ == "__main__":
    write(ROOT / "lessons" / "_template" / "lesson.ipynb", template_cells())
    write(ROOT / "lessons" / "01-powerplay-to-total-linear-regression" / "lesson.ipynb", LESSON_01)
