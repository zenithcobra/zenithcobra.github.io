from bs4 import BeautifulSoup
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime
from datetime import datetime
from datetime import datetime
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from dateutil.parser import parse
from fractions import Fraction
from os import listdir
from os.path import isfile, join
from pathlib import Path
from pathlib import Path
from pathlib import Path  # Import Path
from typing import Any, Dict, List, Optional
import ast
import csv
import csv
import csv
import csv
import csv
import csv
import csv
import csv
import file_operations
import file_operations
import hashlib
import json
import json
import json
import json
import numpy as np
import os
import os
import os
import os
import os
import os
import os
import os
import os
import os
import pandas as pd
import pandas as pd
import pandas as pd
import pandas as pd
import pandas as pd
import pathlib
import pytz
import re
import re
import re  # Import the regular expressions module
import requests
import requests
import requests
import requests
import requests
import requests
import shutil

def parse_txt_to_array(input_file):
    """
    Parses a text file into an array of lines with values separated.

    Args:
        input_file (str): Path to the input text file.

    Returns:
        list: A list of parsed lines, where each line is an array of values.
    """
    parsed_lines = []

    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Skip the first line (header) and parse the rest
    for line in lines[1:]:
        parts = line.strip().split()  # Split the line into parts
        if len(parts) < 8:
            continue  # Skip malformed lines

        # Extract fields
        home_away = parts[0]  # H or A
        date = parts[1]  # Date
        team1 = parts[2]  # Team 1 abbreviation
        team1_score = parts[3]  # Team 1 score
        dash = parts[4]  # Dash ('-')
        team2 = parts[5]  # Team 2 abbreviation
        team2_score = parts[6]  # Team 2 score
        ot_so = parts[7] if '(' in parts[7] else ' '  # OT/SO if present, otherwise empty
        win_loss = parts[-1]  # W, L, or T

        # Append the parsed line as an array
        parsed_lines.append([home_away, date, team1, team1_score, dash, team2, team2_score, ot_so, win_loss])

    return parsed_lines


def format_games_to_string(games):
    """
    Formats an array of game data into a single string in the desired format.

    Args:
        games (list): A list of arrays, where each array represents a game.

    Returns:
        str: A formatted string summarizing the games.
    """
    if not games:
        return ""

    # Extract the team abbreviations from the first game
    team1 = games[0][2]  # Team 1 abbreviation
    team2 = games[0][5]  # Team 2 abbreviation

    # Start building the formatted string
    formatted_string = f"{team1} vs {team2}"

    # Add each game's details
    game_details = []
    for game in games:
        location = game[0]  # H or A
        team1_score = game[3]  # Team 1 score
        team2_score = game[6]  # Team 2 score
        ot_so = game[7].strip()  # OT/SO if present, otherwise empty
        if ot_so:  # Append OT/SO if it exists
            game_details.append(f"{location}:{team1_score}-{team2_score}{ot_so.lower()}")
        else:
            game_details.append(f"{location}:{team1_score}-{team2_score}")

    # Combine the game details into the final string
    formatted_string += " " + " | ".join(game_details)
    return formatted_string


def process_all_modified_files(game_data_dir):
    """
    Processes all files in the game_data directory that have `_modified.txt` in their name,
    generates a formatted string for each file, and writes the results to 'todays_history.txt'.
    Each line in the output file will only include the first 7 '|'-separated segments.

    Args:
        game_data_dir (str): Path to the directory containing the game files.

    Returns:
        None
    """
    output_file = os.path.join("todays_history.txt")

    with open(output_file, "w", encoding="utf-8") as outfile:
        for filename in os.listdir(game_data_dir):
            if filename.endswith("_modified.txt"):
                input_file = os.path.join(game_data_dir, filename)
                parsed_data = parse_txt_to_array(input_file)
                formatted_string = format_games_to_string(parsed_data)

                # Limit the formatted string to the first 7 '|'-separated segments
                parts = formatted_string.split(" | ")
                limited_string = " | ".join(parts[:7])

                # Write the limited string to the output file
                outfile.write(limited_string + "\n")
                print(limited_string)

    print(f"History saved to {output_file}")

# def process_all_modified_files(game_data_dir):
#     """
#     Processes all files in the game_data directory that have `_modified.txt` in their name
#     and prints the formatted string for each file.

#     Args:
#         game_data_dir (str): Path to the directory containing the game files.

#     Returns:
#         None
#     """
#     for filename in os.listdir(game_data_dir):
#         if filename.endswith("_modified.txt"):
#             input_file = os.path.join(game_data_dir, filename)
#             parsed_data = parse_txt_to_array(input_file)
#             formatted_string = format_games_to_string(parsed_data)
#             # print(f"File: {filename}")
#             print(formatted_string)
#             # print()

def replace_team_names_in_file(input_txt_file, input_csv_file, output_txt_file):
    """
    Reads a text file and replaces all team names that match the `NAME` column in the CSV file
    with the corresponding abbreviation from the `ABBREV` column.

    Args:
        input_txt_file (str): Path to the input text file.
        input_csv_file (str): Path to the input CSV file.
        output_txt_file (str): Path to the output text file where the modified content will be saved.

    Returns:
        None
    """
    # Load the mapping of team names to abbreviations from the CSV file
    name_to_abbrev = {}
    with open(input_csv_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name_to_abbrev[row['NAME']] = row['ABBREV']

    # Read the input text file and replace team names
    with open(input_txt_file, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    modified_lines = []
    for line in lines:
        modified_line = line
        for name, abbrev in name_to_abbrev.items():
            if name in modified_line:
                modified_line = modified_line.replace(name, abbrev)
        modified_lines.append(modified_line)

    # Write the modified content to the output text file
    with open(output_txt_file, 'w', encoding='utf-8') as outfile:
        outfile.writelines(modified_lines)

    print(f"Modified file saved to {output_txt_file}")


def process_all_game_files(game_data_dir, input_csv_file):
    """
    Processes all files in the game_data directory that match the pattern `nhl_games_cleaned{0+}.txt`
    and creates a modified file for each.

    Args:
        game_data_dir (str): Path to the directory containing the game files.
        input_csv_file (str): Path to the input CSV file.

    Returns:
        None
    """
    for filename in os.listdir(game_data_dir):
        if filename.startswith("nhl_games_cleaned") and filename.endswith(".txt"):
            input_txt_file = os.path.join(game_data_dir, filename)
            output_txt_file = os.path.join(game_data_dir, filename.replace(".txt", "_modified.txt"))
            replace_team_names_in_file(input_txt_file, input_csv_file, output_txt_file)


def parse_nhl_games_to_array(input_file):
    """
    Reads an NHL games text file and parses each line into an array of values.

    Args:
        input_file (str): Path to the input text file.

    Returns:
        list: A list of parsed lines, where each line is an array of values.
    """
    parsed_lines = []

    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Skip the first line and parse the rest
    for line in lines[1:]:
        parts = line.split()
        if len(parts) < 8:
            continue  # Skip malformed lines

        # Extract fields
        home_away = parts[0]  # H or A
        date = parts[1]  # Date
        team1 = " ".join(parts[2:parts.index('-') - 1])  # Team 1 name
        team1_score = parts[parts.index('-') - 1]  # Team 1 score
        team2 = " ".join(parts[parts.index('-') + 1:parts.index(parts[-2])])  # Team 2 name
        team2_score = parts[parts.index('-') + 1]  # Team 2 score
        ot_so = parts[-2] if '(' in parts[-2] else ""  # OT or SO if present
        win_loss = parts[-1]  # W, L, or T

        # Append the parsed line as an array
        parsed_lines.append([home_away, date, team1, team1_score, team2, team2_score, ot_so, win_loss])

    return parsed_lines


def extract_and_clean_all_games_section(input_file_path, output_file_path):
    """
    Extracts the 'ALL GAMES' section from the input file, removes HTML tags, and saves it to a new file.

    Args:
        input_file_path (str): Path to the input file.
        output_file_path (str): Path to the output file where cleaned content will be saved.

    Returns:
        None
    """
    try:
        with open(input_file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Extract the 'ALL GAMES' section
        match = re.search(r"<b>ALL GAMES:</b>.*?</pre>", content, re.DOTALL)
        if not match:
            raise ValueError("Could not find the 'ALL GAMES' section in the file.")

        all_games_section = match.group(0)

        # Remove HTML tags
        cleaned_content = re.sub(r"<[^>]*>", "", all_games_section)

        # Save the cleaned content to the output file
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(cleaned_content.strip())

        print(f"Cleaned 'ALL GAMES' section saved to {output_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

def save_url_to_text_file(url, output_file_path):
    """
    Fetches the content of a URL and saves it to a text file.

    Args:
        url (str): The URL to fetch.
        output_file_path (str): The path to save the content as a text file.

    Returns:
        None
    """
    try:
        # Fetch the webpage
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes

        # Save the content to a text file
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(response.text)

        print(f"Content saved to {output_file_path}")
    except Exception as e:
        print(f"Error fetching or saving the URL content: {e}")
def get_all_games_from_url(url):
    """
    Fetches the 'ALL GAMES' section from the given URL and parses the game data.

    Args:
        url (str): The URL of the page to scrape.

    Returns:
        list: A list of game data, where each game is represented as a string.
    """
    try:
        # Fetch the webpage
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the "ALL GAMES" section
        all_games_section = soup.find(string="ALL GAMES:").find_next("pre")
        if not all_games_section:
            raise ValueError("Could not find the 'ALL GAMES' section on the page.")

        # Extract the text and split into lines
        all_games_text = all_games_section.get_text()
        all_games_lines = all_games_text.splitlines()

        # Remove empty lines and return the data
        return [line.strip() for line in all_games_lines if line.strip()]

    except Exception as e:
        print(f"Error fetching or parsing the URL: {e}")
        return []


def generate_matchup_urls(matchups):
    """
    Generates URLs for each matchup in both directions.

    Args:
        matchups (list): A list of matchups, where each matchup is a list of two team abbreviations.

    Returns:
        list: A list of URLs for each matchup in both directions.
    """
    urls = []
    for team1, team2 in matchups:
        urls.append(f"https://mcubed.net/nhl/{team1}/{team2}.shtml")
        urls.append(f"https://mcubed.net/nhl/{team2}/{team1}.shtml")
    return urls

def replace_team_names_with_other_short(matchups, team_names):
    """
    Replaces team names in matchups with their corresponding 'OTHER_SHORT' values.

    Args:
        matchups (list): A list of matchups, where each matchup is a list of two team names.
        team_names (list): A list of team data, where each entry contains team details.

    Returns:
        list: A new list of matchups with team names replaced by 'OTHER_SHORT' values.
    """
    # Create a mapping of team names to their 'OTHER_SHORT' values
    name_to_other_short = {team[1]: team[3] for team in team_names}

    # Replace team names in matchups with their 'OTHER_SHORT' values
    updated_matchups = []
    for matchup in matchups:
        team1, team2 = matchup
        updated_matchups.append([
            name_to_other_short.get(team1, team1),  # Replace team1 if found, else keep original
            name_to_other_short.get(team2, team2)   # Replace team2 if found, else keep original
        ])

    return updated_matchups

def parse_schedule_to_matchups(schedule_text):
    """
    Parses a schedule text into an array of team matchups.

    Args:
        schedule_text (str): The multiline schedule text.

    Returns:
        list: A list of matchups, where each matchup is a list of two teams.
    """
    lines = schedule_text.splitlines()
    matchups = []

    for line in lines:
        # Split the line into parts and extract the teams
        parts = line.split(" - ")
        if len(parts) == 2:
            teams = parts[1].split(" @ ")
            if len(teams) == 2:
                matchups.append([teams[0].strip(), teams[1].strip()])

    return matchups

def text_to_csv(array1, output_csv_path):
    """
    Converts a multiline text string into a CSV file.

    Args:
        text (str): The multiline text string to convert.
        output_csv_path (str): The path to save the CSV file.

    Returns:
        None
    """
    lines = array1
    if not lines:
        raise ValueError("The input text is empty.")

    # Extract headers and data
    headers = lines[0].split()
    data = []

    for line in lines[1:]:
        # Split the line into columns based on whitespace
        # Use rsplit to handle team names with spaces
        parts = line.rsplit(maxsplit=len(headers) - 1)
        data.append(parts)

    # Write to CSV
    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)  # Write headers
        writer.writerows(data)    # Write data rows

    print(f"CSV file saved to {output_csv_path}")

def split_text_into_lines(multiline_text):
    """
    Splits a multiline text string into an array of lines.

    Args:
        multiline_text (str): The multiline text string to split.

    Returns:
        list: A list of lines from the input text.
    """
    return multiline_text.splitlines()

def remove_indices_from_list(input_list, indices_to_remove):
    """
    Removes multiple entries from a list at specific index locations.

    Args:
        input_list (list): The original list.
        indices_to_remove (list): A list of indices to remove.

    Returns:
        list: A new list with the specified indices removed.
    """
    indices_to_remove = set(indices_to_remove)  # Convert to set for faster lookup
    return [item for idx, item in enumerate(input_list) if idx not in indices_to_remove]

def get_match_results(daily_scores_dir, team_names_csv, teams_today):
    """
    Processes daily scores and matches today's teams with their short names from the CSV.
    Finds results for each match and returns a list of results in the format:
    OTT vs BOS - W-L-W
    BOS vs OTT - L-W-L

    Args:
        daily_scores_dir (str): Path to the directory containing daily scores files.
        team_names_csv (str): Path to the CSV file containing team abbreviations and names.
        teams_today (list): List of team abbreviations organized as matches for the night.

    Returns:
        list: A list of strings with match results.
    """
    # Load team name mappings from the CSV
    team_name_map = {}
    with open(team_names_csv, "r", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # Skip the header
        for row in reader:
            abbrev, name, short = row
            team_name_map[abbrev] = short

    # Swap abbreviations with short names for today's teams
    teams_today_short = [team_name_map.get(team, team) for team in teams_today]

    # Get all files in the directory
    files = [
        f
        for f in os.listdir(daily_scores_dir)
        if f.startswith("NHL_scores_") and f.endswith(".json")
    ]
    files.sort(
        key=lambda x: datetime.strptime(x.split("_")[2].split(".")[0], "%Y-%m-%d"),
        reverse=True,
    )

    # Initialize results dictionary for matches
    match_results = []

    # Process each file
    for file in files:
        file_path = os.path.join(daily_scores_dir, file)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            # Process each game
            for game in data:
                home_team = game.get("home_team")
                away_team = game.get("away_team")
                winner = game.get("winner")

                # Check if today's teams are playing each other
                for i in range(
                    0, len(teams_today), 2
                ):  # Iterate through pairs of teams
                    team1 = teams_today_short[i]
                    team2 = teams_today_short[i + 1]

                    if (home_team == team1 and away_team == team2) or (
                        home_team == team2 and away_team == team1
                    ):
                        # Determine result for each team
                        if home_team == team1:
                            result1 = "W" if winner == home_team else "L"
                            result2 = "W" if winner == away_team else "L"
                        else:
                            result1 = "W" if winner == away_team else "L"
                            result2 = "W" if winner == home_team else "L"

                        # Add results to match results
                        match_results.append(
                            f"{team1} vs {team2} - {result1}-{result2}"
                        )
                        match_results.append(
                            f"{team2} vs {team1} - {result2}-{result1}"
                        )

    new_listy = []
    for index, item in enumerate(match_results):
        new_listy.append(item)
        # Check if the current index (plus 1 for 1-based counting) is a multiple of 2
        # and if it's not the very end of the original list
        if (index + 1) % 2 == 0 and index + 1 < len(match_results):
            new_listy.append("       ")

    return new_listy


def get_team_records(daily_scores_dir, team_names_csv, teams_today):
    """
    Processes daily scores and matches today's teams with their short names from the CSV.
    Finds results for each team and returns a list of results in the format:
    CGY - W-L-W-W-L

    Args:
        daily_scores_dir (str): Path to the directory containing daily scores files.
        team_names_csv (str): Path to the CSV file containing team abbreviations and names.
        teams_today (list): List of team abbreviations playing today.

    Returns:
        dict: A dictionary with team abbreviations as keys and their results as values.
    """
    # Load team name mappings from the CSV
    team_name_map = {}
    with open(team_names_csv, "r", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # Skip the header
        for row in reader:
            abbrev, name, short = row
            team_name_map[abbrev] = short

    # Swap abbreviations with short names for today's teams
    teams_today_short = [team_name_map.get(team, team) for team in teams_today]

    # Get all files in the directory
    files = [
        f
        for f in os.listdir(daily_scores_dir)
        if f.startswith("NHL_scores_") and f.endswith(".json")
    ]
    files.sort(
        key=lambda x: datetime.strptime(x.split("_")[2].split(".")[0], "%Y-%m-%d"),
        reverse=True,
    )

    # Initialize results dictionary
    team_results = {team: [] for team in teams_today}

    # Process each file
    for file in files:
        file_path = os.path.join(daily_scores_dir, file)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            # Process each game
            for game in data:
                home_team = game.get("home_team")
                away_team = game.get("away_team")
                winner = game.get("winner")

                # Check if today's teams are playing
                if home_team in teams_today_short or away_team in teams_today_short:
                    # Determine result for each team
                    if home_team in teams_today_short:
                        abbrev = next(
                            (
                                key
                                for key, value in team_name_map.items()
                                if value == home_team
                            ),
                            home_team,
                        )
                        result = "W" if winner == home_team else "L"
                        team_results[abbrev].append(result)

                    if away_team in teams_today_short:
                        abbrev = next(
                            (
                                key
                                for key, value in team_name_map.items()
                                if value == away_team
                            ),
                            away_team,
                        )
                        result = "W" if winner == away_team else "L"
                        team_results[abbrev].append(result)

    # Format results
    formatted_results = {
        team: f"{team} - {'-'.join(results)}" for team, results in team_results.items()
    }

    # for record in team_records.values():
    #     file.write(record + "\n")  # Write team records to file


    # new_listy = []
    # for index, item in enumerate(formatted_results):
    #     new_listy.append(item)
    #     # Check if the current index (plus 1 for 1-based counting) is a multiple of 2
    #     # and if it's not the very end of the original list
    #     if (index + 1) % 2 == 0 and index + 1 < len(formatted_results):
    #         new_listy.append("-----------next match----------")
    return formatted_results


def get_goal_scorers(daily_scores_dir):
    """
    Reads all files in the 'daily_scores' directory, processes them from most recent to oldest,
    and returns a text list of players who scored goals in the format:

    yyyy-mm-dd
    ========
    name - TEAM
    name - TEAM

    Args:
        daily_scores_dir (str): Path to the directory containing daily scores files.

    Returns:
        str: A formatted text list of goal scorers.
    """
    # Get all files in the directory
    files = [
        f
        for f in os.listdir(daily_scores_dir)
        if f.startswith("NHL_scores_") and f.endswith(".json")
    ]

    # Sort files by date (most recent to oldest)
    files.sort(
        key=lambda x: datetime.strptime(x.split("_")[2].split(".")[0], "%Y-%m-%d"),
        reverse=True,
    )

    report = ""

    # Process each file
    for file in files:
        file_date = file.split("_")[2].split(".")[0]  # Extract date from filename
        report += f"{file_date}\n"
        report += "=" * len(file_date) + "\n"

        file_path = os.path.join(daily_scores_dir, file)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Extract goal scorers
            for event in data:
                for goal in event.get("goals", []):
                    scorer = goal.get("name", "Unknown")
                    team = goal.get("team", {})
                    g2d = str(goal.get("goals_to_date", {}))
                    if g2d is None:
                        g2d = "0"
                    if g2d == "None":
                        g2d = "0"
                    report += f"{team:<4} {scorer:<23} {g2d}\n"

        report += "\n"

    return report


def get_nhl_standings_now():
    """
    Fetch NHL standings (current) via requests and cache the JSON response.

    Uses:
    - requests.get with allow_redirects to match `curl -L -X GET`
    - cache.get_or_fetch to reuse a fresh cached file

    Tune freshness via config.CACHE_EXPIRY_HOURS (in your CacheManager).
    """

    curl = "https://api-web.nhle.com/v1/standings/now"
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


def generate_text_report(standings):
    """
    Generates a text report from the standings data.

    Args:
        standings (list): A list of dictionaries containing team standings data.

    Returns:
        str: A formatted text report.
    """
    report = ""
    divisions = {}

    # Organize teams by division and conference
    for team in standings:
        division_name = team.get("divisionName", "Unknown Division")
        conference_name = team.get("conferenceName", "Unknown Conference")
        team_name = team.get("teamName", {}).get("default", "Unknown Team")
        gp = team.get("gamesPlayed", 0)
        wins = team.get("wins", 0)
        losses = team.get("losses", 0)
        ot_losses = team.get("otLosses", 0)
        points = team.get("points", 0)
        gf = team.get("goalFor", 0)
        ga = team.get("goalAgainst", 0)
        diff = team.get("goalDifferential", 0)
        l10 = f"{team.get('l10Wins', 0)}-{team.get('l10Losses', 0)}-{team.get('l10OtLosses', 0)}"
        streak = f"{team.get('streakCode', 'N/A')}{team.get('streakCount', 0)}"

        # Add team data to divisions
        if conference_name not in divisions:
            divisions[conference_name] = {}
        if division_name not in divisions[conference_name]:
            divisions[conference_name][division_name] = []
        divisions[conference_name][division_name].append(
            f"{team_name:<25} {gp:>3} {wins:>3} {losses:>3} {ot_losses:>3} {points:>4} {gf:>4} {ga:>3} {diff:>4} {streak:>4}"
        )

    # Build the report
    for conference, conference_divisions in divisions.items():
        report += f"{conference} Conference\n"
        for division, teams in conference_divisions.items():
            report += f"{division} Division\n"
            report += f"{'Team':<25} {'GP':>3} {'W':>3} {'L':>3} {'OTL':>4} {'Pts':>4} {'GF':>3} {'GA':>3} {'Diff':>4} {'Strk':<5}\n"
            report += "\n".join(teams)
            report += "\n\n"

    return report


def make_nhl_report_today():
    output_file = "NHL_data/nhl_report.txt"
    daily_reports_dir = "NHL_data/daily_reports"
    today_date = datetime.now().strftime("%Y-%m-%d")
    daily_report_file = os.path.join(daily_reports_dir, f"nhl_report_{today_date}.txt")

    # Ensure the daily_reports directory exists
    os.makedirs(daily_reports_dir, exist_ok=True)

    # Check if the daily report file already exists
    # if os.path.exists(daily_report_file):
    #     print(f"Daily report for {today_date} already exists. Skipping creation.")
    #     return

    with open(output_file, "w", encoding="utf-8") as file:
        # DOWNLOAD LINK
        file.write('<a href="NHL_data/SOG_per_game.csv" download>Download SOG</a>')
        file.write('\n')
        file.write('\n')
        # Standings
        beans = get_nhl_standings_now()
        report = generate_text_report(beans["standings"])
        file.write(report + "\n")  # Write standings report to file

        # Schedule
        # open schedule 'NHL_data/schedule/NHL_schedule_yyy-mm-dd.txt for today schedule
        today_date = datetime.now().strftime("%Y-%m-%d")
        schedule_file = f"NHL_data/schedule/NHL_schedule_{today_date}.txt"

        if os.path.exists(schedule_file):
            with open(schedule_file, "r", encoding="utf-8") as schedule:
                file.write("\nSchedule:\n")
                file.write(schedule.read() + "\n")
        else:
            file.write("\nSchedule: No schedule available for today.\n")

        # Match results
        file.write("\n")  # Add a blank line
        daily_scores_dir = "NHL_data/daily_scores"
        team_names_csv = "NHL_data/static_data/nhl_team_names2.csv"
        teams_today1 = teams_today()
        team_records = get_team_records(daily_scores_dir, team_names_csv, teams_today1)
        record_array = []
        for record in team_records.values():
            # file.write(record + "\n")  # Write team records to file
            record_array.append(record + "\n")
        new_listy = []
        for index, item in enumerate(record_array):
            new_listy.append(item)
            # Check if the current index (plus 1 for 1-based counting) is a multiple of 2
            # and if it's not the very end of the original list
            if (index + 1) % 2 == 0 and index + 1 < len(record_array):
                new_listy.append("       \n")
        for record in new_listy:
            file.write(record)  # Write team records to file
        

        # Team matchups
        file.write("\n")  # Add a blank line
        daily_scores_dir = "NHL_data/daily_scores"
        team_names_csv = "NHL_data/static_data/nhl_team_names.csv"
        teams_today2 = teams_today()
        match_results = get_match_results(
            daily_scores_dir, team_names_csv, teams_today2
        )
        for result in match_results:
            file.write(result + "\n")  # Write match results to file

        # Goals
        file.write("\n")  # Add a blank line
        daily_scores_dir = "NHL_data/daily_scores"
        goal_scorers_report = get_goal_scorers(daily_scores_dir)
        file.write(goal_scorers_report)  # Write goal scorers report to file

    print(f"Report saved to {output_file}")

    # Save a copy to the daily_reports folder
    with open(daily_report_file, "w", encoding="utf-8") as file:
        with open(output_file, "r", encoding="utf-8") as original_file:
            file.write(original_file.read())

    print(f"Daily report saved to {daily_report_file}")


def add_checkboxes_to_html(file_path):
    """
    Adds a checkbox to the first column of every row in an HTML table and overwrites the file.

    Args:
        file_path (str): The path to the HTML file containing the table.

    Returns:
        None
    """
    # Read the HTML file
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    # Find the table
    table = soup.find("table", {"class": "dataframe"})
    if not table:
        raise ValueError("No table with class 'dataframe' found in the HTML file.")

    # Add the "PICK" header to the table
    thead = table.find("thead")
    if thead:
        header_row = thead.find("tr")
        pick_header = soup.new_tag("th")
        pick_header.string = "PICK"
        header_row.insert(0, pick_header)

    # Add a checkbox to the first column of every row in the table body
    tbody = table.find("tbody")
    if tbody:
        for row in tbody.find_all("tr"):
            checkbox_cell = soup.new_tag("td")
            checkbox = soup.new_tag("input", type="checkbox")
            checkbox_cell.append(checkbox)
            row.insert(0, checkbox_cell)

    # Overwrite the file with the updated HTML
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(str(soup))

    print(f"Checkboxes added to the table in {file_path}")


def load_stats_from_csv_to_list_of_dict(csv_file_path):
    """Read the CSV file and load stats, returning a list of dictionaries."""
    stats = []
    with open(csv_file_path, mode="r") as file:
        stats_csv_file = csv.reader(file)
        # Read the header
        headers = next(stats_csv_file)
        # Load the data and create a list of dictionaries
        for row in stats_csv_file:
            # Create a dictionary for each row using headers as keys
            stats.append({headers[i]: row[i] for i in range(len(headers))})
    return stats


def csv_to_html(csv_file_path):
    """
    Reads a CSV file and converts it to an HTML file with the same name but with a .html extension.

    Args:
        csv_file_path (str): Path to the CSV file.

    Returns:
        str: Path to the generated HTML file.
    """
    # Generate the HTML file path
    html_file_path = csv_file_path.replace(".csv", ".html")

    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Convert the DataFrame to an HTML file
    df.to_html(html_file_path, index=False)

    print(f"HTML file has been created: {html_file_path}")
    return html_file_path


def get_todays_combined_skaters_json():
    """
    Returns the file path of today's combined skaters CSV file.
    ex. 'NHL_data/combined_skaters_2025-10-15.json'
    """
    todays_date = datetime.now().strftime("%Y-%m-%d")
    json_file_path = f"NHL_data/combined_skaters/combined_skaters_{todays_date}.json"
    json_data = read_json_to_list(json_file_path)
    return json_data


def analyze_sequence(sequence):
    """
    Analyzes a numerical sequence by calculating the differential, normalization, and variance.

    Args:
        sequence (list): A list of numerical values.

    Returns:
        dict: A dictionary containing the original sequence, differential, normalized sequence,
              and variance of the differential.
    """
    # Calculate the differential
    differential = np.diff(sequence)

    # Replace NaN values in the differential with 0
    differential = np.where(np.isnan(differential), 0, differential)

    # Normalize the sequence
    min_val, max_val = min(sequence), max(sequence)
    if max_val == min_val:
        # If all values are the same, set normalized values to 0.0
        normalized = [0.0 for _ in sequence]
    else:
        normalized = [(x - min_val) / (max_val - min_val) for x in sequence]

    # Calculate variance of the differential
    variance = np.var(differential)

    # Replace NaN variance with a default value (e.g., 99)
    if np.isnan(variance):
        variance = 99

    return {
        "original": sequence,
        "differential": differential.tolist(),
        "normalized": normalized,
        "variance_of_differential": variance,
    }


def read_json_to_list(json_file_path):
    """
    Reads a JSON file and returns its contents as a list of dictionaries.

    Args:
        json_file_path (str): Path to the JSON file.

    Returns:
        list: List of dictionaries containing the JSON data.
    """
    data = file_operations.read_json_to_list(json_file_path)
    return data


def combine_skaters_playing_today():

    teams_list = teams_today()
    # NHL_script.update_rosters()

    # ids for players on the teams playing today
    roster_ids = []
    for x in teams_list:
        roster = get_roster(x)
        for x in roster[1:]:
            roster_ids.append(x[9])

    # get a list of skater paths

    # Example usage
    directory = "NHL_data/daily_skaters"
    file_paths = get_sorted_skater_paths(directory)
    list11 = []
    for x in file_paths:
        csv_file_path = x
        file1 = file_operations.read_csv(csv_file_path)
        list11.append(file1)

    list_of_data = []
    for z in roster_ids:
        for x in list11:
            for y in x:
                if z == y[0] and y[5] == "all":
                    list_of_data.append(y)

    # Combine rows by ID
    combined_data = defaultdict(
        lambda: defaultdict(set)
    )  # Use sets to ensure unique values

    for row in list_of_data:
        player_id = row[0]
        for i, value in enumerate(row):
            if i > 6:  # Convert numeric values to floats and store in sets
                combined_data[player_id][i].add(float(value))
            else:  # Store non-numeric values in sets
                combined_data[player_id][i].add(value)

    # Convert sets to sorted lists for the final output
    final_data = []
    for player_id, columns in combined_data.items():
        combined_row = []
        for i in range(len(list_of_data[0])):
            if i in columns:
                if i > 6:  # Sort numeric values in descending order
                    combined_row.append(sorted(columns[i], reverse=True))
                else:  # Sort non-numeric values (if needed)
                    combined_row.append(sorted(columns[i], reverse=True))
            else:
                combined_row.append([])
        final_data.append(combined_row)

    # Define the headers
    headers = [
        "playerId",
        "season",
        "name",
        "team",
        "position",
        "situation",
        "games_played",
        "icetime",
        "shifts",
        "gameScore",
        "onIce_xGoalsPercentage",
        "offIce_xGoalsPercentage",
        "onIce_corsiPercentage",
        "offIce_corsiPercentage",
        "onIce_fenwickPercentage",
        "offIce_fenwickPercentage",
        "iceTimeRank",
        "I_F_xOnGoal",
        "I_F_xGoals",
        "I_F_xRebounds",
        "I_F_xFreeze",
        "I_F_xPlayStopped",
        "I_F_xPlayContinuedInZone",
        "I_F_xPlayContinuedOutsideZone",
        "I_F_flurryAdjustedxGoals",
        "I_F_scoreVenueAdjustedxGoals",
        "I_F_flurryScoreVenueAdjustedxGoals",
        "I_F_primaryAssists",
        "I_F_secondaryAssists",
        "I_F_shotsOnGoal",
        "I_F_missedShots",
        "I_F_blockedShotAttempts",
        "I_F_shotAttempts",
        "I_F_points",
        "I_F_goals",
        "I_F_rebounds",
        "I_F_reboundGoals",
        "I_F_freeze",
        "I_F_playStopped",
        "I_F_playContinuedInZone",
        "I_F_playContinuedOutsideZone",
        "I_F_savedShotsOnGoal",
        "I_F_savedUnblockedShotAttempts",
        "penalties",
        "I_F_penalityMinutes",
        "I_F_faceOffsWon",
        "I_F_hits",
        "I_F_takeaways",
        "I_F_giveaways",
        "I_F_lowDangerShots",
        "I_F_mediumDangerShots",
        "I_F_highDangerShots",
        "I_F_lowDangerxGoals",
        "I_F_mediumDangerxGoals",
        "I_F_highDangerxGoals",
        "I_F_lowDangerGoals",
        "I_F_mediumDangerGoals",
        "I_F_highDangerGoals",
        "I_F_scoreAdjustedShotsAttempts",
        "I_F_unblockedShotAttempts",
        "I_F_scoreAdjustedUnblockedShotAttempts",
        "I_F_dZoneGiveaways",
        "I_F_xGoalsFromxReboundsOfShots",
        "I_F_xGoalsFromActualReboundsOfShots",
        "I_F_reboundxGoals",
        "I_F_xGoals_with_earned_rebounds",
        "I_F_xGoals_with_earned_rebounds_scoreAdjusted",
        "I_F_xGoals_with_earned_rebounds_scoreFlurryAdjusted",
        "I_F_shifts",
        "I_F_oZoneShiftStarts",
        "I_F_dZoneShiftStarts",
        "I_F_neutralZoneShiftStarts",
        "I_F_flyShiftStarts",
        "I_F_oZoneShiftEnds",
        "I_F_dZoneShiftEnds",
        "I_F_neutralZoneShiftEnds",
        "I_F_flyShiftEnds",
        "faceoffsWon",
        "faceoffsLost",
        "timeOnBench",
        "penalityMinutes",
        "penalityMinutesDrawn",
        "penaltiesDrawn",
        "shotsBlockedByPlayer",
        "OnIce_F_xOnGoal",
        "OnIce_F_xGoals",
        "OnIce_F_flurryAdjustedxGoals",
        "OnIce_F_scoreVenueAdjustedxGoals",
        "OnIce_F_flurryScoreVenueAdjustedxGoals",
        "OnIce_F_shotsOnGoal",
        "OnIce_F_missedShots",
        "OnIce_F_blockedShotAttempts",
        "OnIce_F_shotAttempts",
        "OnIce_F_goals",
        "OnIce_F_rebounds",
        "OnIce_F_reboundGoals",
        "OnIce_F_lowDangerShots",
        "OnIce_F_mediumDangerShots",
        "OnIce_F_highDangerShots",
        "OnIce_F_lowDangerxGoals",
        "OnIce_F_mediumDangerxGoals",
        "OnIce_F_highDangerxGoals",
        "OnIce_F_lowDangerGoals",
        "OnIce_F_mediumDangerGoals",
        "OnIce_F_highDangerGoals",
        "OnIce_F_scoreAdjustedShotsAttempts",
        "OnIce_F_unblockedShotAttempts",
        "OnIce_F_scoreAdjustedUnblockedShotAttempts",
        "OnIce_F_xGoalsFromxReboundsOfShots",
        "OnIce_F_xGoalsFromActualReboundsOfShots",
        "OnIce_F_reboundxGoals",
        "OnIce_F_xGoals_with_earned_rebounds",
        "OnIce_F_xGoals_with_earned_rebounds_scoreAdjusted",
        "OnIce_F_xGoals_with_earned_rebounds_scoreFlurryAdjusted",
        "OnIce_A_xOnGoal",
        "OnIce_A_xGoals",
        "OnIce_A_flurryAdjustedxGoals",
        "OnIce_A_scoreVenueAdjustedxGoals",
        "OnIce_A_flurryScoreVenueAdjustedxGoals",
        "OnIce_A_shotsOnGoal",
        "OnIce_A_missedShots",
        "OnIce_A_blockedShotAttempts",
        "OnIce_A_shotAttempts",
        "OnIce_A_goals",
        "OnIce_A_rebounds",
        "OnIce_A_reboundGoals",
        "OnIce_A_lowDangerShots",
        "OnIce_A_mediumDangerShots",
        "OnIce_A_highDangerShots",
        "OnIce_A_lowDangerxGoals",
        "OnIce_A_mediumDangerxGoals",
        "OnIce_A_highDangerxGoals",
        "OnIce_A_lowDangerGoals",
        "OnIce_A_mediumDangerGoals",
        "OnIce_A_highDangerGoals",
        "OnIce_A_scoreAdjustedShotsAttempts",
        "OnIce_A_unblockedShotAttempts",
        "OnIce_A_scoreAdjustedUnblockedShotAttempts",
        "OnIce_A_xGoalsFromxReboundsOfShots",
        "OnIce_A_xGoalsFromActualReboundsOfShots",
        "OnIce_A_reboundxGoals",
        "OnIce_A_xGoals_with_earned_rebounds",
        "OnIce_A_xGoals_with_earned_rebounds_scoreAdjusted",
        "OnIce_A_xGoals_with_earned_rebounds_scoreFlurryAdjusted",
        "OffIce_F_xGoals",
        "OffIce_A_xGoals",
        "OffIce_F_shotAttempts",
        "OffIce_A_shotAttempts",
        "xGoalsForAfterShifts",
        "xGoalsAgainstAfterShifts",
        "corsiForAfterShifts",
        "corsiAgainstAfterShifts",
        "fenwickForAfterShifts",
        "fenwickAgainstAfterShifts",
    ]

    # Get today's date
    todays_date = datetime.now().strftime("%Y-%m-%d")

    # Define the output file path
    output_file = f"NHL_data/combined_skaters/combined_skaters_{todays_date}.csv"
    json_file_path = f"NHL_data/combined_skaters/combined_skaters_{todays_date}.json"
    html_file_path = f"NHL_data/combined_skaters/combined_skaters_{todays_date}.html"

    # Write the data to the CSV file
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write the headers
        writer.writerow(headers)

        # Write the rows
        writer.writerows(final_data)

    print(f"Data has been saved to {output_file}")

    file_operations.convert_csv_to_json(output_file, json_file_path)

    # Convert to html
    html_file_path = csv_to_html(output_file)


def generate_hockey_reference_link(name):
    """
    Generates a Hockey Reference player link based on the player's name.

    Args:
        name (str): The player's full name in the format "FirstName LastName".

    Returns:
        str: The Hockey Reference player link.
    """
    # Split the name into first and last names
    try:
        first_name, last_name = name.split(" ")
    except ValueError:
        return "Invalid name format. Expected 'FirstName LastName'."

    # Extract the first letter of the last name
    last_name_initial = last_name[0].lower()

    # Extract the first two letters of the first name
    first_name_initials = first_name[:2].lower()

    # Format the link
    link = f"https://www.hockey-reference.com/players/{last_name_initial}/{last_name[:5].lower()}{first_name_initials}01.html"

    return link


def process_yesterdays_scores_to_report():
    """
    Fetches yesterday's NHL scores from the NHL API, processes the data,
    """
    # Get yesterday's date in the required format
    yesterdays_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    url = f"https://api-web.nhle.com/v1/score/{yesterdays_date}"
    print(url)
    resp = requests.get(
        url,
        timeout=30,
        allow_redirects=True,
        headers={"Accept": "application/json"},
    )
    resp.raise_for_status()
    resp.json()

    # File paths
    output_dir = Path("NHL_data/daily_scores")  # Convert to Path object

    data = resp.json()

    # Prepare the output file path
    output_file = f"NHL_data/daily_scores/NHL_scores_{yesterdays_date}.json"

    # Ensure the output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract and format the games data
    formatted_games = []
    for game in data.get("games", []):
        home_team = game["homeTeam"]["name"]["default"]
        away_team = game["awayTeam"]["name"]["default"]
        home_score = game["homeTeam"]["score"]
        away_score = game["awayTeam"]["score"]
        winner = home_team if home_score > away_score else away_team
        condensed_game = game.get("condensedGame", "")
        condensed_game = "https://www.nhl.com" + condensed_game

        # Extract goals data
        goals = []
        for goal in game.get("goals", []):
            goal_data = {
                "player_id": goal["playerId"],
                "name": f"{goal['firstName']['default']} {goal['lastName']['default']}",
                "team": goal["teamAbbrev"],
                "goals_to_date": goal.get("goalsToDate", None),
                "assists": [
                    {
                        "name": assist["name"]["default"],
                        "assists_to_date": assist["assistsToDate"],
                        "player_id": assist["playerId"],
                    }
                    for assist in goal.get("assists", [])
                ],
            }
            goals.append(goal_data)

        # Add the formatted game data
        formatted_games.append(
            {
                "date": yesterdays_date,
                "home_team": home_team,
                "away_team": away_team,
                "home_score": home_score,
                "away_score": away_score,
                "winner": winner,
                "condensed_game": condensed_game,
                "goals": goals,
            }
        )

    # Save the formatted data to the output file
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(formatted_games, file, indent=4)

    print(f"Processed scores saved to {output_file}")

    # Run the function
    yesterdays_scores = formatted_games

    # Generate the report
    data = yesterdays_scores

    # Initialize the report
    report_lines = []

    # Extract the date from the first game (assuming all games are from the same date)
    if data:
        report_lines.append(f"<h2>DATE: {data[0]['date']}</h2>")
    else:
        return "<p>No games available to report.</p>"

    # Process each game
    for i, game in enumerate(data, start=1):
        # Add match header with video link
        report_lines.append(
            f"<h2>MATCH {i}: <a target='_blank' rel='noopener noreferrer' href='{game['condensed_game']}'>Video</a></h2>"
        )
        report_lines.append(
            f"<h2>{game['home_team']} {game['home_score']} vs {game['away_team']} {game['away_score']}</h2>"
        )

        # Start the table
        report_lines.append(
            "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        )
        report_lines.append(
            "<tr><th>Team</th><th>Name</th><th>Assist1</th><th>Assist2</th></tr>"
        )

        # Process each goal
        for goal in game.get("goals", []):
            # Extract assists
            assists = goal.get("assists", [])
            assist1 = (
                f"{assists[0]['name']} ({assists[0].get('assists_to_date', 'N/A')})"
                if len(assists) > 0
                else ""
            )
            assist2 = (
                f"{assists[1]['name']} ({assists[1].get('assists_to_date', 'N/A')})"
                if len(assists) > 1
                else ""
            )

            # Add a row for the goal
            report_lines.append(
                f"<tr>"
                f"<td>{goal['team']}</td>"
                f"<td><a target='_blank' rel='noopener noreferrer' href='{generate_hockey_reference_link(goal['name'])}'>{goal['name']}</a> ({goal.get('goals_to_date', 'N/A')})</td>"
                f"<td>{assist1}</td>"
                f"<td>{assist2}</td>"
                f"</tr>"
            )

        # End the table
        report_lines.append("</table>")
        report_lines.append("<br>")  # Add spacing between matches

    # Join the report lines into a single HTML string
    report = "\n".join(report_lines)
    # Print the report
    # print(report)

    # Optionally, save the report to a text file
    with open("NHL_data/NHL_yesterdays_scores.txt", "w") as file:
        file.write(report)
    print("report generated")


def get_sorted_skater_paths(directory):
    """
    Reads the directory and returns a list of file paths sorted descendingly
    based on the numeric portion of the filenames.

    Args:
        directory (str): Path to the directory containing skater files.

    Returns:
        list: List of file paths sorted descendingly.
    """
    # Get all files in the directory
    files = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.startswith("nhl_skaters_2025_") and f.endswith(".csv")
    ]

    # Sort files descendingly based on the numeric portion of the filenames
    files.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]), reverse=True)

    return files


def update_rosters():
    # List of team abbreviations
    teams = [
        "ANA",
        "BOS",
        "BUF",
        "CAR",
        "CBJ",
        "CGY",
        "CHI",
        "COL",
        "DAL",
        "DET",
        "EDM",
        "FLA",
        "LAK",
        "MIN",
        "MTL",
        "NJD",
        "NSH",
        "NYI",
        "NYR",
        "OTT",
        "PHI",
        "PIT",
        "SEA",
        "SJS",
        "STL",
        "TBL",
        "TOR",
        "UTA",
        "VAN",
        "VGK",
        "WPG",
        "WSH",
    ]
    # Fetch and save rosters for all teams
    for team in teams:
        get_nhl_team_roster_and_save_csv(team)


def get_nhl_team_roster_and_save_csv(team):
    """
    Fetch NHL team roster and save it as a CSV file.

    Args:
        team (str): Team abbreviation (e.g., "ANA", "BOS").

    Saves:
        CSV file in NHL_data/rosters/<team>.csv containing the roster data.
    """
    # Define the URL and file path
    url = f"https://api-web.nhle.com/v1/roster/{team}/current"
    folder_path = "NHL_data/rosters"
    file_path = os.path.join(folder_path, f"{team}.csv")

    # Ensure the folder exists
    os.makedirs(folder_path, exist_ok=True)

    try:
        # Fetch the roster data
        resp = requests.get(
            url,
            timeout=30,
            allow_redirects=True,
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        roster_data = resp.json()

        # Combine players from all categories (forwards, defensemen, goalies)
        players = []
        for category in ["forwards", "defensemen", "goalies"]:
            category_players = roster_data.get(category, [])
            for player in category_players:
                players.append(
                    {
                        "Player Name": f"{player.get('firstName', {}).get('default', 'Unknown')} {player.get('lastName', {}).get('default', 'Unknown')}",
                        "Position": player.get("positionCode", "Unknown"),
                        "Jersey Number": player.get("sweaterNumber", "Unknown"),
                        "Height (in)": player.get("heightInInches", "Unknown"),
                        "Weight (lbs)": player.get("weightInPounds", "Unknown"),
                        "Birth Date": player.get("birthDate", "Unknown"),
                        "Birth City": player.get("birthCity", {}).get(
                            "default", "Unknown"
                        ),
                        "Birth Country": player.get("birthCountry", "Unknown"),
                        "Team": team,
                        "player_id": player.get("id", "unknown"),
                    }
                )

        # Check if there are players to save
        if not players:
            print(f"No roster data found for team {team}.")
            return

        # Convert the player data to a DataFrame
        df = pd.DataFrame(players)

        # Save the DataFrame as a CSV file
        df.to_csv(file_path, index=False)
        print(f"Roster for team {team} saved to {file_path}.")
    except requests.RequestException as e:
        print(f"Failed to fetch roster for team {team}: {e}")


def get_roster(team_name):
    csv_file_path = f"NHL_data/rosters/{team_name}.csv"
    with open(csv_file_path, mode="r") as file:
        return list(csv.reader(file))


def get_nhl_skaters():
    # Calculate yesterday's date in YYYYMMDD format
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

    # Define the file path and URL
    folder_path = "NHL_data/daily_skaters"
    file_name = f"nhl_skaters_2025_{yesterday}.csv"
    file_path = os.path.join(folder_path, file_name)
    url = "https://moneypuck.com/moneypuck/playerData/seasonSummary/2025/regular/skaters.csv"

    # Check if the file exists
    if os.path.exists(file_path):
        print(f"File '{file_name}' already exists. No action needed.")
    else:
        # Download the file
        print(f"File '{file_name}' does not exist. Downloading...")
        response = requests.get(url)
        if response.status_code == 200:
            # Ensure the folder exists
            os.makedirs(folder_path, exist_ok=True)
            # Save the file
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"File downloaded and saved as '{file_path}'.")
        else:
            print(
                f"Failed to download the file. HTTP Status Code: {response.status_code}"
            )


def get_nhl_goalies():
    # Calculate yesterday's date in YYYYMMDD format
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

    # Define the file path and URL
    folder_path = "NHL_data/daily_goalies"
    file_name = f"nhl_goalies_2025_{yesterday}.csv"
    file_path = os.path.join(folder_path, file_name)
    url = "https://moneypuck.com/moneypuck/playerData/seasonSummary/2025/regular/goalies.csv"

    # Check if the file exists
    if os.path.exists(file_path):
        print(f"File '{file_name}' already exists. No action needed.")
    else:
        # Download the file
        print(f"File '{file_name}' does not exist. Downloading...")
        response = requests.get(url)
        if response.status_code == 200:
            # Ensure the folder exists
            os.makedirs(folder_path, exist_ok=True)
            # Save the file
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"File downloaded and saved as '{file_path}'.")
        else:
            print(
                f"Failed to download the file. HTTP Status Code: {response.status_code}"
            )


def get_nhl_lines():
    # Calculate yesterday's date in YYYYMMDD format
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

    # Define the file path and URL
    folder_path = "NHL_data/daily_lines"
    file_name = f"nhl_lines_2025_{yesterday}.csv"
    file_path = os.path.join(folder_path, file_name)
    url = "https://moneypuck.com/moneypuck/playerData/seasonSummary/2025/regular/lines.csv"

    # Check if the file exists
    if os.path.exists(file_path):
        print(f"File '{file_name}' already exists. No action needed.")
    else:
        # Download the file
        print(f"File '{file_name}' does not exist. Downloading...")
        response = requests.get(url)
        if response.status_code == 200:
            # Ensure the folder exists
            os.makedirs(folder_path, exist_ok=True)
            # Save the file
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"File downloaded and saved as '{file_path}'.")
        else:
            print(
                f"Failed to download the file. HTTP Status Code: {response.status_code}"
            )


def get_nhl_teams():
    # Calculate yesterday's date in YYYYMMDD format
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

    # Define the file path and URL
    folder_path = "NHL_data/daily_teams"
    file_name = f"nhl_teams_2025_{yesterday}.csv"
    file_path = os.path.join(folder_path, file_name)
    url = "https://moneypuck.com/moneypuck/playerData/seasonSummary/2025/regular/teams.csv"

    # Check if the file exists
    if os.path.exists(file_path):
        print(f"File '{file_name}' already exists. No action needed.")
    else:
        # Download the file
        print(f"File '{file_name}' does not exist. Downloading...")
        response = requests.get(url)
        if response.status_code == 200:
            # Ensure the folder exists
            os.makedirs(folder_path, exist_ok=True)
            # Save the file
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"File downloaded and saved as '{file_path}'.")
        else:
            print(
                f"Failed to download the file. HTTP Status Code: {response.status_code}"
            )


def teams_today():
    """
    Explanation:
    Load Team Names:

    The script reads nhl_team_names.csv into a pandas DataFrame.
    It creates a dictionary mapping full team names (e.g., "Calgary Flames") to their abbreviations (e.g., "CGY").
    Read Schedule File:

    The script opens NHL_todays_schedule.txt and reads each line.
    It extracts the team names by splitting the lines based on the @ symbol.
    Map Team Names to Abbreviations:

    For each team name extracted from the schedule, the script looks up its abbreviation using the dictionary created earlier.
    Output:

    The script prints a list of abbreviations for the teams playing today.
    """
    # File paths
    schedule_file = "NHL_data/NHL_todays_schedule.txt"
    team_names_file = "NHL_data/static_data/nhl_team_names.csv"

    # Load the team names CSV into a DataFrame
    team_names = pd.read_csv(team_names_file)

    # Create a dictionary mapping full team names to abbreviations
    team_name_to_abbrev = dict(zip(team_names["NAME"], team_names["ABBREV"]))

    # Read the schedule file
    with open(schedule_file, "r") as file:
        schedule_lines = file.readlines()

    # Extract team names from the schedule
    teams_playing_today = []
    for line in schedule_lines:
        # Remove HTML tags using a regular expression
        line = re.sub(r"<[^>]*>", "", line)  # Removes anything between < and >

        # Split the line to isolate team names
        if "@" in line:
            parts = line.split("@")
            home_team = parts[1].strip()
            away_team = parts[0].split("-")[-1].strip()
            teams_playing_today.extend([home_team, away_team])

    # Map team names to abbreviations
    team_abbreviations = [
        team_name_to_abbrev[team]
        for team in teams_playing_today
        if team in team_name_to_abbrev
    ]

    # Print the list of abbreviations
    return team_abbreviations


def process_nhl_data_and_generate_html():
    """
    Processes NHL data by filtering, combining, and transforming data from multiple CSV files in a folder,
    and generates an HTML table from the combined data.

    Workflow:
    1. Filters and combines data from the static file and daily skater files.
    2. Saves the combined data to a CSV file.
    3. Generates an HTML table from the combined data and saves it to a file.

    Returns:
        None
    """
    # File paths
    static_file_path = "NHL_data/static_data/nhl_skaters_2024_2025.csv"
    daily_folder_path = "NHL_data/daily_skaters"
    output_file_path = "NHL_data/combined_skaters_2025-10-14.csv"
    table_path = "NHL_data/skaters_html_table.html"

    # Get the list of teams playing today
    team_list = teams_today()

    # Step 1: Load the static CSV file and filter rows
    static_df = pd.read_csv(static_file_path)
    static_filtered = static_df[
        (static_df["team"].isin(team_list)) & (static_df["situation"] == "all")
    ]

    # Convert numeric columns to lists for combining data
    combined_data = static_filtered.copy()
    numeric_columns = combined_data.select_dtypes(include=["number"]).columns
    for col in numeric_columns:
        combined_data[col] = combined_data[col].apply(lambda x: [x])

    # Step 2: Process daily skater files sequentially
    daily_files = [
        f
        for f in os.listdir(daily_folder_path)
        if f.startswith("nhl_skaters_2025_") and f.endswith(".csv")
    ]
    daily_files.sort(
        key=lambda x: datetime.strptime(x.split("_")[-1].split(".")[0], "%Y%m%d")
    )

    for daily_file in daily_files:
        daily_file_path = os.path.join(daily_folder_path, daily_file)
        daily_df = pd.read_csv(daily_file_path)

        # Filter rows by team and 'all' situation
        daily_filtered = daily_df[
            (daily_df["team"].isin(team_list)) & (daily_df["situation"] == "all")
        ]

        # Update or append rows to the combined data
        for _, daily_row in daily_filtered.iterrows():
            player_name = daily_row["name"]
            team = daily_row["team"]

            # Check if the player already exists in the combined data
            existing_player = combined_data[
                (combined_data["name"] == player_name) & (combined_data["team"] == team)
            ]

            if not existing_player.empty:
                # Append daily values to existing player's numeric columns
                for col in numeric_columns:
                    combined_data.loc[existing_player.index, col].iloc[0].append(
                        daily_row[col]
                    )
            else:
                # Add new player to the combined data
                new_row = daily_row.copy()
                for col in numeric_columns:
                    new_row[col] = [new_row[col]]  # Convert numeric values to lists
                combined_data = pd.concat(
                    [combined_data, pd.DataFrame([new_row])], ignore_index=True
                )

    # Step 3: Save the combined data to a CSV file
    combined_data.to_csv(output_file_path, index=False)
    print(f"Combined data saved to {output_file_path}")

    # Step 4: Generate an HTML table from the combined data
    df = pd.read_csv(output_file_path)
    html_table = df.to_html(index=False, classes="table table-striped", border=0)

    # Save the HTML table to the specified file
    with open(table_path, "w", encoding="utf-8") as file:
        file.write(html_table)

    print(f"Filtered HTML table saved to {table_path}")


def format_schedule(schedule):
    """
    Takes the schedule and makes an array of lines formatted for a txt file.
    If "Toronto Maple Leafs" exists in a line, it wraps it in a styled <b> tag.
    """
    formatted_lines = []
    for row in schedule:
        date, time, away, home = row
        formatted_line = f"{date} {time:<8} EDT - {away:<22} @ {home:<25}"

        # Wrap "Toronto Maple Leafs" with the styled <b> tag
        formatted_line = formatted_line.replace(
            "Toronto Maple Leafs", '<b style="color: #5A62FF;">Toronto Maple Leafs</b>'
        )

        formatted_lines.append(formatted_line)

    return formatted_lines


def make_todays_schedule():
    """
    Finds today's schedule file in the 'NHL_data/schedule' folder and copies it to
    'NHL_data/NHL_todays_schedule.txt', overwriting the existing file if it exists.

    The schedule file is expected to be named in the format 'NHL_schedule_[date].txt',
    where [date] is today's date in 'YYYY-MM-DD' format.
    """
    # Define paths
    schedule_dir = Path("NHL_data/schedule")
    todays_schedule_path = Path("NHL_data/NHL_todays_schedule.txt")

    # Get today's date in 'YYYY-MM-DD' format
    today = datetime.now().strftime("%Y-%m-%d")

    # Construct the expected schedule file name
    todays_schedule_file = schedule_dir / f"NHL_schedule_{today}.txt"

    # Check if the schedule file for today exists
    if not todays_schedule_file.exists():
        print(f"Schedule file for today ({todays_schedule_file}) not found.")
        return

    # Copy the file to overwrite 'NHL_todays_schedule.txt'
    shutil.copy(todays_schedule_file, todays_schedule_path)
    print(f"Today's schedule copied to {todays_schedule_path}")


def process_todays_skaters():
    """
    Reads the NHL skaters CSV file and generates an HTML table.

    The HTML table only includes rows where the 'situation' column equals 'all'.
    The table is saved to the file path specified in `table_path`.

    File Paths:
    - Input:     csv_path = "NHL_data/combined_nhl_skaters.csv"
    - Output:    table_path = "NHL_data/skaters_html_table.html"
    """
    # File paths
    csv_path = "NHL_data/combined_nhl_skaters.csv"
    table_path = "NHL_data/skaters_html_table.html"

    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_path)

    # Generate the HTML table
    html_table = df.to_html(index=False, classes="table table-striped", border=0)

    # Save the HTML table to the specified file
    with open(table_path, "w", encoding="utf-8") as file:
        file.write(html_table)

    print(f"Filtered HTML table saved to {table_path}")


def process_nhl_data_old(
    team_list, static_file_path, latest_file_path, output_file_path
):
    """
    Processes NHL data by filtering, combining, and transforming data from two CSV files.

    Args:
        team_list (list): List of team abbreviations to filter by (e.g., ['EDM', 'CGY', 'TOR']).
        static_file_path (str): Path to the static 2024 CSV file.
        latest_file_path (str): Path to the latest 2025 CSV file.
        output_file_path (str): Path to save the combined output CSV file.

    Returns:
        None
    """
    # Step 1: Load the CSV files
    static_df = pd.read_csv(static_file_path)
    latest_df = pd.read_csv(latest_file_path)

    # Step 2: Filter rows by team and 'all' situation
    static_filtered = static_df[
        (static_df["team"].isin(team_list)) & (static_df["situation"] == "all")
    ]
    latest_filtered = latest_df[
        (latest_df["team"].isin(team_list)) & (latest_df["situation"] == "all")
    ]

    # Step 3: Combine the data
    # Convert static data to a format where numeric columns are lists
    combined_data = static_filtered.copy()
    numeric_columns = combined_data.select_dtypes(include=["number"]).columns

    # Turn static numeric values into lists
    for col in numeric_columns:
        combined_data[col] = combined_data[col].apply(lambda x: [x])

    # Iterate through the latest data and update or append to the combined data
    for _, latest_row in latest_filtered.iterrows():
        player_name = latest_row["name"]
        team = latest_row["team"]

        # Check if the player already exists in the combined data
        existing_player = combined_data[
            (combined_data["name"] == player_name) & (combined_data["team"] == team)
        ]

        if not existing_player.empty:
            # Update the existing player's numeric columns by appending the latest values
            for col in numeric_columns:
                combined_data.loc[existing_player.index, col].iloc[0].append(
                    latest_row[col]
                )
        else:
            # Add the new player to the combined data
            new_row = latest_row.copy()
            for col in numeric_columns:
                new_row[col] = [new_row[col]]  # Turn the numeric value into a list
            combined_data = pd.concat(
                [combined_data, pd.DataFrame([new_row])], ignore_index=True
            )

    # Step 4: Save the combined data to a new CSV file
    combined_data.to_csv(output_file_path, index=False)


def process_nhl_data_from_folder():
    """
    Processes NHL data by filtering, combining, and transforming data from multiple CSV files in a folder.

    Args:
        team_list (list): List of team abbreviations to filter by (e.g., ['EDM', 'CGY', 'TOR']).
        static_file_path (str): Path to the static 2024 CSV file.
        daily_folder_path (str): Path to the folder containing daily skater files.
        output_file_path (str): Path to save the combined output CSV file.

    Returns:
        None
    """
    team_list = teams_today()
    static_file_path = "NHL_data/static_data/nhl_skaters_2024_2025.csv"
    daily_folder_path = "NHL_data/daily_skaters"
    output_file_path = "NHL_data/combined_nhl_skaters.csv"
    # Step 1: Load the static CSV file
    static_df = pd.read_csv(static_file_path)

    # Step 2: Filter rows by team and 'all' situation in the static file
    static_filtered = static_df[
        (static_df["team"].isin(team_list)) & (static_df["situation"] == "all")
    ]

    # Convert static data to a format where numeric columns are lists
    combined_data = static_filtered.copy()
    numeric_columns = combined_data.select_dtypes(include=["number"]).columns

    # Turn static numeric values into lists
    for col in numeric_columns:
        combined_data[col] = combined_data[col].apply(lambda x: [x])

    # Step 3: Get all daily skater files and sort them by date
    daily_files = [
        f
        for f in os.listdir(daily_folder_path)
        if f.startswith("nhl_skaters_2025_") and f.endswith(".csv")
    ]
    daily_files.sort(
        key=lambda x: datetime.strptime(x.split("_")[-1].split(".")[0], "%Y%m%d")
    )

    # Step 4: Process each daily file sequentially
    for daily_file in daily_files:
        daily_file_path = os.path.join(daily_folder_path, daily_file)
        daily_df = pd.read_csv(daily_file_path)

        # Filter rows by team and 'all' situation
        daily_filtered = daily_df[
            (daily_df["team"].isin(team_list)) & (daily_df["situation"] == "all")
        ]

        # Iterate through the daily data and update or append to the combined data
        for _, daily_row in daily_filtered.iterrows():
            player_name = daily_row["name"]
            team = daily_row["team"]

            # Check if the player already exists in the combined data
            existing_player = combined_data[
                (combined_data["name"] == player_name) & (combined_data["team"] == team)
            ]

            if not existing_player.empty:
                # Update the existing player's numeric columns by appending the daily values
                for col in numeric_columns:
                    combined_data.loc[existing_player.index, col].iloc[0].append(
                        daily_row[col]
                    )
            else:
                # Add the new player to the combined data
                new_row = daily_row.copy()
                for col in numeric_columns:
                    new_row[col] = [new_row[col]]  # Turn the numeric value into a list
                combined_data = pd.concat(
                    [combined_data, pd.DataFrame([new_row])], ignore_index=True
                )

    # Step 5: Save the combined data to a new CSV file
    combined_data.to_csv(output_file_path, index=False)


def get_skater_history(int_shots_average):

    STATS_2022_CSV = "NHL_data/static_data/skaters2022.csv"
    STATS_2023_CSV = "NHL_data/static_data/skaters2023.csv"
    STATS_2024_CSV = "NHL_data/static_data/skaters2024.csv"

    teams_playing_today = teams_today()

    # get a list of paths from skaters directory
    # Example usage
    directory = "NHL_data/daily_skaters"
    sorted_csv_file_paths = get_sorted_skater_paths(directory)

    skaters_from_today = load_stats_from_csv_to_list_of_dict(sorted_csv_file_paths[0])
    skaters_from_today_filtered_for_all = [
        player
        for player in skaters_from_today
        if player.get("situation") == "all"
        and player.get("team") in teams_playing_today
    ]

    skaters_from_today_filtered_for_all_and_asog = [
        player
        for player in skaters_from_today_filtered_for_all
        if "I_F_shotsOnGoal" in player
        and "games_played" in player
        and float(player["games_played"]) > 0
        and (
            avg_sog := round(
                float(player["I_F_shotsOnGoal"]) / float(player["games_played"]), 2
            )
            > int_shots_average
        )
    ]

    for player in skaters_from_today_filtered_for_all_and_asog:
        player.update(
            {
                "past_games": str(int(round(float(player.get("games_played"))))),
                "past_sog": str(int(round(float(player["I_F_shotsOnGoal"])))),
                "past_a_sog": str(
                    int(
                        round(
                            float(player["I_F_shotsOnGoal"])
                            / float(player["games_played"])
                        )
                    )
                ),
                "past_e_shot": str(int(round(float(player["I_F_xOnGoal"])))),
                "past_goals": str(int(round(float(player["I_F_goals"])))),
                "past_a_goals": str(
                    int(
                        round(
                            float(player["I_F_goals"]) / float(player["games_played"])
                        )
                    )
                ),
                "past_e_goals": str(int(round(float(player["I_F_xGoals"])))),
                "past_on_ice_goal": str(int(round(float(player["OnIce_F_goals"])))),
                "past_a_on_ice_goal": str(
                    int(
                        round(
                            float(player["OnIce_F_goals"])
                            / float(player["games_played"])
                        )
                    )
                ),
                "past_assists1": str(int(round(float(player["I_F_primaryAssists"])))),
                "past_assists2": str(int(round(float(player["I_F_secondaryAssists"])))),
                "past_rebound_goals": str(
                    int(round(float(player["I_F_reboundGoals"])))
                ),
            }
        )

    for file_path in sorted_csv_file_paths[1:]:
        additional_data = load_stats_from_csv_to_list_of_dict(file_path)
        for player in skaters_from_today_filtered_for_all_and_asog:
            for x in additional_data:
                if player.get("name") == x.get("name") and x.get("situation") == "all":
                    player["past_games"] += ":" + str(
                        int(round(float(x.get("games_played"))))
                    )
                    player["past_sog"] += ":" + str(
                        int(round(float(x["I_F_shotsOnGoal"])))
                    )
                    player["past_a_sog"] += ":" + str(
                        int(
                            round(
                                float(x["I_F_shotsOnGoal"]) / float(x["games_played"])
                            )
                        )
                    )
                    player["past_e_shot"] += ":" + str(
                        int(round(float(x["I_F_xOnGoal"])))
                    )
                    player["past_goals"] += ":" + str(int(round(float(x["I_F_goals"]))))
                    player["past_a_goals"] += ":" + str(
                        int(round(float(x["I_F_goals"]) / float(x["games_played"])))
                    )
                    player["past_e_goals"] += ":" + str(
                        int(round(float(x["I_F_xGoals"])))
                    )
                    player["past_on_ice_goal"] += ":" + str(
                        int(round(float(x["OnIce_F_goals"])))
                    )
                    player["past_a_on_ice_goal"] += ":" + str(
                        int(round(float(x["OnIce_F_goals"]) / float(x["games_played"])))
                    )
                    player["past_assists1"] += ":" + str(
                        int(round(float(x["I_F_primaryAssists"])))
                    )
                    player["past_assists2"] += ":" + str(
                        int(round(float(x["I_F_secondaryAssists"])))
                    )
                    player["past_rebound_goals"] += ":" + str(
                        int(round(float(x["I_F_reboundGoals"])))
                    )

    stats_2022 = load_stats_from_csv_to_list_of_dict(STATS_2022_CSV)
    stats_2023 = load_stats_from_csv_to_list_of_dict(STATS_2023_CSV)
    stats_2024 = load_stats_from_csv_to_list_of_dict(STATS_2024_CSV)
    for player in skaters_from_today_filtered_for_all_and_asog:
        for x in stats_2022:
            if player.get("name") == x.get("name") and x.get("situation") == "all":
                stats = {
                    "SOG_22": str(int(round(float(x["I_F_shotsOnGoal"])))),
                    "AVG_SOG_22": str(
                        int(
                            round(
                                float(x["I_F_shotsOnGoal"]) / float(x["games_played"])
                            )
                        )
                    ),
                    "GOALS_22": str(int(round(float(x["I_F_goals"])))),
                    "AVG_GOALS_22": str(
                        int(round(float(x["I_F_goals"]) / float(x["games_played"])))
                    ),
                    "ASSISTS1_22": str(int(round(float(x["I_F_primaryAssists"])))),
                    "ASSISTS2_22": str(int(round(float(x["I_F_secondaryAssists"])))),
                    "AVG_ASSISTS_22": str(
                        int(
                            round(
                                (
                                    float(x["I_F_secondaryAssists"])
                                    + float(x["I_F_primaryAssists"])
                                )
                                / float(x["games_played"])
                            )
                        )
                    ),
                    "REBOUNDS_22": str(int(round(float(x["I_F_reboundGoals"])))),
                    "AVG_REBOUNDS_22": str(
                        int(
                            round(
                                float(x["I_F_reboundGoals"]) / float(x["games_played"])
                            )
                        )
                    ),
                    "ONICE_GOALS_22": str(int(round(float(x["OnIce_A_xGoals"])))),
                }
                player.update(stats)
        for x in stats_2023:
            if player.get("name") == x.get("name") and x.get("situation") == "all":
                stats = {
                    "SOG_23": str(int(round(float(x["I_F_shotsOnGoal"])))),
                    "AVG_SOG_23": str(
                        int(
                            round(
                                float(x["I_F_shotsOnGoal"]) / float(x["games_played"])
                            )
                        )
                    ),
                    "GOALS_23": str(int(round(float(x["I_F_goals"])))),
                    "AVG_GOALS_23": str(
                        int(round(float(x["I_F_goals"]) / float(x["games_played"])))
                    ),
                    "ASSISTS1_23": str(int(round(float(x["I_F_primaryAssists"])))),
                    "ASSISTS2_23": str(int(round(float(x["I_F_secondaryAssists"])))),
                    "AVG_ASSISTS_23": str(
                        int(
                            round(
                                (
                                    float(x["I_F_secondaryAssists"])
                                    + float(x["I_F_primaryAssists"])
                                )
                                / float(x["games_played"])
                            )
                        )
                    ),
                    "REBOUNDS_23": str(int(round(float(x["I_F_reboundGoals"])))),
                    "AVG_REBOUNDS_23": str(
                        int(
                            round(
                                float(x["I_F_reboundGoals"]) / float(x["games_played"])
                            )
                        )
                    ),
                    "ONICE_GOALS_23": str(int(round(float(x["OnIce_A_xGoals"])))),
                }
                player.update(stats)
        for x in stats_2024:
            if player.get("name") == x.get("name") and x.get("situation") == "all":
                stats = {
                    "SOG_24": str(int(round(float(x["I_F_shotsOnGoal"])))),
                    "AVG_SOG_24": str(
                        int(
                            round(
                                float(x["I_F_shotsOnGoal"]) / float(x["games_played"])
                            )
                        )
                    ),
                    "GOALS_24": str(int(round(float(x["I_F_goals"])))),
                    "AVG_GOALS_24": str(
                        int(round(float(x["I_F_goals"]) / float(x["games_played"])))
                    ),
                    "ASSISTS1_24": str(int(round(float(x["I_F_primaryAssists"])))),
                    "ASSISTS2_24": str(int(round(float(x["I_F_secondaryAssists"])))),
                    "AVG_ASSISTS_24": str(
                        int(
                            round(
                                (
                                    float(x["I_F_secondaryAssists"])
                                    + float(x["I_F_primaryAssists"])
                                )
                                / float(x["games_played"])
                            )
                        )
                    ),
                    "REBOUNDS_24": str(int(round(float(x["I_F_reboundGoals"])))),
                    "AVG_REBOUNDS_24": str(
                        int(
                            round(
                                float(x["I_F_reboundGoals"]) / float(x["games_played"])
                            )
                        )
                    ),
                    "ONICE_GOALS_24": str(int(round(float(x["OnIce_A_xGoals"])))),
                }
                player.update(stats)

        # List of keys to process
        keys_to_process = [
            "past_games",
            "past_sog",
            "past_a_sog",
            "past_e_shot",
            "past_goals",
            "past_a_goals",
            "past_e_goals",
            "past_on_ice_goal",
            "past_a_on_ice_goal",
            "past_assists1",
            "past_assists2",
            "past_rebound_goals",
        ]

        # Process each key
        for key in keys_to_process:
            string_to_split = str(player.get(key)).split(":")
            new_string_to_update = ":" + ":".join(string_to_split[:30])
            player.update({key: new_string_to_update})

        # print(player.get('name'))

    return skaters_from_today_filtered_for_all_and_asog


def find_duplicate_positions(data_string):
    """
    Takes a colon-separated string, converts it into an array,
    and returns a list of indices for all duplicate values.

    Args:
        data_string (str): A colon-separated string (e.g., ':6:6:5:5:4:4:3:3:3:2:2:1').

    Returns:
        list: A list of indices where duplicate values occur.
    """
    # Step 1: Convert the string into an array of integers
    data_array = [int(x) for x in data_string.split(":") if x]

    # Step 2: Find indices of duplicate values
    seen = {}
    duplicate_positions = []
    for i, value in enumerate(data_array):
        if value in seen:
            duplicate_positions.append(i)  # Add the current index if it's a duplicate
        else:
            seen[value] = i  # Mark the value as seen

    return duplicate_positions


def process_and_filter(data_string, indices_to_remove):
    """
    Takes a colon-separated string, converts it into an array, removes values at specified indices,
    and converts the resulting array back to a colon-separated string.

    Args:
        data_string (str): A colon-separated string (e.g., ':19:19:15:15:9:9:5:5:5:4:4:3').
        indices_to_remove (list): A list of indices to remove from the array (e.g., [1, 3, 5, 7, 8, 10]).

    Returns:
        str: A colon-separated string after removing the specified indices.
    """
    # Step 1: Convert the string into an array of integers
    data_array = [int(x) for x in data_string.split(":") if x]

    # Step 2: Remove values at the specified indices
    filtered_array = [
        value for i, value in enumerate(data_array) if i not in indices_to_remove
    ]

    # Step 3: Convert the filtered array back to a colon-separated string
    result_string = "-" + "-".join(map(str, filtered_array))

    new_string = result_string[1:]

    return new_string


def process_skaters_duplicates(skater_data):
    """
    Processes a list of skater data dictionaries to remove duplicate entries
    based on their past performance statistics.

    Args:
        skater_data (list): A list of dictionaries containing skater data.

    Returns:
        None: The function modifies the input list in place.
    """
    for x in skater_data:
        past_games = x.get("past_games")  # ':6:6:5:5:4:4:3:3:3:2:2:1',
        clean_up_array = find_duplicate_positions(past_games)
        new_past_games = process_and_filter(past_games, clean_up_array)
        x.update({"past_games": new_past_games})

        past_sog = x.get("past_sog")  # ':19:19:15:15:9:9:5:5:5:4:4:3',
        new_past_sog = process_and_filter(past_sog, clean_up_array)
        x.update({"past_sog": new_past_sog})

        past_a_sog = x.get("past_a_sog")  # ':3:3:3:3:2:2:2:2:2:2:2:3',
        new_past_a_sog = process_and_filter(past_a_sog, clean_up_array)
        x.update({"past_a_sog": new_past_a_sog})

        past_e_shot = x.get("past_e_shot")  # ':19:19:15:15:9:9:5:5:5:4:4:3',
        new_past_e_shot = process_and_filter(past_e_shot, clean_up_array)
        x.update({"past_e_shot": new_past_e_shot})

        past_goals = x.get("past_goals")  # ':2:2:0:0:0:0:0:0:0:0:0:0',
        new_past_goals = process_and_filter(past_goals, clean_up_array)
        x.update({"past_goals": new_past_goals})

        past_a_goals = x.get("past_a_goals")  # ':0:0:0:0:0:0:0:0:0:0:0:0',
        new_past_a_goals = process_and_filter(past_a_goals, clean_up_array)
        x.update({"past_a_goals": new_past_a_goals})

        past_e_goals = x.get("past_e_goals")  # ':3:3:2:2:1:1:1:1:1:1:1:1',
        new_past_e_goals = process_and_filter(past_e_goals, clean_up_array)
        x.update({"past_e_goals": new_past_e_goals})

        past_on_ice_goal = x.get("past_on_ice_goal")  # ':15:15:10:10:7:7:5:5:5:4:4:2',
        new_past_on_ice_goal = process_and_filter(past_on_ice_goal, clean_up_array)
        x.update({"past_on_ice_goal": new_past_on_ice_goal})

        past_a_on_ice_goal = x.get("past_a_on_ice_goal")  # ':2:2:2:2:2:2:2:2:2:2:2:2',
        new_past_a_on_ice_goal = process_and_filter(past_a_on_ice_goal, clean_up_array)
        x.update({"past_a_on_ice_goal": new_past_a_on_ice_goal})

        past_assists1 = x.get("past_assists1")  # ':10:10:8:8:6:6:5:5:5:4:4:2',
        new_past_assists1 = process_and_filter(past_assists1, clean_up_array)
        x.update({"past_assists1": new_past_assists1})

        past_assists2 = x.get("past_assists2")  # ':1:1:1:1:0:0:0:0:0:0:0:0',
        new_past_assists2 = process_and_filter(past_assists2, clean_up_array)
        x.update({"past_assists2": new_past_assists2})

        past_rebound_goals = x.get("past_rebound_goals")  # ':1:1:0:0:0:0:0:0:0:0:0:0',
        new_past_rebound_goals = process_and_filter(past_rebound_goals, clean_up_array)
        x.update({"past_rebound_goals": new_past_rebound_goals})
    return skater_data


def add_analysis_to_skaters(skater_data):
    """
    Adds analysis fields to each skater's data.

    Args:
        skater_data (list): A list of dictionaries containing skater data.
    """
    for skater in skater_data:
        # sog_list = skater.get("past_sog").split("-")
        # int_sog_list = [int(x) for x in sog_list]
        # analyze_sog_list = analyze_sequence(int_sog_list)
        # analyze_sog_diff = analyze_sog_list.get("differential", 0)
        # analyze_sog_var = analyze_sog_list.get("variance_of_differential", 99)
        # new_list1 = []
        # for x in analyze_sog_diff:
        #     new_list1.append(abs(x))
        # analyze_sog_diff = new_list1
        # skater.update({"sog_diff": "-".join(map(str, analyze_sog_diff))})
        # skater.update({"sog_var": round(analyze_sog_var, 2)})
        sog_list = skater.get("past_sog", "").split("-")
        int_sog_list = [
            int(x) for x in sog_list if x.isdigit()
        ]  # Ensure valid integers
        analyze_sog_list = analyze_sequence(int_sog_list)
        analyze_sog_diff = analyze_sog_list.get("differential", [0])
        analyze_sog_var = analyze_sog_list.get("variance_of_differential", 99)

        # Ensure analyze_sog_diff is valid
        if not analyze_sog_diff or all(x == 0 for x in analyze_sog_diff):
            analyze_sog_diff = [0]  # Default value for empty or invalid differential

        # Convert differential to absolute values
        analyze_sog_diff = [abs(x) for x in analyze_sog_diff]

        # Update skater data
        skater.update({"sog_diff": "-".join(map(str, analyze_sog_diff))})
        skater.update({"sog_var": round(analyze_sog_var, 2)})

        # g_list = skater.get("past_goals")
        # int_g_list = [int(x) for x in g_list.split("-")]
        # analyze_g_list = analyze_sequence(int_g_list)
        # analyze_g_diff = analyze_g_list.get("differential", 0)
        # analyze_g_var = analyze_g_list.get("variance_of_differential", 99)

        # new_list2 = []
        # for x in analyze_g_diff:
        #     new_list2.append(abs(x))
        # analyze_g_diff = new_list2
        g_list = skater.get("past_goals", "").split("-")
        int_g_list = [int(x) for x in g_list if x.isdigit()]  # Ensure valid integers
        analyze_g_list = analyze_sequence(int_g_list)
        analyze_g_diff = analyze_g_list.get("differential", [0])
        analyze_g_var = analyze_g_list.get("variance_of_differential", 99)

        # Ensure analyze_g_diff is valid
        if not analyze_g_diff or all(x == 0 for x in analyze_g_diff):
            analyze_g_diff = [0]  # Default value for empty or invalid differential

        # Convert differential to absolute values
        analyze_g_diff = [abs(x) for x in analyze_g_diff]

        skater.update({"goals_diff": "-".join(map(str, analyze_g_diff))})
        skater.update({"goals_var": round(analyze_g_var, 2)})

        # a1_list = skater.get("past_assists1")
        # int_a1_list = [int(x) for x in a1_list.split("-")]
        # analyze_a1_list = analyze_sequence(int_a1_list)
        # analyze_a1_diff = analyze_a1_list.get("differential", 0)
        # analyze_a1_var = analyze_a1_list.get("variance_of_differential", 99)
        # new_list3 = []
        # for x in analyze_a1_diff:
        #     new_list3.append(abs(x))
        # analyze_a1_diff = new_list3
        a1_list = skater.get("past_goals", "").split("-")
        int_a1_list = [int(x) for x in a1_list if x.isdigit()]  # Ensure valid integers
        analyze_a1_list = analyze_sequence(int_a1_list)
        analyze_a1_diff = analyze_a1_list.get("differential", [0])
        analyze_a1_var = analyze_a1_list.get("variance_of_differential", 99)

        # Ensure analyze_a1_diff is valid
        if not analyze_a1_diff or all(x == 0 for x in analyze_a1_diff):
            analyze_a1_diff = [0]  # Default value for empty or invalid differential

        # Convert differential to absolute values
        analyze_a1_diff = [abs(x) for x in analyze_a1_diff]

        skater.update({"assists1_diff": "-".join(map(str, analyze_a1_diff))})
        skater.update({"assists1_var": round(analyze_a1_var, 2)})

    return skater_data


def filter_skater_data_for_csv(skater_data):
    """
    Filters the skater data to include only relevant fields for CSV output.

    Args:
        skater_data (list): A list of dictionaries containing skater data.
    """
    filtered_data = []
    relevant_fields = [
        "playerId",
        "season",
        "name",
        "team",
        "games_played",
        "position",
        "I_F_shotsOnGoal",
        "I_F_goals",
        "I_F_xGoals",
        "past_games",
        "past_sog",
        "past_a_sog",
        "past_e_shot",
        "past_goals",
        "past_a_goals",
        "past_e_goals",
        "past_on_ice_goal",
        "past_a_on_ice_goal",
        "past_assists1",
        "past_assists2",
        "past_rebound_goals",
        "GOALS_22",
        "GOALS_23",
        "GOALS_24",
    ]

    for skater in skater_data:
        filtered_skater = {field: skater.get(field, "") for field in relevant_fields}
        filtered_data.append(filtered_skater)

    return filtered_data


def add_strings_by_index(string1, string2):
    """
    Adds the values at each index of two strings formatted as sequences of numbers separated by '-'.

    Args:
        string1 (str): The first string (e.g., '2-2-2-1-1-0-0').
        string2 (str): The second string (e.g., '1-1-1-1-1-1-1').

    Returns:
        str: A computed string where each index is the sum of the corresponding indices in the input strings.
    """
    # Convert strings to lists of integers
    list1 = [int(x) for x in string1.split("-")]
    list2 = [int(x) for x in string2.split("-")]

    # Add values at each index
    result_list = [x + y for x, y in zip(list1, list2)]

    # Convert the result list back to a string
    result_string = "-".join(map(str, result_list))

    return result_string


def filter_skater_data_for_csv_again(skater_data):
    """
    Filters the skater data to include only relevant fields for CSV output.

    Args:
        skater_data (list): A list of dictionaries containing skater data.
    """
    # for x in skater_data:
    #     g24 = float(int(x.get('GOALS_24', 0)))
    #     avg24 = g24 / 80.0
    #     x.update({'avg24': round(avg24, 2)})
    #     assists1 = x.get('past_assists1', '0')
    #     assists2 = x.get('past_assists2', '0')
    #     points = add_strings_by_index(assists1, assists2)
    #     a1 = int(assists1[0])
    #     a2 = int(assists2[0])
    #     p = a1 + a2
    #     x.update({'points': p})
    #     x.update({'past_points': points})
    for x in skater_data:
        # Ensure GOALS_24 is a valid number
        goals_24 = x.get("GOALS_24", "0")  # Default to '0' if the key is missing
        if not goals_24.isdigit():  # Check if the value is not a valid number
            goals_24 = "0"  # Default to '0' for invalid values

        g24 = float(int(goals_24))  # Convert to integer and then float
        avg24 = g24 / 80.0
        x.update({"avg24": round(avg24, 2)})

        # Process assists and points
        assists1 = x.get("past_assists1", "0")
        assists2 = x.get("past_assists2", "0")
        past_goals1 = x.get("past_goals", "0")

        points1 = add_strings_by_index(assists1, assists2)
        points = add_strings_by_index(points1, past_goals1)
        a1 = int(assists1.split("-")[0]) if assists1 else 0  # Handle empty assists1
        a2 = int(assists2.split("-")[0]) if assists2 else 0  # Handle empty assists2
        g1 = (
            int(past_goals1.split("-")[0]) if past_goals1 else 0
        )  # Handle empty past_goals1
        p = a1 + a2 + g1

        x.update({"points": p})
        x.update({"past_points": points})

        points_list = points.split("-")
        int_points_list = [
            int(x) for x in points_list if x.isdigit()
        ]  # Ensure valid integers
        analyze_points_list = analyze_sequence(int_points_list)
        analyze_points_diff = analyze_points_list.get("differential", [0])
        analyze_points_var = analyze_points_list.get("variance_of_differential", 99)

        # Ensure analyze_points_diff is valid
        if not analyze_points_diff or all(x == 0 for x in analyze_points_diff):
            analyze_points_diff = [0]  # Default value for empty or invalid differential

        # Convert differential to absolute values
        analyze_points_diff = [abs(x) for x in analyze_points_diff]

        x.update({"points_diff": "-".join(map(str, analyze_points_diff))})
        x.update({"points_var": round(analyze_points_var, 2)})
        x.update({"avg_p": round(p / float(x.get("games_played", 1)), 2)})

        goals_25 = x.get("I_F_goals", 1)
        games_played25 = x.get("games_played", 1)
        avg_goals_25 = (
            float(goals_25) / float(games_played25) if float(games_played25) > 0 else 0
        )
        x.update({"avg25": round(avg_goals_25, 2)})

        g22 = x.get("GOALS_22", "1")
        avg22 = float(int(g22 if g22.strip() else "1")) / 80.0
        x.update({"avg22": round(avg22, 2)})
        g23 = x.get("GOALS_23", "1")
        avg23 = float(int(g23 if g23.strip() else "1")) / 80.0
        x.update({"avg23": round(avg23, 2)})

        g24 = x.get("GOALS_24", "1")
        all_avgs = (
            float(int(g22 if g22.strip() else "1"))
            + float(int(g23 if g23.strip() else "1"))
            + float(int(g24 if g24.strip() else "1"))
        ) / 240.0
        x.update({"avg_all": round(all_avgs, 2)})

        g25 = x.get("I_F_goals", "1")

        # Handle empty or invalid values
        g24 = float(g24) if g24.strip() else 0.0
        g25 = float(g25) if g25.strip() else 0.0

        g_diff_24_25 = float(g24) - float(g25)

        x.update({"24-25": round(g_diff_24_25, 2)})

        ag24 = float(int(g24)) / 80.0
        diffof2425 = avg_goals_25 - ag24
        x.update({"24a-25a": round(diffof2425, 2)})

        sog25 = x.get("I_F_shotsOnGoal", 1)
        avg_sog_25 = float(sog25) / float(games_played25)
        x.update({"asog": round(avg_sog_25, 2)})

        games_left = 82.0 - float(games_played25)
        goal_spread = round(g_diff_24_25 / games_left, 2)
        x.update({"goal_spread": goal_spread})
        pick = " "
        x.update({"pick": pick})

    filtered_data = []
    relevant_fields = [
        "name",
        "team",
        "position",
        "games_played",
        "past_e_shot",
        "past_sog",
        "sog_diff",
        "I_F_shotsOnGoal",
        "asog",
        "sog_var",
        "past_a_sog",
        "GOALS_22",
        "GOALS_23",
        "GOALS_24",
        "I_F_goals",
        "I_F_xGoals",
        "avg24",
        "avg25",
        "goal_spread",
        "24-25",
        "past_goals",
        "goals_diff",
        "goals_var",
        "past_e_goals",
        "past_a_goals",
        "points",
        "avg_p",
        "past_points",
        "points_diff",
        "points_var",
        "pick",
    ]

    for skater in skater_data:
        filtered_skater = {field: skater.get(field, "") for field in relevant_fields}
        filtered_data.append(filtered_skater)

    return filtered_data


def rename_keys(data, key_mapping):
    """
    Renames keys in a list of dictionaries based on a provided mapping.

    Args:
        data (list): A list of dictionaries.
        key_mapping (dict): A dictionary mapping old keys to new keys.

    Returns:
        list: A list of dictionaries with renamed keys.

        # # Example usage
        # data = [
        #     {"GOALS_24": 5, "I_F_goals": 3, "past_assists1": 2},
        #     {"GOALS_24": 4, "I_F_goals": 2, "past_assists1": 1},
        # ]

        # key_mapping = {
        #     "GOALS_24": "Goals_Last_24",
        #     "I_F_goals": "Goals_Current",
        #     "past_assists1": "Assists_Last_24",
        # }

        # renamed_data = rename_keys(data, key_mapping)
        # print(renamed_data)

    """
    renamed_data = []
    for item in data:
        renamed_item = {key_mapping.get(k, k): v for k, v in item.items()}
        renamed_data.append(renamed_item)
    return renamed_data


def save_dicts_to_csv(data, file_path):
    """
    Converts a list of dictionaries to a CSV file and saves it to the specified path.

    Args:
        data (list): A list of dictionaries to be written to the CSV file.
        file_path (str): The path where the CSV file will be saved.

    Returns:
        None
    """
    if not data:
        raise ValueError("The data list is empty. Cannot write an empty CSV file.")

    # Extract the headers from the keys of the first dictionary
    headers = data[0].keys()

    # Write the data to the CSV file
    with open(file_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()  # Write the header row
        writer.writerows(data)  # Write the data rows

    print(f"CSV file has been saved to {file_path}")


def rename_csv_headers():
    """
    Renames the headers of a CSV file and overwrites the file with the updated headers.

    Args:
        file_path (str): Path to the CSV file.
        new_headers (list): List of new headers to replace the existing ones.

    Returns:
        None
    """
    file_path = "NHL_data/SOG_per_game.csv"
    new_headers = [
        "name",
        "team",
        "position",
        "GP",
        "past_e_shot",
        "past_sog",
        "sog_diff",
        "SOG",
        "asog",
        "sog_var",
        "past_a_sog",
        "G22",
        "G23",
        "G24",
        "G25",
        "xG25",
        "aG24",
        "aG25",
        "GS",
        "24-25",
        "past_goals",
        "goals_diff",
        "goals_var",
        "past_e_goals",
        "past_a_goals",
        "P",
        "aP",
        "past_points",
        "points_diff",
        "points_var",
        "pick",
    ]
    # Read the existing CSV file
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        rows = list(reader)  # Read all rows

    # Replace the headers with the new headers
    rows[0] = new_headers

    # Write the updated CSV file
    with open(file_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    print(f"Headers updated successfully in {file_path}")


def tweak_data_again(data):
    for x in data:
        x.update({"past_e_shot": x.get("past_e_shot").split("-")[0]})
        # print(x.get('past_e_shot'))

    new_data = []
    for x in data:
        new_dict = {}
        new_dict["name"] = x.get("name")
        new_dict["team"] = x.get("team")
        new_dict["pos"] = x.get("position")
        new_dict["gp"] = x.get("games_played")
        new_dict["eG25"] = x.get("I_F_xGoals")
        new_dict["aG24"] = x.get("avg24")
        new_dict["aG25"] = x.get("avg25")
        new_dict["24-25"] = x.get("24-25")
        new_dict["a24-25"] = x.get("goal_spread")
        new_dict["G22"] = x.get("GOALS_22")
        new_dict["G23"] = x.get("GOALS_23")
        new_dict["G24"] = x.get("GOALS_24")
        new_dict["G25"] = x.get("I_F_goals")
        new_dict["pastG"] = x.get("goals_diff")
        new_dict["Gvar"] = x.get("goals_var")
        new_dict["aP"] = x.get("avg_p")
        new_dict["P"] = x.get("points")
        new_dict["pastP"] = x.get("points_diff")
        new_dict["Pvar"] = x.get("points_var")
        new_dict["eSOG"] = x.get("past_e_shot")
        new_dict["aSOG"] = x.get("asog")
        new_dict["SOG"] = x.get("I_F_shotsOnGoal")
        new_dict["pastSOG"] = x.get("sog_diff")
        new_dict["SOGvar"] = x.get("sog_var")
        new_dict["Gpick"] = x.get("pick")
        new_dict["Ppick"] = x.get("pick")
        new_dict["Spick"] = x.get("pick")
        new_data.append(new_dict)

    for x in new_data:
        for key, value in x.items():
            print(key, value)
    return new_data


def combine_and_save_skaters(int_shots_average, file_path):
    skater_data = get_skater_history(int_shots_average)
    filtered_data = filter_skater_data_for_csv(skater_data)
    processed_data = process_skaters_duplicates(filtered_data)
    super_processed_data = add_analysis_to_skaters(processed_data)
    processed_twice_data = filter_skater_data_for_csv_again(super_processed_data)
    # rename_csv_headers()
    tweaked_data = tweak_data_again(processed_twice_data)
    save_dicts_to_csv(tweaked_data, file_path)
