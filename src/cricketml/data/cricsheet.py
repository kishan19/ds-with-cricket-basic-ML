"""Turn Cricsheet's match JSON into two tidy tables.

Cricsheet (https://cricsheet.org) publishes ball-by-ball data for most
professional cricket under CC BY 4.0 — which is why this project uses it rather
than scraping a scorecard site. One zip per competition, one JSON per match.

This module flattens that into:

* ``matches``    — one row per match (the context: venue, toss, result, season)
* ``deliveries`` — one row per legal or illegal ball bowled

Both land in ``data/processed`` as parquet. Nothing downstream re-parses JSON.
"""

from __future__ import annotations

import json
import zipfile
from collections.abc import Iterator
from pathlib import Path
from urllib.request import urlopen

import pandas as pd

from cricketml.config import BOWLER_WICKET_KINDS, PATHS

__all__ = ["SOURCES", "build", "download", "flatten_match", "iter_matches"]

BASE_URL = "https://cricsheet.org/downloads"

#: Friendly name -> Cricsheet zip. Start with ``ipl``: ~1,100 matches is big
#: enough to be interesting and small enough to iterate on over lunch.
SOURCES: dict[str, str] = {
    "ipl": "ipl_json.zip",
    "t20i": "t20s_json.zip",
    "odi": "odis_json.zip",
    "test": "tests_json.zip",
    "wbbl": "wbb_json.zip",
    "wt20i": "t20s_female_json.zip",
}

#: Extras that do not count as a ball faced by the batter.
_NON_BALL_EXTRAS = ("wides", "noballs")


def download(source: str = "ipl", *, force: bool = False) -> Path:
    """Fetch a Cricsheet zip into ``data/raw``. Cached unless ``force``."""
    if source not in SOURCES:
        raise KeyError(f"Unknown source {source!r}. Choose from {sorted(SOURCES)}.")

    PATHS.ensure()
    dest = PATHS.raw / SOURCES[source]
    if dest.exists() and not force:
        return dest

    url = f"{BASE_URL}/{SOURCES[source]}"
    with urlopen(url) as response, dest.open("wb") as fh:
        fh.write(response.read())
    return dest


def iter_matches(zip_path: Path) -> Iterator[tuple[str, dict]]:
    """Yield ``(match_id, parsed_json)`` for every match in a Cricsheet zip.

    The match id is the filename stem, which is Cricsheet's own stable id.
    """
    with zipfile.ZipFile(zip_path) as zf:
        for name in sorted(zf.namelist()):
            if not name.endswith(".json") or name.startswith("README"):
                continue
            with zf.open(name) as fh:
                yield Path(name).stem, json.load(fh)


def _match_row(match_id: str, info: dict) -> dict:
    teams = info.get("teams", [None, None])
    outcome = info.get("outcome", {})
    toss = info.get("toss", {})
    event = info.get("event") or {}
    return {
        "match_id": match_id,
        "date": pd.to_datetime(info["dates"][0]),
        "season": str(info.get("season", "")),
        "match_type": info.get("match_type"),
        "gender": info.get("gender"),
        "event": event.get("name") if isinstance(event, dict) else event,
        "venue": info.get("venue"),
        "city": info.get("city"),
        "team_1": teams[0],
        "team_2": teams[1] if len(teams) > 1 else None,
        "toss_winner": toss.get("winner"),
        "toss_decision": toss.get("decision"),
        "winner": outcome.get("winner"),
        # 'tie', 'no result', 'draw' — a match with no winner is not a missing
        # value, it is a result, and lessons on classification must handle it.
        "result": outcome.get("result"),
        "win_by_runs": (outcome.get("by") or {}).get("runs"),
        "win_by_wickets": (outcome.get("by") or {}).get("wickets"),
        # 'D/L' when rain revised the target. The chase was then not for the
        # first-innings total plus one, so chase lessons must drop these.
        "method": outcome.get("method"),
        "overs_per_innings": info.get("overs"),
        "balls_per_over": info.get("balls_per_over", 6),
    }


def _delivery_rows(match_id: str, date: pd.Timestamp, innings: list[dict]) -> Iterator[dict]:
    for innings_no, inn in enumerate(innings, start=1):
        # Super overs carry the same structure; flag rather than drop them.
        is_super_over = bool(inn.get("super_over", False))
        ball_in_innings = 0
        for over in inn.get("overs", []):
            over_no = over["over"]
            for ball_in_over, d in enumerate(over.get("deliveries", []), start=1):
                extras = d.get("extras", {}) or {}
                runs = d.get("runs", {}) or {}
                wickets = d.get("wickets", []) or []
                legal = not any(k in extras for k in _NON_BALL_EXTRAS)
                if legal:
                    ball_in_innings += 1

                wicket = wickets[0] if wickets else {}
                kind = wicket.get("kind")
                yield {
                    "match_id": match_id,
                    "date": date,
                    "innings": innings_no,
                    "is_super_over": is_super_over,
                    "batting_team": inn.get("team"),
                    "over": over_no,
                    "ball_in_over": ball_in_over,
                    "ball_in_innings": ball_in_innings,
                    "batter": d.get("batter"),
                    "non_striker": d.get("non_striker"),
                    "bowler": d.get("bowler"),
                    "runs_batter": runs.get("batter", 0),
                    "runs_extras": runs.get("extras", 0),
                    "runs_total": runs.get("total", 0),
                    "wides": extras.get("wides", 0),
                    "noballs": extras.get("noballs", 0),
                    "byes": extras.get("byes", 0),
                    "legbyes": extras.get("legbyes", 0),
                    "is_legal_ball": legal,
                    "is_wicket": bool(wickets),
                    "wicket_kind": kind,
                    "player_out": wicket.get("player_out"),
                    # Run-outs are not the bowler's; see config.BOWLER_WICKET_KINDS.
                    "is_bowler_wicket": kind in BOWLER_WICKET_KINDS if kind else False,
                }


def flatten_match(match_id: str, match: dict) -> tuple[dict, list[dict]]:
    """Flatten one Cricsheet match into its match row and its delivery rows."""
    info = match["info"]
    row = _match_row(match_id, info)
    deliveries = list(_delivery_rows(match_id, row["date"], match.get("innings", [])))
    return row, deliveries


def build(source: str = "ipl", *, force_download: bool = False) -> dict[str, Path]:
    """Download (if needed), flatten, and write ``matches`` and ``deliveries``.

    Returns the two written paths, keyed by table name.
    """
    zip_path = download(source, force=force_download)

    match_rows: list[dict] = []
    delivery_rows: list[dict] = []
    for match_id, match in iter_matches(zip_path):
        row, balls = flatten_match(match_id, match)
        match_rows.append(row)
        delivery_rows.extend(balls)

    if not match_rows:
        raise RuntimeError(f"No matches parsed from {zip_path}.")

    matches = pd.DataFrame(match_rows).sort_values("date").reset_index(drop=True)
    deliveries = (
        pd.DataFrame(delivery_rows)
        .sort_values(["date", "match_id", "innings", "over", "ball_in_over"])
        .reset_index(drop=True)
    )

    PATHS.ensure()
    out = {
        "matches": PATHS.processed / f"{source}_matches.parquet",
        "deliveries": PATHS.processed / f"{source}_deliveries.parquet",
    }
    matches.to_parquet(out["matches"], index=False)
    deliveries.to_parquet(out["deliveries"], index=False)
    return out
