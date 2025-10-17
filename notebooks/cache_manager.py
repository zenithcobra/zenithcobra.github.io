"""
Cache management for MLB data to reduce API calls and improve performance.

This module provides a single class, CacheManager, that:
- Ensures data directories exist (via config.ensure_directories()).
- Checks whether a cached file is still "fresh" based on an expiry window.
- Reads cached data (JSON or plain text) if it's still valid.
- Saves data (with optional archiving of the previous file, dated as "yesterday").
- Offers convenience helpers (save_json/save_text/save_html, load_json/load_text).
- Provides a get_or_fetch() method to hide the "check cache vs. fetch" decision.

It depends on config.py for:
- Directory paths: DATA_DIR, DOCS_DIR, ARCHIVED_DATA_DIR
- DATE_FORMAT_FILE: strftime-compatible format for file names (e.g., "%Y%m%d")
- CACHE_EXPIRY_HOURS: how long a cached file is considered valid
- ensure_directories(): a function that creates required folders
"""

import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable

import notebooks.config as config


class CacheManager:
    """
    Manages caching of data to reduce redundant network/API calls.

    Typical usage:
    - cache = CacheManager()
    - data = cache.get_or_fetch("games_today", fetch_games_from_api, arg1, arg2)
      -> If a fresh cache exists at DATA_DIR/games_today.json, it returns that.
      -> Otherwise, it calls fetch_games_from_api(...), saves JSON to cache, returns fresh data.
    """

    def __init__(self) -> None:
        # Ensure required directories are present (DATA_DIR, DOCS_DIR, ARCHIVED_DATA_DIR, etc.)
        # This prevents failures when saving/archiving files later.
        config.ensure_directories()

    # -----------------------------
    # Cache validation and reading
    # -----------------------------

    def is_cache_valid(
        self,
        file_path: str,
        expiry_hours: int = config.CACHE_EXPIRY_HOURS
    ) -> bool:
        """
        Determine if a cache file is still valid.

        A cache is considered valid if:
        - The file exists, and
        - Its modification time is newer than (now - expiry_hours)

        This is a simple and fast check using the file's last modified timestamp.
        """
        if not os.path.exists(file_path):
            return False

        file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        expiry_cutoff = datetime.now() - timedelta(hours=expiry_hours)

        return file_mod_time > expiry_cutoff

    def get_cached_data(
        self,
        file_path: str,
        expiry_hours: int = config.CACHE_EXPIRY_HOURS
    ) -> Optional[Any]:
        """
        Read cached data if it's valid; otherwise return None.

        Behavior:
        - If valid, open the file.
          - If the filename ends with ".json", parse and return JSON (dict/list).
          - Otherwise, return the raw text content.
        - If invalid or an error occurs (e.g., malformed JSON), return None.
        """
        if not self.is_cache_valid(file_path, expiry_hours):
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as fh:
                if file_path.endswith(".json"):
                    return json.load(fh)
                return fh.read()
        except (json.JSONDecodeError, OSError, IOError) as exc:
            # If cache is corrupted or unreadable, treat as a cache miss.
            print(f"Error reading cached file {file_path}: {exc}")
            return None

    # -----------------------------
    # Saving and archiving
    # -----------------------------

    def save_data(
        self,
        data: Any,
        file_path: str,
        archive_existing: bool = True
    ) -> None:
        """
        Save data to a file, optionally archiving the previous version.

        - If archive_existing is True and the file already exists, we move it into
          ARCHIVED_DATA_DIR with a suffix for yesterday's date (e.g., _20250131).
        - Then we write the new data:
          - If file_path ends with ".json", we json.dump(data, indent=4).
          - Otherwise:
            * If data is a list, we write each item as-is via writelines()
              (NOTE: items should already contain newline characters if desired).
            * Else, we str() the data and write it as text.
        """
        # Ensure the target directory exists (safety, even though config ensured top-level dirs)
        os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)

        if archive_existing and os.path.exists(file_path):
            self._archive_existing_file(file_path)

        try:
            with open(file_path, "w", encoding="utf-8") as fh:
                if file_path.endswith(".json"):
                    json.dump(data, fh, indent=4)
                else:
                    if isinstance(data, list):
                        # Each element is written directly; include '\n' in each element if you want new lines.
                        fh.writelines(data)
                    else:
                        fh.write(str(data))
            print(f"Data saved to {file_path}")
        except (OSError, IOError, TypeError, ValueError) as exc:
            print(f"Error saving data to {file_path}: {exc}")

    def _archive_existing_file(self, file_path: str) -> None:
        """
        Move an existing file to ARCHIVED_DATA_DIR with a 'yesterday' date suffix.

        Example:
        - If file_path is data/scores.json and DATE_FORMAT_FILE is "%Y%m%d",
          yesterday might be "20250916", so we archive to:
          ARCHIVED_DATA_DIR/scores_20250916.json

        Notes:
        - We only archive if that dated file doesn't already exist, to avoid overwriting history.
        """
        yesterday_date = (datetime.now() - timedelta(days=1)).strftime(config.DATE_FORMAT_FILE)

        filename = os.path.basename(file_path)          # e.g., "scores.json"
        name, ext = os.path.splitext(filename)          # -> "scores", ".json"
        archived_filename = f"{name}_{yesterday_date}{ext}"
        archived_path = os.path.join(config.ARCHIVED_DATA_DIR, archived_filename)

        # Ensure archive directory exists (in case ensure_directories changes or custom paths used)
        os.makedirs(os.path.dirname(archived_path) or ".", exist_ok=True)

        if not os.path.exists(archived_path):
            try:
                os.rename(file_path, archived_path)     # Move the file (fast within same filesystem)
                print(f"Archived existing file to {archived_path}")
            except OSError as exc:
                print(f"Error archiving file {file_path}: {exc}")
        else:
            print(f"Archived file already exists: {archived_path}")

    # -----------------------------
    # Convenience helpers
    # -----------------------------

    def save_json(self, data: List[Dict], filename: str) -> None:
        """
        Save JSON to DATA_DIR/<filename>.json with archiving.
        'data' should be JSON-serializable (typically a list[dict]).
        """
        file_path = os.path.join(config.DATA_DIR, f"{filename}.json")
        self.save_data(data, file_path)

    def save_text(self, content: str, filename: str) -> None:
        """
        Save plain text to DATA_DIR/<filename>.txt with archiving.
        """
        file_path = os.path.join(config.DATA_DIR, f"{filename}.txt")
        self.save_data(content, file_path)

    def save_html(self, content: str, filename: str) -> None:
        """
        Save HTML to DOCS_DIR/<filename>.html without archiving.

        Rationale:
        - HTML outputs are often rebuilt frequently for presentation. If you want to
          archive HTML too, set archive_existing=True here or provide a separate method.
        """
        file_path = os.path.join(config.DOCS_DIR, f"{filename}.html")
        self.save_data(content, file_path, archive_existing=False)

    def load_json(
        self,
        filename: str,
        expiry_hours: int = config.CACHE_EXPIRY_HOURS
    ) -> Optional[List[Dict]]:
        """
        Load JSON from DATA_DIR/<filename>.json if cache is still valid.
        Returns the parsed data or None if missing/expired/invalid.
        """
        file_path = os.path.join(config.DATA_DIR, f"{filename}.json")
        return self.get_cached_data(file_path, expiry_hours)

    def load_text(
        self,
        filename: str,
        expiry_hours: int = config.CACHE_EXPIRY_HOURS
    ) -> Optional[str]:
        """
        Load plain text from DATA_DIR/<filename>.txt if cache is still valid.
        Returns the text or None if missing/expired/unreadable.
        """
        file_path = os.path.join(config.DATA_DIR, f"{filename}.txt")
        return self.get_cached_data(file_path, expiry_hours)

    # -----------------------------
    # Cache-or-fetch helper
    # -----------------------------

    def get_or_fetch(
        self,
        cache_key: str,
        fetch_function: Callable[..., Any],
        *args,
        **kwargs
    ) -> Any:
        """
        Try to load JSON from cache (DATA_DIR/<cache_key>.json).
        If not available or expired, call fetch_function(*args, **kwargs),
        save the JSON to cache, and return the fresh data.

        This is a common pattern to reduce network/API calls:
        - First try cache.
        - If cache miss, compute/fetch, then save and return.
        """
        cached = self.load_json(cache_key)
        if cached is not None:
            print(f"Using cached data for {cache_key}")
            return cached

        print(f"Fetching fresh data for {cache_key}")
        fresh = fetch_function(*args, **kwargs)
        self.save_json(fresh, cache_key)
        return fresh

    # -----------------------------
    # Maintenance
    # -----------------------------

    def clear_cache(self, pattern: Optional[str] = None) -> None:
        """
        Remove files from DATA_DIR. If pattern is provided, only files whose
        names contain that substring are removed.

        Examples:
        - clear_cache() -> clears all files in DATA_DIR
        - clear_cache("scores") -> clears any files with "scores" in the name
        """
        try:
            for filename in os.listdir(config.DATA_DIR):
                if pattern is None or pattern in filename:
                    file_path = os.path.join(config.DATA_DIR, filename)
                    try:
                        os.remove(file_path)
                        print(f"Removed cached file: {file_path}")
                    except OSError as exc:
                        print(f"Error removing file {file_path}: {exc}")
        except OSError as exc:
            print(f"Error listing directory {config.DATA_DIR}: {exc}")


# Create a global instance for convenience. You can import this directly:
# from cache_manager import cache
cache = CacheManager()