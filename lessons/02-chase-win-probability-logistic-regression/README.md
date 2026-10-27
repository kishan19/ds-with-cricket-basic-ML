# Lesson 02 — Learning Logistic Regression: Who is winning the chase?

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kishan19/ds-with-cricket-basic-ML/blob/main/lessons/02-chase-win-probability-logistic-regression/lesson.ipynb)

| | |
|---|---|
| **Concept** | Logistic regression, and why a forecast should be a probability |
| **Cricket question** | Halfway through a chase, who is going to win? |
| **Data** | IPL ball-by-ball (Cricsheet), 1,195 chases as 21,376 end-of-over states, 2008–2026 |
| **Baseline to beat** | "Ahead of the rate": the chasing side is winning if its run rate is at least the rate it needs |
| **Sets up** | Lesson 03: taking the answer key away entirely (clustering) |

## In one paragraph

Lesson 01 dropped every second innings, because a chase stops once the target
is reached. This lesson picks those innings up and asks the chase's own
question: who wins? The commentator's rule answers "yes" or "no", and it is
right three times in four. But because it never admits doubt, its Brier score
is worse than always saying 54%. Logistic regression on three scoreboard
numbers, runs needed, balls left and wickets in hand, nearly halves that error
and prices a wicket in hand at about 11 runs. The lesson follows one chase
throughout: Rajasthan's 224 at Eden Gardens in 2024, which the model gave 2%
with 36 balls left.

## Result

| model | AUC | Brier | accuracy | Brier vs baseline |
|---|---|---|---|---|
| Base rate | 0.500 | 0.249 | 0.53 | +1% |
| Ahead of the rate *(baseline)* | 0.754 | 0.252 | 0.75 | — |
| Logistic: scoreboard | 0.898 | 0.147 | 0.79 | +42% |
| **Logistic: + required rate** | **0.910** | **0.138** | **0.80** | **+45%** |

Test set: the most recent 20% of chase dates (220 chases, 3,877 states, from
18 May 2023).

## Three things worth stealing from this lesson

1. **Certainty is expensive.** A 0-or-1 rule that is right 75% of the time
   loses on Brier score to a constant that knows nothing about the match.
   Classifiers return probabilities in this repo for exactly this reason.
2. **Ratios of coefficients are exchange rates.** −0.056 per run needed and
   +0.604 per wicket in hand mean one wicket is worth about 11 runs, or about
   two overs.
3. **Calibrated on the past is not calibrated now.** On 2008–2023 chases the
   model's 50% means 49%. On 2023–2026 chases it means 70%. The ranking held up
   but the percentages went stale, which is distribution shift.

## Logistic regression from scratch

The appendix builds the algorithm by hand on ten made-up chases, small enough
to draw. Lesson 01's straight line says 140% at 4 an over. A sigmoid squashes
that line into a probability, log-loss scores it, and gradient descent walks
downhill to the answer. The same function, run on all 17,499 real training
states, matches scikit-learn's coefficients.

## Run it

```bash
make data
uv run jupyter lab lessons/02-chase-win-probability-logistic-regression/lesson.ipynb
```
