# Data

## Source

All data comes from **[Cricsheet](https://cricsheet.org)** — ball-by-ball JSON
for most professional cricket, published under
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
