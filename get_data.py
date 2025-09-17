import csv
import json
import os
import re
import requests
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import mlbstatsapi
import pytz
import statsapi
from bs4 import BeautifulSoup
import hashlib

import config
from cache_manager import cache


def get_roster_names(team_id: int) -> List[str]:
    """Get a list of player names in the roster."""
    cache_key = f"roster_{team_id}"

    def fetch_roster():
        roster_string = statsapi.roster(team_id)
        roster_list_unprocessed = roster_string.split("\n")
        roster_list = []

        for entry in roster_list_unprocessed:
            player_name = " ".join(entry.split()[2:])
            roster_list.append(player_name)

        # Filter out empty names
        return [name for name in roster_list if name != ""]

    return cache.get_or_fetch(cache_key, fetch_roster)


def get_homerun_leaders_by_team(team_id: int) -> List[Dict[str, Any]]:
    """Return a list of home run leaders for a given team ID."""

    season = config.CURRENT_SEASON
    leaderGameTypes = "R"
    limit = 10
    cache_key = f"hr_leaders_{team_id}_{season}"

    def fetch_leaders():
        homerun_leaders_by_team = []
        home_leaders_data = statsapi.team_leader_data(
            team_id,
            "homeRuns",
            season=season,
            leaderGameTypes=leaderGameTypes,
            limit=limit,
        )

        for z in home_leaders_data:
            homerun_leaders_by_team.append({"name": z[1], "homeRuns": z[2]})

        return homerun_leaders_by_team

    return cache.get_or_fetch(cache_key, fetch_leaders)


def get_nhl_standings_now() -> Dict[str, Any]:
    """
    Fetch NHL standings (current) via requests and cache the JSON response.

    Uses:
    - requests.get with allow_redirects to match `curl -L -X GET`
    - cache.get_or_fetch to reuse a fresh cached file

    Tune freshness via config.CACHE_EXPIRY_HOURS (in your CacheManager).
    """
    cache_key = "nhl_standings_now"

    def fetch_standings() -> Dict[str, Any]:
        url = "https://api-web.nhle.com/v1/standings/now"
        resp = requests.get(
            url,
            timeout=30,
            allow_redirects=True,
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()

    return cache.get_or_fetch(cache_key, fetch_standings)




def get_nhl_skaters_json(season: str = "2024", phase: str = "regular") -> List[Dict[str, Any]]:
    """
    Download MoneyPuck skaters CSV for the given season/phase, convert to JSON (list[dict]),
    and cache the result with a 'latest' file. When cache expires, fetch again and:
      - If data changed: write a dated snapshot (YYYYMMDD) into DATA_DIR/daily_skaters
      - Always keep/update 'latest' in DATA_DIR (top level)
    """
    url = f"https://moneypuck.com/moneypuck/playerData/seasonSummary/{season}/{phase}/skaters.csv"
    latest_key = f"nhl_skaters_{season}_{phase}_latest"
    dated_key_prefix = f"nhl_skaters_{season}_{phase}_"
    daily_dir = "daily_skaters"  # subfolder inside DATA_DIR for dated snapshots
    
    # 1) Try using the cache if still valid
    latest_cached = None
    try:
        # Uses CacheManager's expiry logic; returns None if expired/missing
        latest_cached = cache.load_json(latest_key)
    except Exception:
        latest_cached = None

    if latest_cached is not None:
        return latest_cached

    # 2) Cache expired -> fetch fresh CSV
    resp = requests.get(url, timeout=30, allow_redirects=True, headers={"Accept": "text/csv"})
    resp.raise_for_status()

    # Parse CSV -> rows (list[dict])
    text = resp.content.decode("utf-8", errors="replace")
    reader = csv.DictReader(text.splitlines())
    new_rows: List[Dict[str, Any]] = []

    for row in reader:
        converted: Dict[str, Any] = {}
        for k, v in row.items():
            if v is None:
                converted[k] = None
                continue
            s = v.strip()
            if s == "":
                converted[k] = ""
                continue
            # Try int -> float -> fallback str
            try:
                converted[k] = int(s)
            except ValueError:
                try:
                    converted[k] = float(s)
                except ValueError:
                    converted[k] = s
        new_rows.append(converted)

    # 3) Compare with previous 'latest' (ignore expiry to compare content)
    latest_path = os.path.join(config.DATA_DIR, f"{latest_key}.json")
    old_rows = None
    if os.path.exists(latest_path):
        try:
            with open(latest_path, "r", encoding="utf-8") as fh:
                old_rows = json.load(fh)
        except Exception:
            old_rows = None

    def rows_hash(rows: List[Dict[str, Any]]) -> str:
        # Stable hash for content comparison
        payload = json.dumps(rows, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    changed = True
    if old_rows is not None:
        changed = rows_hash(new_rows) != rows_hash(old_rows)

    # 4) If changed -> save dated + update latest. If same -> do nothing.
    if changed:
        today = datetime.now().strftime("%Y%m%d")
        dated_key = f"{dated_key_prefix}{today}"
        # Save a dated snapshot in DATA_DIR/daily_skaters/<dated_key>.json
        cache.save_json(new_rows, f"{daily_dir}/{dated_key}")
        # Update the rolling 'latest' at DATA_DIR/<latest_key>.json
        cache.save_json(new_rows, latest_key)
        return new_rows
    else:
        # Keep current files; return what we already had or the new rows (equivalent)
        return old_rows if old_rows is not None else new_rows


def get_nhl_skaters(season: str = "2024", phase: str = "regular") -> str:
    """
    Download MoneyPuck skaters CSV for the given season/phase and cache as CSV only.

    Caching logic:
      - If DATA_DIR/<latest_key>.csv is fresh (mtime within CACHE_EXPIRY_HOURS), return its contents.
      - Otherwise fetch the CSV. If content differs from the previous 'latest':
          * Save a dated snapshot to DATA_DIR/daily_skaters/<dated_key>.csv (YYYYMMDD)
          * Update DATA_DIR/<latest_key>.csv
        If content is identical, keep existing files unchanged.

    Returns:
      CSV text (string).
    """
    url = f"https://moneypuck.com/moneypuck/playerData/seasonSummary/{season}/{phase}/skaters.csv"
    latest_key = f"nhl_skaters_{season}_{phase}_latest"   # file: DATA_DIR/<latest_key>.csv
    dated_key_prefix = f"nhl_skaters_{season}_{phase}_"   # file: DATA_DIR/daily_skaters/<prefix><YYYYMMDD>.csv
    daily_dir = "daily_skaters"

    # Ensure directories exist
    os.makedirs(config.DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(config.DATA_DIR, daily_dir), exist_ok=True)

    expiry_hours = getattr(config, "CACHE_EXPIRY_HOURS", 12)

    latest_path = os.path.join(config.DATA_DIR, f"{latest_key}.csv")

    # 1) If latest exists and is still fresh, return cached CSV
    if os.path.exists(latest_path):
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(latest_path))
            if mtime > datetime.now() - timedelta(hours=expiry_hours):
                with open(latest_path, "r", encoding="utf-8") as fh:
                    return fh.read()
        except Exception:
            pass  # Treat as cache miss

    # 2) Cache expired/missing -> fetch fresh CSV
    resp = requests.get(url, timeout=30, allow_redirects=True, headers={"Accept": "text/csv"})
    resp.raise_for_status()
    new_csv = resp.text  # Server sends UTF-8; if not, requests will try to detect encoding.

    # 3) Compare to previous latest (if exists), ignoring expiry
    old_csv = None
    if os.path.exists(latest_path):
        try:
            with open(latest_path, "r", encoding="utf-8") as fh:
                old_csv = fh.read()
        except Exception:
            old_csv = None

    def text_hash(s: str) -> str:
        return hashlib.sha256(s.encode("utf-8")).hexdigest()

    changed = True if old_csv is None else (text_hash(new_csv) != text_hash(old_csv))

    # 4) If changed -> save dated snapshot + update latest. If same -> do nothing.
    if changed:
        today = datetime.now().strftime("%Y%m%d")
        dated_filename = f"{dated_key_prefix}{today}.csv"
        dated_path = os.path.join(config.DATA_DIR, daily_dir, dated_filename)

        # Write dated snapshot (keeps history)
        with open(dated_path, "w", encoding="utf-8", newline="") as fh:
            fh.write(new_csv)

        # Update rolling 'latest'
        with open(latest_path, "w", encoding="utf-8", newline="") as fh:
            fh.write(new_csv)

        return new_csv
    else:
        # Return the existing cached CSV
        return old_csv if old_csv is not None else new_csv
