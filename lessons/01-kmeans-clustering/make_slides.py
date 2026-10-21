"""Build the shareable slide deck for this lesson from a live run of the data.

Needs the Hawk-Eye CSV (``make hawkeye``). Regenerate after re-running the
notebook, or after any change to the analysis:

    uv run python lessons/01-kmeans-clustering/make_slides.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler

from cricketml import SEED
from cricketml.data.hawkeye import ATTRIBUTION, FEATURE_COLUMNS, PACE_STYLES, load_hawkeye
from cricketml.viz import CATEGORICAL, annotate_source, use_theme
from cricketml.viz.slides import SlideDeck

HERE = Path(__file__).parent
OUT = HERE / "slides" / "delivery-archetypes-kmeans.pdf"
MS_TO_KPH = 3.6


def name_archetypes(centres: pd.DataFrame) -> dict[int, str]:
    """Name the K=4 clusters from their centres, not their arbitrary numbers."""
    spin = centres["ballSpeed"].idxmin()
    pace = centres.drop(spin)
    full = pace["pitchY"].idxmin()
    other_side = pace.drop(full)["pitchX"].idxmax()
    (length,) = pace.index.difference([full, other_side])
    return {
        spin: "spin",
        full: "full / yorker",
        length: "short of a length",
        other_side: "the other line",
    }


def main() -> None:
    use_theme()
    df = load_hawkeye()
    features = list(FEATURE_COLUMNS)
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
    if best_k != 4:
        raise RuntimeError(f"Silhouette now picks K={best_k}; the deck's story assumes K=4.")

    final = KMeans(n_clusters=best_k, random_state=SEED, n_init=10).fit(X)
    df = df.assign(
        cluster=final.labels_,
        family=np.where(df["bowlingStyle"].isin(PACE_STYLES), "pace", "spin"),
    )
    centres = df.groupby("cluster")[features].mean()
    names = name_archetypes(centres)
    df["archetype"] = df["cluster"].map(names)
    trusted = ~df["bowlingStyle"].eq("SEAM")
    ari_family = adjusted_rand_score(df["family"], df["cluster"])
    ari_arm = adjusted_rand_score(df.loc[trusted, "rightArmedBowl"], df.loc[trusted, "cluster"])

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
    annotate_source(axes[0], text=ATTRIBUTION)

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
            label=names[c],
        )
    ax2.set_title(f"K = {best_k}, PCA-projected")
    ax2.legend(markerscale=3)
    annotate_source(ax2, text=ATTRIBUTION)

    # --- results table, in cricket units ---
    g = df.groupby("archetype")
    results = pd.DataFrame(
        {
            "share": g.size() / len(df),
            "kph": g["ballSpeed"].mean() * MS_TO_KPH,
            "length (m)": g["pitchY"].mean(),
            "spin share": g["family"].apply(lambda f: f.eq("spin").mean()),
            "left-hand batter": g["rightHandedBat"].apply(lambda r: (~r).mean()),
        }
    ).sort_values("kph")
    results = results.reset_index().assign(
        share=lambda t: t["share"].map("{:.0%}".format),
        kph=lambda t: t["kph"].map("{:.0f}".format),
        **{
            "length (m)": lambda t: t["length (m)"].map("{:.1f}".format),
            "spin share": lambda t: t["spin share"].map("{:.0%}".format),
            "left-hand batter": lambda t: t["left-hand batter"].map("{:.0%}".format),
        },
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with SlideDeck(str(OUT), subtitle="cricketml — a lesson from ds-with-cricket-basic-ML") as deck:
        deck.title(
            "Can we find delivery\ntypes without labels?",
            "K-means clustering, on real Hawk-Eye data",
        )
        deck.bullets(
            "The cricket question",
            [
                "Hawk-Eye prints speed, where it pitched, where it passed the stumps.",
                "Could you tell fast bowler from spinner on those numbers alone?",
                "Left arm from right arm? Or do the balls group some other way?",
            ],
        )
        deck.bullets(
            "The data",
            [
                f"{len(df):,} IPL deliveries, 5 Hawk-Eye measurements per ball.",
                "Tracker failures and impossible readings dropped (~6%).",
                "bowler + arm/style held out — used only to interpret clusters.",
                "Source: github.com/alittlefitness/HawkeyeStats (Hawk-Eye via the ICC).",
            ],
        )
        deck.bullets(
            "The naive answer",
            [
                "The scorecard already labels every bowler: arm + style.",
                "RIGHT_FAST_SEAM, LEFT_ORTHODOX, RIGHT_LEG_SPIN, ...",
                "Coarsest split, pace vs spin, must be recovered before anything else counts.",
                "Caveat: the 'SEAM' fallback style has an unreliable arm flag.",
            ],
        )
        deck.figure(
            "Choosing K: elbow + silhouette", fig1, kicker=f"Silhouette peaks at K={best_k}"
        )
        deck.figure(f"K = {best_k}, projected to 2D", fig2)
        deck.table(
            "What the clusters found",
            results,
            kicker=f"ARI vs pace/spin {ari_family:.2f}; vs bowling arm {ari_arm:.2f}",
        )
        deck.bullets(
            "What it gets wrong",
            [
                "'The other line' is left-handed batters: X coordinates are pitch-fixed.",
                "Arm is invisible: release position isn't in these five columns.",
                "Clusters are deliveries, not bowlers; every seamer bowls full and short.",
                "Standardising gives line and height the same vote as speed.",
            ],
        )
        deck.closing("Next: compressing these\nfeatures with PCA", "cricketml")

    print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
