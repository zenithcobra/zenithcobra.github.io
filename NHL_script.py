from datetime import datetime, timedelta
from pathlib import Path
import file_operations
import pandas as pd
import shutil
import json
from pathlib import Path
import csv
import pathlib
import requests
import pandas as pd
import os
from os import listdir
from os.path import isfile, join
from datetime import datetime
from dateutil.parser import parse
from fractions import Fraction
import pandas as pd
import re  # Import the regular expressions module
import pandas as pd
import os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import csv
import hashlib
import json
import os
import pytz
import re
import requests
import pandas as pd
import os
import csv


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
        "ANA", "BOS", "BUF", "CAR", "CBJ", "CGY", "CHI", "COL", "DAL", "DET",
        "EDM", "FLA", "LAK", "MIN", "MTL", "NJD", "NSH", "NYI", "NYR", "OTT",
        "PHI", "PIT", "SEA", "SJS", "STL", "TBL", "TOR", "UTA", "VAN", "VGK",
        "WPG", "WSH"
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
                players.append({
                    "Player Name": f"{player.get('firstName', {}).get('default', 'Unknown')} {player.get('lastName', {}).get('default', 'Unknown')}",
                    "Position": player.get("positionCode", "Unknown"),
                    "Jersey Number": player.get("sweaterNumber", "Unknown"),
                    "Height (in)": player.get("heightInInches", "Unknown"),
                    "Weight (lbs)": player.get("weightInPounds", "Unknown"),
                    "Birth Date": player.get("birthDate", "Unknown"),
                    "Birth City": player.get("birthCity", {}).get("default", "Unknown"),
                    "Birth Country": player.get("birthCountry", "Unknown"),
                    "Team": team,
                    "player_id": player.get("id","unknown")
                })

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
    with open(csv_file_path, mode='r') as file:
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
