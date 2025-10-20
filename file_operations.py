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
import csv
import notebooks.config as config


def convert_csv_to_json(csv_file_path, json_file_path):
    """
    Converts a CSV file to a JSON file.
    Args:
        csv_file_path (str): Path to the input CSV file.
        json_file_path (str): Path to the output JSON file.
    """
    # Read the CSV file and convert it to a list of dictionaries
    data = []
    with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)  # Automatically uses the headers as keys
        for row in csv_reader:
            # Convert any string representations of lists back to Python lists
            for key, value in row.items():
                if value.startswith('[') and value.endswith(']'):
                    try:
                        row[key] = json.loads(value)  # Parse the string as a list
                    except json.JSONDecodeError:
                        pass  # Leave the value as is if it can't be parsed
            data.append(row)

    # Write the data to a JSON file
    with open(json_file_path, mode='w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)

    print(f"CSV data has been converted to JSON and saved to {json_file_path}")


def read_json_to_list(json_file_path):
    """
    Reads a JSON file and returns its contents as a list of dictionaries.

    Args:
        json_file_path (str): Path to the JSON file.

    Returns:
        list: List of dictionaries containing the JSON data.
    """
    with open(json_file_path, mode='r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data

def read_csv(csv_file_path):
    """read csv to list"""
    with open(csv_file_path, mode='r') as file:
        return list(csv.reader(file))

def read_json_file(file_path):
    """
    Reads a JSON file containing a list of dictionaries and returns the data.

    Args:
        file_path (str): The path to the JSON file to be read.

    Returns:
        list: A list of dictionaries if the file is successfully read and contains valid JSON data.
        None: If the file does not exist, is not valid JSON, or does not contain a list of dictionaries.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
        ValueError: If the JSON data is not a list of dictionaries.

    Example:
        >>> data = read_json_file("data.json")
        >>> if data:
        ...     for item in data:
        ...         print(item)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                return data
            else:
                raise ValueError("The JSON file does not contain a list of dictionaries.")
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON. {e}")
    except ValueError as e:
        print(f"Error: {e}")
    return None

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

def save_to_csv(csv_lines, headers, file_path):
    with open(file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)  # Write the headers
        writer.writerows(csv_lines)  # Write the data
