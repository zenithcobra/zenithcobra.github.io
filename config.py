"""
Configuration settings for MLB analysis application
"""

import os
from datetime import datetime, timedelta

# Directories
DATA_DIR = "NHL_data"
# DOCS_DIR = "docs"
# TEXT_OUTPUT_DIR = "text_output2"
ARCHIVED_DATA_DIR = os.path.join(DATA_DIR, "archived_nhl_data")
DAILY_SKATERS_DIR = os.path.join(DATA_DIR, "daily_skaters")
DAILY_SCORES_DIR = os.path.join(DATA_DIR, "daily_scores")
# ARCHIVED_DOCS_DIR = os.path.join(DOCS_DIR, "archived_data2")

# File paths
BALLPARK_DATA_FILE = os.path.join(DATA_DIR, "ballpark_data.json")
SCHEDULE_DATA_FILE = os.path.join(DATA_DIR, "schedule_data.json")
TEAM_DATA_FILE = os.path.join(DATA_DIR, "team_data.json")
ALL_TEAM_DATA_FILE = os.path.join(DATA_DIR, "all_team_data.json")
PITCHER_DATA_FILE = os.path.join(DATA_DIR, "pitcher_data.json")
BATTER_DATA_FILE = os.path.join(DATA_DIR, "batter_data.json")
BVP_DATA_FILE = os.path.join(DATA_DIR, "batter_vs_pitcher_data.json")
DH_BATTER_DATA_FILE = os.path.join(DATA_DIR, "dh_batter_data.json")
YESTERDAY_HOME_RUN_DATA_FILE = os.path.join(DATA_DIR, "yesterday_home_run_data.json")
TEAMS_PLAYING_TODAY_FILE = os.path.join(DATA_DIR, "teams_playing_today_data.json")

# Leader data files
ERA_LEADER_DATA_FILE = os.path.join(DATA_DIR, "ERA_leader_data.json")
SO9_LEADER_DATA_FILE = os.path.join(DATA_DIR, "SO9_leader_data.json")
HR_LEADER_DATA_FILE = os.path.join(DATA_DIR, "HR_leader_data.json")

# Text files
PARLAY_BANNED_LIST_FILE = os.path.join(DATA_DIR, "parlay_banned_list.txt")
YESTERDAYS_REPORT_TEXT_FILE = os.path.join(DATA_DIR, "yesterdays_report_text.txt")
STANDINGS_TEXT_FILE = os.path.join(DATA_DIR, "standings_text.txt")
SCHEDULE_TEXT_FILE = os.path.join(DATA_DIR, "schedule_text.txt")

# Output files
# INDEX_HTML_FILE = os.path.join(DOCS_DIR, "index.html")

# Cache settings
CACHE_EXPIRY_HOURS = 4  # How long to keep cached data
CURRENT_SEASON = 2025

# API settings
MLB_LEAGUES = {"AL": 103, "NL": 104}

# Date formats
DATE_FORMAT_MLB = "%m/%d/%Y"
DATE_FORMAT_FILE = "%Y-%m-%d"


def ensure_directories():
    """Ensure all required directories exist."""
    directories = [
        DATA_DIR,
        # DOCS_DIR,
        # TEXT_OUTPUT_DIR,
        ARCHIVED_DATA_DIR,
        # ARCHIVED_DOCS_DIR,
        DAILY_SKATERS_DIR,
        DAILY_SCORES_DIR
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def get_current_date():
    """Get current date in MLB API format."""
    return datetime.now().strftime(DATE_FORMAT_MLB)


def get_current_date_file():
    """Get current date in file format."""
    return datetime.now().strftime(DATE_FORMAT_FILE)


def get_yesterday(date_str):
    """
    Gets the date previous to the one supplied.
    Args:
        date_str (str): A date string formatted as 'MM/DD/YYYY'.
    Returns:
        str: The previous date formatted as 'MM/DD/YYYY'.
    """
    # Convert the input date string to a datetime object
    date = datetime.strptime(date_str, "%m/%d/%Y")
    # Subtract one day
    yesterday = date - timedelta(days=1)
    # Return the formatted date
    return yesterday.strftime("%m/%d/%Y")


def get_yesterday_NHL():
    """
    Gets the date previous to the one supplied.
    Args:
        date_str (str): A date string formatted as 'MM/DD/YYYY'.
    Returns:
        str: The previous date formatted as 'MM/DD/YYYY'.
    """
    date_str = get_current_date()
    # Convert the input date string to a datetime object
    date = datetime.strptime(date_str, "%m/%d/%Y")
    # Subtract one day
    yesterday = date - timedelta(days=1)
    # Return the formatted date
    return yesterday.strftime("%Y-%m-%d")