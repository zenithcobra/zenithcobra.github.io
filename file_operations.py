from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from fractions import Fraction
import csv
import json
import mlbstatsapi
import os
import pytz
import re
import requests
import statsapi
import requests
from bs4 import BeautifulSoup
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from pathlib import Path
from typing import Optional, Tuple, Union, List, Dict

import config


def read_csv(csv_file_path):
    """read csv to list"""
    with open(csv_file_path, mode='r') as file:
        return list(csv.reader(file))


def _archive_if_exists(
    target_path: Path, archived_dir: Path, base_name: str, ext: str
) -> None:
    """Archive existing file to archived_dir with yesterday's date suffix."""
    if target_path.exists():
        yesterday_date = (datetime.now() - timedelta(days=1)).strftime(
            config.DATE_FORMAT_FILE
        )
        archived_dir.mkdir(parents=True, exist_ok=True)
        archived_path = archived_dir / f"{base_name}_{yesterday_date}.{ext}"
        if not archived_path.exists():
            target_path.rename(archived_path)
            print(f"Archived existing file to {archived_path}")
        else:
            print(f"Archived file already exists: {archived_path}")


def _write_file(target_path: Path, writer, data) -> None:
    """Create parent dirs and write using provided writer(fh, data)."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open("w", encoding="utf-8") as fh:
        writer(fh, data)


def save_json(data, supplied_filename: str) -> None:
    """Unified JSON saver using config directories and archiving."""
    target_path = Path(config.DATA_DIR) / f"{supplied_filename}.json"
    _archive_if_exists(
        target_path, Path(config.ARCHIVED_DATA_DIR), supplied_filename, "json"
    )
    _write_file(target_path, lambda fh, d: json.dump(d, fh, indent=4), data)
    print(f"Today's data saved to {target_path}")


def save_text(text_or_lines, supplied_filename: str) -> None:
    """Save text or list of lines to data/<name>.txt with archiving."""
    if isinstance(text_or_lines, (list, tuple)):
        # Join with newline to preserve lines; adjust if you intentionally omit newlines
        content = "\n".join(map(str, text_or_lines))
    else:
        content = str(text_or_lines)
    target_path = Path(config.DATA_DIR) / f"{supplied_filename}.txt"
    _archive_if_exists(
        target_path, Path(config.ARCHIVED_DATA_DIR), supplied_filename, "txt"
    )
    _write_file(target_path, lambda fh, d: fh.write(d), content)
    print(f"Today's data saved to {target_path}")


def save_html(html: str, supplied_filename: str) -> None:
    """Save HTML to docs/<name>.html with archiving into docs/archived_data."""
    target_path = Path(config.DOCS_DIR) / f"{supplied_filename}.html"
    _archive_if_exists(
        target_path, Path(config.ARCHIVED_DOCS_DIR), supplied_filename, "html"
    )
    _write_file(target_path, lambda fh, d: fh.write(d), html)
    print(f"Today's data saved to {target_path}")


def save_to_json(list_of_dicts, supplied_filename):
    """Backward-compatible wrappers (delete old duplicate implementations)"""
    return save_json(list_of_dicts, supplied_filename)


def save_to_json_dictionary(dictionary, supplied_filename):
    """Backward-compatible wrappers (delete old duplicate implementations)"""
    # Fixed bug: was dumping undefined list_of_dicts
    return save_json(dictionary, supplied_filename)


def save_list_to_text(list_of_lines, supplied_filename):
    """Backward-compatible wrappers (delete old duplicate implementations)"""
    return save_text(list_of_lines, supplied_filename)


def save_to_text(content, supplied_filename):
    """Backward-compatible wrappers (delete old duplicate implementations)"""
    return save_text(content, supplied_filename)


def save_to_html(content, supplied_filename):
    """Backward-compatible wrappers (delete old duplicate implementations)"""
    return save_html(content, supplied_filename)
