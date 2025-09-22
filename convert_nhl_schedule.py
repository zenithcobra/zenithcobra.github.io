import csv
import json
from pathlib import Path
import sys
from typing import Any, Dict, Iterable


HEADERS = ["date", "easternUTCOffset", "gameType", "awayTeamAbbrev", "homeTeamAbbrev"]


def _read_json_allowing_line_comments(path) -> Dict[str, Any]:
    """
    Load JSON, ignoring lines that start with '//' (helpful if the file has a filepath banner).
    """
    text = path.read_text(encoding="utf-8")
    lines = [ln for ln in text.splitlines() if not ln.lstrip().startswith("//")]
    return json.loads("\n".join(lines))


def _get(d: Dict[str, Any], keys: Iterable[str], default: Any = "") -> Any:
    cur: Any = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def export_schedule_to_csv(json_path, csv_path: Path) -> None:
    data = _read_json_allowing_line_comments(json_path)

    rows = []
    for week in data.get("gameWeek", []):
        date = week.get("date", "")
        for game in week.get("games", []):
            row = {
                "date": date,
                "easternUTCOffset": game.get("easternUTCOffset", ""),
                "gameType": game.get("gameType", ""),
                "awayTeamAbbrev": _get(game, ("awayTeam", "abbrev")),
                "homeTeamAbbrev": _get(game, ("homeTeam", "abbrev")),
            }
            rows.append(row)

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows -> {csv_path}")


if __name__ == "__main__":
    # Usage:
    #   python3 scripts/export_nhl_schedule_csv.py [input_json] [output_csv]
    default_in = "NHL_data/nhl_schedule.json"
    default_out = "NHL_data/nhl_schedule.csv"

    export_schedule_to_csv(default_in, default_out)