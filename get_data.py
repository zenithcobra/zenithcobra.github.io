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


