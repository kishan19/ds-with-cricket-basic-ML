# Lesson 01 — Can we find delivery types without being told what they are?

| | |
|---|---|
| **Concept** | K-means clustering |
| **Cricket question** | Does a delivery's physics alone reveal what "kind" of ball it was? |
| **Data** | Hawk-Eye ball tracking, 140,233 IPL deliveries, from [alittlefitness/HawkeyeStats](https://github.com/alittlefitness/HawkeyeStats) |
| **Baseline to beat** | The scorecard's own arm + style label, held out and used only to interpret the clusters |
| **Sets up** | A later lesson: compressing these features with PCA |

> **Folder number vs. curriculum position.** This is lesson 01 in build order —
> the first one made — but K-means sits later in the topic sequence in the main
> README's roadmap (it needs supervised-learning basics as a contrast first).
> Reconciling folder names with the roadmap is part of the pending numbering
> pass; until then, treat the number in a folder name as "built Nth," not
> "watch Nth."

## Data, and credit

Per-delivery Hawk-Eye numbers for the IPL, collected from the ICC's Pulselive
feed and tidied into one CSV by
**[alittlefitness/HawkeyeStats](https://github.com/alittlefitness/HawkeyeStats)**.
All credit for the data goes there. That repo states no licence, so the file
isn't committed here. Download it with:

```bash
make hawkeye
```

- **Features (5):** `ballSpeed`, `pitchX`, `pitchY`, `stumpsX`, `stumpsY`: speed,
  where it bounced, and where it passed the stumps
- **Held out (interpretation only):** `bowler`, and `bowler_type` =
  `rightArmedBowl` + `bowlingStyle` combined (`RIGHT_FAST_SEAM`,
  `LEFT_FAST_SEAM`, `LEFT_ORTHODOX`, …)
- **Dropped:** 8,894 tracker failures (`ballSpeed == -1` or no coordinates) and
  297 physically impossible readings

## In one paragraph

K-means (K=4, chosen by silhouette) finds spin, then splits pace by **length**,
not by bowler style: "short of a length" against "full / yorker". Seamers of
every label land in both. Malinga and Starc lean full, while Bumrah, Steyn and
Bhuvneshwar lean short. Arm is invisible in these five numbers (ARI 0.005). The
fourth cluster is the lesson's best surprise: it's 74% *left-handed batters*,
because Hawk-Eye's `X` coordinates are fixed to the pitch, not to the batter.
K-means found the batter's stance, not a type of delivery.

## Result

| cluster | share | kph | length (m from stumps) | spin share (by label) | left-hand batters |
|---|---|---|---|---|---|
| spin | 32% | 91 | 5.3 | 80% | 29% |
| the other line | 20% | 119 | 5.8 | 25% | **74%** |
| short of a length | 32% | 132 | 9.0 | 0.3% | 27% |
| full / yorker | 16% | 133 | 3.4 | 3% | 24% |

Silhouette 0.282 at K=4 (0.265 at K=2, 0.274 at K=5). ARI against the held-out
labels: pace/spin 0.25, `bowler_type` 0.20 (excluding `*_SEAM`), arm 0.005.

**The validation label has a flaw.** `bowlingStyle == "SEAM"` is upstream's
fallback, and its arm flag is unreliable. `LEFT_SEAM` is mostly right-armers
(Mohit Sharma, L Balaji), and `RIGHT_SEAM` includes leg-spinner Samuel Badree.
Most of the non-spin 20% of the spin cluster comes from those two labels.

The from-scratch appendix shows why `KMeans` defaults to `n_init=10`. Nine of ten
single random starts agree with scikit-learn (ARI 0.96–1.00); one lands in a
worse basin (ARI 0.34, higher inertia).

## Three things worth stealing from this lesson

1. **Audit the validation label before grading against it.** Otherwise
   upstream's `SEAM` fallback would have looked like K-means' mistake.
2. **Check what your coordinates are relative to.** A pitch-fixed frame let the
   batter's stance take over a whole cluster. Mirroring `X` for left-handers is
   the one-line fix.
3. **The unit you cluster is the unit you learn about.** Clustering deliveries
   gives delivery types, like full and short. It can't give bowler types,
   because every seamer bowls both.

## Artefacts

- `lesson.ipynb` — the notebook (interactive: drag K from 2–8 live)
- `make_slides.py` — regenerates `slides/delivery-archetypes-kmeans.pdf`
- `slides/delivery-archetypes-kmeans.pdf` — an 8-slide deck built from this run's real numbers

## Run it

```bash
make hawkeye
uv run jupyter lab lessons/01-kmeans-clustering/lesson.ipynb
uv run python lessons/01-kmeans-clustering/make_slides.py
```
