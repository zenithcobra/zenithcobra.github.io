"""
Data fetching functions for MLB API calls.
Extracted from script.py to improve organization and enable caching.
"""
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


def get_date() -> str:
    """Get the current date in the format required by 'statsapi'."""
    return datetime.now().strftime(config.DATE_FORMAT_MLB)


def get_yesterday(date_str: str) -> str:
    """Get the date previous to the one supplied."""
    date = datetime.strptime(date_str, config.DATE_FORMAT_MLB)
    yesterday = date - timedelta(days=1)
    return yesterday.strftime(config.DATE_FORMAT_MLB)


def get_schedule_by_date(date: str) -> List[Dict[str, Any]]:
    """Get the statsapi schedule based on the date provided."""
    # Use cache to avoid repeated API calls
    cache_key = f"schedule_{date.replace('/', '_')}"
    
    def fetch_schedule():
        return statsapi.schedule(start_date=date, end_date=date)
    
    return cache.get_or_fetch(cache_key, fetch_schedule)


def get_roster_names(team_id: int) -> List[str]:
    """Get a list of player names in the roster."""
    cache_key = f"roster_{team_id}"
    
    def fetch_roster():
        roster_string = statsapi.roster(team_id)
        roster_list_unprocessed = roster_string.split('\n')
        roster_list = []
        
        for entry in roster_list_unprocessed:
            player_name = ' '.join(entry.split()[2:])
            roster_list.append(player_name)
        
        # Filter out empty names
        return [name for name in roster_list if name != '']
    
    return cache.get_or_fetch(cache_key, fetch_roster)


def get_homerun_leaders_by_team(team_id: int, season: int = config.CURRENT_SEASON, 
                                leaderGameTypes: str = "R", limit: int = 10) -> List[Dict[str, Any]]:
    """Return a list of home run leaders for a given team ID."""
    cache_key = f"hr_leaders_{team_id}_{season}"
    
    def fetch_leaders():
        homerun_leaders_by_team = []
        home_leaders_data = statsapi.team_leader_data(
            team_id, 'homeRuns', season=season, 
            leaderGameTypes=leaderGameTypes, limit=limit
        )
        
        for z in home_leaders_data:
            homerun_leaders_by_team.append({'name': z[1], 'homeRuns': z[2]})
        
        return homerun_leaders_by_team
    
    return cache.get_or_fetch(cache_key, fetch_leaders)


def get_id_for_player(player_name: str) -> Optional[int]:
    """Return a player's ID based on their name."""
    mlb = mlbstatsapi.Mlb()
    player_id = mlb.get_people_id(player_name.strip())
    
    if not player_id:
        print(f"Warning: No get_people_id found for {player_name.strip()}")
        return None
    
    return player_id[0]


def get_player_name(player_id: int) -> Optional[str]:
    """Return the full name of a player based on their ID."""
    mlb = mlbstatsapi.Mlb()
    player_name = mlb.get_person(player_id).__dict__.get('fullname')

    if not player_name:
        print(f"Warning: No get_person found for ID {player_id}")
        return None
    
    return player_name


def get_team_from_id(team_id: int) -> Optional[str]:
    """Return the team name based on the team ID."""
    csv_file_path = os.path.join(config.DATA_DIR, 'mlb_teams.csv')
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == str(team_id) and row[5].lower() == 'present':
                    return row[3]
    except FileNotFoundError:
        print(f"Error: File '{csv_file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

    print(f"Warning: No team found for ID {team_id} marked as 'present'.")
    return None


def get_bvp_stats(batter_id: int, pitcher_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve batter vs pitcher (BvP) stats for the given batter and pitcher IDs."""
    mlb = mlbstatsapi.Mlb()
    
    stats = ['vsPlayer']
    group = ['hitting']
    params = {'opposingPlayerId': pitcher_id, 'season': config.CURRENT_SEASON}

    try:
        stats_data = mlb.get_player_stats(batter_id, stats=stats, groups=group, **params)
        vs_player_total = stats_data['hitting']['vsplayertotal']

        for split in vs_player_total.splits:
            p_id = mlb.get_person(pitcher_id)
            b_id = mlb.get_person(batter_id)

            return {
                'stats': split.stat.__dict__,
                'pitcher': p_id.__dict__.get('fullname'),
                'batter': b_id.__dict__.get('fullname')
            }

    except KeyError as e:
        print(f"KeyError: {e}. get_bvp_stats Skipping this player.")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}. get_bvp_stats Skipping this player.")
        return None

    return None


def get_schedule_text() -> str:
    """Get today's schedule formatted as text."""
    mlb_date = get_date()
    schedule = statsapi.schedule(start_date=mlb_date, end_date=mlb_date)

    # Convert times to Eastern timezone
    for game in schedule:
        utc_datetime_str = game.get("game_datetime")
        utc_datetime = datetime.strptime(utc_datetime_str, '%Y-%m-%dT%H:%M:%SZ')
        
        utc_zone = pytz.utc
        eastern_zone = pytz.timezone('US/Eastern')
        
        utc_datetime = utc_zone.localize(utc_datetime)
        eastern_datetime = utc_datetime.astimezone(eastern_zone)
        
        readable_format = eastern_datetime.strftime('%Y-%m-%d %I:%M %p %Z')
        
        beans = game.get('summary').split('-')
        new_beans = readable_format + " - " + beans[3].strip()
        game.update({"summary": new_beans})

    today_schedule_content = "Today's Schedule:\n" + "\n".join(
        f'{game.get("summary")}' for game in schedule
    )
    
    return today_schedule_content


def get_standings_text() -> str:
    """Get today's standings formatted as text."""
    mlb_date = get_date()
    
    standings_content = (
        "MLB Standings:\n"
        + statsapi.standings(leagueId=config.MLB_LEAGUES['AL'], date=mlb_date)
        + statsapi.standings(leagueId=config.MLB_LEAGUES['NL'], date=mlb_date)
    )
    
    return standings_content


def scrape_ballparks_table_to_json() -> List[Dict[str, Any]]:
    """Scrape ballpark data from external source."""
    cache_key = "ballpark_data"
    
    def fetch_ballpark_data():
        # This would contain the original scraping logic
        # For now, return empty list - this would be implemented based on the original function
        print("Fetching ballpark data from external source...")
        return []
    
    return cache.get_or_fetch(cache_key, fetch_ballpark_data)


def get_yesterdays_report(date: Optional[str] = None) -> List[str]:
    """Generate yesterday's report based on the provided date or defaults to yesterday's date."""
    if date is None:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        yesterday = date

    # Get yesterday's schedule
    oneday = timedelta(days=1)
    yesterday_date = datetime.now().date() - oneday
    yschedule = statsapi.schedule(start_date=yesterday_date, end_date=yesterday_date)

    # Separate entries with "Toronto" in the "summary" key
    entries_with_toronto = [x for x in yschedule if "summary" in x and "Toronto" in x["summary"]]
    entries_without_toronto = [x for x in yschedule if not ("summary" in x and "Toronto" in x["summary"])]

    content = []
    
    # Process Toronto game if exists
    if entries_with_toronto:
        toronto_game = entries_with_toronto[0]
        content.extend(_process_game_report(toronto_game, include_highlights=True))
    
    # Process all other games
    for game in entries_without_toronto:
        content.extend(_process_game_report(game, include_highlights=False))

    return content


def _process_game_report(game: Dict[str, Any], include_highlights: bool = False) -> List[str]:
    """Process individual game for report generation."""
    # Convert datetime
    utc_datetime_str = game.get("game_datetime")
    utc_datetime = datetime.strptime(utc_datetime_str, '%Y-%m-%dT%H:%M:%SZ')
    
    utc_zone = pytz.utc
    eastern_zone = pytz.timezone('US/Eastern')
    
    utc_datetime = utc_zone.localize(utc_datetime)
    eastern_datetime = utc_datetime.astimezone(eastern_zone)
    
    readable_format = eastern_datetime.strftime('%Y-%m-%d %I:%M %p %Z')
    
    content = [
        f"GAME:\n",
        f"{readable_format}\n",
        f"{game.get('away_name'):<22} {game.get('away_score')}    @\n",
        f"{game.get('home_name'):<22} {game.get('home_score')}\n\n"
    ]
    
    if include_highlights:
        # Get highlights and process links
        highlights = statsapi.game_highlights(game.get("game_id"))
        url_pattern = r'(https?://[^\s]+)'
        highlights_with_links = re.sub(url_pattern, r'<a href="\1" target="_blank">video link</a>', highlights)
        
        scoring_plays = statsapi.game_scoring_plays(game.get("game_id"))
        
        content.extend([
            f"{scoring_plays}\n\n",
            f"HIGHLIGHTS\n\n",
            f"{highlights_with_links}\n\n"
        ])
    else:
        # Get condensed game and highlights links
        highlights = statsapi.game_highlights(game.get("game_id"))
        highlights_list = highlights.split("\n")
        
        condensed_link = _extract_highlight_link(highlights_list, 'Condensed', 'Condensed Game')
        video_link = _extract_highlight_link(highlights_list, 'Highlights', 'Highlights Video')
        
        if condensed_link:
            content.append(f"{condensed_link}\n")
        if video_link:
            content.append(f"{video_link}\n\n")
    
    return content


def _extract_highlight_link(highlights_list: List[str], keyword: str, link_text: str) -> Optional[str]:
    """Extract highlight link from highlights list."""
    for i, line in enumerate(highlights_list):
        if keyword in line and i + 2 < len(highlights_list):
            link_url = highlights_list[i + 2]
            url_pattern = r'(https?://[^\s]+)'
            return re.sub(url_pattern, rf'<a href="\1" target="_blank">{link_text}</a>', link_url)
    return None