"""Project-wide constants: paths, the seed, and cricket domain facts.

Everything that would otherwise be re-typed (and eventually mistyped) in a
notebook lives here.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

# The one seed. Every split, every model, every bootstrap uses it, so a lesson
# re-run a year from now prints the same numbers as the prose around it.
SEED: int = 1983  # India's first World Cup.


@dataclass(frozen=True)
class Paths:
    """Canonical locations. Override the root with CRICKETML_ROOT if needed."""

    root: Path

    @property
    def data(self) -> Path:
        return self.root / "data"

    @property
    def raw(self) -> Path:
        """Immutable downloads. Never written to by a notebook."""
        return self.data / "raw"

    @property
    def interim(self) -> Path:
        """Parsed but not yet modelling-ready."""
        return self.data / "interim"

    @property
    def processed(self) -> Path:
        """Analysis-ready tables. The only thing lessons should load."""
        return self.data / "processed"

    @property
    def lessons(self) -> Path:
        return self.root / "lessons"

    @property
    def docs(self) -> Path:
        return self.root / "docs"

    def ensure(self) -> Paths:
        for p in (self.raw, self.interim, self.processed):
            p.mkdir(parents=True, exist_ok=True)
        return self


def _find_root() -> Path:
    if env := os.environ.get("CRICKETML_ROOT"):
        return Path(env).expanduser().resolve()
    # src/cricketml/config.py -> src/cricketml -> src -> repo root
    return Path(__file__).resolve().parents[2]


PATHS = Paths(root=_find_root())

# --------------------------------------------------------------- cricket ---

BALLS_PER_OVER: int = 6

FORMAT_OVERS: dict[str, int] = {
    "T20": 20,
    "ODI": 50,
}

POWERPLAY_OVERS: dict[str, int] = {
    "T20": 6,
    "ODI": 10,
}

#: Dismissals credited to the bowler. The rest (run out, retired, obstructing)
#: are not, and forgetting this is the single most common bug in cricket
#: feature engineering.
BOWLER_WICKET_KINDS: frozenset[str] = frozenset(
    {"bowled", "caught", "caught and bowled", "lbw", "stumped", "hit wicket"}
)

__all__ = [
    "BALLS_PER_OVER",
    "BOWLER_WICKET_KINDS",
    "FORMAT_OVERS",
    "PATHS",
    "POWERPLAY_OVERS",
    "SEED",
    "Paths",
]
