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
from datetime import datetime, timedelta
import json
import csv
import requests
from pathlib import Path  # Import Path
import file_operations
from collections import defaultdict
import csv
from datetime import datetime
import ast
import numpy as np
from bs4 import BeautifulSoup


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


# PROCESS STATS

# READ CSV TO A LIST OF LINES WHERE EACH LINE IS A DICT


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
            avg_sog := int(
                round(float(player["I_F_shotsOnGoal"]) / float(player["games_played"]))
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
            new_string_to_update = ":" + ":".join(string_to_split[:20])
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
        int_sog_list = [int(x) for x in sog_list if x.isdigit()]  # Ensure valid integers
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
    list1 = [int(x) for x in string1.split('-')]
    list2 = [int(x) for x in string2.split('-')]

    # Add values at each index
    result_list = [x + y for x, y in zip(list1, list2)]

    # Convert the result list back to a string
    result_string = '-'.join(map(str, result_list))

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
        goals_24 = x.get('GOALS_24', '0')  # Default to '0' if the key is missing
        if not goals_24.isdigit():  # Check if the value is not a valid number
            goals_24 = '0'  # Default to '0' for invalid values
    
        g24 = float(int(goals_24))  # Convert to integer and then float
        avg24 = g24 / 80.0
        x.update({'avg24': round(avg24, 2)})
    
        # Process assists and points
        assists1 = x.get('past_assists1', '0')
        assists2 = x.get('past_assists2', '0')
        past_goals1 = x.get('past_goals', '0')
        
        points1 = add_strings_by_index(assists1, assists2)
        points = add_strings_by_index(points1, past_goals1)
        a1 = int(assists1.split('-')[0]) if assists1 else 0  # Handle empty assists1
        a2 = int(assists2.split('-')[0]) if assists2 else 0  # Handle empty assists2
        g1 = int(past_goals1.split('-')[0]) if past_goals1 else 0  # Handle empty past_goals1
        p = a1 + a2 + g1

        x.update({'points': p})
        x.update({'past_points': points})

        points_list = points.split("-")
        int_points_list = [int(x) for x in points_list if x.isdigit()]  # Ensure valid integers
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
        x.update({"avg_p": round(p/float(x.get('games_played',1)), 2)})



    filtered_data = []
    relevant_fields = [
        "name",
        "team",
        "position",
        "games_played",
        "I_F_shotsOnGoal",
        "past_e_shot",
        "past_sog",
        "sog_diff",
        "sog_var",
        "past_a_sog",
        "GOALS_24",
        'avg24',
        "I_F_goals",
        "past_goals",
        "goals_diff",
        "I_F_xGoals",
        "past_e_goals",
        "goals_var",
        "past_a_goals",
        "points",
        "avg_p",
        "past_points",
        "points_diff",
        "points_var"
    ]

    for skater in skater_data:
        filtered_skater = {field: skater.get(field, "") for field in relevant_fields}
        filtered_data.append(filtered_skater)

    return filtered_data


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


def combine_and_save_skaters(int_shots_average, file_path):
    skater_data = get_skater_history(int_shots_average)
    filtered_data = filter_skater_data_for_csv(skater_data)
    processed_data = process_skaters_duplicates(filtered_data)
    super_processed_data = add_analysis_to_skaters(processed_data)
    processed_twice_data = filter_skater_data_for_csv_again(super_processed_data)
    save_dicts_to_csv(processed_twice_data, file_path)
