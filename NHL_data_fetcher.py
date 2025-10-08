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

import config
from cache_manager import cache
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


def get_nhl_skaters_2024_2025_json() -> List[Dict[str, Any]]:
    """
    Download MoneyPuck skaters CSV for the given season/phase, convert to JSON (list[dict]),
    and cache the result with a 'latest' file. When cache expires, fetch again and:
      - If data changed: write a dated snapshot (YYYYMMDD) into DATA_DIR/daily_skaters
      - Always keep/update 'latest' in DATA_DIR (top level)
    """
    url = "https://moneypuck.com/moneypuck/playerData/seasonSummary/2024/regular/skaters.csv"
    latest_key = "nhl_skaters_2024_2025_regular_latest"
    dated_key_prefix = "nhl_skaters_2024_2025_regular_"
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
    resp = requests.get(
        url, timeout=30, allow_redirects=True, headers={"Accept": "text/csv"}
    )
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


def get_nhl_skaters() -> str:
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
    url = "https://moneypuck.com/moneypuck/playerData/seasonSummary/2025/regular/skaters.csv"
    latest_key = "nhl_skaters_2025_latest"  # file: DATA_DIR/<latest_key>.csv
    dated_key_prefix = (
        "nhl_skaters_2025_"  # file: DATA_DIR/daily_skaters/<prefix><YYYYMMDD>.csv
    )
    daily_dir = "daily_skaters"

    # Ensure directories exist
    os.makedirs(config.DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(config.DATA_DIR, daily_dir), exist_ok=True)

    expiry_hours = getattr(config, "CACHE_EXPIRY_HOURS", 4)

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
    resp = requests.get(
        url, timeout=30, allow_redirects=True, headers={"Accept": "text/csv"}
    )
    resp.raise_for_status()
    new_csv = (
        resp.text
    )  # Server sends UTF-8; if not, requests will try to detect encoding.

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
        # today = datetime.now().strftime("%Y%m%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        today = yesterday
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


def get_nhl_goalies() -> str:
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
    url = "https://moneypuck.com/moneypuck/playerData/seasonSummary/2025/regular/goalies.csv"
    latest_key = "nhl_goalies_2025_latest"  # file: DATA_DIR/<latest_key>.csv
    dated_key_prefix = (
        "nhl_goalies_2025_"  # file: DATA_DIR/daily_skaters/<prefix><YYYYMMDD>.csv
    )
    daily_dir = "daily_goalies"

    # Ensure directories exist
    os.makedirs(config.DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(config.DATA_DIR, daily_dir), exist_ok=True)

    expiry_hours = getattr(config, "CACHE_EXPIRY_HOURS", 4)

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
    resp = requests.get(
        url, timeout=30, allow_redirects=True, headers={"Accept": "text/csv"}
    )
    resp.raise_for_status()
    new_csv = (
        resp.text
    )  # Server sends UTF-8; if not, requests will try to detect encoding.

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
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        today = yesterday
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


def get_nhl_lines() -> str:
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
    url = "https://moneypuck.com/moneypuck/playerData/seasonSummary/2025/regular/lines.csv"
    latest_key = "nhl_lines_2025_latest"  # file: DATA_DIR/<latest_key>.csv
    dated_key_prefix = (
        "nhl_lines_2025_"  # file: DATA_DIR/daily_skaters/<prefix><YYYYMMDD>.csv
    )
    daily_dir = "daily_lines"

    # Ensure directories exist
    os.makedirs(config.DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(config.DATA_DIR, daily_dir), exist_ok=True)

    expiry_hours = getattr(config, "CACHE_EXPIRY_HOURS", 4)

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
    resp = requests.get(
        url, timeout=30, allow_redirects=True, headers={"Accept": "text/csv"}
    )
    resp.raise_for_status()
    new_csv = (
        resp.text
    )  # Server sends UTF-8; if not, requests will try to detect encoding.

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
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        today = yesterday
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


def get_nhl_teams() -> str:
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
    url = "https://moneypuck.com/moneypuck/playerData/seasonSummary/2025/regular/teams.csv"
    latest_key = "nhl_teams_2025_latest"  # file: DATA_DIR/<latest_key>.csv
    dated_key_prefix = (
        "nhl_teams_2025_"  # file: DATA_DIR/daily_skaters/<prefix><YYYYMMDD>.csv
    )
    daily_dir = "daily_teams"

    # Ensure directories exist
    os.makedirs(config.DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(config.DATA_DIR, daily_dir), exist_ok=True)

    expiry_hours = getattr(config, "CACHE_EXPIRY_HOURS", 4)

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
    resp = requests.get(
        url, timeout=30, allow_redirects=True, headers={"Accept": "text/csv"}
    )
    resp.raise_for_status()
    new_csv = (
        resp.text
    )  # Server sends UTF-8; if not, requests will try to detect encoding.

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
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        today = yesterday
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


def get_nhl_skaters_2024_2025_csv() -> str:
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
    url = "https://moneypuck.com/moneypuck/playerData/seasonSummary/2024/regular/skaters.csv"
    latest_key = "static_data/nhl_skaters_2024_2025"  # file: DATA_DIR/<latest_key>.csv
    dated_key_prefix = "nhl_skaters_2024_2025_regular_"  # file: DATA_DIR/daily_skaters/<prefix><YYYYMMDD>.csv
    daily_dir = "daily_skaters"

    # Ensure directories exist
    os.makedirs(config.DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(config.DATA_DIR, daily_dir), exist_ok=True)

    expiry_hours = getattr(config, "CACHE_EXPIRY_HOURS", 4)

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
    resp = requests.get(
        url, timeout=30, allow_redirects=True, headers={"Accept": "text/csv"}
    )
    resp.raise_for_status()
    new_csv = (
        resp.text
    )  # Server sends UTF-8; if not, requests will try to detect encoding.

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


def get_nhl_team_roster(team) -> Dict[str, Any]:
    """
    Fetch NHL standings (current) via requests and cache the JSON response.

    Uses:
    - requests.get with allow_redirects to match `curl -L -X GET`
    - cache.get_or_fetch to reuse a fresh cached file

    Tune freshness via config.CACHE_EXPIRY_HOURS (in your CacheManager).
    """
    cache_key = f"nhl_{team}_roster"

    def fetch_standings() -> Dict[str, Any]:
        # url = "https://api-web.nhle.com/v1/standings/now"
        url = f"https://api-web.nhle.com/v1/roster/{team}/current"
        resp = requests.get(
            url,
            timeout=30,
            allow_redirects=True,
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()

    return cache.get_or_fetch(cache_key, fetch_standings)


def get_nhl_week_schedule_now() -> Dict[str, Any]:
    """
    Fetch NHL standings (current) via requests and cache the JSON response.

    Uses:
    - requests.get with allow_redirects to match `curl -L -X GET`
    - cache.get_or_fetch to reuse a fresh cached file

    Tune freshness via config.CACHE_EXPIRY_HOURS (in your CacheManager).
    """
    cache_key = "nhl_week_schedule"

    def fetch_schedule() -> Dict[str, Any]:
        url = "https://api-web.nhle.com/v1/schedule/now"
        resp = requests.get(
            url,
            timeout=30,
            allow_redirects=True,
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()

    return cache.get_or_fetch(cache_key, fetch_schedule)


def get_nhl_calendar_schedule_now() -> Dict[str, Any]:
    """
    Fetch NHL standings (current) via requests and cache the JSON response.

    Uses:
    - requests.get with allow_redirects to match `curl -L -X GET`
    - cache.get_or_fetch to reuse a fresh cached file

    Tune freshness via config.CACHE_EXPIRY_HOURS (in your CacheManager).
    """
    cache_key = "nhl_calendar_schedule"

    def fetch_schedule() -> Dict[str, Any]:
        url = "https://api-web.nhle.com/v1/schedule/now"
        resp = requests.get(
            url,
            timeout=30,
            allow_redirects=True,
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()

    return cache.get_or_fetch(cache_key, fetch_schedule)


def get_nhl_yesterdays_scores() -> Dict[str, Any]:
    """
    Fetch NHL standings (current) via requests and cache the JSON response.

    Uses:
    - requests.get with allow_redirects to match `curl -L -X GET`
    - cache.get_or_fetch to reuse a fresh cached file

    Tune freshness via config.CACHE_EXPIRY_HOURS (in your CacheManager).
    """
    yesterdays_date = config.get_yesterday_NHL()
    cache_key = f"nhl_yesterdays_scores"

    def fetch_schedule() -> Dict[str, Any]:
        url = f"https://api-web.nhle.com/v1/score/{yesterdays_date}"
        resp = requests.get(
            url,
            timeout=30,
            allow_redirects=True,
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()

    return cache.get_or_fetch(cache_key, fetch_schedule)


def get_nhl_team_by_season_type() -> Dict[str, Any]:
    """
    Fetch NHL standings (current) via requests and cache the JSON response.

    Uses:
    - requests.get with allow_redirects to match `curl -L -X GET`
    - cache.get_or_fetch to reuse a fresh cached file

    Tune freshness via config.CACHE_EXPIRY_HOURS (in your CacheManager).
    """
    cache_key = "nhl_team_stats_season_type2"

    def fetch_standings() -> Dict[str, Any]:
        # url = "https://api-web.nhle.com/v1/standings/now"
        url = "https://api-web.nhle.com/v1/club-stats/TOR/20252026/2"
        resp = requests.get(
            url,
            timeout=30,
            allow_redirects=True,
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()

    return cache.get_or_fetch(cache_key, fetch_standings)


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
        # url = "https://api-web.nhle.com/v1/standings-season"
        resp = requests.get(
            url,
            timeout=30,
            allow_redirects=True,
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()

    return cache.get_or_fetch(cache_key, fetch_standings)


def get_nhl_api_leading_skaters() -> Dict[str, Any]:
    """
    Fetch NHL standings (current) via requests and cache the JSON response.

    Uses:
    - requests.get with allow_redirects to match `curl -L -X GET`
    - cache.get_or_fetch to reuse a fresh cached file

    Tune freshness via config.CACHE_EXPIRY_HOURS (in your CacheManager).
    """
    cache_key = "nhl_api_TOR_now"

    def fetch_schedule() -> Dict[str, Any]:
        url = "https://api-web.nhle.com/v1/club-schedule-season/TOR/20252026"
        resp = requests.get(
            url,
            timeout=30,
            allow_redirects=True,
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()

    return cache.get_or_fetch(cache_key, fetch_schedule)
