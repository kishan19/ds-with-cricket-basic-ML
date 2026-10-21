"""Every lesson opens in Colab: a badge pointing at its own path, and a setup cell."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

LESSONS = Path(__file__).resolve().parents[1] / "lessons"
COLAB = "https://colab.research.google.com/github/kishan19/ds-with-cricket-basic-ML/blob/main/"
NOTEBOOKS = sorted(p for p in LESSONS.glob("*/lesson.ipynb") if p.parent.name != "_template")


@pytest.mark.parametrize("notebook", NOTEBOOKS, ids=lambda p: p.parent.name)
def test_lesson_opens_in_colab(notebook: Path) -> None:
    cells = json.loads(notebook.read_text())["cells"]
    link = f"{COLAB}lessons/{notebook.parent.name}/lesson.ipynb"

    assert link in "".join(cells[0]["source"]), "Colab badge missing or points at another lesson"
    assert link in (notebook.parent / "README.md").read_text(), "README Colab badge missing"
    assert cells[1].get("id") == "c00-colab", "Colab setup cell must come straight after the title"
