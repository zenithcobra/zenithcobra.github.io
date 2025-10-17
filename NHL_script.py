from datetime import datetime, timedelta
from pathlib import Path
import file_operations
import NHL_data_fetcher
import config
from cache_manager import CacheManager
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


# Main function to handle the schedule processing
def process_schedule():
    """
    Processes the NHL schedule for today's games and saves it to a text file.

    This function reads the NHL schedule from a CSV file, filters the games to include only those
    scheduled for today's date, formats the schedule into a human-readable text format, and saves
    it to a text file. It uses a caching mechanism to avoid redundant processing if the schedule
    for today has already been generated within the last 4 hours.

    Workflow:
    1. Initializes the CacheManager to handle caching and archiving.
    2. Checks if the output file (`NHL_todays_schedule.txt`) is valid and up-to-date.
       - If valid, the function exits early without further processing.
    3. Archives the old schedule file if it exists and is outdated.
    4. Reads the NHL schedule from the CSV file (`nhl_schedule.csv`).
    5. Filters the schedule to include only games scheduled for today's date.
    6. Formats the filtered schedule into a readable text format.
    7. Saves the formatted schedule to the output file (`NHL_todays_schedule.txt`).

    File Paths:
    - Input: `NHL_data/nhl_schedule.csv` (CSV file containing the full NHL schedule).
    - Output: `NHL_data/NHL_todays_schedule.txt` (Text file containing today's games).

    Caching:
    - The CacheManager ensures that the schedule is only processed if the cache is invalid
      (i.e., the file is older than 4 hours or does not exist).

    Example Output (saved in `NHL_todays_schedule.txt`):
    ```
    2025-09-22 7:15 PM   EDT - Washington Capitals       @ Boston Bruins
    2025-09-22 9:40 PM   EDT - New York Rangers          @ Pittsburgh Penguins
    ```

    Dependencies:
    - [file_operations.read_csv](http://_vscodecontentref_/1): Reads the schedule from the CSV file.
    - [file_operations.save_text](http://_vscodecontentref_/2): Saves the formatted schedule to a text file.
    - [CacheManager](http://_vscodecontentref_/3): Handles caching and archiving of the output file.

    Raises:
    - FileNotFoundError: If the input CSV file does not exist.
    - ValueError: If the CSV file is improperly formatted.

    Notes:
    - The function assumes the CSV file has the following columns:
      `Date, Time, Away Team, Home Team`.
    - The date format in the CSV must be `YYYY-MM-DD`.

    """
    # Initialize CacheManager
    cache = CacheManager()
    # File paths
    csv_path = "NHL_data/nhl_schedule.csv"
    output_file = "NHL_data/NHL_todays_schedule.txt"
    # Check if the cache is valid for today
    if cache.is_cache_valid(output_file, expiry_hours=4):
        print(f"Today's schedule is already cached: {output_file}")
        return

    # Archive the old file if it exists
    if Path(output_file).exists():
        cache._archive_existing_file(output_file)

    # Read the schedule CSV
    nhl_schedule = file_operations.read_csv(csv_path)

    # Get today's date in the format "YYYY-MM-DD"
    today = datetime.now().strftime("%Y-%m-%d")

    # Filter the schedule to include only today's games
    todays_games = [row for row in nhl_schedule[1:] if row[0] == today]

    # Format the schedule
    formatted_schedule = format_schedule(todays_games)

    # Save the formatted schedule to the text file
    file_operations.save_text(formatted_schedule, "NHL_todays_schedule")


def process_full_schedule():
    """
    Processes the NHL schedule and saves a separate text file for each day in the schedule.

    This function reads the NHL schedule from a CSV file, formats the schedule for each unique date,
    and saves it to a text file in the `NHL_data/schedule` folder. Each file is named
    `NHL_schedule_[date].txt`, where `[date]` is the date of the games.

    File Paths:
    - Input: `NHL_data/nhl_schedule.csv` (CSV file containing the full NHL schedule).
    - Output: `NHL_data/schedule/NHL_schedule_[date].txt` (Text files for each day's games).

    Notes:
    - The function assumes the CSV file has the following columns:
      `Date, Time, Away Team, Home Team`.
    - The date format in the CSV must be `YYYY-MM-DD`.
    """
    # File paths
    csv_path = "NHL_data/nhl_schedule.csv"
    output_dir = Path("schedule")

    # Ensure the output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read the schedule CSV
    nhl_schedule = file_operations.read_csv(csv_path)

    # Group games by date
    games_by_date = {}
    for row in nhl_schedule[1:]:  # Skip the header row
        date = row[0]
        if date not in games_by_date:
            games_by_date[date] = []
        games_by_date[date].append(row)

    # Process each date
    for date, games in games_by_date.items():
        # Format the schedule for the date
        formatted_schedule = format_schedule(games)

        # Save the formatted schedule to a text file
        output_file = output_dir / f"NHL_schedule_{date}"
        file_operations.save_text(formatted_schedule, output_file)

    print(f"Schedules saved to {output_dir}")


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

    def make_report(data):
        """
        Processes a JSON string of NHL scores and generates an HTML report.

        Args:
            data (list): List of games containing NHL scores data.

        Returns:
            str: A formatted HTML report of the games and their details.
        """
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
        return "\n".join(report_lines)

    # Run the function
    yesterdays_scores = process_scores(resp, output_dir)

    # Generate the report
    report = make_report(yesterdays_scores)

    # Print the report
    # print(report)

    # Optionally, save the report to a text file
    with open("NHL_data/NHL_yesterdays_scores.txt", "w") as file:
        file.write(report)
    print("report generated")


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

    