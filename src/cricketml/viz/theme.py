"""A single matplotlib theme for the whole curriculum.

Call :func:`use_theme` once at the top of a lesson. Do not set colours by hand
anywhere else — the point of a fixed palette is that "blue" means the same team,
the same model, the same class in lesson 1 and lesson 15.

The categorical order below is validated for colour-vision deficiency: worst
adjacent pair ΔE 9.1 (protan) against a ΔE ≥ 8 target, and 19.6 for normal
vision against a ≥ 15 floor. **Do not re-order or extend it** — the ordering is
what makes it safe. A ninth series is not a ninth colour; it is an "Other"
bucket or a small-multiple.

Three slots (aqua, yellow, magenta) sit below 3:1 contrast on the light
surface, so charts using them must carry direct labels or an accompanying
table — colour is never the only channel.
"""

from __future__ import annotations

from collections.abc import Sequence

import matplotlib as mpl
import matplotlib.pyplot as plt
from cycler import cycler

__all__ = [
    "CATEGORICAL",
    "DIVERGING",
    "SEQUENTIAL_BLUE",
    "STATUS",
    "SURFACE",
    "TEXT",
    "annotate_source",
    "use_theme",
]

#: Fixed categorical order. Assign by slot, never cycle past slot 8.
CATEGORICAL: tuple[str, ...] = (
    "#2a78d6",  # 1 blue
    "#eb6834",  # 2 orange
    "#1baf7a",  # 3 aqua
    "#eda100",  # 4 yellow
    "#e87ba4",  # 5 magenta
    "#008300",  # 6 green
    "#4a3aa7",  # 7 violet
    "#e34948",  # 8 red
)

#: Single hue, light -> dark, for magnitude (heatmaps of a wagon wheel, pitch maps).
SEQUENTIAL_BLUE: tuple[str, ...] = (
    "#cde2fb",
    "#b7d3f6",
    "#9ec5f4",
    "#86b6ef",
    "#6da7ec",
    "#5598e7",
    "#3987e5",
    "#2a78d6",
    "#256abf",
    "#1c5cab",
    "#184f95",
    "#104281",
    "#0d366b",
)

#: Two poles plus a neutral middle — for things with a sign, like runs above par.
DIVERGING: tuple[str, str, str] = ("#2a78d6", "#f0efec", "#d03b3b")

#: Reserved. Never used for a data series.
STATUS: dict[str, str] = {
    "good": "#0ca30c",
    "warning": "#fab219",
    "serious": "#ec835a",
    "critical": "#d03b3b",
}

SURFACE = "#fcfcfb"
TEXT = {"primary": "#0b0b0b", "secondary": "#52514e", "muted": "#8a8880"}
_GRID = "#e6e5e1"


def use_theme(*, palette: Sequence[str] | None = None, dpi: int = 120) -> None:
    """Install the project theme into matplotlib's global rcParams.

    Args:
        palette: Override the categorical cycle. Only for a lesson that is
            deliberately about colour; otherwise leave it alone.
        dpi: Figure DPI. 120 reads well both in JupyterLab and on GitHub.
    """
    colors = list(palette) if palette is not None else list(CATEGORICAL)

    mpl.rcParams.update(
        {
            "figure.figsize": (8.0, 4.5),
            "figure.dpi": dpi,
            "figure.facecolor": SURFACE,
            "savefig.facecolor": SURFACE,
            "savefig.bbox": "tight",
            "axes.prop_cycle": cycler(color=colors),
            "axes.facecolor": SURFACE,
            "axes.edgecolor": _GRID,
            "axes.labelcolor": TEXT["secondary"],
            "axes.titlecolor": TEXT["primary"],
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.titlelocation": "left",
            "axes.titlepad": 12,
            "axes.labelsize": 10,
            # Recessive frame: keep the data, lose the box.
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "axes.axisbelow": True,
            "grid.color": _GRID,
            "grid.linewidth": 0.8,
            "xtick.color": TEXT["muted"],
            "ytick.color": TEXT["muted"],
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "lines.linewidth": 2.0,
            "lines.markersize": 8,
            "legend.frameon": False,
            "legend.fontsize": 9,
            "legend.labelcolor": TEXT["secondary"],
            "font.size": 10,
            "font.family": "sans-serif",
            "font.sans-serif": ["Inter", "Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
        }
    )


def annotate_source(ax: plt.Axes, text: str = "Data: Cricsheet (CC BY 4.0)") -> plt.Axes:
    """Stamp the data provenance under a chart. Every published chart gets one."""
    ax.annotate(
        text,
        xy=(0, -0.18),
        xycoords="axes fraction",
        fontsize=8,
        color=TEXT["muted"],
        va="top",
    )
    return ax
