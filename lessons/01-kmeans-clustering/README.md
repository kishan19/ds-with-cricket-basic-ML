# Lesson 01 — Can we find delivery types without being told what they are?

| | |
|---|---|
| **Concept** | K-means clustering |
| **Cricket question** | Does a delivery's physics alone reveal what "kind" of ball it was? |
| **Data** | Proprietary ball-tracking export, 194,592 deliveries (see the caveat below) |
| **Baseline to beat** | The broadcast graphic's own pace/spin label — held out, used only to grade the clusters |
| **Sets up** | A later lesson: compressing these features with PCA |

> **Folder number vs. curriculum position.** This is lesson 01 in build order —
> the first one made — but K-means sits later in the topic sequence in the main
> README's roadmap (it needs supervised-learning basics as a contrast first).
> Reconciling folder names with the roadmap is part of the pending numbering
> pass; until then, treat the number in a folder name as "built Nth," not
> "watch Nth."

## ⚠️ This lesson cannot be re-run on a fresh clone

Every other lesson in this repo runs on `make data`. This one can't: the
ball-tracking CSV (`release_speed_kph`, `swing_angle`, `deviation`, bounce/
crease/stumps position, `bowling_type`, `runs`, `wicket`) is a proprietary
export that lives only in `data/raw/data.csv` on this machine and is never
committed. `cricketml.data.ball_tracking.load_ball_tracking()` reads a fixed
schema, so a licensed or synthetic replacement with the same columns works
without touching the notebook — see [`docs/data.md`](../../docs/data.md).

## In one paragraph

Ball-tracking data has no player identity, so this clusters *deliveries*, not
bowlers, on seven physical measurements — speed, swing, seam deviation, bounce
and stumps position, bounce angle, drop angle. K-means (K=3, chosen by
silhouette) rediscovers the pace/spin split almost perfectly without ever being
shown it, which is the sanity check passing. The genuinely interesting result is
the third cluster: deliveries a single pace/spin label can't describe at all.

## Result

**Cluster centres** (standardised features, K=3 chosen by silhouette 0.278 vs. 0.268 at K=2):

| cluster | share | speed (kph) | swing | deviation | bowling_type purity | wicket rate |
|---|---|---|---|---|---|---|
| "genuine pace" | 51.8% | 129.9 | +0.17 | −0.01 | **97.1% pace** | 5.0% |
| "genuine spin" | 23.3% | 89.1 | +1.12 | −2.40 | **93.3% spin** | 4.7% |
| "neither" | 24.9% | 100.4 | −0.70 | +1.44 | 42% pace / 58% spin | 5.3% |

The from-scratch appendix also caught something real: a single random
initialisation landed in a worse local optimum than scikit-learn's default
(ARI 0.396 against it), and restarting 10 times and keeping the best (ARI 1.000)
is exactly why `KMeans` defaults to `n_init=10`. Left in deliberately — a clean
number the first time would have taught nothing about why that default exists.

## Three things worth stealing from this lesson

1. **Validate an unsupervised result against a label you withheld.** Two of
   three clusters recover pace/spin at 93–97% purity — proof the clustering
   found something real before trusting the piece it invented.
2. **The invented cluster is the point.** "Medium pace, sharp turn" isn't a
   labeling mistake — it's cutters and brisk-armed spin sharing one physical
   envelope, which a two-bucket broadcast graphic can't represent.
3. **A single-run from-scratch implementation can silently give the wrong
   answer.** `n_init=10` isn't scikit-learn being careful for no reason —
   demonstrated here with a real 0.396 → 1.000 swing on this exact data.

## Artefacts

- `lesson.ipynb` — the notebook (interactive: drag K from 2–8 live)
- `make_slides.py` — regenerates `slides/delivery-archetypes-kmeans.pdf`
- `slides/delivery-archetypes-kmeans.pdf` — an 8-slide deck built from this run's real numbers

## Run it

Requires `data/raw/data.csv` locally (see the caveat above).

```bash
uv run jupyter lab lessons/01-kmeans-clustering/lesson.ipynb
uv run python lessons/01-kmeans-clustering/make_slides.py
```
