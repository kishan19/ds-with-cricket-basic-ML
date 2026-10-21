# Data

This repo uses three kinds of data, documented separately below:
**Cricsheet** (public and licensed; every lesson can rely on it), **Hawk-Eye
ball tracking** from the HawkeyeStats repo (public but unlicensed; downloaded
on demand, never committed), and a **proprietary ball-tracking export**
(local-only; no lesson currently needs it).

## Cricsheet — the default source

All scorecard-level data comes from **[Cricsheet](https://cricsheet.org)** —
ball-by-ball JSON for most professional cricket, published under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

This is a deliberate choice. Cricsheet is openly licensed, versioned, complete
to the delivery, and can be redistributed with attribution. Scraping a scorecard
site would give a repo that is legally awkward to share and that silently breaks
— neither is acceptable for something meant to be handed to other people.

**Attribution requirement:** every published chart and any derived dataset must
credit Cricsheet. `cricketml.viz.annotate_source()` does this for charts.

## Building it

```bash
make data                # IPL — the default, ~1,250 matches, seconds to build
make data SOURCE=t20i    # men's T20 internationals
make data SOURCE=odi
make data SOURCE=test
make data SOURCE=wt20i   # women's T20 internationals
```

Downloads land in `data/raw/` and are cached. Flattened tables are written to
`data/processed/` as parquet.

## The two tables

**`{source}_matches.parquet`** — one row per match: date, season, venue, city,
both teams, toss winner and decision, result, margin, overs per innings.

**`{source}_deliveries.parquet`** — one row per ball bowled: match id, innings,
over, ball, batter, non-striker, bowler, runs split into batter/extras/total,
each extra type, and wicket details.

## Three things the flattener already gets right

Each of these is a bug that silently corrupts cricket analysis, so they are
handled once, in `cricketml.data.cricsheet`, and tested:

1. **Wides and no-balls are not balls faced.** `is_legal_ball` marks the
   difference, and `ball_in_innings` only advances on legal deliveries. Count
   raw rows instead and every strike rate you compute is wrong.
2. **Run-outs are not the bowler's wicket.** `is_wicket` is any dismissal;
   `is_bowler_wicket` is the subset credited to the bowler. In IPL data that is
   a ~8% difference — enough to reorder a bowling leaderboard.
3. **Super overs are tagged, not merged.** Three-ball innings destroy per-innings
   aggregates. `load_deliveries()` drops them by default.

## Why `data/` is not in git

Data is downloadable and licensed to someone else. The repo commits the *code
that produces* the tables, which is reproducible and reviewable; the tables
themselves are build output. `.gitignore` enforces it and pre-commit blocks
files over 2 MB.

## Hawk-Eye ball tracking — HawkeyeStats

The K-means lesson uses per-delivery ball tracking from
**[alittlefitness/HawkeyeStats](https://github.com/alittlefitness/HawkeyeStats)**.
That repo is a tidy CSV of the Hawk-Eye numbers the ICC's Pulselive API
(`cricketapi-icc.pulselive.com`) publishes per delivery. It did all of the
collection and tidying; this repo only downloads `mensIPLHawkeyeStats.csv` and
cleans it.

```bash
make hawkeye     # ~20 MB into data/raw/mensIPLHawkeyeStats.csv
```

**Licence: none stated upstream.** So the CSV is never committed, sampled into a
committed artefact, or redistributed. It is fetched on demand like Cricsheet.
Credit the repo on anything derived from it; `cricketml.data.hawkeye.ATTRIBUTION`
is the chart footer.

**What the lesson uses** (`cricketml.data.hawkeye`):

| column | role | meaning |
|---|---|---|
| `ballSpeed` | feature | release speed, m/s (`-1` = tracker failed) |
| `pitchX`, `pitchY` | feature | where it bounced, m: across the pitch (line), distance from the batter's stumps (length) |
| `stumpsX`, `stumpsY` | feature | where it passed the stumps, m: across, and height |
| `bowler` | label | held out, used to interpret clusters |
| `rightArmedBowl`, `bowlingStyle` | label | combined into `bowler_type`: `RIGHT_FAST_SEAM`, `LEFT_ORTHODOX`, … |

**Two traps, both handled or flagged in code:**

1. **Tracker failures and impossible readings.** About 6% of rows have
   `ballSpeed == -1` or no coordinates. A few hundred more are physically
   impossible (for example, a bounce 897 m down a 20 m pitch).
   `load_hawkeye()` drops anything outside `PLAUSIBLE_RANGES`.
2. **`bowlingStyle == "SEAM"` is a fallback, and its arm flag is unreliable.**
   `LEFT_SEAM` is mostly right-armers (Mohit Sharma, L Balaji), and
   `RIGHT_SEAM` includes a leg-spinner (Samuel Badree). Treat `*_SEAM` as
   unverified when grading against it. The other six styles check out.

The `X` coordinates are fixed to the pitch, not to the batter. A ball on a
left-hander's off stump has the opposite sign to the same ball bowled to a
right-hander.

## Ball-tracking data — proprietary, unused

An earlier version of the K-means lesson used per-delivery physics
— release speed, swing, seam deviation, where the ball pitched and passed the
stumps — that Cricsheet does not have. There is no public source for this at
all; it is a proprietary export supplied locally as **`data/raw/data.csv`** and
read by `cricketml.data.ball_tracking.load_ball_tracking()`.

**This file is never committed, never sampled into a committed artefact, and
cannot be downloaded by `make data`.** No lesson currently needs it; the loader
is kept for lessons that want swing and seam deviation, which Hawk-Eye's public
feed doesn't include.

**Required schema** (`cricketml.data.ball_tracking.REQUIRED_COLUMNS`):

| column | meaning |
|---|---|
| `release_speed_kph`, `swing_angle`, `deviation` | how the ball moved through the air |
| `bounce_position_x`, `bounce_angle`, `drop_angle` | length — where and how it bounced |
| `stumps_position_y` | line — how far off the stumps it passed |
| `batting_hand`, `bowling_hand`, `bowling_type` | context — held out as labels, never features |
| `runs`, `wicket` | outcome — held out, checked against clusters afterwards |

A licensed export from a different provider, or a synthetic stand-in, works
without touching any lesson code as long as it has these columns — that's the
point of routing every read through `load_ball_tracking()` rather than a
hardcoded path. `tests/fixtures/ball_tracking_sample.csv` is a small **synthetic**
dataset (fabricated, not derived from anyone's real export) used to test the
loader itself, so CI and a fresh clone never need the real file.
