# Lesson 03 — How many will they get from here?

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kishan19/ds-with-cricket-basic-ML/blob/main/lessons/03-powerplay-to-total-linear-regression/lesson.ipynb)

| | |
|---|---|
| **Concept** | Linear regression, and the baseline it has to beat |
| **Cricket question** | Six overs are gone. What will the first-innings total be? |
| **Data** | IPL ball-by-ball (Cricsheet), 1,214 first innings, 2008–2026 |
| **Baseline to beat** | Current run rate, extrapolated to 20 overs — what the commentator says |
| **Sets up** | A later lesson: venue and opposition features, and how they become leakage |

## In one paragraph

Every commentator projects a final score from the powerplay, and they do it with
one number: the run rate. Linear regression does the same job with four numbers —
runs, wickets, boundaries and dots — each weighted by what the data says rather
than by assertion. It beats the commentator by about a fifth. It also shows why
that improvement matters less than it sounds: after six overs, the honest answer
is a thirty-run range, not a number.

## Result

| model | RMSE (runs) | R² | vs baseline |
|---|---|---|---|
| Current run rate *(baseline)* | 38.8 | −0.29 | — |
| Team historical mean | 43.8 | −0.64 | −12.8% |
| **Linear regression** | **30.6** | **0.20** | **+21.2%** |

Test set: the most recent 20% of innings by date (222 innings from May 2023).

## Three things worth stealing from this lesson

1. **The commentator beats the record book.** Current form outperforms the team's
   historical average. Two lines of arithmetic, and a real finding.
2. **Collinearity is caught before it is patched.** `pp_run_rate` correlates with
   `pp_runs` at 0.999997 — the powerplay is always 36 balls. Left in, it turns
   the coefficients into cancelling nonsense (+18.7 and −106.2).
3. **A coefficient is never read alone.** Dot balls get a *positive* weight,
   which is only sensible once you see it is conditional on runs: same score,
   more dots means the runs came in boundaries.

## Run it

```bash
make data
uv run jupyter lab lessons/03-powerplay-to-total-linear-regression/lesson.ipynb
```
