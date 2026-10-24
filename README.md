# Machine learning, explained through cricket

[![ci](https://github.com/kishan19/ds-with-cricket-basic-ML/actions/workflows/ci.yml/badge.svg)](https://github.com/kishan19/ds-with-cricket-basic-ML/actions/workflows/ci.yml)
[![data: Cricsheet](https://img.shields.io/badge/data-Cricsheet%20CC%20BY%204.0-2a78d6)](https://cricsheet.org)
[![licence: MIT](https://img.shields.io/badge/licence-MIT-informational)](LICENSE)

Every machine learning concept, taught through a question a cricket fan would
actually ask.

Not *"here is logistic regression, and here is a cricket dataset to try it on."*
The other way round: **"who is winning this match right now?"** — and then the
discovery that answering it honestly requires logistic regression, and calibrated
probabilities, and a split that does not read tomorrow's newspaper.

Cricket is an unusually good teacher. It is a game of averages that everyone
already argues about; it generates dense, openly licensed, ball-by-ball data; and
almost every statistical trap has a cricketing name people already understand.
Overfitting is picking a player on one good season. Leakage is choosing the XI
after seeing the result. Class imbalance is that wickets almost never happen.

---

## Two things this repo is

**A learning log.** I am working through ML fundamentals properly rather than by
recall, one concept at a time, with the working shown. Lessons are in order and
build on each other.

**A teaching tool.** Every lesson is written to be handed to someone else — a
colleague, a mentee, a cricket-mad friend who wants to know what a data scientist
actually does. Which means the reasoning is visible, the baselines are honest,
and the failures are documented rather than trimmed out.

Those two goals mostly agree. Where they disagree, the second wins: the discipline
of writing for a reader is what stops "I ran a model and got 0.8" from counting
as understanding.

---

## Start here

```bash
git clone https://github.com/kishan19/ds-with-cricket-basic-ML.git
cd ds-with-cricket-basic-ML

make setup      # uv venv, all deps, pre-commit hooks, Jupyter kernel
make data       # ~1,250 IPL matches from Cricsheet — takes about 6 seconds
make lab        # open lessons/01-powerplay-to-total-linear-regression/
```

Needs [uv](https://docs.astral.sh/uv/) and Python 3.11+. `make` on its own lists
every command.

---

## The curriculum

Nineteen lessons in six phases. Each is one cricket question and one concept,
and each ends by naming the problem that makes the next one necessary.

### Phase 1 · The three foundations

A number, a probability, and a pattern nobody labelled: one of each of the
three things machine learning does, before anything is refined.

| # | The question | The concept | |
|---|---|---|---|
| 01 | How many will they get from here? | Linear regression, and the baseline it must beat | ✅ [lesson](lessons/01-powerplay-to-total-linear-regression/) |
| 02 | Who is winning the chase? | Logistic regression, and why a forecast should be a probability | |
| 03 | Can we find delivery types without being told what they are? | K-means clustering | |

### Phase 2 · Trees

| # | The question | The concept | |
|---|---|---|---|
| 04 | What is a par score on this pitch? | Decision trees, and non-linearity | |
| 05 | Can many rough guesses beat one careful one? | Random forests and gradient boosting | |

### Phase 3 · Reading the game

| # | The question | The concept | |
|---|---|---|---|
| 06 | Does the ground change the score? | Feature engineering — and how fast it becomes leakage | |
| 07 | Who is actually the better batter? | The average trap: not-outs, medians, and what a mean hides | |
| 08 | Is he in form, or just lucky? | Sampling variance and regression to the mean | |

### Phase 4 · Sharper predictions

| # | The question | The concept | |
|---|---|---|---|
| 09 | Which of forty player stats actually matter? | Regularisation — ridge, lasso, and collinearity | |
| 10 | How sure are we about "they'll get 180"? | Prediction intervals and quantile regression | |
| 11 | Will this ball be a wicket? | Class imbalance, and why accuracy lies | |
| 12 | Should they review that LBW? | Precision, recall, and the threshold as a decision | |
| 13 | Does "70% chance" mean 70%? | Calibration | |

### Phase 5 · Finding structure

| # | The question | The concept | |
|---|---|---|---|
| 14 | Can forty stats become three? | PCA and dimensionality reduction | |
| 15 | Which teams play alike? | Similarity and embeddings | |

### Phase 6 · Earning trust

| # | The question | The concept | |
|---|---|---|---|
| 16 | Why did the model say that? | Feature importance and SHAP | |
| 17 | Does winning the toss cause winning? | Causal inference and confounding | |
| 18 | Why did last year's model stop working? | Distribution shift and monitoring | |
| 19 | Can we believe a three-innings average? | Bayesian shrinkage and priors | |

---

## Every lesson has the same seven sections

This is the spine of the whole project, and the reason it should stay readable at
lesson 19. Full version in **[`docs/lesson-contract.md`](docs/lesson-contract.md)**.

1. **The cricket question** — one sentence, no ML vocabulary
2. **The data** — the grain, and every exclusion with its reason
3. **The naive answer** — the commentator's rule, scored first
4. **The idea** — in cricket, then in maths, then the assumption it makes
5. **Build it** — short, with a leakage-safe split
6. **Judge it** — one results table, baseline included, read out loud in prose
7. **What it gets wrong** — the failure modes, and the concept that fixes them

Sections 3 and 7 are the ones people skip, so they are mandatory. A model is not
a result until it has beaten something and admitted what it cannot do.

### The rules that never change

| Rule | Why |
|---|---|
| Split only with `cricketml.evaluation.splits` | Cricket data is temporal *and* grouped by match; a shuffled split invents skill that is not there |
| Seed is `cricketml.SEED` (1983) | A lesson re-run next year prints the numbers its prose quotes |
| Baseline before model, always | Complexity is earned, not assumed |
| Classifiers return probabilities, not labels | The threshold is a cricketing decision, not a default |
| Charts via `cricketml.viz.use_theme()` | Blue means the same thing in lesson 1 and lesson 19 |
| Notebook outputs stripped on commit | Enforced by pre-commit; diffs stay reviewable |
| If two lessons need it, it moves to `src/` | Lesson code is narrative; shared code is tested |

---

## What is in `src/`

The shared machinery, so no two lessons can disagree about how a model is judged.

```
src/cricketml/
├── config.py            paths, the seed, cricket constants
├── data/
│   ├── cricsheet.py     download + flatten Cricsheet JSON → two parquet tables
│   └── __init__.py      load_matches() / load_deliveries()
├── features/innings.py  innings totals, powerplay summaries, chase states
├── models/baselines.py  the rules a model has to beat
├── evaluation/
│   ├── splits.py        temporal_split, season_split, match_group_cv
│   └── metrics.py       one-row scorecards, identical across lessons
└── viz/theme.py         one colourblind-safe palette, applied once
```

Three cricket-specific bugs are handled once, here, and covered by tests — wides
and no-balls are not balls faced, run-outs are not the bowler's wicket, and super
overs are not innings. Each of them silently corrupts analysis that does not
account for it. See **[`docs/data.md`](docs/data.md)**.

---

## Data

[Cricsheet](https://cricsheet.org) — ball-by-ball JSON for most professional
cricket, under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Openly
licensed, complete to the delivery, and redistributable with attribution, which
is exactly what a repo meant to be shared needs.

```bash
make data                # IPL (default)
make data SOURCE=t20i    # also: odi, test, wt20i, wbbl
```

Downloads are cached in `data/raw/`; flattened tables land in `data/processed/`.
Neither is committed — the repo holds the code that produces them.

**Ball tracking** (the K-means lesson only) comes from
[alittlefitness/HawkeyeStats](https://github.com/alittlefitness/HawkeyeStats):
Hawk-Eye speed, pitch and stumps positions for every IPL delivery the ICC's feed
covers, tidied into one CSV by that repo's author. It has no stated licence, so
it's downloaded rather than committed:

```bash
make hawkeye
```

---

## Working on it

```bash
make check      # lint + typecheck + tests, the same as CI
make test
make fmt
```

New lesson:

```bash
cp -r lessons/_template lessons/NN-short-slug
```

Then fill in the seven sections, add the row to the roadmap above, and run
`make check`.

---

## Reference

- **[`docs/lesson-contract.md`](docs/lesson-contract.md)** — the seven sections, in full
- **[`docs/glossary.md`](docs/glossary.md)** — cricket ↔ ML, both directions
- **[`docs/data.md`](docs/data.md)** — sources, licence, and the three traps

## Licence

Code MIT (see [LICENSE](LICENSE)). Data © Cricsheet, CC BY 4.0 — if you reuse the
charts or derived tables, credit Cricsheet. Ball-tracking data is Hawk-Eye via
the ICC, tidied by [alittlefitness/HawkeyeStats](https://github.com/alittlefitness/HawkeyeStats);
credit that repo, and note it carries no licence of its own.
