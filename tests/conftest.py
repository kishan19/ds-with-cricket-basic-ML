from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from cricketml.data.cricsheet import flatten_match

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def sample_match() -> dict:
    return json.loads((FIXTURES / "sample_match.json").read_text())


@pytest.fixture()
def deliveries(sample_match: dict) -> pd.DataFrame:
    _, rows = flatten_match("fixture-001", sample_match)
    return pd.DataFrame(rows)


@pytest.fixture()
def match_row(sample_match: dict) -> dict:
    row, _ = flatten_match("fixture-001", sample_match)
    return row
