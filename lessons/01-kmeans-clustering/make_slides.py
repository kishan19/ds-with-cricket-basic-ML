"""Build the shareable slide deck for this lesson from a live run of the data.

Regenerate after re-running the notebook, or after any change to the analysis:

    uv run python lessons/01-kmeans-clustering/make_slides.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from cricketml import SEED
from cricketml.data.ball_tracking import PHYSICS_COLUMNS, load_ball_tracking
from cricketml.viz import CATEGORICAL, use_theme
from cricketml.viz.slides import SlideDeck

HERE = Path(__file__).parent
OUT = HERE / "slides" / "delivery-archetypes-kmeans.pdf"


def main() -> None:
    use_theme()
    df = load_ball_tracking()
    features = list(PHYSICS_COLUMNS)
    X = StandardScaler().fit_transform(df[features])
    rng = np.random.default_rng(SEED)

    sil_sample = rng.choice(len(X), size=10_000, replace=False)
    curve = pd.DataFrame(
        [
            {
                "k": k,
                "inertia": (
                    m := KMeans(n_clusters=k, random_state=SEED, n_init=10).fit(X)
                ).inertia_,
                "silhouette": silhouette_score(X[sil_sample], m.labels_[sil_sample]),
            }
            for k in range(2, 9)
        ]
    )
    best_k = int(curve.loc[curve.silhouette.idxmax(), "k"])

    final = KMeans(n_clusters=best_k, random_state=SEED, n_init=10).fit(X)
    df = df.assign(cluster=final.labels_)
    purity = pd.crosstab(df["cluster"], df["bowling_type"], normalize="index")
    outcomes = df.groupby("cluster").agg(runs=("runs", "mean"), wicket_rate=("wicket", "mean"))
    sizes = df["cluster"].value_counts(normalize=True)

    # --- figure: elbow + silhouette ---
    fig1, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(curve.k, curve.inertia, marker="o")
    axes[0].set_title("Inertia")
    axes[0].set_xlabel("K")
    axes[1].plot(curve.k, curve.silhouette, marker="o", color=CATEGORICAL[1])
    axes[1].axvline(best_k, color=CATEGORICAL[7], linestyle="--", linewidth=1)
    axes[1].set_title("Silhouette")
    axes[1].set_xlabel("K")
    fig1.tight_layout()

    # --- figure: PCA scatter of the chosen K ---
    demo_idx = rng.choice(len(X), size=20_000, replace=False)
    X_demo_2d = PCA(n_components=2, random_state=SEED).fit_transform(X[demo_idx])
    labels_demo = final.labels_[demo_idx]
    fig2, ax2 = plt.subplots(figsize=(7, 5.5))
    for c in range(best_k):
        m = labels_demo == c
        ax2.scatter(
            X_demo_2d[m, 0],
            X_demo_2d[m, 1],
            s=6,
            alpha=0.5,
            color=CATEGORICAL[c % len(CATEGORICAL)],
            label=f"cluster {c}",
        )
    ax2.set_title(f"K = {best_k}, PCA-projected")
    ax2.legend(markerscale=3)

    # --- results table ---
    # Name clusters by their dominant label rather than hardcoding an index,
    # so the deck stays correct if a re-run assigns cluster numbers differently.
    dominant = purity.idxmax(axis=1)
    name_counts: dict[str, int] = {}
    names = {}
    for c in purity.index:
        base = "mixed" if purity.loc[c].max() < 0.75 else f"genuine {dominant[c]}"
        name_counts[base] = name_counts.get(base, 0) + 1
        names[c] = base if name_counts[base] == 1 else f"{base} ({name_counts[base]})"

    results = pd.DataFrame(
        {
            "cluster": [names[c] for c in purity.index],
            "share": [f"{sizes[c]:.1%}" for c in purity.index],
            "pace %": [
                f"{purity.loc[c, 'pace']:.1%}" if "pace" in purity.columns else "—"
                for c in purity.index
            ],
            "spin %": [
                f"{purity.loc[c, 'spin']:.1%}" if "spin" in purity.columns else "—"
                for c in purity.index
            ],
            "wicket rate": [f"{outcomes.loc[c, 'wicket_rate']:.1%}" for c in purity.index],
        }
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with SlideDeck(str(OUT), subtitle="cricketml — a lesson from ds-with-cricket-basic-ML") as deck:
        deck.title(
            "Can we find delivery\ntypes without labels?",
            "K-means clustering, on real ball-tracking data",
        )
        deck.bullets(
            "The cricket question",
            [
                "A tracker prints speed, swing, seam deviation for every ball.",
                "Could you tell fast bowler from spinner on those numbers alone?",
                "Is 'pace or spin' even the only real split?",
            ],
        )
        deck.bullets(
            "The data",
            [
                f"{len(df):,} deliveries, 7 physical measurements per ball.",
                "No player identity — this clusters deliveries, not bowlers.",
                "bowling_type (pace/spin) is held out — used only to grade clusters.",
            ],
        )
        deck.bullets(
            "The naive answer",
            [
                "Cricket already has a 2-bucket answer: pace or spin.",
                "Assigned from the run-up, not the ball's physics.",
                "Any clustering should recover this before it earns credit for more.",
            ],
        )
        deck.figure(
            "Choosing K: elbow + silhouette", fig1, kicker=f"Silhouette peaks at K={best_k}"
        )
        deck.figure(f"K = {best_k}, projected to 2D", fig2)
        deck.table(
            "What the clusters found", results, kicker="pace/spin purity was withheld from training"
        )
        deck.bullets(
            "What it gets wrong",
            [
                "Only one label (pace/spin) exists to validate against.",
                "K chosen by silhouette on a 10k-row subsample, for speed.",
                "Standardising treats line & length as equal to speed — they aren't, cricket-wise.",
                "A from-scratch single-init run misses scikit-learn's answer (ARI 0.396) — n_init exists for a reason.",
            ],
        )
        deck.closing("Next: compressing these\nfeatures with PCA", "cricketml")

    print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
