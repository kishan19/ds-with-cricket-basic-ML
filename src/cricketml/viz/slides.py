"""A minimal slide deck, rendered to PDF with matplotlib.

No LaTeX, no browser, no PowerPoint — just figures on a page, using the same
theme every chart in this project uses. Built for one purpose: turn a lesson's
seven sections into something that can go up on screen for a recording,
without re-deriving layout and colour choices per lesson.

    from cricketml.viz.slides import SlideDeck

    with SlideDeck("out.pdf") as deck:
        deck.title("K-means clustering", "Finding delivery types without labels")
        deck.bullets("The cricket question", ["One sentence...", "..."])
        deck.figure("Results", my_matplotlib_figure)
        deck.table("Cluster centres", dataframe)
"""

from __future__ import annotations

from collections.abc import Sequence
from types import TracebackType

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure

from cricketml.viz.theme import CATEGORICAL, SURFACE, TEXT, use_theme

__all__ = ["SlideDeck"]

#: Standard widescreen, matching a 1920x1080 recording at 96 DPI equivalent.
_SIZE = (13.333, 7.5)


class SlideDeck:
    """Append slides in order, then close to flush the PDF.

    Use as a context manager so an exception mid-deck still leaves whatever
    was rendered so far on disk rather than a truncated, unreadable file.
    """

    def __init__(self, path: str, *, subtitle: str = "") -> None:
        use_theme()
        self.path = path
        self.subtitle = subtitle
        self._pdf = PdfPages(path)
        self._n = 0

    def __enter__(self) -> SlideDeck:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self._pdf.close()

    def _new_slide(self) -> Figure:
        self._n += 1
        fig = plt.figure(figsize=_SIZE, facecolor=SURFACE)
        return fig

    def _footer(self, fig: Figure, kicker: str) -> None:
        fig.text(0.06, 0.05, kicker, fontsize=11, color=TEXT["muted"])
        fig.text(0.94, 0.05, f"{self._n:02d}", fontsize=11, color=TEXT["muted"], ha="right")

    def _save(self, fig: Figure) -> None:
        self._pdf.savefig(fig, facecolor=SURFACE)
        plt.close(fig)

    def title(self, headline: str, subhead: str = "") -> None:
        """The opening slide: a big headline, one line under it."""
        fig = self._new_slide()
        fig.text(0.08, 0.58, headline, fontsize=40, weight="bold", color=TEXT["primary"])
        if subhead:
            fig.text(0.08, 0.46, subhead, fontsize=18, color=TEXT["secondary"])
        fig.text(0.08, 0.10, self.subtitle, fontsize=13, color=TEXT["muted"])
        self._save(fig)

    def section(self, headline: str) -> None:
        """A short divider slide — just a number and a heading."""
        fig = self._new_slide()
        fig.text(0.08, 0.5, f"{self._n:02d}", fontsize=18, color=CATEGORICAL[0])
        fig.text(0.08, 0.40, headline, fontsize=32, weight="bold", color=TEXT["primary"])
        self._save(fig)

    def bullets(self, heading: str, lines: Sequence[str], *, kicker: str = "") -> None:
        """A heading with a short list beneath it. Keep it to 3-5 lines."""
        fig = self._new_slide()
        fig.text(0.08, 0.86, heading, fontsize=26, weight="bold", color=TEXT["primary"])
        y = 0.68
        for line in lines:
            fig.text(0.10, y, f"—  {line}", fontsize=17, color=TEXT["secondary"], wrap=True)
            y -= 0.12
        self._footer(fig, kicker or heading)
        self._save(fig)

    def figure(self, heading: str, source_fig: Figure, *, kicker: str = "") -> None:
        """Embed an existing matplotlib figure (e.g. from the lesson notebook)."""
        fig = self._new_slide()
        fig.text(0.08, 0.92, heading, fontsize=26, weight="bold", color=TEXT["primary"])
        ax = fig.add_axes((0.08, 0.14, 0.86, 0.72))
        ax.axis("off")
        source_fig.canvas.draw()
        # buffer_rgba() is an Agg-backend method, not on the base canvas type —
        # matplotlib's default backend guarantees it in practice.
        ax.imshow(source_fig.canvas.buffer_rgba())  # type: ignore[attr-defined]
        self._footer(fig, kicker or heading)
        self._save(fig)

    def table(self, heading: str, df: pd.DataFrame, *, kicker: str = "") -> None:
        """A small results table — for a results row count, not a full frame."""
        fig = self._new_slide()
        fig.text(0.08, 0.92, heading, fontsize=26, weight="bold", color=TEXT["primary"])
        ax = fig.add_axes((0.08, 0.20, 0.86, 0.62))
        ax.axis("off")
        tbl = ax.table(
            cellText=df.to_numpy(),
            colLabels=df.columns,
            cellLoc="center",
            loc="center",
        )
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(13)
        tbl.scale(1, 2.2)
        for (row, _col), cell in tbl.get_celld().items():
            cell.set_edgecolor(SURFACE)
            if row == 0:
                cell.set_text_props(weight="bold", color=TEXT["primary"])
                cell.set_facecolor("#eceae3")
            else:
                cell.set_facecolor(SURFACE)
                cell.set_text_props(color=TEXT["secondary"])
        self._footer(fig, kicker or heading)
        self._save(fig)

    def closing(self, headline: str, subhead: str = "") -> None:
        """The last slide — same shape as the title, for a consistent bookend."""
        self.title(headline, subhead)
