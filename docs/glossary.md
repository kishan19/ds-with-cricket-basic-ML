# Cricket ↔ machine learning

The translation table this repo is built on. The left column is what a fan
already understands; the right is what the textbook calls it. Lessons always
introduce the left before the right.

## Cricket for the data scientist

| Term | What it means | Why the model cares |
|---|---|---|
| Innings | One team's turn to bat | The natural unit of a "match outcome" row |
| Over | Six legal balls from one bowler | The clock; almost every rate is per over |
| Powerplay | First 6 overs (T20) / 10 (ODI) with fielding limits | A clean information cut-off: everything before it is a legal feature |
| Wicket | A batter is dismissed | The rare event; ~5% of legal balls in the IPL |
| Extras | Wides, no-balls, byes, leg-byes | Runs not credited to the batter; wides and no-balls are not a ball faced |
| Strike rate | Runs per 100 balls | Scoring speed — the T20 currency |
| Batting average | Runs ÷ times **out** | Not runs ÷ innings. Not-outs inflate it; see the "average trap" lesson |
| Economy rate | Runs conceded per over | The bowler's mirror of strike rate |
| Toss | Coin flip deciding who bats first | The tempting confounder in every "does X cause winning" question |
| DLS | Duckworth–Lewis–Stern par score | A hand-built model — and the benchmark any score predictor should respect |
| Death overs | The last ~4 overs | A different scoring regime; pooling them with the rest hides structure |

## ML in cricket terms

| Concept | The cricket version |
|---|---|
| Features / target | The scorecard so far / the final total |
| Baseline | What the commentator says before the model speaks |
| Overfitting | Picking a player on one great season |
| Regularisation | Selection bias toward proven performers over hot streaks |
| Train/test leakage | Picking the XI after seeing the result |
| Temporal split | Never using 2024 to predict 2019 |
| Grouped CV | Keeping a whole match inside one fold — same pitch, same dew |
| Class imbalance | Predicting wickets, which almost never happen |
| Precision vs recall | Reviewing every LBW shout vs never wasting a review |
| Calibration | "70% chance" should win about 70 times in 100 |
| Regression to the mean | The purple-patch batter returning to his average |
| Confounding | Winning the toss vs winning at a venue where the toss matters |
| Shrinkage / Bayesian priors | Not believing a 3-innings average |
| Feature importance | Which part of the scorecard actually decided the game |
| Distribution shift | A model trained on 2010 pitches, scoring 2026 cricket |
