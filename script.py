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

def detect_current_streak(sequence):
    """
    Detects the current streak (value and length) in the sequence.

    Args:
        sequence (list): A list of 1s and 0s representing wins and losses.

    Returns:
        tuple: A tuple containing the current streak value (1 or 0) and its length.
    """
    last_value = sequence[-1]
    streak_length = 0
    for value in reversed(sequence):
        if value == last_value:
            streak_length += 1
        else:
            break
    return last_value, streak_length

def predict_streak_continuation(current_streak, stats):
    """
    Predicts whether the current streak will continue or transition.

    Args:
        current_streak (tuple): A tuple containing the current streak value (1 or 0) and its length.
        stats (dict): A dictionary containing streak statistics.

    Returns:
        int: The predicted next value (1 for win, 0 for loss).
    """
    streak_value, streak_length = current_streak

    if streak_value == 1:  # Current streak is a win streak
        if streak_length >= stats["longest_win_streak"]:
            return 0  # Predict a transition to a loss
        elif streak_length < stats["average_win_streak_length"]:
            return 1  # Predict continuation of the win streak
    elif streak_value == 0:  # Current streak is a loss streak
        if streak_length >= stats["longest_lose_streak"]:
            return 1  # Predict a transition to a win
        elif streak_length < stats["average_lose_streak_length"]:
            return 0  # Predict continuation of the loss streak

    # Default to continuation if no clear prediction can be made
    return streak_value

def parse_html_table(html_content):
    """
    Parses an HTML table into a list of dictionaries, excluding checkbox columns.

    Args:
        html_content (str): The HTML content as a string.

    Returns:
        list: A list of dictionaries where each dictionary represents a row of the table.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')  # Find the first table in the HTML

    if not table:
        # raise ValueError("No table found in the provided HTML content.")
        return {}
    # Identify columns with checkboxes by inspecting the first data row
    first_data_row = table.find_all('tr')[1]  # Skip the header row
    checkbox_columns = []
    for i, td in enumerate(first_data_row.find_all('td')):
        if td.find('input', {'type': 'checkbox'}):
            checkbox_columns.append(i)

    # Extract headers, excluding checkbox columns
    headers = []
    for i, th in enumerate(table.find('tr').find_all('th')):
        if i not in checkbox_columns:
            headers.append(th.text.strip())

    # Extract rows, excluding checkbox columns
    rows = []
    for tr in table.find_all('tr')[1:]:  # Skip the header row
        row_data = []
        for i, td in enumerate(tr.find_all('td')):
            if i not in checkbox_columns:
                row_data.append(td.get_text(strip=True))
        if len(row_data) == len(headers):  # Ensure row matches header length
            rows.append(dict(zip(headers, row_data)))

    return rows

def read_json_list(file_path):
    """Read a JSON file and return its content as a list."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
            else:
                raise ValueError("The JSON file does not contain a list.")
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        print(f"Error reading JSON file: {e}")
        return []

def read_json_dictionary(file_path):
    """Read a JSON file and return its content as a dictionary."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if isinstance(data, dict):
                return data
            else:
                raise ValueError("The JSON file does not contain a dictionary.")
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        print(f"Error reading JSON file: {e}")
        return {}

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

def read_text_file(file_path):
    """
    Reads a text file and returns its content as a single string.

    Args:
        file_path (str): The path to the text file to be read.

    Returns:
        str: A string containing the content of the text file if the file is successfully read.
        None: If the file does not exist or is empty.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        IOError: If there is an error reading the file.

    Example:
        >>> content = read_text_file("data.txt")
        >>> if content:
        ...     print(content)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().strip()
            return content if content else None
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except IOError as e:
        print(f"Error: Failed to read the file. {e}")
    return None

def save_to_json(list_of_dicts, supplied_filename):
    """
    Saves today's matches to a JSON file in the 'data' folder. If the file already exists, 
    it archives the existing file with yesterday's date in the 'data/archived_data' folder.

    Args:
        todays_matches (dict): The data to save to the JSON file.
        supplied_filename (str): The base name of the file to save (e.g., 'todays_matches').

    Returns:
        None
    """
    # Directories
    data_dir = "data"
    archived_dir = os.path.join(data_dir, "archived_data")
    os.makedirs(data_dir, exist_ok=True)  # Ensure the 'data' directory exists
    os.makedirs(archived_dir, exist_ok=True)  # Ensure the 'archived_data' directory exists

    # File paths
    today_date = datetime.now().strftime("%Y-%m-%d")
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    file_path = os.path.join(data_dir, f"{supplied_filename}.json")
    archived_file_path = os.path.join(archived_dir, f"{supplied_filename}_{yesterday_date}.json")

    # Check if the file already exists in the 'data' folder
    if os.path.exists(file_path):
        # Archive the existing file with yesterday's date
        if not os.path.exists(archived_file_path):
            os.rename(file_path, archived_file_path)
            print(f"Archived existing file to {archived_file_path}")
        else:
            print(f"Archived file already exists: {archived_file_path}")

    # Save today's matches to the JSON file in the 'data' folder
    with open(file_path, "w") as json_file:
        json.dump(list_of_dicts, json_file, indent=4)

    print(f"Today's data saved to {file_path}")

def save_to_json_dictionary(dictionary, supplied_filename):
    """
    Saves today's matches to a JSON file in the 'data' folder. If the file already exists, 
    it archives the existing file with yesterday's date in the 'data/archived_data' folder.

    Args:
        todays_matches (dict): The data to save to the JSON file.
        supplied_filename (str): The base name of the file to save (e.g., 'todays_matches').

    Returns:
        None
    """
    # Directories
    data_dir = "data"
    archived_dir = os.path.join(data_dir, "archived_data")
    os.makedirs(data_dir, exist_ok=True)  # Ensure the 'data' directory exists
    os.makedirs(archived_dir, exist_ok=True)  # Ensure the 'archived_data' directory exists

    # File paths
    today_date = datetime.now().strftime("%Y-%m-%d")
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    file_path = os.path.join(data_dir, f"{supplied_filename}.json")
    archived_file_path = os.path.join(archived_dir, f"{supplied_filename}_{yesterday_date}.json")

    # Check if the file already exists in the 'data' folder
    if os.path.exists(file_path):
        # Archive the existing file with yesterday's date
        if not os.path.exists(archived_file_path):
            os.rename(file_path, archived_file_path)
            print(f"Archived existing file to {archived_file_path}")
        else:
            print(f"Archived file already exists: {archived_file_path}")

    # Save today's matches to the JSON file in the 'data' folder
    with open(file_path, "w") as json_file:
        json.dump(list_of_dicts, json_file, indent=4)

    print(f"Today's data saved to {file_path}")


def save_list_to_text(list_of_lines, supplied_filename):
    """
    Saves today's matches to a text file in the 'data' folder. If the file already exists, 
    it archives the existing file with yesterday's date in the 'data/archived_data' folder.

    Args:
        list of lines: The data to save to the txt file.
        supplied_filename (str): The base name of the file to save (e.g., 'todays_matches').

    Returns:
        None
    """
    # Directories
    data_dir = "data"
    archived_dir = os.path.join(data_dir, "archived_data")
    os.makedirs(data_dir, exist_ok=True)  # Ensure the 'data' directory exists
    os.makedirs(archived_dir, exist_ok=True)  # Ensure the 'archived_data' directory exists

    # File paths
    today_date = datetime.now().strftime("%Y-%m-%d")
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    file_path = os.path.join(data_dir, f"{supplied_filename}.txt")
    archived_file_path = os.path.join(archived_dir, f"{supplied_filename}_{yesterday_date}.txt")

    # Check if the file already exists in the 'data' folder
    if os.path.exists(file_path):
        # Archive the existing file with yesterday's date
        if not os.path.exists(archived_file_path):
            os.rename(file_path, archived_file_path)
            print(f"Archived existing file to {archived_file_path}")
        else:
            print(f"Archived file already exists: {archived_file_path}")

    # Save today's matches to the JSON file in the 'data' folder
    # with open(file_path, "w") as json_file:
    #     json.dump(list_of_dicts, json_file, indent=4)
    with open(file_path, "w") as file:
        for content in list_of_lines:
            file.write(content)

    print(f"Today's data saved to {file_path}")

def save_to_text(content, supplied_filename):
    """
    Saves today's matches to a text file in the 'data' folder. If the file already exists, 
    it archives the existing file with yesterday's date in the 'data/archived_data' folder.

    Args:
        string of text: The data to save to the txt file.
        supplied_filename (str): The base name of the file to save (e.g., 'todays_matches').

    Returns:
        None
    """
    # Directories
    data_dir = "data"
    archived_dir = os.path.join(data_dir, "archived_data")
    os.makedirs(data_dir, exist_ok=True)  # Ensure the 'data' directory exists
    os.makedirs(archived_dir, exist_ok=True)  # Ensure the 'archived_data' directory exists

    # File paths
    today_date = datetime.now().strftime("%Y-%m-%d")
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    file_path = os.path.join(data_dir, f"{supplied_filename}.txt")
    archived_file_path = os.path.join(archived_dir, f"{supplied_filename}_{yesterday_date}.txt")

    # Check if the file already exists in the 'data' folder
    if os.path.exists(file_path):
        # Archive the existing file with yesterday's date
        if not os.path.exists(archived_file_path):
            os.rename(file_path, archived_file_path)
            print(f"Archived existing file to {archived_file_path}")
        else:
            print(f"Archived file already exists: {archived_file_path}")

    # Save today's matches to the JSON file in the 'data' folder
    # with open(file_path, "w") as json_file:
    #     json.dump(list_of_dicts, json_file, indent=4)
    with open(file_path, "w") as file:
        file.write(content)

    print(f"Today's data saved to {file_path}")

def save_to_html(content, supplied_filename):
    """
    Saves today's matches to a text file in the 'data' folder. If the file already exists, 
    it archives the existing file with yesterday's date in the 'data/archived_data' folder.

    Args:
        string of text: The data to save to the txt file.
        supplied_filename (str): The base name of the file to save (e.g., 'todays_matches').

    Returns:
        None
    """
    # Directories
    data_dir = "docs"
    archived_dir = os.path.join(data_dir, "archived_data")
    os.makedirs(data_dir, exist_ok=True)  # Ensure the 'data' directory exists
    os.makedirs(archived_dir, exist_ok=True)  # Ensure the 'archived_data' directory exists

    # File paths
    today_date = datetime.now().strftime("%Y-%m-%d")
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    file_path = os.path.join(data_dir, f"{supplied_filename}.html")
    archived_file_path = os.path.join(archived_dir, f"{supplied_filename}_{yesterday_date}.html")

    # Check if the file already exists in the 'data' folder
    if os.path.exists(file_path):
        # Archive the existing file with yesterday's date
        if not os.path.exists(archived_file_path):
            os.rename(file_path, archived_file_path)
            print(f"Archived existing file to {archived_file_path}")
        else:
            print(f"Archived file already exists: {archived_file_path}")

    # Save today's matches to the JSON file in the 'data' folder
    # with open(file_path, "w") as json_file:
    #     json.dump(list_of_dicts, json_file, indent=4)
    with open(file_path, "w") as file:
        file.write(content)

    print(f"Today's data saved to {file_path}")

def get_date():
    """
    Gets the current date in the format required by 'statsapi'.
    Returns:
        str: The current date formatted as 'MM/DD/YYYY'.
    """
    return datetime.now().strftime("%m/%d/%Y")

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

def get_roster_names(team_id):
    """
    This method gets a list of just names of the players in the roster.
    Args:
        team_id (int): The ID of the team whose roster is to be fetched.
    Returns:
        list: A list of player names in the roster.
    """
    # Roster and processing logic

    roster_string = statsapi.roster(team_id)
    roster_list_unprocessed = roster_string.split('\n')
    roster_list = []
    # Extract and print only the player names
    for a in roster_list_unprocessed:
        # Split the line and get the last part (the name)
        player_name = ' '.join(a.split()[2:])
        roster_list.append(player_name)
    # roster_string = statsapi.roster(team_id)
    # roster_list_unprocessed = roster_string.split('\n')
    # roster_list = []
    
    # for x in roster_list_unprocessed:
    #     roster_line = ''
    #     for y in x.split(' ')[4:]:  # Skip the first 4 elements to get the name
    #         roster_line = roster_line + y + ' '
    #     roster_list.append(roster_line.lstrip())  # Remove leading whitespace
    
    # filter through roster_list for values that equal '' and exclude them
    roster_list = [name for name in roster_list if name != '']

    # roster_list2 = []
    # for roster_entry in roster_list:
    #     roster_list2.append(roster_entry.strip())

    # return roster_list2
    return roster_list

def get_homerun_leaders_by_team(team_id, season=2025, leaderGameTypes="R", limit=10):
    """
    Returns a list of home run leaders for a given team ID.
    Args:
        team_id (int): The ID of the team to fetch home run leaders for.
        season (int): The MLB season year (default is 2025).
        leaderGameTypes (str): The type of games to consider (default is "R" for regular season).
        limit (int): The maximum number of leaders to fetch (default is 10).
    Returns:
        list: A list of dictionaries containing player names and their home run counts.
    """
    homerun_leaders_by_team = []
    home_leaders_data = statsapi.team_leader_data(team_id, 'homeRuns', season=season, leaderGameTypes=leaderGameTypes, limit=limit)
    
    for z in home_leaders_data:
        homerun_leaders_by_team.append({'name': z[1], 'homeRuns': z[2]})
    
    return homerun_leaders_by_team

def get_schedule_by_date(date):
    """
    Gets the statsapi schedule based on the date provided and returns the schedule.
    Args:
        date (str): The date formatted as 'MM/DD/YYYY'.
    Returns:
        list: A list of dictionaries representing the schedule for the given date.
    extra_info: keys for dicts
        away_id
        away_name
        away_pitcher_note
        away_probable_pitcher
        away_score
        current_inning
        doubleheader
        game_date
        game_datetime
        game_id
        game_num
        game_type
        home_id
        home_name
        home_pitcher_note
        home_probable_pitcher
        home_score
        inning_state
        national_broadcasts
        series_status
        status
        summary
        venue_id
        venue_name
    """
    # print(date)
    # Get the schedule as a dictionary for the provided date
    schedule = statsapi.schedule(start_date=date, end_date=date)
    return schedule

def get_id_for_player(player_name):
    """
    Returns a player's ID based on their name.

    Args:
        player_name (str): The name of the player.

    Returns:
        int: The player's ID if found, otherwise None.
    """
    mlb = mlbstatsapi.Mlb()
    player_id = mlb.get_people_id(player_name.strip())
    
    # Validate pitcher_ids
    if not player_id:
        print(f"Warning: No get_people_id found for {player_name.strip()}")
        return None
    
    # Safely access the first element
    return player_id[0]

def get_player_name(player_id):
    """
    Returns the full name of a player based on their ID.

    Args:
        player_id (int): The ID of the player.

    Returns:
        str: The full name of the player if found, otherwise None.
    """
    mlb = mlbstatsapi.Mlb()
    player_name = mlb.get_person(player_id).__dict__.get('fullname')

    if not player_name:
        print(f"Warning: No get_person found for ID {player_id}")
        return None
    
    return player_name

def get_streaks_data():
    """
    TODO do this yourself
    """
    
    return None

def get_team_from_id(team_id):
    """
    Returns the team name based on the team ID.

    Args:
        team_id (int): The ID of the team.

    Returns:
        str: The name of the team if found, otherwise None.
    """
    # open up csv file 'data/mlb_teams.csv' and match the id with team_id at index 0 of csv and 'present' at index 5 of the csv file
    csv_file_path = 'data/mlb_teams.csv'
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                # Ensure the row has enough columns to avoid index errors
                if row[0] == str(team_id) and row[5].lower() == 'present':
                    return row[3]  # Assuming the team name is at index 3
    except FileNotFoundError:
        print(f"Error: File '{csv_file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

    print(f"Warning: No team found for ID {team_id} marked as 'present'.")
    return None

def get_bvp_stats(batter_id, pitcher_id):
    """
    Retrieves batter vs pitcher (BvP) stats for the given batter and pitcher IDs.

    Args:
        batter_id (int): The ID of the batter.
        pitcher_id (int): The ID of the pitcher.

    Returns:
        list: A list of dictionaries containing BvP stats, matchup details, and player names.
    """
    mlb = mlbstatsapi.Mlb()
    BvP = []  # Initialize an empty list to store BvP stats

    # variables for the api call
    stats = ['vsPlayer']
    group = ['hitting']
    params = {'opposingPlayerId': pitcher_id, 'season': 2025}

    try:
        # Fetch player stats
        stats = mlb.get_player_stats(batter_id, stats=stats, groups=group, **params)
        vs_player_total = stats['hitting']['vsplayertotal']

        # Process splits in the stats
        for split in vs_player_total.splits:
            p_id = mlb.get_person(pitcher_id)
            b_id = mlb.get_person(batter_id)

            # Create a dictionary for the BvP stats
            dict2 = {'stats': split.stat.__dict__}  # Dict of stats from the BvP stats
            dict2.update({'pitcher': p_id.__dict__.get('fullname')})
            dict2.update({'batter': b_id.__dict__.get('fullname')})
            BvP.append(dict2)

    except KeyError as e:
        print(f"KeyError: {e}. get_bvp_stats Skipping this player. Stats: {stats}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}. get_bvp_stats Skipping this player.")
        return None

    return BvP[0]

def get_schedule_text():
    # GET TODAYS SCHEDULE

    # Ensure the "text_output" folder exists
    os.makedirs("text_output", exist_ok=True)

    # Get yesterday's date
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # File paths
    file_name = "todays_schedule.txt"
    report_file_path = f"text_output/{file_name}"

    # Get today's date
    mlb_date = datetime.now().strftime("%m/%d/%Y")
    schedule = statsapi.schedule(start_date=mlb_date, end_date=mlb_date)

    # -----------------------------------
    for x in schedule:
        # Example UTC datetime string
        utc_datetime_str = x.get("game_datetime")

        # Parse the UTC datetime string
        utc_datetime = datetime.strptime(utc_datetime_str, '%Y-%m-%dT%H:%M:%SZ')

        # Define the UTC and Eastern Time zones
        utc_zone = pytz.utc
        eastern_zone = pytz.timezone('US/Eastern')

        # Localize the datetime to UTC
        utc_datetime = utc_zone.localize(utc_datetime)

        # Convert to Eastern Time
        eastern_datetime = utc_datetime.astimezone(eastern_zone)

        # Format the datetime in a readable format
        readable_format = eastern_datetime.strftime('%Y-%m-%d %I:%M %p %Z')

        beans = x.get('summary').split('-')
        new_beans = readable_format + " - " + beans[3].strip()
        x.update({"summary": new_beans})
    # -----------------------------------

    today_schedule_content = "Today's Schedule:\n" + "\n".join(
        f'{x.get("summary")}' for x in schedule
    )
    # ----------------------------------

    # Combine all content
    full_content = (
        today_schedule_content
    )
    return full_content

def process_schedule_text(raw_text: str) -> str:
    """
    Takes raw schedule text (first line is a header like "Today's Schedule"),
    removes the first line, parses each game line, and aligns spacing around '@'.
    Returns a single aligned multiline string.
    """
    lines = [ln.rstrip() for ln in raw_text.strip().splitlines() if ln.strip()]
    if not lines:
        return ""
    # Drop the header (first line)
    game_lines = lines[1:]

    line_re = re.compile(
        r'^(?P<dt>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+[AP]M\s+\w+)\s+-\s+'
        r'(?P<away>.+?)\s+@\s+(?P<home>.+?)\s+\((?P<status>[^)]+)\)$'
    )

    rows = []
    for line in game_lines:
        m = line_re.match(line)
        if m:
            rows.append(m.groupdict())

    if not rows:
        return ""

    max_away = max(len(r['away']) for r in rows)
    max_home = max(len(r['home']) for r in rows)
    fmt = f"{{dt}} - {{away:<{max_away}}} @ {{home:<{max_home}}} ({{status}})"
    aligned = [fmt.format(**r) for r in rows]
    return "\n".join(aligned)


def get_yesterdays_report(date=None):
    """
    Generates yesterday's report based on the provided date or defaults to yesterday's date.

    Args:
        date (str, optional): The date for which the report is generated, formatted as 'YYYY-MM-DD'.
                              If not provided, defaults to yesterday's date.

    Returns:
        list: A list containing the report content.
    """
    import re
    # Ensure the "text_output" folder exists
    os.makedirs("text_output", exist_ok=True)

    # Use the provided date or default to yesterday's date
    if date is None:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        yesterday = date

    # File paths
    file_name = "Yesterdays_Report.txt"
    report_file_path = f"text_output/{file_name}"
    backup_file_path = f"text_output/Yesterdays_Report_{yesterday}.txt"

    # Check if Todays_Report.txt exists and rename it
    if os.path.exists(report_file_path):
        os.rename(report_file_path, backup_file_path)

    # Get yesterday's schedule
    oneday = timedelta(days=1)
    yesterday_date = datetime.now().date() - oneday
    yschedule = statsapi.schedule(start_date=yesterday_date, end_date=yesterday_date)

    # Separate entries with "Toronto" in the "summary" key
    entries_with_toronto = [x for x in yschedule if "summary" in x and "Toronto" in x["summary"]]

    # check if entries_with_toronto is empty
    if not entries_with_toronto:
        
        # If no entries with "Toronto", set it to an empty list
        entries_with_toronto = []

    # Separate entries without "Toronto" in the "summary" key
    entries_without_toronto = [x for x in yschedule if not ("summary" in x and "Toronto" in x["summary"])]

    # Combine the two lists, bringing entries with "Toronto" to the top
    sorted_list = entries_without_toronto

    # get the toronto game
    toronto_content = []

    # process toronto summaries
    if entries_with_toronto:
        toronto_game = entries_with_toronto[0]
        if "Toronto" in toronto_game.get('summary'):
            # Example UTC datetime string
            utc_datetime_str = toronto_game.get("game_datetime")
            
            # Parse the UTC datetime string
            utc_datetime = datetime.strptime(utc_datetime_str, '%Y-%m-%dT%H:%M:%SZ')
            
            # Define the UTC and Eastern Time zones
            utc_zone = pytz.utc
            eastern_zone = pytz.timezone('US/Eastern')
            
            # Localize the datetime to UTC
            utc_datetime = utc_zone.localize(utc_datetime)
            
            # Convert to Eastern Time
            eastern_datetime = utc_datetime.astimezone(eastern_zone)
            
            # Format the datetime in a readable format
            readable_format = eastern_datetime.strftime('%Y-%m-%d %I:%M %p %Z')
            # print(readable_format)
            
            # Get scoring plays as a string
            s_plays = statsapi.game_scoring_plays(toronto_game.get("game_id"))
            scoring_plays = statsapi.game_scoring_plays(toronto_game.get("game_id"))
            
            # Convert the scoring plays string into a list of lines
            scoring_plays_list = scoring_plays.split("\n")
            
            # Filter the lines to only include those that contain "homers"
            filtered_plays = [line for line in scoring_plays_list if "homers" in line]
            
            # Process each kept line to only include the part before the first ")"
            processed_plays = [line.split(")")[0] + ")" for line in filtered_plays if ")" in line]
            
            # Join the processed lines back into a string if needed
            new_scoring_plays = "\n".join(processed_plays)
            
            # get the toronto highlights and leave basically unprocessed
            highlights = statsapi.game_highlights(toronto_game.get("game_id"))

            # process links in the highlights
            import re

            # Example highlights string (replace this with your actual highlights string)
            highlights = statsapi.game_highlights(toronto_game.get("game_id"))

            # Regular expression to find URLs
            url_pattern = r'(https?://[^\s]+)'

            # Replace URLs with clickable HTML links
            highlights_with_links = re.sub(url_pattern, r'<a href="\1" target="_blank">video link</a>', highlights)

            # update data in dictionary for combining step
            toronto_game.update({"time_scheduled": readable_format})
            toronto_game.update({"scoring_plays": s_plays})

            # combining into text step
            toronto_content.append(
                f"{toronto_game.get('time_scheduled')}\n"
                # f"Status: {x.get('')}\n"
                f"{toronto_game.get('away_name'):<22} {toronto_game.get('away_score')}    @\n"
                f"{toronto_game.get('home_name'):<22} {toronto_game.get('home_score')}\n\n"
                f"{toronto_game.get('scoring_plays')}\n\n"
                f"HIGHLIGHTS\n\n"
                f"{highlights_with_links}\n\n"
            )

    # All non toronto games
    yesterdays_content = []
    for x in sorted_list:
        
        # Example UTC datetime string
        utc_datetime_str = x.get("game_datetime")

        # Parse the UTC datetime string
        utc_datetime = datetime.strptime(utc_datetime_str, '%Y-%m-%dT%H:%M:%SZ')

        # Define the UTC and Eastern Time zones
        utc_zone = pytz.utc
        eastern_zone = pytz.timezone('US/Eastern')

        # Localize the datetime to UTC
        utc_datetime = utc_zone.localize(utc_datetime)

        # Convert to Eastern Time
        eastern_datetime = utc_datetime.astimezone(eastern_zone)

        # Format the datetime in a readable format
        readable_format = eastern_datetime.strftime('%Y-%m-%d %I:%M %p %Z')

        # get the scoring plays text
        scoring_plays = statsapi.game_scoring_plays(x.get("game_id"))

        # Convert the scoring plays string into a list of lines
        scoring_plays_list = scoring_plays.split("\n")

        # Filter the lines to only include those that contain "homers"
        filtered_plays = [line for line in scoring_plays_list if "homers" in line]

        # Process each kept line to only include the part before the first ")"
        processed_plays = [line.split(")")[0] + ")" for line in filtered_plays if ")" in line]

        # Join the processed lines back into a string if needed
        # new_scoring_plays = "\n".join(processed_plays)

        x.update({"time_scheduled": readable_format})
        # x.update({"scoring_plays": new_scoring_plays})

        # get specific Highlights and process for only links
        highlights = statsapi.game_highlights(x.get("game_id"))
        highlights_list = highlights.split("\n")
        
        # Initialize a variable to store the link
        condensed_game_link = None
        processed_condensed_game_link = None
        
        # Iterate through the highlights list
        for i, line in enumerate(highlights_list):
            if 'Condensed' in line:
                # Check if the link is two lines ahead
                if i + 2 < len(highlights_list):  # Ensure the index is within bounds
                    condensed_game_link = highlights_list[i + 2]
                    # print(condensed_game_link)
                    # Regular expression to find URLs
                    url_pattern = r'(https?://[^\s]+)'
                    # Replace URLs with clickable HTML links
                    processed_condensed_game_link = re.sub(url_pattern, r'<a href="\1" target="_blank">Condensed Game</a>', condensed_game_link)
                    # print(processed_condensed_game_link)
                    break  # Exit the loop once the link is found

        # Initialize a variable to store the link
        video_highlights_game_link = None
        processed_video_highlights_game_link = None

        # Iterate through the highlights list
        for i, line in enumerate(highlights_list):
            if 'Highlights' in line:
                # Check if the link is two lines ahead
                if i + 2 < len(highlights_list):  # Ensure the index is within bounds
                    video_highlights_game_link = highlights_list[i + 2]
                    # print('high')
                    # Regular expression to find URLs
                    url_pattern = r'(https?://[^\s]+)'
                    # Replace URLs with clickable HTML links
                    processed_video_highlights_game_link = re.sub(url_pattern, r'<a href="\1" target="_blank">Highlights Video</a>', video_highlights_game_link)
                    # print(processed_video_highlights_game_link)
                    break  # Exit the loop once the link is found

        # if processed_video_highlights_game_link == None:
        #     processed_video_highlights_game_link = ''
        # if processed_condensed_game_link == None:
        #     processed_condensed_game_link = ''

        yesterdays_content.append(
            f"GAME:\n"
            f"{x.get('time_scheduled')}\n"
            # f"Status: {x.get('')}\n"
            f"{x.get('away_name'):<22} {x.get('away_score')}    @\n"
            f"{x.get('home_name'):<22} {x.get('home_score')}\n\n"
            f"{processed_condensed_game_link + '\n' if processed_condensed_game_link else ''}"
            f"{processed_video_highlights_game_link + '\n\n' if processed_video_highlights_game_link else ''}"
        )

    content = toronto_content + yesterdays_content

    return content

def get_yesterdays_homers(batters_with_streaks):
    
    # Ensure the "text_output" folder exists
    os.makedirs("text_output", exist_ok=True)

    # Get yesterday's date
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # File paths
    file_name = "Yesterdays_Report.txt"
    report_file_path = f"text_output/{file_name}"
    backup_file_path = f"text_output/Yesterdays_Report_{yesterday}.txt"

    # Check if Todays_Report.txt exists and rename it
    if os.path.exists(report_file_path):
        os.rename(report_file_path, backup_file_path)

    # Get yesterday's schedule
    oneday = timedelta(days=1)
    yesterday_date = datetime.now().date() - oneday
    yschedule = statsapi.schedule(start_date=yesterday_date, end_date=yesterday_date)

    sorted_list = yschedule

    homers = []

    yesterdays_content = []

    for x in sorted_list:
        
        # Example UTC datetime string
        utc_datetime_str = x.get("game_datetime")

        # Parse the UTC datetime string
        utc_datetime = datetime.strptime(utc_datetime_str, '%Y-%m-%dT%H:%M:%SZ')

        # Define the UTC and Eastern Time zones
        utc_zone = pytz.utc
        eastern_zone = pytz.timezone('US/Eastern')

        # Localize the datetime to UTC
        utc_datetime = utc_zone.localize(utc_datetime)

        # Convert to Eastern Time
        eastern_datetime = utc_datetime.astimezone(eastern_zone)

        # Format the datetime in a readable format
        readable_format = eastern_datetime.strftime('%Y-%m-%d %I:%M %p %Z')

        # print(readable_format)
        # print(x)
        # print(x)
        # scoring_plays = statsapi.game_scoring_plays(x.get("game_id"))
        # new_scoring_plays = ""
        # Get scoring plays as a string
        scoring_plays = statsapi.game_scoring_plays(x.get("game_id"))

        # Convert the scoring plays string into a list of lines
        scoring_plays_list = scoring_plays.split("\n")

        # Filter the lines to only include those that contain "homers"
        filtered_plays = [line for line in scoring_plays_list if "homers" in line]

        # Process each kept line to only include the part before the first ")"
        processed_plays = [line.split(")")[0] + ")" for line in filtered_plays if ")" in line]

        # Join the processed lines back into a string if needed
        # new_scoring_plays = "\n".join(processed_plays)

        x.update({"time_scheduled": readable_format})
        # x.update({"scoring_plays": new_scoring_plays})

        # get specific Highlights and process for only links
        highlights = statsapi.game_highlights(x.get("game_id"))
        highlights_list = highlights.split("\n")
        # Initialize a variable to store the link
        condensed_game_link = None
        processed_condensed_game_link = None
        # Iterate through the highlights list
        for i, line in enumerate(highlights_list):
            if 'Condensed' in line:
                # Check if the link is two lines ahead
                if i + 2 < len(highlights_list):  # Ensure the index is within bounds
                    condensed_game_link = highlights_list[i + 2]
                    # print(condensed_game_link)
                    # Regular expression to find URLs
                    url_pattern = r'(https?://[^\s]+)'
                    # Replace URLs with clickable HTML links
                    processed_condensed_game_link = re.sub(url_pattern, r'<a href="\1" target="_blank">Condensed Game</a>', condensed_game_link)
                    # print(processed_condensed_game_link)
                    break  # Exit the loop once the link is found


        # Initialize a variable to store the link
        video_highlights_game_link = None
        processed_video_highlights_game_link = None
        # Iterate through the highlights list
        for i, line in enumerate(highlights_list):
            if 'Highlights' in line:
                # Check if the link is two lines ahead
                if i + 2 < len(highlights_list):  # Ensure the index is within bounds
                    video_highlights_game_link = highlights_list[i + 2]
                    # print('high')
                    # Regular expression to find URLs
                    url_pattern = r'(https?://[^\s]+)'
                    # Replace URLs with clickable HTML links
                    processed_video_highlights_game_link = re.sub(url_pattern, r'<a href="\1" target="_blank">Highlights Video</a>', video_highlights_game_link)
                    # print(processed_video_highlights_game_link)
                    break  # Exit the loop once the link is found

        # if processed_video_highlights_game_link == None:
        #     processed_video_highlights_game_link = ''
        # if processed_condensed_game_link == None:
        #     processed_condensed_game_link = ''

        homers.append(processed_plays)
        # yesterdays_content.append(
        #     f"GAME:\n"
        #     f"{x.get('time_scheduled')}\n"
        #     # f"Status: {x.get('')}\n"
        #     f"{x.get('away_name'):<22} {x.get('away_score')}    @\n"
        #     f"{x.get('home_name'):<22} {x.get('home_score')}\n\n"
        #     f"{processed_condensed_game_link}\n"
        #     f"{processed_video_highlights_game_link}\n\n"
        # )

    new_homers = []
    for x in homers:
        for y in x:
            new_homers.append('\n')
            new_homers.append(y)

    # go through homers and get all the text before the first "(" character
    new_homers = [homer.split("homers")[0].strip() for homer in new_homers if "(" in homer]


    # search homers for team name and hr stats
    stat_homers = []
    for z in new_homers:
        # print(z)
        # beans = ''
        name = z

        try:
            beans = statsapi.player_stat_data(next(x['id'] for x in statsapi.get('sports_players', {'season': '2025', 'gameType': 'W'})['people'] if x['fullName'] == name),'hitting','season')
        except StopIteration:
            print(f"No player found with the name '{name}'.")
            beans = None  # Set beans to None or handle it appropriately
        except Exception as e:
            print(f"An error occurred: {e}")
            beans = None  # Set beans to None or handle it appropriately
        # beans = statsapi.player_stat_data(next(x['id'] for x in statsapi.get('sports_players',{'season':'2025','gameType':'W'})['people'] if x['fullName']==name), 'hitting', 'season') 
        # beans_id = player = statsapi.lookup_player(name)
        # print(beans_id[0].get('id'))
        
        


        new_list_with_stats = {}
        if beans:  # Only proceed if a matching player is found
            name = z
            new_list_with_stats.update({'name':name})
            team_name = beans.get('current_team')    
            new_list_with_stats.update({'team': team_name})
            player_id = beans.get('id')  
            new_list_with_stats.update({'player_id': player_id})
            for a in beans.get('stats'):
                games_played = float(int(a.get('stats').get('gamesPlayed')))
                # hits = float(int(a.get('stats').get('hits')))
                # new_list_with_stats.append(f"{hits}")
                hrs = float(int(a.get('stats').get('homeRuns')))
                new_list_with_stats.update({'HR': int(hrs)})
                # rbi = float(int(a.get('stats').get('rbi')))
                # new_list_with_stats.append(f"{rbi}")
                hrs_per_game = round((hrs / games_played), 2)
                new_list_with_stats.update({"HRpg": hrs_per_game})
                hrs_per_game2 = str(Fraction(round((hrs / games_played), 2)).limit_denominator(7))
                #str(Fraction(round(float(x[18])/float(x[6]),2)).limit_denominator(5))
                new_list_with_stats.update({'fHRpg': hrs_per_game2})
                # hits_per_game = round((hits / games_played), 3)
                # new_list_with_stats.append(f"{hits_per_game}")
                # rbis_per_game = round((rbi / games_played), 3)
                # new_list_with_stats.append(f"{rbis_per_game}")
        else:
            # If no stats are found, append empty strings or placeholders
            new_list_with_stats.update({"name":"", "team":"", "HR":"", "HRpg":'', "fHRpg":""})

        try:
            # beans2 = statsapi.player_stat_data(next(x['id'] for x in statsapi.get('sports_players',{'season':2025,'gameType':'W'})['people'] if x['fullName']==z), 'hitting', season=2024) 
            beans2 = statsapi.player_stat_data(player_id, group="hitting", type="season", sportId=1, season=2024) 
        except StopIteration:
            print(f"No player found with the name '{z}'.")
            beans2 = None  # Set beans to None or handle it appropriately
        except Exception as e:
            print(f"An error occurred: {e}")
            beans2 = None  # Set beans to None or handle it appropriately
        
        if beans2:
            beans2_id = beans2.get('id')
            beans3 = statsapi.player_stat_data(beans2_id, group="hitting", type="season", sportId=1, season=2024)
        
            for b in beans3.get('stats'):
                hrs2 = float(int(b.get('stats').get('homeRuns')))
                games_played2 = float(int(b.get('stats').get('gamesPlayed')))
                hrs_per_game4 = round((hrs2 / games_played2), 2)
                hrs_per_game3 = str(Fraction(round((hrs2 / games_played2), 2)).limit_denominator(7))
                
                # print(hrs2)
                new_list_with_stats.update({"HR24":int(hrs2)})  
                new_list_with_stats.update({"HR24pg":hrs_per_game4})  
                new_list_with_stats.update({"fHR24pg":hrs_per_game3})  
        else:
            # If no stats are found, append empty strings or placeholders
            new_list_with_stats.update({"HR24":"", "HR24pg":"", "fHR24pg":""})
        
        stat_homers.append(new_list_with_stats)



    # # Filter out empty entries
    # stat_homers = [x for x in stat_homers if x]  # Keeps only non-empty entries

    # # Iterate through the filtered list
    # # Filter out entries where x[0] is an empty string
    # stat_homers = [x for x in stat_homers if x[0] != '']

    # Print the filtered list
    # for x in stat_homers:
    #     print(x)

    # # Filter out empty entries
    # stat_homers = [x for x in stat_homers if x]  # Keeps only non-empty entries

    # Print the list of homers
    # for x in stat_homers:
    #     print(x)

    # Filter out entries where all values are empty strings
    filtered_stat_homers = [
        x for x in stat_homers
        if not all(value == "" for value in x.values())
    ]

    for x in filtered_stat_homers:
        player_id = x.get('player_id')
        for y in batters_with_streaks:
            batter_id = y.get('player_id')
            if batter_id == player_id:
                hr_streak = y.get("HR_record")
                x.update({'HR_record':hr_streak})

    return filtered_stat_homers

def get_standings_text():
    # GET TODAYS STANDINGS
    
    # Get today's date for api call
    mlb_date = get_date()

    # Get yesterday's date
    yesterday = get_yesterday(mlb_date)

    # ---------------------------
    
    standings_content = (
        "MLB Standings:\n"
        + statsapi.standings(leagueId=103, date=mlb_date)
        + statsapi.standings(leagueId=104, date=mlb_date)
    )
    # -----------------------------
    # Combine all content
    full_content = (
        standings_content
    )

    return full_content

def contains_date(string):
    # Regular expression to match years (e.g., 2025)
    year_pattern = r'\b(19|20)\d{2}\b'
    
    # Regular expression to match months (e.g., January, Jan, 01, etc.)
    month_pattern = r'\b(January|February|March|April|May|June|July|August|September|October|November|December|' \
                    r'Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|' \
                    r'0[1-9]|1[0-2])\b'
    
    # Regular expression to match full dates (e.g., 2025-08-15, 15/08/2025, etc.)
    date_pattern = r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b'
    
    # Combine all patterns
    combined_pattern = f"({year_pattern}|{month_pattern}|{date_pattern})"
    
    # Search for any of the patterns in the string
    if re.search(combined_pattern, string, re.IGNORECASE):
        return True
    return False

def get_team_records_new(teams_history, team_name):
    """
    Processes team history to generate a record of wins and losses for each team.

    Args:
        teams_history (list): A list of dictionaries containing team history data.

    Returns:
        list: The updated list of team histories with win/loss records and additional game details.
    """
    team_record = ''
    list_of_results = []

    for x in teams_history:
        schedule1 = statsapi.schedule(game_id=x)

        # Ensure the schedule data exists and is valid
        if not schedule1 or not schedule1[0]:
            print(f"Warning: No schedule data found for game_id {x}")
            continue

        game_data = schedule1[0]
        venue = game_data.get('venue_name')


        # Determine the winning team
        # winning_team = game_data.get('winning_team')
        # if not winning_team:
        # Fallback: Determine the winner based on scores
        away_score = game_data.get('away_score', 0)
        home_score = game_data.get('home_score', 0)
        away_team = game_data.get('away_name')
        home_team = game_data.get('home_name')

        if away_score > home_score:
            winning_team = away_team
            winning_score = away_score
            loosing_score = home_score
        elif home_score > away_score:
            winning_team = home_team
            winning_score = home_score
            loosing_score = away_score
        else:
            print(f"Warning: Unable to determine winner for game_id {x}")
            continue  # Skip this game if scores are tied or invalid

        # Determine if the current team won or lost
        if winning_team == team_name:
            team_record += 'W-'
            dict_of_info = {
                'game_id': x,
                'vs_team': game_data.get('losing_team', game_data.get('home_name') if game_data.get('away_name') == team_name else game_data.get('away_name')),
                'game_date': game_data.get('game_date'),
                'result': 'W',
                'points_for': winning_score, 
                'points_against': loosing_score,
                'venue': venue 
            }
        else:
            team_record += 'L-'
            dict_of_info = {
                'game_id': x,
                'vs_team': winning_team,
                'game_date': game_data.get('game_date'),
                'result': 'L',
                'points_for': loosing_score, 
                'points_against': winning_score,
                'venue': venue  
            }

        list_of_results.append(dict_of_info)

       

    return list_of_results


def get_team_records(teams_history):
    """
    Processes team history to generate a record of wins and losses for each team.

    Args:
        teams_history (list): A list of dictionaries containing team history data.

    Returns:
        list: The updated list of team histories with win/loss records and additional game details.
    """
    for a in teams_history:
        team_id = a.get('team_id')
        team_name = a.get('team_name')
        team_history = a.get('last_games')
        team_record = ''
        list_of_previous_games = team_history
        list_of_results = []

        for x in list_of_previous_games:
            schedule1 = statsapi.schedule(game_id=x)

            # Ensure the schedule data exists and is valid
            if not schedule1 or not schedule1[0]:
                print(f"Warning: No schedule data found for game_id {x}")
                continue

            game_data = schedule1[0]

            # Determine the winning team
            winning_team = game_data.get('winning_team')
            if not winning_team:
                # Fallback: Determine the winner based on scores
                away_score = game_data.get('away_score', 0)
                home_score = game_data.get('home_score', 0)
                away_team = game_data.get('away_name')
                home_team = game_data.get('home_name')

                if away_score > home_score:
                    winning_team = away_team
                elif home_score > away_score:
                    winning_team = home_team
                else:
                    print(f"Warning: Unable to determine winner for game_id {x}")
                    continue  # Skip this game if scores are tied or invalid

            # Determine if the current team won or lost
            if winning_team == team_name:
                team_record += 'W-'
                dict_of_info = {
                    'game_id': x,
                    'vs_team': game_data.get('losing_team', game_data.get('home_name') if game_data.get('away_name') == team_name else game_data.get('away_name')),
                    'game_date': game_data.get('game_date'),
                    'result': 'W'
                }
            else:
                team_record += 'L-'
                dict_of_info = {
                    'game_id': x,
                    'vs_team': winning_team,
                    'game_date': game_data.get('game_date'),
                    'result': 'L'
                }

            list_of_results.append(dict_of_info)

        # Update the team history with the record and detailed results
        a.update({'team_record': team_record, 'team_record_plus': list_of_results})

    return teams_history


# def get_team_records(teams_history):
#     list_of_lists = []
#     for a in teams_history:
#         team_id = a.get('team_id')
#         team_name = a.get('team_name')
#         team_history = a.get('last_games')
#         team_record = ''
#         list_of_previous_games = team_history
#         list_of_results = []
#         for x in list_of_previous_games:
#             schedule1 = statsapi.schedule(game_id=x)
#             if schedule1[0].get('winning_team') == team_name:
#                 team_record = team_record + 'W-'
#                 dict_of_info = {
#                     'game_id': x,
#                     'vs_team': schedule1[0].get('losing_team'),
#                     'game_date': schedule1[0].get('game_date'),
#                     'result': 'W'
#                 }
#             else:
#                 team_record = team_record + 'L-'
#                 dict_of_info = {
#                     'game_id': x,
#                     'vs_team': schedule1[0].get('winning_team'),
#                     'game_date': schedule1[0].get('game_date'),
#                     'result': 'L'
#                 }
#             list_of_results.append(dict_of_info)
            
#         a.update({'team_record': team_record, 'team_record_plus': list_of_results})

#     return teams_history

# def get_team_records(teams_history):
#     list_of_lists = []
#     for a in teams_history:
#         team_id = a.get('team_id')
#         team_name = a.get('team_name')
#         team_history = a.get('last_games')
#         team_record = ''
#         list_of_previous_games = team_history
#         for x in list_of_previous_games:
#             schedule1 = statsapi.schedule(game_id=x)
#             if schedule1[0].get('winning_team') == team_name:
#                 team_record = team_record + 'W-'
#             else:
#                 team_record = team_record + 'L-'
#         a.update({'team_record': team_record})

#     return teams_history

def process_pitchers_from_processed_schedule(processed_schedule):
    """
    Extracts probable pitchers from the processed schedule and returns a list of dictionaries.

    Args:
        processed_schedule (list): A list of dictionaries representing the processed schedule.

    Returns:
        list: A list of dictionaries, each containing details about a probable pitcher.
              Example format:
              [
                  {"pitcher": probable_pitcher_name, "pitchers_team": team_name, "pitchers_team_id": team_id, "home_or_away": "home"},
                  {"pitcher": probable_pitcher_name, "pitchers_team": team_name, "pitchers_team_id": team_id, "home_or_away": "away"}
              ]
    """

    pitchers_today = []

    for game in processed_schedule:
        # Extract home probable pitcher
        home_pitcher = game.get("home_probable_pitcher")
        if home_pitcher:  # Ensure the pitcher exists
            home_pitcher_dict = {
                "pitcher": home_pitcher,
                "pitchers_team": game.get("home_name"),
                "pitchers_team_id": game.get("home_id"),
                "home_or_away": "home"
            }
            pitchers_today.append(home_pitcher_dict)

        # Extract away probable pitcher
        away_pitcher = game.get("away_probable_pitcher")
        if away_pitcher:  # Ensure the pitcher exists
            away_pitcher_dict = {
                "pitcher": away_pitcher,
                "pitchers_team": game.get("away_name"),
                "pitchers_team_id": game.get("away_id"),
                "home_or_away": "away"
            }
            pitchers_today.append(away_pitcher_dict)

    return pitchers_today

def process_the_schedule(schedule):
    """
    Processes the given schedule and returns a list of dictionaries 
    containing detailed information about each game.

    Args:
        schedule (list): A list of dictionaries representing the game schedule.

    Returns:
        list: A list of dictionaries containing game details, including team rosters, 
              home run leaders, and probable pitchers.
    """
    game_schedule_list_of_data = []
    for x in schedule:
        # Date
        date = get_date()

        # venue name
        venue_name = x.get('venue_name')

        # Away team data
        away_name = x.get('away_name')
        away_id = x.get('away_id')
        away_probable_pitcher = x.get('away_probable_pitcher')
        away_team_roster = get_roster_names(away_id)
        away_team_hr_leaders = get_homerun_leaders_by_team(away_id)

        # Home team data
        home_name = x.get('home_name')
        home_id = x.get('home_id')
        home_probable_pitcher = x.get('home_probable_pitcher')
        home_team_roster = get_roster_names(home_id)
        home_team_hr_leaders = get_homerun_leaders_by_team(home_id)

        # Dictionary for the game
        game_in_schedule = {
            "date": date,
            "venue": venue_name,
            "away_name": away_name,
            "away_id": away_id,
            "away_probable_pitcher": away_probable_pitcher,
            "away_team_roster": away_team_roster,
            "away_team_leaders_hr": away_team_hr_leaders,
            "home_name": home_name,
            "home_id": home_id,
            "home_probable_pitcher": home_probable_pitcher,
            "home_team_roster": home_team_roster,
            "home_team_leaders_hr": home_team_hr_leaders
        }

        game_schedule_list_of_data.append(game_in_schedule)

    return game_schedule_list_of_data

def get_teams_playing_today_from_processed_schedule(processed_schedule):
    """
    Produces a list of dictionaries containing team names and ids for teams playing today

    Args:
        iether a processed schedule or a regular schedule (basically a list of dicts)

    Returns:
        list: A list of dictionaries of team names and ids
    """  
    teams_playing_today = []
    for match in processed_schedule:
        teams_playing_today.append({"team_id": match.get('away_id'),"team_name": match.get('away_name')})
        teams_playing_today.append({"team_id": match.get('home_id'),"team_name": match.get('home_name')})
    
    return teams_playing_today

def process_batter_vs_pitcher_stats(processed_schedule):
    """
    Produces a list of dictionaries containing batter vs pitcher stats.

    Args:
        pitchers_today (list): A list of dictionaries containing probable pitchers and their teams.

    Returns:
        list: A list of dictionaries in the format:
              [{"batter_name": batter_name, "batter_id": batter_id, "opposing_pitcher": pitcher_name}]
    """
    mlb = mlbstatsapi.Mlb()

    returned_list = []

    for x in processed_schedule:

        # get away pitcher and validate
        away_probable_pitcher = x.get('away_probable_pitcher')
        if away_probable_pitcher is None:
            print(f"Warning: Missing away_probable_pitcher for game: {x}")
            continue
        # print(away_probable_pitcher)

        # get then Validate pitcher_ids
        away_pitcher_id = get_id_for_player(away_probable_pitcher)
        if away_pitcher_id is None:  # Check if pitcher_ids is None
            print(f"away_probable_pitcher -> Could not find ID for {away_probable_pitcher}")
            continue  # Skip to the next iteration of the loop
        # print(away_pitcher_id)

        # get pitcher name and validate
        away_pitcher_name = get_player_name(away_pitcher_id)
        if away_pitcher_name is None:
            print(f"Warning: away_probable_name No player name found for ID {away_pitcher_id}")
            continue
        # print(away_pitcher_name)

        # get away team_id
        away_pitcher_team_id = x.get('away_id')
        # print(away_pitcher_team_id)

        # get away pitcher name
        away_pitcher_team = get_team_from_id(away_pitcher_team_id)
        if away_pitcher_team is None:
            print(f"Warning: away_pitcher_team_id No team found for ID {away_pitcher_team_id}")
            continue
        # print(away_pitcher_team)
        
        # Process home team batters
        for y in x.get('home_team_roster', []):  # Default to an empty list if key is missing
            
            # print(y)
            
            # get and validate batter id
            home_batter_id = get_id_for_player(y)
            if home_batter_id is None:  # Check if batter_id is None
                print(f"home_batter_id Could not find ID for batter {y}")
                continue  # Skip to the next iteration of the loop
            # print(home_batter_id)

            # get batter name and validate
            home_batter_name = get_player_name(home_batter_id)
            if home_batter_name is None:
                print(f"Warning: home_batter_name -> No player name found for ID {home_batter_id}")
                continue
            # print(home_batter_name)

            #batter team id
            home_batter_team_id = x.get('home_id')
            # print(home_batter_team_id)

            # get home batter name
            home_batter_team = get_team_from_id(home_batter_team_id)
            if home_batter_team is None:
                print(f"Warning: home_batter_name -> No team found for ID {home_batter_team_id}")
                continue
            # print(home_batter_team)
            
            # get bvp stats
            batter_vs_pitcher_stats = get_bvp_stats(home_batter_id, away_pitcher_id)
            if batter_vs_pitcher_stats is None:
                print(f"Warning: get_bvp_stats1 No team found for ID {home_batter_id} {away_pitcher_id}")
                continue
            
            # print(batter_vs_pitcher_stats)

            bvp_dict = {
                "batter": home_batter_name,
                "batter_id": home_batter_id,
                "batter_team": home_batter_team,
                "pitcher": away_pitcher_name,
                "pitcher_id": away_pitcher_id,
                "pitcher_team": away_pitcher_team,
                "pitcher_team_id": away_pitcher_team_id,
                "AB": batter_vs_pitcher_stats.get('stats').get('atbats'),
                "H": batter_vs_pitcher_stats.get('stats').get('hits'),
                "HR": batter_vs_pitcher_stats.get('stats').get('homeruns'),
                "AVG": batter_vs_pitcher_stats.get('stats').get('avg'),
                "RBI": batter_vs_pitcher_stats.get('stats').get('rbi'),
                "OBP": batter_vs_pitcher_stats.get('stats').get('obp'),
                "OPS": batter_vs_pitcher_stats.get('stats').get('ops')
            }

            returned_list.append(bvp_dict)

        # get home pitcher and validate
        home_probable_pitcher = x.get('home_probable_pitcher')
        if home_probable_pitcher is None:
            print(f"Warning: Missing away_probable_pitcher for game: {x}")
            continue
        # print(home_probable_pitcher)

        # get then Validate pitcher_ids
        home_pitcher_id = get_id_for_player(home_probable_pitcher)
        if home_pitcher_id is None:  # Check if pitcher_ids is None
            print(f"home_pitcher_id Could not find ID for {home_probable_pitcher}")
            continue  # Skip to the next iteration of the loop
        # print(home_pitcher_id)

        # get pitcher name and validate
        home_pitcher_name = get_player_name(home_pitcher_id)
        if home_pitcher_name is None:
            print(f"Warning: home_pitcher_name -> No player name found for ID home_pitcher name{home_pitcher_id}")
            continue
        # print(home_pitcher_name)

        # get away team_id
        home_pitcher_team_id = x.get('home_id')
        # print(home_pitcher_team_id)

        # get away pitcher name
        home_pitcher_team = get_team_from_id(home_pitcher_team_id)
        if home_pitcher_team is None:
            print(f"Warning: home_pitcher_team -> No team found for ID home pitcher team id {home_pitcher_team_id}")
            continue
        # print(home_pitcher_team)
        
        # Process home team batters
        for z in x.get('away_team_roster', []):  # Default to an empty list if key is missing
            
            # print(z)
            # get and validate batter id
            away_batter_id = get_id_for_player(z)
            if away_batter_id is None:  # Check if batter_id is None
                print(f"Could not find ID foraway  batter id {z}")
                continue  # Skip to the next iteration of the loop
            # print(away_batter_id)

            # get batter name and validate
            away_batter_name = get_player_name(away_batter_id)
            if away_batter_name is None:
                print(f"Warning: away_batter_name -> No player name found for ID away batter name{away_batter_id}")
                continue
            # print(away_batter_name)

            #batter team id
            away_batter_team_id = x.get('away_id')
            # print(away_batter_team_id)

            # get home batter name
            away_batter_team = get_team_from_id(away_batter_team_id)
            if away_batter_team is None:
                print(f"Warning: away_batter_team -> No team found for ID away batter team id {away_batter_team_id}")
                continue
            # print(away_batter_team)

            # get bvp stats
            batter_vs_pitcher_stats2 = get_bvp_stats(away_batter_id, home_pitcher_id)
            if batter_vs_pitcher_stats2 is None:
                print(f"Warning: bvp_stats2 -> No team found for ID {home_batter_id} {away_pitcher_id}")
                continue
            # print(batter_vs_pitcher_stats2)

            bvp_dict = {
                "batter": home_batter_name,
                "batter_id": home_batter_id,
                "batter_team": home_batter_team,
                "pitcher": away_pitcher_name,
                "pitcher_id": away_pitcher_id,
                "pitcher_team": away_pitcher_team,
                "pitcher_team_id": away_pitcher_team_id,
                "AB": batter_vs_pitcher_stats2.get('atbats'),
                "H": batter_vs_pitcher_stats2.get('hits'),
                "HR": batter_vs_pitcher_stats2.get('homeruns'),
                "AVG": batter_vs_pitcher_stats2.get('avg'),
                "RBI": batter_vs_pitcher_stats2.get('rbi'),
                "OBP": batter_vs_pitcher_stats2.get('obp'),
                "OPS": batter_vs_pitcher_stats2.get('ops')
            }

            returned_list.append(bvp_dict)

    return returned_list

def process_players_from_roster_into_list(processed_schedule):
    list_of_players = []
    
    for x in processed_schedule:
        away_roster = x.get("away_team_roster")
        for y in away_roster:
            player = {}
            player.update({"player_name": y, "team": x.get("away_name"), "team_id": x.get("away_id")})
            list_of_players.append(player)
        home_roster = x.get("home_team_roster")
        for z in home_roster:
            player = {}
            player.update({"player_name": z, "team": x.get("home_name"), "team_id": x.get('home_id')})
            list_of_players.append(player)

    for x in list_of_players:
        player_name = x.get("player_name")
        player_id = get_id_for_player(player_name)
        if player_id is None:
            print('no id found for player')
            x.update({"player_id": ''})
        else:
            x.update({"player_id": player_id})

    for x in list_of_players:
        player_id = x.get("player_id")
        

    return list_of_players

def get_gameid_team_history(team_id):
    
    date = get_date()
    mlb_date = get_yesterday(date)

    new_team_list = []
    
    team_dict = {}
    sched = statsapi.schedule(start_date='03/27/2025',end_date=mlb_date,team=team_id)
    newlist = sorted(sched, key = lambda k: k["game_date"], reverse=True)
    game_data_list = []
    for game in newlist:
        game_data_list.append(game.get('game_id'))
    return game_data_list

def get_team_history(teams_playing_today):
    
    date = get_date()
    mlb_date = get_yesterday(date)

    new_team_list = []
    for a in teams_playing_today:
        team_dict = {}
        # how to get the last 15 games for a team
        team_id = a.get("team_id")
        team_name = a.get("team_name")
        sched = statsapi.schedule(start_date='03/27/2025',end_date=mlb_date,team=team_id)
        newlist = sorted(sched, key = lambda k: k["game_date"], reverse=True)
        game_data_list = []
        for game in newlist:
        #     # beans = statsapi.get("game", {"gamePk": game.get('game_id')})
        #     beans = statsapi.get("game", {"gamePk": game.get('gamePk')})
            game_data_list.append(game.get('game_id'))
            # print(f"{a} -> {}")
        team_dict.update({"team_id":team_id, "team_name": team_name, "last_games": game_data_list})
        new_team_list.append(team_dict)

    return new_team_list
    # # save the new team list to a JSON file
    # output_json_path = "text_output/teams_last_10_games.json"
    # with open(output_json_path, "w", encoding="utf-8") as output_file:
    #     json.dump(team_dict, output_file, indent=4)
    # print(f"Teams' last 10 games saved to {output_json_path}")



    # for x in new_team_list:
    #     print(x)

def get_player_position_2025(type_of_stat, player_id):
    """
    Fetches player stats for the given player ID and type of stat.

    Args:
        type_of_stat (str): The type of stat to fetch (e.g., "hitting", "pitching").
        player_id (int): The ID of the player.

    Returns:
        dict: A dictionary containing player stats, or None if an error occurs or data is unavailable.
    """
    try:
        stats = statsapi.player_stat_data(player_id, group=type_of_stat, type="season", sportId=1, season=2025)
        # print(stats)
    except Exception as e:
        print(f"An error occurred while fetching player stats: {e}")
        return None

    # Check if stats is valid and contains the expected structure
    if stats is None or "stats" not in stats or not stats["stats"]:
        print(f"No stats available for player ID {player_id}")
        return None

    try:
        stats_dict = stats['position']
    except (IndexError, KeyError) as e:
        print(f"Error accessing stats data for player ID {player_id}: {e}")
        return None

    return stats_dict

def get_player_stats_2025(type_of_stat, player_id):
    """
    Fetches player stats for the given player ID and type of stat.

    Args:
        type_of_stat (str): The type of stat to fetch (e.g., "hitting", "pitching").
        player_id (int): The ID of the player.

    Returns:
        dict: A dictionary containing player stats, or None if an error occurs or data is unavailable.
    """
    try:
        stats = statsapi.player_stat_data(player_id, group=type_of_stat, type="season", sportId=1, season=2025)
        # print(stats)
    except Exception as e:
        print(f"An error occurred while fetching player stats: {e}")
        return None

    # Check if stats is valid and contains the expected structure
    if stats is None or "stats" not in stats or not stats["stats"]:
        print(f"No stats available for player ID {player_id}")
        return None

    try:
        stats_dict = stats["stats"][0]["stats"]
    except (IndexError, KeyError) as e:
        print(f"Error accessing stats data for player ID {player_id}: {e}")
        return None

    return stats_dict

def get_player_stats_2024(type_of_stat, player_id):
    """
    Fetches player stats for the given player ID and type of stat.

    Args:
        type_of_stat (str): The type of stat to fetch (e.g., "hitting", "pitching").
        player_id (int): The ID of the player.

    Returns:
        dict: A dictionary containing player stats, or None if an error occurs or data is unavailable.
    """
    try:
        stats = statsapi.player_stat_data(player_id, group=type_of_stat, type="season", sportId=1, season=2024)
        # print(stats)
    except Exception as e:
        print(f"An error occurred while fetching player stats: {e}")
        return None

    # Check if stats is valid and contains the expected structure
    if stats is None or "stats" not in stats or not stats["stats"]:
        print(f"get stats method 25No stats available for player ID {player_id}")
        return None

    try:
        stats_dict = stats["stats"][0]["stats"]
    except (IndexError, KeyError) as e:
        print(f"Error accessing stats data for player ID {player_id}: {e}")
        return None

    return stats_dict

def add_stats_to_batters(list_of_players):
    """
    pass this method the roster list maybe
    """
    # list_of_batters = []

    for x in list_of_players:
        # get name
        batter_name = x.get("player_name")
        # get id for pitcher
        player_id = x.get("player_id")
        if player_id is None:
            print(f"player id not found for batter{batter_name}")
            x.update({"player_id":""})
            continue
        else:
            x.update({"player_id": player_id})
        # get pitchers stats by ids
        # Get the stats for the away probable pitcher
        stats = get_player_stats_2025('hitting',player_id)
        position = get_player_position_2025('hitting',player_id)

        if position is None:
            print(f"process position - could not get position for batter id {player_id}")
            continue
        else:
            x.update({"position":position})

        if stats is None:
            print(f"process batters - could not get stats for batter id {player_id}")
            continue
        else:
            # print('stats')
            games_played = float(int(stats.get('gamesPlayed')))
            hits = float(int(stats.get('hits')))
            hrs = float(int(stats.get('homeRuns')))
            rbi = float(int(stats.get('rbi')))
            hrs_per_game = round((hrs / games_played), 3)
            fhrs_per_game = str(Fraction(round((hrs / games_played), 2)).limit_denominator(7))
            hits_per_game = round((hits / games_played), 3)
            fhits_per_game = str(Fraction(round((hits / games_played), 2)).limit_denominator(7))
            rbis_per_game = round((rbi / games_played), 3)
            frbis_per_game = str(Fraction(round((rbi / games_played), 2)).limit_denominator(7))
            x.update({
                "games_played": games_played,
                "H": hits,
                "HR": hrs,
                "RBI": rbi,
                "HRpg": hrs_per_game,
                "fHRpg": fhrs_per_game,
                "Hpg": hits_per_game,
                "fHpg": fhits_per_game,
                "RBIpg": rbis_per_game,
                "fRBIpg": frbis_per_game
            })
            # # Get the stats for the away probable pitcher
            # stats2 = get_player_stats_2024('hitting',player_id)
            # if stats2 is None:
            #     print(f"2024 process batters could not get stats for batter id {player_id}")
            #     x.update({
            #         "HR24": '',
            #         "HR24pg": '',
            #         "fHR24pg": '' 
            #     })
            #     continue
            # else:
            #     # print('stats')
            #     hrs2 = float(int(stats.get('homeRuns')))
            #     games_played2 = float(int(stats.get('gamesPlayed')))
            #     hrs_per_game4 = round((hrs2 / games_played2), 2)
            #     hrs_per_game3 = str(Fraction(round((hrs2 / games_played2), 2)).limit_denominator(7))
            #     x.update({
            #         "HR24": hrs2,
            #         "HR24pg": hrs_per_game4,
            #         "fHR24pg": hrs_per_game3 
            #     })
            try:
                # beans2 = statsapi.player_stat_data(next(x['id'] for x in statsapi.get('sports_players',{'season':2025,'gameType':'W'})['people'] if x['fullName']==z), 'hitting', season=2024) 
                beans2 = statsapi.player_stat_data(player_id, group="hitting", type="season", sportId=1, season=2024) 
            except StopIteration:
                print(f"No player found with the name '{z}'.")
                beans2 = None  # Set beans to None or handle it appropriately
            except Exception as e:
                print(f"An error occurred: {e}")
                beans2 = None  # Set beans to None or handle it appropriately
            
            if beans2:
                # beans2_id = beans2.get('id')
                # beans3 = statsapi.player_stat_data(beans2_id, group="hitting", type="season", sportId=1, season=2024)
            
                for b in beans2.get('stats'):
                    hrs2 = float(int(b.get('stats').get('homeRuns')))
                    games_played2 = float(int(b.get('stats').get('gamesPlayed')))
                    hrs_per_game4 = round((hrs2 / games_played2), 2)
                    hrs_per_game3 = str(Fraction(round((hrs2 / games_played2), 2)).limit_denominator(7))
                    
                    # print(hrs2)
                    x.update({"HR24":int(hrs2)})  
                    x.update({"HR24pg":hrs_per_game4})  
                    x.update({"fHR24pg":hrs_per_game3})  
            else:
                # If no stats are found, append empty strings or placeholders
                x.update({"HR24":"", "HR24pg":"", "fHR24pg":""})

    return list_of_players

def add_stats_to_pitchers(list_of_players):
    for x in list_of_players:
        # get name
        pitcher_name = x.get('pitcher')
        # get id for pitcher
        player_id = get_id_for_player(pitcher_name)
        if player_id is None:
            print(f"player id not found for pitcher{pitcher_name}")
            x.update({"player_id":""})
        else:
            x.update({"player_id": player_id})
        # get pitchers stats by ids
        # Get the stats for the away probable pitcher
        stats = get_player_stats_2025('pitching',player_id)
        if stats is None:
            print(f"could not get stats for pitching and id {player_id}")
            continue
        else:
            # print(stats)
            era1 = stats.get("era")
            x.update({"ERA":era1})
            so9 = stats.get("strikeoutsPer9Inn")
            x.update({"SO9":so9})
            x.update({"stats":stats})

        
    return list_of_players

def get_boxscore(game_id):
    """
    Fetches the boxscore for a given game ID.

    Args:
        game_id (int): The ID of the game to fetch the boxscore for.

    Returns:
        dict: A dictionary containing the boxscore data for the game.
    """
    try:
        boxscore = statsapi.boxscore_data(game_id, timecode=None)
        return boxscore
    except Exception as e:
        print(f"An error occurred while fetching boxscore data: {e}")
        return None

def process_batters(batters, teams_histories):
    """
    Processes a list of batters by filtering out those without stats and updating their 
    performance records (home runs, hits, and RBIs) based on their last 20 games.

    Args:
        batters (list): A list of dictionaries, where each dictionary represents a batter 
                        and contains details such as 'player_id', 'team_id', and stats.
        teams_histories (list): A list of dictionaries, where each dictionary represents 
                                a team's history, including 'team_id' and 'last_games'.

    Returns:
        list: A filtered list of batters with updated performance records. Each batter 
              dictionary includes additional keys:
              - 'HR_record': A string representing the batter's home run record over the last 20 games.
              - 'H_record': A string representing the batter's hit record over the last 20 games.
              - 'RBI_record': A string representing the batter's RBI record over the last 20 games.
    """    
    # go through batters get rid of all batters without stats since they are probably pitchers who don't hit
    # # Filter out batters without the "games_played" key

    # Using list comprehension
    filtered_batters = [batter for batter in batters if "games_played" in batter]
    
    # for q in players_bvp:
    for q in filtered_batters:
        player_id = q.get('player_id')
        team_id = q.get('team_id')
        # last_games_list = teams_last_10_games.get(str(team_id), [])
        for r in teams_histories:
            team_history_id = r.get('team_id')
            if team_history_id == team_id:
                last_games_list = r.get('last_games')
        hr_record = ''
        hits_record = ''
        rbi_record = ''
        for game in last_games_list:
            boxscore = statsapi.boxscore_data(game, timecode=None)
            for x in boxscore.get('awayBatters'):
                if player_id == x.get('personId'):
                    hr_record = hr_record + x.get('hr') + '-'
                    hits_record = hits_record + x.get('h') + '-'
                    rbi_record = rbi_record + x.get('rbi') + '-'
            for x in boxscore.get('homeBatters'):
                if player_id == x.get('personId'):
                    hr_record = hr_record + x.get('hr') + '-'
                    hits_record = hits_record + x.get('h') + '-'
                    rbi_record = rbi_record + x.get('rbi') + '-'
        q.update({'HR_record': hr_record, 'H_record': hits_record, 'RBI_record': rbi_record})

    return filtered_batters

def get_streaks_for_bvp(batter_vs_pitcher_stats, batters_with_streaks):
    for x in batter_vs_pitcher_stats:
        batter_id = x.get('batter_id')
        for y in batters_with_streaks:
            player_id = y.get('player_id')
            if batter_id == player_id:
                x.update({
                    "team_id": y.get("team_id"),
                    "all_games_played": y.get("games_played"),
                    "all_H": y.get("H"),
                    "all_HR": y.get("HR"),
                    "all_RBI": y.get("RBI"),
                    "all_HRpg": y.get("HRpg"),
                    "all_fHRpg": y.get("fHRpg"),
                    "all_Hpg": y.get("Hpg"),
                    "all_fHpg": y.get("fHpg"),
                    "all_RBIpg": y.get("RBIpg"),
                    "all_fRBIpg": y.get("fRBIpg"),
                    "all_HR24": y.get("HR24"),
                    "all_HR24pg": y.get("HR24pg"),
                    "all_fHR24pg": y.get("fHR24pg"),
                    "all_HR_record": y.get("HR_record"),
                    "all_H_record": y.get("H_record"),
                    "all_RBI_record": y.get("RBI_record")
                })
    return batter_vs_pitcher_stats

def old_batter_vs_pitchers_get():
    import statsapi
    import mlbstatsapi
    from datetime import datetime




    # GET ALL THE MATCHES TODAY LOTS OF API
    def get_matches_today_data():
        

        # Get today's schedule
        matches_today = []

        # get the proper formatted date
        mlb_date = datetime.now().strftime("%m/%d/%Y")

        # get the schedule as a dictionary for today
        schedule = statsapi.schedule(start_date=mlb_date, end_date=mlb_date)

        # iterate through each game of the schedule
        for x in schedule:

            # initialize game data dictionary
            game_data = {}
            
            # away_name
            game_data.update({'away_name': x.get('away_name')}) 
            
            # home_name
            game_data.update({'home_name': x.get('home_name')})
            
            # away_id
            game_data.update({'away_id': x.get('away_id')})

            away_team_leaders_hr = []
            # add top away team guys here
            away_leaders = statsapi.team_leader_data(x.get('away_id'), 'homeRuns', season=2025, leaderGameTypes="R", limit=20)
            for z in away_leaders:
                away_team_leaders_hr.append({'name': z[1],'homeRuns': z[2]})

            game_data.update({'away_team_leaders_hr': away_team_leaders_hr})

            home_team_leaders_hr = []
            # add top away team guys here
            home_leaders = statsapi.team_leader_data(x.get('home_id'), 'homeRuns', season=2025, leaderGameTypes="R", limit=20)
            for z in home_leaders:
                home_team_leaders_hr.append({'name': z[1],'homeRuns': z[2]})

            game_data.update({'home_team_leaders_hr': home_team_leaders_hr})

            # home_id
            game_data.update({'home_id': x.get('home_id')})
            # home_probable_pitcher
            game_data.update({'home_probable_pitcher': x.get('home_probable_pitcher')})
            # away_probable_pitcher
            game_data.update({'away_probable_pitcher': x.get('away_probable_pitcher')})

            matches_today.append(game_data)


        mlb = mlbstatsapi.Mlb()

        for x in matches_today:
    
            away_probable_pitcher = x.get('away_probable_pitcher')
            
            # Check if away_probable_pitcher is valid
            if not away_probable_pitcher:
                print(f"Warning: Missing away_probable_pitcher for game: {x}")
                continue  # Skip this game if no pitcher is available

            pitcher_ids = mlb.get_people_id(away_probable_pitcher)
            
            # Check if pitcher_ids is not empty
            if not pitcher_ids:
                print(f"Warning: No pitcher ID found for {away_probable_pitcher}")
                continue  # Skip this game if no pitcher ID is found

            pitcher_id = pitcher_ids[0]  # Safely access the first element

            BvP = []
            for y in x.get('home_team_leaders_hr', []):  # Default to an empty list if key is missing
                batter_id = mlb.get_people_id(y.get('name'))[0]

                stats = ['vsPlayer']
                group = ['hitting']
                params = {'opposingPlayerId': pitcher_id, 'season': 2025}

                try:
                    stats = mlb.get_player_stats(batter_id, stats=stats, groups=group, **params)
                    vs_player_total = stats['hitting']['vsplayertotal']
                    for split in vs_player_total.splits:
                        p_id = mlb.get_person(pitcher_id)
                        b_id = mlb.get_person(batter_id)
                        
                        bvp_matchup = f"pitcher: {p_id.__dict__.get('fullname')} vs batter: {b_id.__dict__.get('fullname')}"
                        dict2 = {'bvp_stats': split.stat.__dict__}
                        # dict2.update({'bvp_matchup': bvp_matchup})
                        dict2.update({'pitcher': p_id.__dict__.get('fullname')})
                        dict2.update({'batter': b_id.__dict__.get('fullname')})
                        dict2.update({'batter_id': batter_id})
                        dict2.update({'batter_team': x.get('home_name')})
                        dict2.update({'batter_team_id': x.get('home_id')})
                        BvP.append(dict2)

                except KeyError as e:
                    print(f"KeyError: {e}. Skipping this player. Stats: {stats}")
                except Exception as e:
                    print(f"Unexpected error: {e}. Skipping this player.")
            
            
            home_probable_pitcher = x.get('home_probable_pitcher')
            
            # Check if home_probable_pitcher is valid
            if not home_probable_pitcher:
                print(f"Warning: Missing home_probable_pitcher for game: {x}")
                continue  # Skip this game if no pitcher is available

            pitcher_ids = mlb.get_people_id(home_probable_pitcher)
            
            # Check if pitcher_ids is not empty
            if not pitcher_ids:
                print(f"Warning: No pitcher ID found for {home_probable_pitcher}")
                continue  # Skip this game if no pitcher ID is found

            pitcher_id = pitcher_ids[0]  # Safely access the first element

            for y in x.get('away_team_leaders_hr', []):  # Default to an empty list if key is missing
                batter_id = mlb.get_people_id(y.get('name'))[0]

                stats = ['vsPlayer']
                group = ['hitting']
                params = {'opposingPlayerId': pitcher_id, 'season': 2025}

                try:
                    stats = mlb.get_player_stats(batter_id, stats=stats, groups=group, **params)
                    vs_player_total = stats['hitting']['vsplayertotal']
                    for split in vs_player_total.splits:
                        p_id = mlb.get_person(pitcher_id)
                        b_id = mlb.get_person(batter_id)
                        
                        bvp_matchup = f"pitcher: {p_id.__dict__.get('fullname')} vs batter: {b_id.__dict__.get('fullname')}"
                        dict2 = {'bvp_stats': split.stat.__dict__}
                        # dict2.update({'bvp_matchup': bvp_matchup})
                        dict2.update({'pitcher': p_id.__dict__.get('fullname')})
                        dict2.update({'batter': b_id.__dict__.get('fullname')})
                        dict2.update({'batter_id': batter_id})
                        dict2.update({'batter_team': x.get('away_name')})
                        dict2.update({'batter_team_id': x.get('away_id')})
                        BvP.append(dict2)

                except KeyError as e:
                    print(f"KeyError: {e}. Skipping this player. Stats: {stats}")
                except Exception as e:
                    print(f"Unexpected error: {e}. Skipping this player.")
            
            # Add the BvP stats to the matches_today dictionary
            x.update({'BvP_stats': BvP})

        super_beans = []
        for x in matches_today:
            bvp = x.get('BvP_stats')
            # print(type(bvp))
            if bvp is not None:
                for y in bvp:
                    super_beans.append(y)
                
            # super_beans.append(bvp)

        # beans_beans = []
        # for x in super_beans:
        #     for y in x:
        #         beans_beans.append(y)
        # return beans_beans
        return super_beans

    return get_matches_today_data()

def league_leaders_era():
    eras = statsapi.league_leader_data('earnedRunAverage',statGroup='pitching',limit=25,statType='season') 

    # Convert to a list of dictionaries with "place" baked into each dictionary
    eras_list = [
        {
            "place": entry[0],
            "player_name": entry[1],
            "team": entry[2],
            "ERA": entry[3]
        }
        for entry in eras
    ]
    
    # Print the resulting list of dictionaries
    # for x in eras_list:
    #     for key,value in x.items():
    #         print(f"{key} -> {value}")
    return eras_list

def league_leaders_strikeouts_per_9_innings():
    so9 =  statsapi.league_leader_data('strikeoutsPer9Inn',statGroup='pitching',limit=25,season=2025) 
    # Convert to a list of dictionaries with "place" baked into each dictionary
    so9_list = [
        {
            "place": entry[0],
            "player_name": entry[1],
            "team": entry[2],
            "SO9": entry[3]
        }
        for entry in so9
    ]
    
    # Print the resulting list of dictionaries
    # for x in so9_list:
    #     for key,value in x.items():
    #         print(f"{key} -> {value}")
    return so9_list

def league_leaders_hrs():
    hrs = statsapi.league_leader_data('homeRuns',statGroup='hitting',limit=25,sportId=1,statType='season') 
    # Convert to dictionary
    hrs_list = [
        {
            "place": entry[0],
            "player_name": entry[1],
            "team": entry[2],
            "HR": entry[3]
        }
        for entry in hrs
    ]
    # for x in hrs_list:
    #     for key,value in x.items():
    #         print(f"{key} -> {value}")
    return hrs_list

def find_dh_batters_add_stats_streaks(schedule, batters_with_streaks):
    
    games = []
    for x in schedule:
        json_string = statsapi.get("game", {"gamePk": x.get('game_id')})
        games.append(json_string)

    # Fetch the JSON string
    # json_string = statsapi.get("game", {"gamePk": 777807})
    # json_string = games[1]  # Assuming we want the first game in the schedule
    list_of_names = []
    for x in games:
        beans = []
        json_string = x
        livedata = json_string.get('liveData').get('boxscore').get('teams')
        # away
        for player_id, player_data in livedata.get('away').get('players').items():
            full_name = player_data.get('person', {}).get('fullName', 'Unknown')
            abbreviation = player_data.get('position', {}).get('abbreviation', 'N/A')  # Default to 'N/A' if not found
            if abbreviation == 'DH':
                beans.append(full_name)
        # home
        for player_id, player_data in livedata.get('home').get('players').items():
            full_name = player_data.get('person', {}).get('fullName', 'Unknown')
            abbreviation = player_data.get('position', {}).get('abbreviation', 'N/A')  # Default to 'N/A' if not found
            if abbreviation == 'DH':
                beans.append(full_name)
        list_of_names.append(beans)

    # i think this take is out of a list of lists and just adds it to 1 list
    all_names = []
    for x in list_of_names:
        for y in x:
            all_names.append(y)

    # remove duplicates from the list
    all_names = list(set(all_names))

    # Print the unique names
    print("Unique DH Batter Names:")
    for name in all_names:
        print(name)
    
    # search DH's for team name and hr stats
    stat_homers = []
    for z in all_names:
        player_name = z
        player_dict = None
        
        # Check if the player is already in batters_with_streaks
        for xx in batters_with_streaks:
            if z == xx.get('player_name'):
                player_dict = xx
                break  # Exit the loop once the player is found

        if not player_dict:
            # If player_dict is not found, initialize it as an empty dictionary
            player_dict = {"player_name": z}
        
        try:
            beans = statsapi.player_stat_data(next(x['id'] for x in statsapi.get('sports_players',{'season':2025,'gameType':'W'})['people'] if x['fullName']==z), 'hitting', 'season') 
        except StopIteration:
            print(f"No player found with the name '{z}'.")
            beans = None  # Set beans to None or handle it appropriately
        except Exception as e:
            print(f"An error occurred: {e}")
            beans = None  # Set beans to None or handle it appropriately
        
 
        # Populate the dictionary with stats
        if beans:  # Only proceed if a matching player is found
            player_dict.setdefault("team", beans.get('current_team', "Unknown"))
            for a in beans.get('stats'):
                games_played = float(a.get('stats').get('gamesPlayed', 0))
                hrs = float(a.get('stats').get('homeRuns', 0))
                player_dict.setdefault("games_played", games_played)
                player_dict.setdefault("HR", hrs)
                player_dict.setdefault("HRpg", round((hrs / games_played), 2) if games_played > 0 else 0)
                player_dict.setdefault("fHRpg", str(Fraction(player_dict["HRpg"]).limit_denominator(7)))

        try:
            # beans2 = statsapi.player_stat_data(next(x['id'] for x in statsapi.get('sports_players',{'season':2025,'gameType':'W'})['people'] if x['fullName']==z), 'hitting', season=2024) 
            player_id = beans.get('id')
            beans2 = statsapi.player_stat_data(player_id, group="hitting", type="season", sportId=1, season=2024) 
        except StopIteration:
            print(f"No player found with the name beans2'{z}'.")
            beans2 = None  # Set beans to None or handle it appropriately
        except Exception as e:
            print(f"An error occurred: {e}")
            beans2 = None  # Set beans to None or handle it appropriately


        if beans2:
            # beans2_id = beans2.get('id')
            # beans3 = statsapi.player_stat_data(beans2_id, group="hitting", type="season", sportId=1, season=2024)
        
            for b in beans2.get('stats'):
                hrs2 = float(b.get('stats').get('homeRuns', 0))
                games_played2 = float(b.get('stats').get('gamesPlayed', 0))
                player_dict.setdefault("HR24", hrs2)
                player_dict.setdefault("HR24pg", round((hrs2 / games_played2), 2) if games_played2 > 0 else 0)
                player_dict.setdefault("fHR24pg", str(Fraction(player_dict["HR24pg"]).limit_denominator(7)))
        else:
            player_dict.setdefault("HR24", 0)
            player_dict.setdefault("HR24pg", 0)
            player_dict.setdefault("fHR24pg", "0")

        player_dict.setdefault("HR_record", "-")
        player_dict.setdefault("H_record", "-")
        player_dict.setdefault("RBI_record", "-")

        # Append the dictionary to the list
        stat_homers.append(player_dict)

    return stat_homers

def scrape_ballparks_table_to_json():
    """
    Scrapes the table data from the specified URL and saves it to a JSON file.

    Args:
        url (str): The URL of the webpage containing the table.
        output_file (str): The path to the JSON file where the data will be saved.

    Returns:
        None

    Raises:
        requests.RequestException: If there is an issue with the HTTP request.
        Exception: If the table data cannot be found or processed.

    Example:
        >>> scrape_ballparks_table_to_json("https://www.onlyhomers.com/ballparks", "ballparks.json")
    """
    url = "https://www.onlyhomers.com/ballparks"
    try:
        # Fetch the webpage content
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the table in the webpage
        table = soup.find('table')
        if not table:
            raise Exception("No table found on the webpage.")

        # Extract table headers
        headers = [header.text.strip() for header in table.find_all('th')]

        # Extract table rows
        rows = []
        for row in table.find_all('tr')[1:]:  # Skip the header row
            cells = row.find_all('td')
            row_data = {headers[i]: cells[i].text.strip() for i in range(len(cells))}
            rows.append(row_data)
        return rows
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None
    except Exception as e:
        print(f"Error processing the table data: {e}")
        return None

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

def reverse_list(input_list):
    """
    Reverses the given list and returns the reversed list.

    Args:
        input_list (list): The list to be reversed.

    Returns:
        list: A new list with the elements in reverse order.
    """
    return list(reversed(input_list))

def expand_sequence(sequence):
    """
    Converts a sequence string into a list of 1's and 0's.
    Expands numbers greater than 1 into multiple 1's.

    Args:
        sequence (str): A string of numbers separated by '-'.

    Returns:
        list: A list of 1's and 0's.
    """
    result = []
    for item in sequence.split('-'):
        if item.isdigit():  # Check if the item is a number
            num = int(item)
            if num == 0:
                result.append(0)  # Append a single 0
            else:
                result.extend([1] * num)  # Append `num` 1's
    return result

def string_to_binary_list(string):
    """
    Converts a string of 'W' and 'L' into a list of 1's and 0's.

    Args:
        string (str): The input string containing 'W' and 'L' separated by '-'.

    Returns:
        list: A list of 1's for 'W' and 0's for 'L'.
    """
    return [1 if char == 'W' else 0 for char in string.split('-') if char]

def analyze_binary_list(binary_list):
    """
    Analyzes a list of 1's and 0's to calculate its length and count the number of 1's and 0's.

    Args:
        binary_list (list): A list of 1's and 0's.

    Returns:
        dict: A dictionary containing the length of the list, the count of 1's, and the count of 0's.
    """
    length = len(binary_list)
    count_ones = binary_list.count(1)
    count_zeros = binary_list.count(0)
    return {
        "trials": length,
        "success": count_ones,
        "failures": count_zeros
    }

def find_streaks(binary_list):
    """
    Finds all streaks of consecutive 1's in a binary list (ignoring streaks of length 1)
    and provides their lengths and starting indices.

    Args:
        binary_list (list): A list of 1's and 0's.

    Returns:
        list: A list of dictionaries, each containing the streak length and starting index.
    """
    streaks = []
    streak_length = 0
    start_index = None

    for i, value in enumerate(binary_list):
        if value == 1:
            if streak_length == 0:
                start_index = i  # Start of a new streak
            streak_length += 1
        else:
            if streak_length > 1:  # End of a streak (ignore streaks of length 1)
                streaks.append({"streak_length": streak_length, "start_index": start_index})
            streak_length = 0  # Reset streak length

    # Handle the case where the list ends with a streak
    if streak_length > 1:
        streaks.append({"streak_length": streak_length, "start_index": start_index})

    return streaks

def plot_streak_distribution(sequence_analysis):
    streak_lengths_1 = [streak['streak_length'] for streak in sequence_analysis if streak['streak_value'] == 1]
    streak_lengths_0 = [streak['streak_length'] for streak in sequence_analysis if streak['streak_value'] == 0]

    plt.hist(streak_lengths_1, bins=range(1, max(streak_lengths_1) + 2), alpha=0.5, label='1 Streaks')
    plt.hist(streak_lengths_0, bins=range(1, max(streak_lengths_0) + 2), alpha=0.5, label='0 Streaks')
    plt.xlabel('Streak Length')
    plt.ylabel('Frequency')
    plt.legend()
    plt.title('Distribution of Streak Lengths')
    plt.show()


def text_streak_distribution(sequence_analysis):
    """
    Generates a one-line text-based graph of streak distributions for embedding in an HTML row.

    Args:
        sequence_analysis (list): A list of dictionaries containing streak data.

    Returns:
        str: A one-line text-based graph as a string.
    """
    # Extract streak lengths for wins (1) and losses (0)
    streak_lengths_1 = [streak['streak_length'] for streak in sequence_analysis if streak['streak_value'] == 1]
    streak_lengths_0 = [streak['streak_length'] for streak in sequence_analysis if streak['streak_value'] == 0]

    # Calculate frequency distributions
    max_length_1 = max(streak_lengths_1, default=0)
    max_length_0 = max(streak_lengths_0, default=0)
    max_length = max(max_length_1, max_length_0)

    freq_1 = {length: streak_lengths_1.count(length) for length in range(1, max_length + 1)}
    freq_0 = {length: streak_lengths_0.count(length) for length in range(1, max_length + 1)}

    # Generate the one-line text-based graph
    graph_parts = []
    for length in range(1, max_length + 1):
        bar_1 = "#" * freq_1.get(length, 0)
        bar_0 = "*" * freq_0.get(length, 0)
        graph_parts.append(f"{length}:{bar_1}{bar_0}")

    return " | ".join(graph_parts)


def text_streak_distribution1(sequence_analysis):
    """
    Generates a text-based graph of streak distributions for embedding in a text file.

    Args:
        sequence_analysis (list): A list of dictionaries containing streak data.

    Returns:
        str: A text-based graph as a string.
    """
    # Extract streak lengths for wins (1) and losses (0)
    streak_lengths_1 = [streak['streak_length'] for streak in sequence_analysis if streak['streak_value'] == 1]
    streak_lengths_0 = [streak['streak_length'] for streak in sequence_analysis if streak['streak_value'] == 0]

    # Calculate frequency distributions
    max_length_1 = max(streak_lengths_1, default=0)
    max_length_0 = max(streak_lengths_0, default=0)
    max_length = max(max_length_1, max_length_0)

    freq_1 = {length: streak_lengths_1.count(length) for length in range(1, max_length + 1)}
    freq_0 = {length: streak_lengths_0.count(length) for length in range(1, max_length + 1)}

    # Generate the text-based graph
    graph_lines = []
    # graph_lines.append("Distribution of Streak Lengths (Text Graph)")
    graph_lines.append("-" * 50)
    graph_lines.append("Streak Length | 1 Streaks (Wins) | 0 Streaks (Losses)")
    # graph_lines.append("-" * 50)

    for length in range(1, max_length + 1):
        bar_1 = "#" * freq_1.get(length, 0)
        bar_0 = "#" * freq_0.get(length, 0)
        graph_lines.append(f"{length:13} | {bar_1:18} | {bar_0}")

    return "\n".join(graph_lines)

def find_streaks_with_analysis(binary_list):
    """
    Finds all streaks of consecutive 1's and 0's in a binary list (ignoring streaks of length 1)
    and provides their lengths and starting indices. Also computes the average streak length
    and average starting index for 1's streaks that occur after a 0 streak.

    Args:
        binary_list (list): A list of 1's and 0's.

    Returns:
        dict: A dictionary containing:
            - "streaks": A list of dictionaries for all streaks (1's and 0's),
              each containing the streak length, value (1 or 0), and starting index.
            - "average_streak_length_after_0": The average length of 1's streaks after a 0 streak.
            - "average_start_index_after_0": The average starting index of 1's streaks after a 0 streak.
    """
    streaks = []
    streak_length = 0
    start_index = None
    current_value = None

    # Track 1's streaks that occur after a 0 streak
    ones_streaks_after_0 = []
    ones_start_indices_after_0 = []
    last_streak_was_0 = False

    for i, value in enumerate(binary_list):
        if value == current_value:
            streak_length += 1
        else:
            if streak_length > 1:  # End of a streak (ignore streaks of length 1)
                streaks.append({
                    "streak_value": current_value,
                    "streak_length": streak_length,
                    "start_index": start_index
                })
                # If the last streak was a 0 and the current streak is 1, track it
                if current_value == 0 and value == 1:
                    last_streak_was_0 = True
                else:
                    last_streak_was_0 = False

                if last_streak_was_0 and current_value == 1:
                    ones_streaks_after_0.append(streak_length)
                    ones_start_indices_after_0.append(start_index)

            # Start a new streak
            current_value = value
            streak_length = 1
            start_index = i

    # Handle the case where the list ends with a streak
    if streak_length > 1:
        streaks.append({
            "streak_value": current_value,
            "streak_length": streak_length,
            "start_index": start_index
        })
        if last_streak_was_0 and current_value == 1:
            ones_streaks_after_0.append(streak_length)
            ones_start_indices_after_0.append(start_index)

    # Compute averages for 1's streaks after 0 streaks
    average_streak_length_after_0 = (
        sum(ones_streaks_after_0) / len(ones_streaks_after_0)
        if ones_streaks_after_0 else 0
    )
    average_start_index_after_0 = (
        sum(ones_start_indices_after_0) / len(ones_start_indices_after_0)
        if ones_start_indices_after_0 else 0
    )

    return {
        "streaks": streaks,
        "average_streak_length_after_0": average_streak_length_after_0,
        "average_start_index_after_0": average_start_index_after_0
    }

def analyze_streaks(data):
    result = {
        'number_of_win_streaks': 0,
        'longest_win_streak': 0,
        'average_win_streak_length': 0,
        'occurrences_of_longest_win_streaks': 0,
        'shortest_win_streak': float('inf'),
        'occurrences_of_shortest_win_streaks': 0,
        'number_of_lose_streaks': 0,
        'longest_lose_streak': 0,
        'average_lose_streak_length': 0,
        'occurrences_of_longest_lose_streaks': 0,
        'shortest_lose_streak': float('inf'),
        'occurrences_of_shortest_lose_streaks': 0
    }

    # Separate streaks by value
    streaks_1 = [streak for streak in data if streak['streak_value'] == 1]
    streaks_0 = [streak for streak in data if streak['streak_value'] == 0]

    # Analyze streaks for value 1
    if streaks_1:
        result['number_of_win_streaks'] = len(streaks_1)
        lengths_1 = [streak['streak_length'] for streak in streaks_1]
        result['longest_win_streak'] = max(lengths_1)
        result['shortest_win_streak'] = min(lengths_1)
        result['average_win_streak_length'] = round(sum(lengths_1) / len(lengths_1),3)
        result['occurrences_of_longest_win_streaks'] = lengths_1.count(result['longest_win_streak'])
        result['occurrences_of_shortest_win_streaks'] = lengths_1.count(result['shortest_win_streak'])

    # Analyze streaks for value 0
    if streaks_0:
        result['number_of_lose_streaks'] = len(streaks_0)
        lengths_0 = [streak['streak_length'] for streak in streaks_0]
        result['longest_lose_streak'] = max(lengths_0)
        result['shortest_lose_streak'] = min(lengths_0)
        result['average_lose_streak_length'] = round(sum(lengths_0) / len(lengths_0),3)
        result['occurrences_of_longest_lose_streaks'] = lengths_0.count(result['longest_lose_streak'])
        result['occurrences_of_shortest_lose_streaks'] = lengths_0.count(result['shortest_lose_streak'])

    # Replace 'inf' with 0 if no streaks exist
    if result['shortest_win_streak'] == float('inf'):
        result['shortest_win_streak'] = 0
    if result['shortest_lose_streak'] == float('inf'):
        result['shortest_lose_streak'] = 0

    return result

def calculate_transition_matrix(binary_list):
    """
    Calculates the transition matrix for a binary list.

    Args:
        binary_list (list): A list of 1's and 0's representing trial outcomes.

    Returns:
        np.ndarray: A 2x2 transition matrix.
    """
    # Initialize counts for transitions
    transitions = {"0->0": 0, "0->1": 0, "1->0": 0, "1->1": 0}

    # Count transitions
    for i in range(len(binary_list) - 1):
        current = binary_list[i]
        next_ = binary_list[i + 1]
        if current == 0 and next_ == 0:
            transitions["0->0"] += 1
        elif current == 0 and next_ == 1:
            transitions["0->1"] += 1
        elif current == 1 and next_ == 0:
            transitions["1->0"] += 1
        elif current == 1 and next_ == 1:
            transitions["1->1"] += 1

    # Calculate probabilities
    total_0 = transitions["0->0"] + transitions["0->1"]
    total_1 = transitions["1->0"] + transitions["1->1"]

    P_0_to_0 = transitions["0->0"] / total_0 if total_0 > 0 else 0
    P_0_to_1 = transitions["0->1"] / total_0 if total_0 > 0 else 0
    P_1_to_0 = transitions["1->0"] / total_1 if total_1 > 0 else 0
    P_1_to_1 = transitions["1->1"] / total_1 if total_1 > 0 else 0

    # Create the transition matrix
    transition_matrix = np.array([
        [P_0_to_0, P_0_to_1],
        [P_1_to_0, P_1_to_1]
    ])

    return transition_matrix

def predict_next_state(current_state, transition_matrix):
    """
    Predicts the next state based on the current state and transition matrix.

    Args:
        current_state (int): The current state (0 or 1).
        transition_matrix (np.ndarray): The 2x2 transition matrix.

    Returns:
        int: The predicted next state (0 or 1).
    """
    probabilities = transition_matrix[current_state]
    return np.random.choice([0, 1], p=probabilities)

def markov_monte_carlo(sequence):
    """
    Predicts the next value in a binary sequence using Markov Monte Carlo analysis.

    Args:
        sequence (list): A binary list (containing only 0s and 1s).

    Returns:
        tuple: A tuple containing the predicted next value (0 or 1) and the probability of that prediction.
    """
    if len(sequence) < 2:
        raise ValueError("The sequence must contain at least two elements.")

    # Count transitions
    count_0_to_0 = count_0_to_1 = count_1_to_0 = count_1_to_1 = 0
    for i in range(len(sequence) - 1):
        if sequence[i] == 0:
            if sequence[i + 1] == 0:
                count_0_to_0 += 1
            else:
                count_0_to_1 += 1
        else:
            if sequence[i + 1] == 0:
                count_1_to_0 += 1
            else:
                count_1_to_1 += 1

    # Calculate probabilities
    total_0 = count_0_to_0 + count_0_to_1
    total_1 = count_1_to_0 + count_1_to_1
    prob_0_to_1 = count_0_to_1 / total_0 if total_0 > 0 else 0
    prob_1_to_1 = count_1_to_1 / total_1 if total_1 > 0 else 0

    # Predict the next value based on the last value in the sequence
    last_value = sequence[-1]
    if last_value == 0:
        prediction = 1 if prob_0_to_1 > 0.5 else 0
        probability = prob_0_to_1 if prediction == 1 else 1 - prob_0_to_1
    else:
        prediction = 1 if prob_1_to_1 > 0.5 else 0
        probability = prob_1_to_1 if prediction == 1 else 1 - prob_1_to_1

    return prediction, probability

def analyze_team_dict(team_dict):
    for x in team_dict:
        team_record_string = x.get("team_record")
        binary_list = string_to_binary_list(team_record_string)
        r_binary_list = list(reversed(binary_list))
        transition_matrix = calculate_transition_matrix(r_binary_list)
        current_state = binary_list[-1]  # Use the last value in the list as the current state
        predicted_state = predict_next_state(current_state, transition_matrix)
        if predicted_state == 1:
            predict = 'W'
        else:
            predict = 'L'
        x.update({"prediction":predict})
        predicted_value, probability = markov_monte_carlo(r_binary_list)
        if predicted_value == 1:
            predict2 = 'W'
        else:
            predict2 = 'L'
        x.update({"wl_mmp":predict2,"wl_mmpp":probability})
    return team_dict

def analyze_sequence_and_predict(sequence_dict):
    for x in sequence_dict:
        team_record_string = x.get("HR_record")
        if team_record_string is None:
            # print('sorry')
            x.update({"prediction": ''})
        else:
            binary_list = expand_sequence(team_record_string)
            r_binary_list = list(reversed(binary_list))
            transition_matrix = calculate_transition_matrix(r_binary_list)
            current_state = binary_list[-1]  # Use the last value in the list as the current state
            predicted_state = predict_next_state(current_state, transition_matrix)
            x.update({"prediction":predicted_state})
            predicted_value, probability = markov_monte_carlo(r_binary_list)
            x.update({"hr_mmp":predicted_value,"hr_mmpp":probability})
    return sequence_dict

def analyze_sequence_and_predict2(sequence_dict):
    for x in sequence_dict:
        hr_record_string = x.get("HR_record")
        # print(hr_record_string)
        h_record_string = x.get("H_record")
        # print(h_record_string)
        rbi_record_string = x.get("RBI_record")
        # print(rbi_record_string)
        
        if hr_record_string is None:
            # print('sorry')
            x.update({"prediction": ''})
        else:
            binary_list = expand_sequence(hr_record_string)
            if len(binary_list) > 4:
                r_binary_list = list(reversed(binary_list))
                transition_matrix = calculate_transition_matrix(r_binary_list)
                current_state = binary_list[-1]  # Use the last value in the list as the current state
                predicted_state = predict_next_state(current_state, transition_matrix)
                x.update({"hr_prediction": predicted_state})
                predicted_value, probability = markov_monte_carlo(r_binary_list)
                x.update({"hr_mmp":predicted_value,"hr_mmpp":probability})
            else:
                x.update({"hr_prediction": ''})
        
        if h_record_string is None:
            # print('sorry')
            x.update({"prediction": ''})
        else:
            binary_list2 = expand_sequence(h_record_string)
            if len(binary_list2) > 4:
                r_binary_list2 = list(reversed(binary_list2))
                transition_matrix2 = calculate_transition_matrix(r_binary_list2)
                current_state2 = binary_list2[-1]  # Use the last value in the list as the current state
                predicted_state2 = predict_next_state(current_state2, transition_matrix2)
                x.update({"h_prediction":predicted_state2})
                predicted_value2, probability2 = markov_monte_carlo(r_binary_list2)
                x.update({"h_mmp":predicted_value2,"h_mmpp":probability2})
            else:
                x.update({"h_prediction":''})

        if rbi_record_string is None:
            # print('sorry')
            x.update({"prediction": ''})
        else:
            binary_list3 = expand_sequence(rbi_record_string)
            if len(binary_list3) > 4:
                r_binary_list3 = list(reversed(binary_list3))
                transition_matrix3 = calculate_transition_matrix(r_binary_list3)
                current_state3 = binary_list3[-1]  # Use the last value in the list as the current state
                predicted_state3 = predict_next_state(current_state3, transition_matrix3)
                x.update({"rbi_prediction":predicted_state3})
                predicted_value3, probability3 = markov_monte_carlo(r_binary_list3)
                x.update({"rbi_mmp":predicted_value3,"rbi_mmpp":probability3})                
            else:
                x.update({"rbi_prediction":''})

            
        
    return sequence_dict

def analyze_sequence_and_predict3(sequence_dict):
    for x in sequence_dict:
        hr_record_string = x.get("all_HR_record")
        h_record_string = x.get("all_H_record")
        rbi_record_string = x.get("all_RBI_record")
        if hr_record_string is None:
            # print('sorry')
            x.update({"prediction": ''})

        else:
            binary_list = expand_sequence(hr_record_string)
            r_binary_list = list(reversed(binary_list))
            if binary_list:  # Check if the list is not empty
                transition_matrix = calculate_transition_matrix(r_binary_list)
                current_state = binary_list[-1]  # Use the last value in the list as the current state
                predicted_state = predict_next_state(current_state, transition_matrix)
                x.update({"hr_prediction": predicted_state})
                predicted_value, probability = markov_monte_carlo(r_binary_list)
                x.update({"hr_mmp":predicted_value,"hr_mmpp":probability})     
            else:
                # Handle the case where the list is empty
                # current_state = None  # Or any default value you want to use
                print("Warning: binary_list is empty. Setting current_state to None.")
                x.update({"hr_prediction": ''})
        if h_record_string is None:
            # print('sorry')
            x.update({"prediction": ''})
        else:
            binary_list2 = expand_sequence(h_record_string)
            r_binary_list2 = list(reversed(binary_list2))
            if binary_list2:
                transition_matrix2 = calculate_transition_matrix(r_binary_list2)
                current_state2 = binary_list2[-1]  # Use the last value in the list as the current state
                predicted_state2 = predict_next_state(current_state2, transition_matrix2)
                x.update({"h_prediction":predicted_state2})
                predicted_value2, probability2 = markov_monte_carlo(r_binary_list2)
                x.update({"h_mmp":predicted_value2,"h_mmpp":probability2})
            else:
                x.update({"h_prediction": '',"h_mmp":'', "h_mmpp":''})
        if rbi_record_string is None:
            # print('sorry')
            x.update({"prediction": ''})
        else:
            binary_list3 = expand_sequence(rbi_record_string)
            r_binary_list3 = list(reversed(binary_list3))
            if binary_list3:
                transition_matrix3 = calculate_transition_matrix(r_binary_list3)
                current_state3 = binary_list3[-1]  # Use the last value in the list as the current state
                predicted_state3 = predict_next_state(current_state3, transition_matrix3)
                x.update({"rbi_prediction":predicted_state3})
                predicted_value3, probability3 = markov_monte_carlo(r_binary_list3)
                x.update({"rbi_mmp":predicted_value3,"rbi_mmpp":probability3})                 
            else:
                x.update({"rbi_prediction": '', "rbi_mmp":'', "rbi_mmpp":''})
    return sequence_dict

def generate_pitcher_html_table(pitcher_data):
    """
    Converts pitcher data (list of dictionaries) into an HTML table.

    Args:
        pitcher_data (list): A list of dictionaries containing pitcher data.

    Returns:
        str: An HTML string representing the pitcher table.
    """
    if not pitcher_data:
        return "<h2>Pitcher Data</h2><p>No data available</p>"

    # Extract headers from the keys of the first dictionary
    # headers = pitcher_data[0].keys()
    headers = [
        "RBI",
        "H",
        "HR",
        "Name",
        "Team",
        "ERA",
        "SO9",
        "SP",
        "Hp9",
        "HRp9"
    ]

    # Start the HTML table
    html = "<table border='1'>\n<tr>"
    html += "".join(f"<th>{header}</th>" for header in headers)
    html += "</tr>\n"

    # Add rows for each dictionary
    for row in pitcher_data:
        html += "<tr>"
        # html += "".join(f"<td>{row.get(header, '')}</td>" for header in headers)
        html += f"<td><input type='checkbox'></td>"
        html += f"<td><input type='checkbox'></td>"
        html += f"<td><input type='checkbox'></td>"
        html += f"<td>{row.get("pitcher", '')}</td>"
        html += f"<td>{row.get("pitchers_team", '')}</td>"
        html += f"<td>{row.get("ERA", '')}</td>"
        html += f"<td>{row.get("SO9", '')}</td>"
        html += f"<td>{row.get('stats',{"stats":{}}).get("strikePercentage", '')}</td>"
        html += f"<td>{row.get('stats',{"stats":{}}).get("hitsPer9Inn", '')}</td>"
        html += f"<td>{row.get('stats',{"stats":{}}).get("homeRunsPer9", '')}</td>"
        html += "</tr>\n"

    html += "</table>\n"
    return html

# def generate_batter_html_table(batter_data, schedule_data, ball_park_data):
#     """
#     Converts batter data (list of dictionaries) into three HTML tables.

#     Args:
#         batter_data (list): A list of dictionaries containing batter data.

#     Returns:
#         str: An HTML string representing the batter tables.
#     """
#     if not batter_data:
#         return "<h2>Batter Data</h2><p>No data available</p>"
#     if not ball_park_data:
#         return "<h2>Team Data</h2><p>No data available</p>"
#     if not schedule_data:
#         return "<h2>Team Data</h2><p>No data available</p>"

#     for a in ball_park_data:
#         stadium = a.get('Stadium')
#         if stadium == 'Guaranteed Rate Field':
#             a.update({'Stadium': 'Rate Field'})
#         elif stadium == 'Minute Maid Park':
#             a.update({'Stadium': 'Daikin Park'})

#     for x in batter_data:
#         team_id = x.get('team_id')
#         for y in schedule_data:
#             away_id = y.get('away_id')
#             home_id = y.get('home_id')
#             if team_id == away_id:
#                 venue = y.get('venue_name')
#                 for z in ball_park_data:
#                     venue_name = z.get('Stadium')
#                     venue_hr = z.get('HR')
#                     if venue == venue_name:
#                         x.update({"venue": f"{venue} <b>({venue_hr})</b>"})
#             elif team_id == home_id:
#                 venue = y.get('venue_name')
#                 for z in ball_park_data:
#                     venue_name = z.get('Stadium')
#                     venue_hr = z.get('HR')
#                     if venue == venue_name:
#                         x.update({"venue": f"{venue} <b>({venue_hr})</b>"})

#     analyzed_batter_data = analyze_sequence_and_predict2(batter_data)

#     # Define headers for each table
#     headers1 = [
#         "RBI", "H", "HR", "Name", "Team", "Pos", "Venue", "GP", "HR", "HRpg",
#         "fHRpg", "HR24", "HR24pg", "fHR24pg", "HRmc?", "HRmmc?", "HRmmc%?", "HR_record"
#     ]
#     headers2 = [
#         "RBI", "H", "HR", "Name", "Team", "Pos", "Venue", "GP", "H", "Hpg",
#         "fHpg", "Hmc?", "Hmmc?", "Hmmc%?", "H_record"
#     ]
#     headers3 = [
#         "RBI", "H", "HR", "Name", "Team", "Pos", "Venue", "GP", "RBIpg", "fRBIpg",
#         "RBI", "RBImc?", "RBImmc?", "RBImmc%?", "RBI_record"
#     ]

#     # Helper function to generate a table
#     def generate_table(headers, data):
#         html = "<table border='1'>\n<tr>"
#         html += "".join(f"<th>{header}</th>" for header in headers)
#         html += "</tr>\n"
#         for row in data:
#             html += "<tr>"
#             for header in headers:
#                 value = row.get(header, '')
#                 if isinstance(value, float):
#                     value = round(value, 2)
#                 html += f"<td>{value}</td>"
#             html += "</tr>\n"
#         html += "</table>\n"
#         return html

#     # Generate the three tables
#     table1 = generate_table(headers1, analyzed_batter_data)
#     table2 = generate_table(headers2, analyzed_batter_data)
#     table3 = generate_table(headers3, analyzed_batter_data)

#     # Combine the tables into a single HTML string
#     html = f"<h2>Table 1</h2>\n{table1}"
#     html += f"<h2>Table 2</h2>\n{table2}"
#     html += f"<h2>Table 3</h2>\n{table3}"

#     return html
def generate_batter_html_table(batter_data, schedule_data, ball_park_data):
    """
    Converts batter data (list of dictionaries) into an HTML table.

    Args:
        batter_data (list): A list of dictionaries containing batter data.

    Returns:
        str: An HTML string representing the batter table.
    """
    if not batter_data:
        return "<h2>Batter Data</h2><p>No data available</p>"
    if not ball_park_data:
        return "<h2>Team Data</h2><p>No data available</p>"
    if not schedule_data:
        return "<h2>Team Data</h2><p>No data available</p>"

    for a in ball_park_data:
        stadium = a.get('Stadium')
        if stadium == 'Guaranteed Rate Field':
            a.update({'Stadium': 'Rate Field'})
        elif stadium == 'Minute Maid Park':
            a.update({'Stadium': 'Daikin Park'})

    for x in batter_data:
        team_id = x.get('team_id')
        for y in schedule_data:
            away_id = y.get('away_id')
            home_id = y.get('home_id')
            if team_id == away_id:
                venue = y.get('venue_name')
                for z in ball_park_data:
                    venue_name = z.get('Stadium')
                    venue_hr = z.get('HR')
                    if venue == venue_name:
                        x.update({"venue":f"{venue} <b>({venue_hr})</b>"})
            elif team_id == home_id:
                venue = y.get('venue_name')
                for z in ball_park_data:
                    venue_name = z.get('Stadium')
                    venue_hr = z.get('HR')
                    if venue == venue_name:
                        x.update({"venue":f"{venue} <b>({venue_hr})</b>"})

    analyzed_batter_data = analyze_sequence_and_predict2(batter_data)

    # Extract headers from the keys of the first dictionary
    # headers = batter_data[0].keys()
    headers = [
        "RBI",
        "H",
        "HR",
        "Name",
        "Team",
        "GP",
        "HR",
        "HR24",
        "HR_record",
        "GP",
        "H",
        "Hpg",
        "H_record",
        "GP",
        "RBI",
        "RBIpg",
        "RBI_record"
    ]

    # Start the HTML table
    html2 = "<table border='1'>\n<tr>"
    html2 += "".join(f"<th>{header}</th>" for header in headers)
    html2 += "</tr>\n"

    # Add rows for each dictionary
    for row in analyzed_batter_data:
        html2 += "<tr>"
        html2 += f"<td><input type='checkbox'></td>"
        html2 += f"<td><input type='checkbox'></td>"
        html2 += f"<td><input type='checkbox'></td>"
        html2 += f"<td>{row.get("player_name", '')}</td>"
        html2 += f"<td>{row.get("team", '')}</td>"
        html2 += f"<td>{int(row.get("games_played", ''))}</td>"
        html2 += f"<td>{int(row.get("HR", 0))}</td>"
        html2 += f"<td>{int(row.get("HR24", 0))}</td>"
        html2 += f"<td>{row.get("HR_record", '')[:42]}</td>"
        html2 += f"<td>{int(row.get("games_played", ''))}</td>"
        html2 += f"<td>{int(row.get("H", 0))}</td>"
        html2 += f"<td>{row.get("Hpg", '')}</td>"
        html2 += f"<td>{row.get("H_record", '')[:42]}</td>"
        html2 += f"<td>{int(row.get("games_played", ''))}</td>"
        html2 += f"<td>{int(row.get("RBI", 0))}</td>"
        html2 += f"<td>{row.get("RBIpg", '')}</td>"
        html2 += f"<td>{row.get("RBI_record", '')[:42]}</td>"
        html2 += "</tr>\n"
    html2 += "</table>\n"

    html = f"<h2 id='HR'>Player Stats</h2>\n{html2}"
    return html2

def get_pitcher_name_era(pitcher_name: str,
                         pitcher_file: str = "data/pitcher_data.json") -> str:
    """
    Return "PitcherName ERA" for the first matching pitcher in pitcher_data.json.

    Matching:
      - Case-insensitive exact match on the 'pitcher' field first.
      - If no exact match, tries case-insensitive startswith.
      - If still none, returns "".

    Args:
        pitcher_name: Name to look up.
        pitcher_file: Path to pitcher JSON file.

    Returns:
        str like "Garrett Crochet 2.38" or "" if not found.
    """
    if not pitcher_name:
        return ""
    try:
        with open(pitcher_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return ""

    if not isinstance(data, list):
        return ""

    name_lc = pitcher_name.strip().lower()

    # 1. Exact (case-insensitive)
    for entry in data:
        if isinstance(entry, dict) and entry.get("pitcher","").strip().lower() == name_lc:
            return f"{entry.get('pitcher','').strip()} {entry.get('ERA','').strip()}"

    # 2. Startswith fallback
    for entry in data:
        p = entry.get("pitcher","")
        if isinstance(entry, dict) and p.lower().startswith(name_lc):
            return f"{p.strip()} {entry.get('ERA','').strip()}"

    return ""

def generate_bvp_html_table(bvp_data, schedule_data, ball_park_data):
    """
    Converts batter-vs-pitcher (BvP) data into an HTML table.

    Args:
        bvp_data (list): A list of dictionaries containing BvP data.

    Returns:
        str: An HTML string representing the BvP table.
    """
    if not bvp_data:
        return "<h2>BvP Data</h2><p>No data available</p>"
    if not ball_park_data:
        return "<h2>Team Data</h2><p>No data available</p>"
    if not schedule_data:
        return "<h2>Team Data</h2><p>No data available</p>"

    for a in ball_park_data:
        stadium = a.get('Stadium')
        if stadium == 'Guaranteed Rate Field':
            a.update({'Stadium': 'Rate Field'})
        elif stadium == 'Minute Maid Park':
            a.update({'Stadium': 'Daikin Park'})

    for x in bvp_data:
        team_id = x.get('batter_team_id')
        for y in schedule_data:
            away_id = y.get('away_id')
            home_id = y.get('home_id')
            if team_id == away_id:
                venue = y.get('venue_name')
                for z in ball_park_data:
                    venue_name = z.get('Stadium')
                    venue_hr = z.get('HR')
                    if venue == venue_name:
                        x.update({"venue":f"{venue} <b>({venue_hr})</b>"})
            elif team_id == home_id:
                venue = y.get('venue_name')
                for z in ball_park_data:
                    venue_name = z.get('Stadium')
                    venue_hr = z.get('HR')
                    if venue == venue_name:
                        x.update({"venue":f"{venue} <b>({venue_hr})</b>"})

    analyzed_bvp_data = analyze_sequence_and_predict3(bvp_data)

    # Extract headers from the keys of the first dictionary
    # headers = bvp_data[0].keys()
    headers1 = [
        "RBI",
        "H",
        "HRS",
        "Batter",
        "Team",
        "Pitcher",
        "Venue",
        "AB",
        "H",
        "HR",
        "AVG",
        "RBI",
        "OBP",
        "OPS",
        "HR25",
        "HR24",
        "a0g",
        "a0g%",
        "HR Record",
        "AB",
        "H",
        "AVG",
        "H25",
        "Hpg25",
        "Hits Record",
        "AB",
        "AVG",
        "RBI",
        "RBI25",
        "RBIpg25",
        "RBIs Record",
    ]

    # Start the HTML table
    html1 = "<table border='1'>\n<tr>"
    html1 += "".join(f"<th>{header}</th>" for header in headers1)
    html1 += "</tr>\n"

    # Add rows for each dictionary
    for row in analyzed_bvp_data:
        html1 += "<tr>"
        html1 += f"<td><input type='checkbox'></td>"
        html1 += f"<td><input type='checkbox'></td>"
        html1 += f"<td><input type='checkbox'></td>"
        html1 += f"<td>{row.get("batter", '')}</td>"
        html1 += f"<td>{row.get("batter_team", '')}</td>"
        html1 += f"<td>{get_pitcher_name_era(row.get("pitcher", ''))}</td>"
        html1 += f"<td>{extract_first_int(row.get("venue", ''))}</td>"
        html1 += f"<td>{row.get('bvp_stats').get("atbats", '')}</td>"
        html1 += f"<td>{row.get('bvp_stats').get("hits", '')}</td>"
        html1 += f"<td>{row.get('bvp_stats').get("homeruns", '')}</td>"
        html1 += f"<td>{row.get('bvp_stats').get("avg", '')}</td>"
        html1 += f"<td>{row.get('bvp_stats').get("rbi", '')}</td>"
        html1 += f"<td>{row.get('bvp_stats').get("obp", '')}</td>"
        html1 += f"<td>{row.get('bvp_stats').get("ops", '')}</td>"
        html1 += f"<td>{int(row.get("all_HR", 0))}</td>"
        html1 += f"<td>{row.get("all_HR24", '')}</td>"
        html1 += f"<td>{round(float(row.get("all_HR_analysis", {}).get("avg_zero_gap", 0)),3)}</td>"
        html1 += f"<td>{round(float(row.get("all_HR_analysis", {}).get("cv_zero_gap", 0)),3)}</td>"
        html1 += f"<td>{row.get("all_HR_record", '')[:42]}</td>"
        html1 += f"<td>{row.get('bvp_stats').get("atbats", '')}</td>"
        html1 += f"<td>{row.get('bvp_stats').get("hits", '')}</td>"
        html1 += f"<td>{row.get('bvp_stats').get("avg", '')}</td>"
        html1 += f"<td>{int(row.get("all_H", 0))}</td>"
        html1 += f"<td>{row.get("all_Hpg", '')}</td>"
        html1 += f"<td>{row.get("all_H_record", '')[:42]}</td>"
        html1 += f"<td>{row.get('bvp_stats').get("atbats", '')}</td>"
        html1 += f"<td>{row.get('bvp_stats').get("avg", '')}</td>"
        html1 += f"<td>{row.get('bvp_stats').get("rbi", '')}</td>"
        html1 += f"<td>{int(row.get("all_RBI", 0))}</td>"
        html1 += f"<td>{row.get("all_RBIpg", '')}</td>"
        html1 += f"<td>{row.get("all_RBI_record", '')[:42]}</td>"
        html1 += "</tr>\n"
    html1 += "</table>\n"

    return html1

def generate_dh_batter_html_table(dh_batter_data, schedule_data, ball_park_data):
    """
    Converts designated hitter (DH) batter data into an HTML table.

    Args:
        dh_batter_data (list): A list of dictionaries containing DH batter data.

    Returns:
        str: An HTML string representing the DH batter table.
    """
    if not dh_batter_data:
        return "<h2>DH Batter Data</h2><p>No data available</p>"
    if not ball_park_data:
        return "<h2>Team Data</h2><p>No data available</p>"
    if not schedule_data:
        return "<h2>Team Data</h2><p>No data available</p>"

    for a in ball_park_data:
        stadium = a.get('Stadium')
        if stadium == 'Guaranteed Rate Field':
            a.update({'Stadium': 'Rate Field'})
        elif stadium == 'Minute Maid Park':
            a.update({'Stadium': 'Daikin Park'})

    for x in dh_batter_data:
        team_id = x.get('team_id')
        for y in schedule_data:
            away_id = y.get('away_id')
            home_id = y.get('home_id')
            if team_id == away_id:
                venue = y.get('venue_name')
                for z in ball_park_data:
                    venue_name = z.get('Stadium')
                    venue_hr = z.get('HR')
                    if venue == venue_name:
                        x.update({"venue":f"{venue} <b>({venue_hr})</b>"})
            elif team_id == home_id:
                venue = y.get('venue_name')
                for z in ball_park_data:
                    venue_name = z.get('Stadium')
                    venue_hr = z.get('HR')
                    if venue == venue_name:
                        x.update({"venue":f"{venue} <b>({venue_hr})</b>"})

    analyzed_dh_batter_data = analyze_sequence_and_predict2(dh_batter_data)
    # Extract headers from the keys of the first dictionary
    # headers = dh_batter_data[0].keys()
    headers = [
        "RBI",
        "H",
        "HR",
        "Name",
        "Team",
        "venue",
        "GP",
        "HR",
        "HRpg",
        "fHRpg",
        "HR24",
        "HR24pg",
        "fHR24pg",
        "HR record",
        "HRmc?",
        "HRmmc?",
        "HRmmc%?",
        "H",
        "Hpg",
        "fHpg",
        "H record",
        "Hmc?",
        "Hmmc?",
        "Hmmc%?",
        "RBI",
        "RBIpg",
        "fRBIpg",
        "RBImc?",
        "RBImmc?"
        "RBImmc%?"
        "RBI_record"
    ]

    # Start the HTML table
    html = "<table border='1'>\n<tr>"
    html += "".join(f"<th>{header}</th>" for header in headers)
    html += "</tr>\n"

    # Add rows for each dictionary
    for row in analyzed_dh_batter_data:
        html += "<tr>"
        # html += "".join(f"<td>{row.get(header, '')}</td>" for header in headers)
        html += f"<td><input type='checkbox'></td>"
        html += f"<td><input type='checkbox'></td>"
        html += f"<td><input type='checkbox'></td>"
        html += f"<td>{row.get("player_name", '')}</td>"
        html += f"<td>{row.get("team", '')}</td>"
        html += f"<td>{row.get("venue", '')}</td>"
        html += f"<td>{int(row.get("games_played", ''))}</td>"
        html += f"<td>{int(row.get("HR", ''))}</td>"
        html += f"<td>{row.get("HRpg", '')}</td>"
        html += f"<td>{row.get("fHRpg", '')}</td>"
        html += f"<td>{row.get("HR24", '')}</td>"
        html += f"<td>{row.get("HR24pg", '')}</td>"
        html += f"<td>{row.get("fHR24pg", '')}</td>"
        html += f"<td>{row.get("hr_prediction", '')}</td>"
        html += f"<td>{row.get("hr_mmp", '')}</td>"
        value = row.get("hr_mmpp", '')
        html += f"<td>{round(float(value), 2) if value else ''}</td>"
        # html += f"<td>{round(float(row.get("hr_mmpp", '')),2)}</td>"
        html += f"<td>{row.get("HR_record", '')}</td>"
        html += f"<td>{row.get("H", '')}</td>"
        html += f"<td>{row.get("Hpg", '')}</td>"
        html += f"<td>{row.get("fHpg", '')}</td>"
        html += f"<td>{row.get("h_prediction", '')}</td>"
        html += f"<td>{row.get("h_mmp", '')}</td>"
        value2 = row.get("h_mmpp", '')
        html += f"<td>{round(float(value2), 2) if value2 else ''}</td>"
        # html += f"<td>{round(float(row.get("h_mmpp", '')),2)}</td>"
        html += f"<td>{row.get("H_record", '')}</td>"
        html += f"<td>{row.get("RBI", '')}</td>"
        html += f"<td>{row.get("RBIpg", '')}</td>"
        html += f"<td>{row.get("fRBIpg", '')}</td>"
        html += f"<td>{row.get("rbi_prediction", '')}</td>"
        html += f"<td>{row.get("rbi_mmp", '')}</td>"
        value3 = row.get("rbi_mmpp", '')
        html += f"<td>{round(float(value3), 2) if value3 else ''}</td>"
        # html += f"<td>{round(float(row.get("rbi_mmpp", '')),2)}</td>"
        html += f"<td>{row.get("RBI_record", '')}</td>"
        html += "</tr>\n"

    html += "</table>\n"
    return html

def generate_team_list_html_table(team_list):
    """
    Converts team list data (list of dictionaries) into an HTML table.

    Args:
        team_list (list): A list of dictionaries containing team data.

    Returns:
        str: An HTML string representing the teams list table.
    """
    if not team_list:
        return "<h2>Team List Data</h2><p>No data available</p>"

    # Extract headers from the keys of the first dictionary
    # headers = pitcher_data[0].keys()
    headers = [
        "filter",
        "Team"
    ]

    # Start the HTML table
    html = "<table border='1'>\n<tr>"
    html += "".join(f"<th>{header}</th>" for header in headers)
    html += "</tr>\n"

    # Add rows for each dictionary
    for row in team_list:
        html += "<tr>"
        # html += "".join(f"<td>{row.get(header, '')}</td>" for header in headers)
        html += f"<td><input type='radio'></td>"
        html += f"<td>{row.get("team_name", '')}</td>"
        html += "</tr>\n"

    html += "</table>\n"
    return html

def generate_team_html_table(team_data, ball_park_data, schedule_data):
    """
    Converts team data into an HTML table.

    Args:
        team_data (list): A list of dictionaries containing team data.

    Returns:
        str: An HTML string representing the team table.
    """
    if not team_data:
        return "<h2>Team Data</h2><p>No data available</p>"
    if not ball_park_data:
        return "<h2>Team Data</h2><p>No data available</p>"
    if not schedule_data:
        return "<h2>Team Data</h2><p>No data available</p>"

    for a in ball_park_data:
        stadium = a.get('Stadium')
        if stadium == 'Guaranteed Rate Field':
            a.update({'Stadium': 'Rate Field'})
        elif stadium == 'Minute Maid Park':
            a.update({'Stadium': 'Daikin Park'})
            
    new_holder_of_dicts = []
    for x in team_data:
        dict1 = {}
        team_id = x.get('team_id')
        team_name = x.get('team_name')
        team_record = x.get('team_record')
        dict1.update({
            "team_id": team_id,
            "team_record": team_record
        })
        for y in schedule_data:
            away_id = y.get('away_id')
            home_id = y.get('home_id')
            if team_id == away_id:
                vs_team = y.get('home_name')
                series_info = y.get("series_status")
                # print(vs_team)
                dict1.update({"team_name":f"{team_name}"})
                dict1.update({"vs_team": f"{vs_team} (<b>home</b>)"})
                dict1.update({"series_info":y.get("series_status")})
                venue = y.get('venue_name')
                for z in ball_park_data:
                    venue_name = z.get('Stadium')
                    venue_hr = z.get('HR')
                    if venue == venue_name:
                        dict1.update({"venue":f"{venue} <b>({venue_hr})</b>"})
            elif team_id == home_id:
                vs_team = y.get('away_name')
                series_info = y.get("series_status")
                # print(vs_team)
                dict1.update({"team_name":f"{team_name}"})
                dict1.update({"vs_team": f"{vs_team} (<b>away</b>)"})
                dict1.update({"series_info":y.get("series_status")})
                venue = y.get('venue_name')
                for z in ball_park_data:
                    venue_name = z.get('Stadium')
                    venue_hr = z.get('HR')
                    if venue == venue_name:
                        dict1.update({"venue":f"{venue} <b>({venue_hr})</b>"})
        new_holder_of_dicts.append(dict1)

    processed_new_holder_of_dicts = analyze_team_dict(new_holder_of_dicts)

    # Extract headers from the keys of the first dictionary
    # headers = team_data[0].keys()
    headers = [
        "Win",
        "Loss",
        "Team",
        "vs_Team",
        "Series",
        "Venue",
        "WLmc?",
        "WLmmc?",
        "WLmmc%?",
        "Team Record"
    ]

    # Start the HTML table
    html = "<table border='1'>\n<tr>"
    html += "".join(f"<th>{header}</th>" for header in headers)
    html += "</tr>\n"

    # Add rows for each dictionary
    for row in processed_new_holder_of_dicts:
        html += "<tr>"
        html += f"<td><input type='checkbox'></td>"
        html += f"<td><input type='checkbox'></td>"
        html += f"<td>{row.get("team_name", '')}</td>"
        html += f"<td>{row.get("vs_team", '')}</td>"
        html += f"<td>{row.get("series_info", '')}</td>"
        html += f"<td>{row.get("venue", '')}</td>"
        html += f"<td>{row.get("prediction", '')}</td>"
        html += f"<td>{row.get("wl_mmp", '')}</td>"
        value1 = row.get("wl_mmpp", '')
        html += f"<td>{round(float(value1), 2) if value1 else ''}</td>"
        # html += f"<td>{round(float(row.get("wl_mmpp", '')),2)}</td>"
        html += f"<td>{row.get("team_record", '')}</td>"
        html += "</tr>\n"

    html += "</table>\n"
    return html

def generate_yesterday_home_run_html_table(yesterday_home_run_data):
    """
    Converts yesterdays home run data into an HTML table.

    Args:
        yesterday_home_run_data (list): A list of dictionaries containing yesterdays home run data.

    Returns:
        str: An HTML string representing the yesterdays home run table.
    """
    if not yesterday_home_run_data:
        return "<h2>Yesterdays Home Run Data</h2><p>No data available</p>"

    # analyze data
    home_run_data = analyze_sequence_and_predict(yesterday_home_run_data)

    # Extract headers from the keys of the first dictionary
    # headers = ballpark_data[0].keys()
    headers = [
        "RBI",
        "H",
        "HR",
        "Batter",
        "Team",
        "HR",
        "HRpg",
        "fHRpg",
        "HR24",
        "HR24pg",
        "fHR24pg",
        "HRmc?",
        "HRmmc?",
        "HRmmc%?",
        "HR_record only shows if they are playing today"
    ]

    # Start the HTML table
    html = "<table border='1'>\n<tr>"
    # Table Headers
    html += "".join(f"<th>{header}</th>" for header in headers)
    html += "</tr>\n"

    # Add rows for each dictionary
    for row in home_run_data:
        html += "<tr>"
        html += f"<td><input type='checkbox'></td>"
        html += f"<td><input type='checkbox'></td>"
        html += f"<td><input type='checkbox'></td>"
        html += f"<td>{row.get("name", '')}</td>"
        html += f"<td>{row.get("team", '')}</td>"
        html += f"<td>{row.get("HR", '')}</td>"
        html += f"<td>{row.get("HRpg", '')}</td>"
        html += f"<td>{row.get("fHRpg", '')}</td>"
        html += f"<td>{row.get("HR24", '')}</td>"
        html += f"<td>{row.get("HR24pg", '')}</td>"
        html += f"<td>{row.get("fHR24pg", '')}</td>"
        html += f"<td>{row.get("prediction", '')}</td>"
        html += f"<td>{row.get("hr_mmp", '')}</td>"
        value2 = row.get("hr_mmpp", '')
        html += f"<td>{round(float(value2), 2) if value2 else ''}</td>"
        # html += f"<td>{round(float(row.get("hr_mmpp", '')),2)}</td>"
        html += f"<td>{row.get("HR_record", '')}</td>"
        html += "</tr>\n"

    html += "</table>\n"
    return html

def generate_leaders_table(leader_data1, leader_data2, leader_data3):
    """
    Generates three HTML tables for league leaders based on the keys in each dict in the list of dicts.

    Args:
        leader_data1 (list): List of dicts for the first leader category.
        leader_data2 (list): List of dicts for the second leader category.
        leader_data3 (list): List of dicts for the third leader category.

    Returns:
        str: HTML string containing three tables.
    """
    def make_table(data, title):
        if not data or not isinstance(data, list) or not data[0]:
            return f"<h3>{title}</h3><p>No data available</p>"
        headers = data[0].keys()
        html = f"<h3>{title}</h3><table border='1'><tr>"
        html += "".join(f"<th>{h}</th>" for h in headers)
        html += "</tr>\n"
        for row in data:
            html += "<tr>"
            html += "".join(f"<td>{row.get(h, '')}</td>" for h in headers)
            html += "</tr>\n"
        html += "</table>\n"
        return html

    html = ""
    html += make_table(leader_data3, "HR")
    html += make_table(leader_data1, "ERA")
    html += make_table(leader_data2, "SO9")
    return html

def merge_team_data(team_data_1, team_data_2):
    """
    Merges information from the first list of dictionaries into the second list of dictionaries
    based on matching team names.

    Args:
        team_data_1 (list): The first list of dictionaries containing additional team information.
        team_data_2 (list): The second list of dictionaries to be updated with information from the first.

    Returns:
        list: The updated second list of dictionaries with merged information.
    """
    # Create a lookup dictionary for team_data_1 based on team names
    team_data_1_lookup = {team["Team"]: team for team in team_data_1}

    # Iterate through team_data_2 and merge data if team names match
    for team in team_data_2:
        team_name = team.get("team_name")
        if team_name in team_data_1_lookup:
            # Merge the matching dictionary from team_data_1 into the current team in team_data_2
            team.update(team_data_1_lookup[team_name])

    return team_data_2


import math
from collections import Counter
from typing import Dict, Any, List

def analyze_score_sequence(seq: str, latest_first: bool = True) -> Dict[str, Any]:
    """
    Analyze a hyphen-separated sequence of integer scores.
    seq example: "0-1-0-0-2-0-1-"
    latest_first=True means first element is most recent; will reverse for chronological analysis.
    Returns a dictionary of metrics.
    """
    # Clean + parse
    parts = [p for p in seq.strip("-").split("-") if p != ""]
    scores: List[int] = [int(p) for p in parts]
    if latest_first:
        scores = list(reversed(scores))  # chronological (oldest -> newest)

    n = len(scores)
    if n == 0:
        return {"error": "empty sequence"}

    # Basic counts
    ctr = Counter(scores)
    total = n
    zeros = ctr.get(0, 0)
    ones = ctr.get(1, 0)
    gt1 = sum(v for k, v in ctr.items() if k > 1)

    # Probabilities
    p0 = zeros / total
    p1 = ones / total
    pgt1 = gt1 / total
    mean_score = sum(scores) / total
    var_score = sum((x - mean_score) ** 2 for x in scores) / total
    std_score = math.sqrt(var_score)

    # Run-lengths of zeros (gaps between non-zero scores)
    zero_gaps = []
    current_gap = 0
    for s in scores:
        if s == 0:
            current_gap += 1
        else:
            zero_gaps.append(current_gap)
            current_gap = 0
    # If sequence ends with zeros, record trailing gap
    zero_gaps.append(current_gap)
    zero_gaps = [g for g in zero_gaps if g is not None]  # keep zeros (they are meaningful)
    avg_zero_gap = sum(zero_gaps) / len(zero_gaps) if zero_gaps else 0
    cv_zero_gap = ( ( (sum((g - avg_zero_gap)**2 for g in zero_gaps)/len(zero_gaps)) ** 0.5 ) / avg_zero_gap
                   ) if avg_zero_gap > 0 and len(zero_gaps) > 1 else 0

    # Inter-arrival distances of any scoring event (score > 0)
    inter = []
    last_idx = None
    for idx, s in enumerate(scores):
        if s > 0:
            if last_idx is not None:
                inter.append(idx - last_idx)
            last_idx = idx
    avg_inter_scoring = sum(inter) / len(inter) if inter else None
    cv_inter_scoring = ( ( (sum((d - avg_inter_scoring)**2 for d in inter)/len(inter)) ** 0.5 ) / avg_inter_scoring
                        ) if inter and avg_inter_scoring and avg_inter_scoring > 0 and len(inter) > 1 else None

    # Entropy of score distribution
    entropy = -sum((c/total) * math.log2(c/total) for c in ctr.values())

    # Autocorrelation (lag 1..L)
    def autocorr(data: List[int], lag: int) -> float:
        if lag >= len(data):
            return 0.0
        mu = mean_score
        num = sum((data[i]-mu)*(data[i-lag]-mu) for i in range(lag, len(data)))
        den = sum((x-mu)**2 for x in data)
        return num / den if den else 0.0

    max_lag = min(20, n//4)
    autocorrs = {lag: autocorr(scores, lag) for lag in range(1, max_lag+1)}
    # Simple periodicity guess: strongest positive autocorr (excluding very small)
    lag_sorted = sorted(autocorrs.items(), key=lambda kv: kv[1], reverse=True)
    dominant_lag, dominant_corr = (lag_sorted[0] if lag_sorted else (None, None))
    periodic_like = dominant_corr is not None and dominant_corr > 0.25

    # Score >1 density spacing (inter-arrival for score>1)
    inter_gt1 = []
    last_idx = None
    for idx, s in enumerate(scores):
        if s > 1:
            if last_idx is not None:
                inter_gt1.append(idx - last_idx)
            last_idx = idx
    avg_inter_gt1 = sum(inter_gt1)/len(inter_gt1) if inter_gt1 else None

    # Pattern deviation: compare observed distribution of inter-arrival vs geometric expectation (score event probability)
    p_event = 1 - p0
    if p_event > 0 and inter:
        # Expected mean geometric gap (including zero-length): (1-p)/p
        expected_mean_gap = (1 - p_event) / p_event
        observed_mean_gap = avg_inter_scoring - 1 if avg_inter_scoring else None
        gap_mean_deviation = (observed_mean_gap - expected_mean_gap) if (observed_mean_gap is not None) else None
    else:
        gap_mean_deviation = None

    return {
        "total_games": total,
        "mean_score": mean_score,
        "std_score": std_score,
        "prob_0": p0,
        "prob_1": p1,
        "prob_>1": pgt1,
        "count_0": zeros,
        "count_1": ones,
        "count_>1": gt1,
        "entropy_bits": entropy,
        "avg_zero_gap": avg_zero_gap,
        "cv_zero_gap": cv_zero_gap,
        "avg_inter_scoring_distance": avg_inter_scoring,
        "cv_inter_scoring_distance": cv_inter_scoring,
        "avg_inter_>1_distance": avg_inter_gt1,
        "autocorrelations": autocorrs,
        "dominant_lag": dominant_lag,
        "dominant_lag_corr": dominant_corr,
        "periodic_like": periodic_like,
        "gap_mean_deviation_vs_geometric": gap_mean_deviation,
        "raw_zero_gaps_sample": zero_gaps[:10],
        "raw_inter_scoring_sample": inter[:10]
    }

def generate_team_analysis_string(all_team_data, team_history_data):
    """
    Generates a detailed analysis of team data as a formatted string.

    This method processes team data, including win/loss records, streak analysis, 
    and predictions, and returns the results as a single formatted string. 
    The output includes:
    - Team and opponent information
    - Venue details
    - Win/loss record and binary representation
    - Streak analysis (e.g., longest streaks, average streak lengths)
    - Current streak and predicted next outcome
    - Markov and Monte Carlo predictions
    - A text-based graph of streak distributions

    Args:
        team_data (list): A list of dictionaries containing team data. Each dictionary 
                          should include keys like 'Team', 'vs_Team', 'Venue', 
                          'Team Record', 'WLmc?', 'WLmmc?', and 'WLmmc%?'.

    Returns:
        str: A formatted string containing the analysis for all teams.
    """

    # merge team data
    team_data = merge_team_data(all_team_data, team_history_data)

    output = []
    for x in team_data:
        # Convert to 1's and 0's
        list1 = string_to_binary_list(x.get('Team Record'))
        # Count the list
        list_counts = analyze_binary_list(list1)
        # Find streaks in data
        streaks = find_streaks_with_analysis(list1)
        # Analyze all found streaks for specific info
        streak_data = analyze_streaks(streaks.get('streaks'))
        # Detect the current streak and predict
        sequence = reverse_list(list1)
        stats = {
            "longest_win_streak": streak_data.get('longest_win_streak'),
            "average_win_streak_length": streak_data.get('average_win_streak_length'),
            "longest_lose_streak": streak_data.get('longest_lose_streak'),
            "average_lose_streak_length": streak_data.get('average_lose_streak_length'),
        }
        current_streak, amount = detect_current_streak(sequence)
        current_streak_s = "W" if current_streak == 1 else "L"
        predicted_outcome = predict_streak_continuation((current_streak, amount), stats)
        text_graph = text_streak_distribution(streaks.get('streaks'))

        # NAME
        output.append(f"<b>{x.get('Team')}</b>")
        # Today's game info
        output.append(f"{x.get('Team')} vs {x.get('vs_Team')}")
        output.append(f"{x.get('Venue')}")
        # Print name and record
        output.append(f"Record: {x.get('Team Record')[:45]} ... etc")
        output.append(f"Games Played: {list_counts.get('trials')}, Wins: {list_counts.get('success')}, Losses: {list_counts.get('failures')}, Win Percentage: {round(list_counts.get('success') / list_counts.get('trials'), 2)}%")
        # Print a graph
        output.append(text_graph)
        output.append("-" * 50)
        # Print out found data
        # for key, value in streak_data.items():
        #     # output.append(f"{key}{':':<40}{value:<10}")
        #     output.append(f"{key + ':':<40}{value:<10}")
        output.append(f"{'number of win streaks':<40}{streak_data.get('number_of_win_streaks'):<10}")
        # output.append(f"{streak_data.get('longest_win_streak')}")
        output.append(f"{'average win streak length':<40}{streak_data.get('average_win_streak_length'):<10}")
        # output.append(f"{streak_data.get('occurrences_of_longest_win_streaks')}")
        # output.append(f"{streak_data.get('shortest_win_streak')}")
        # output.append(f"{streak_data.get('occurrences_of_shortest_win_streaks')}")
        output.append(f"{'number of lose streaks':<40}{streak_data.get('number_of_lose_streaks'):<10}")
        # output.append(f"{streak_data.get('longest_lose_streak')}")
        output.append(f"{'average lose streak length':<40}{streak_data.get('average_lose_streak_length'):<10}")
        # output.append(f"{streak_data.get('occurrences_of_longest_lose_streaks')}")
        # output.append(f"{streak_data.get('shortest_lose_streak')}")
        # output.append(f"{streak_data.get('occurrences_of_shortest_lose_streaks')}")
        output.append(f"{'Current Streak:':<40}{current_streak_s}, {amount}")
        output.append(f"{'Predicted Next Outcome:':<40}{'W' if predicted_outcome == 1 else 'L':<10}")
        # Markov / Monte Carlo
        output.append(f"{'markov prediction:':<40}{x.get('WLmc?'):<10}")
        output.append(f"{'markov monte carlo:':<40}{x.get('WLmmc?'):<10}")
        output.append(f"{'markov monte carlo certainty:':<40}{x.get('WLmmc%?'):<10}\n\n")

    return "\n".join(output)


def merge_team_data(team_data_1, team_data_2):
    """
    Merges information from the first list of dictionaries into the second list of dictionaries
    based on matching team names.

    Args:
        team_data_1 (list): The first list of dictionaries containing additional team information.
        team_data_2 (list): The second list of dictionaries to be updated with information from the first.

    Returns:
        list: The updated second list of dictionaries with merged information.
    """
    # Create a lookup dictionary for team_data_1 based on team names
    team_data_1_lookup = {team["Team"]: team for team in team_data_1}

    # Iterate through team_data_2 and merge data if team names match
    for team in team_data_2:
        team_name = team.get("team_name")
        if team_name in team_data_1_lookup:
            # Merge the matching dictionary from team_data_1 into the current team in team_data_2
            team.update(team_data_1_lookup[team_name])

    return team_data_2

def generate_team_analysis_dict(all_team_data, team_history_data):
    """
    Generates a detailed analysis of team data as a dictionary.

    This method processes team data, including win/loss records, streak analysis, 
    and predictions, and returns the results as a dictionary. 
    The output includes:
    - Team and opponent information
    - Venue details
    - Win/loss record and binary representation
    - Streak analysis (e.g., longest streaks, average streak lengths)
    - Current streak and predicted next outcome
    - Markov and Monte Carlo predictions
    - A text-based graph of streak distributions

    Args:
        all_team_data (list): A list of dictionaries containing team data.
        team_history_data (list): A list of dictionaries containing historical team data.

    Returns:
        dict: A dictionary containing the analysis for all teams.
    """

    # Merge team data
    team_data = merge_team_data(all_team_data, team_history_data)

    result = {}
    for x in team_data:
        # Convert to 1's and 0's
        list1 = string_to_binary_list(x.get('Team Record'))
        # Count the list
        list_counts = analyze_binary_list(list1)
        # Find streaks in data
        streaks = find_streaks_with_analysis(list1)
        # Analyze all found streaks for specific info
        streak_data = analyze_streaks(streaks.get('streaks'))
        # Detect the current streak and predict
        sequence = reverse_list(list1)
        stats = {
            "longest_win_streak": streak_data.get('longest_win_streak'),
            "average_win_streak_length": streak_data.get('average_win_streak_length'),
            "longest_lose_streak": streak_data.get('longest_lose_streak'),
            "average_lose_streak_length": streak_data.get('average_lose_streak_length'),
        }
        current_streak, amount = detect_current_streak(sequence)
        current_streak_s = "W" if current_streak == 1 else "L"
        predicted_outcome = predict_streak_continuation((current_streak, amount), stats)
        text_graph = text_streak_distribution(streaks.get('streaks'))

        
        # Build the dictionary for the current team
        result[x.get('Team')] = {
            "team_name": x.get('Team'),
            "opponent": x.get('vs_Team'),
            "venue": x.get('Venue'),
            "record": x.get('Team Record'),
            "binary_record": list1,
            "games_played": list_counts.get('trials'),
            "wins": list_counts.get('success'),
            "losses": list_counts.get('failures'),
            "win_percentage": round(list_counts.get('success') / list_counts.get('trials'), 2),
            "streak_analysis": {
                "number_of_win_streaks": streak_data.get('number_of_win_streaks'),
                "longest_win_streak": streak_data.get('longest_win_streak'),
                "average_win_streak_length": streak_data.get('average_win_streak_length'),
                "number_of_lose_streaks": streak_data.get('number_of_lose_streaks'),
                "longest_lose_streak": streak_data.get('longest_lose_streak'),
                "average_lose_streak_length": streak_data.get('average_lose_streak_length'),
            },
            "current_streak": {
                "streak_type": current_streak_s,
                "streak_length": amount,
            },
            "predicted_outcome": "W" if predicted_outcome == 1 else "L",
            "markov_predictions": {
                "markov_prediction": x.get('WLmc?'),
                "markov_monte_carlo": x.get('WLmmc?'),
                "markov_monte_carlo_certainty": x.get('WLmmc%?'),
            },
            "streak_distribution_graph": text_graph,
        }

    return result

def combine_dicts_for_data(beans, list_of_matches,team_data):
    """
    Combines the team analysis dictionary with match data and team data.

    Args:
        beans (dict): The team analysis dictionary.
        list_of_matches (list): A list of dictionaries containing match data.
        team_data (dict): A dictionary containing additional team information.

    Returns:
        dict: A combined dictionary containing all relevant data.
    """
    for x in beans:
        team_name = beans[x].get('team_name')
        vs_team = beans[x].get('opponent')
        for y in team_data:
            if team_name == y.get('team_name'):
                team_record_plus = y.get('team_record_plus')
                holder = []
                for z in team_record_plus:
                    # print(vs_team.split('(', 1)[0].strip())
                    # print(z.get('vs_team'))
                    if z.get('vs_team') == vs_team.split('(', 1)[0].strip():
                        holder.append(z.get('result'))
                # print(holder)
                beans[x].update({'vs_record': holder})
    
    matches = []
    for a in list_of_matches:
        dict1 = {'away': beans.get(a.get('away')), 'home': beans.get(a.get('home'))}
        matches.append(dict1)
    return matches

def get_combined_team_data():
    """
    Fetches and combines team data, schedule, and match information into a single dataset.

    This method performs the following steps:
    - Retrieves the current date and schedule.
    - Builds a list of matches from the schedule.
    - Reads team data and additional team data from JSON files.
    - Generates a detailed analysis of team data.
    - Combines the team analysis with match data.

    Returns:
        list: A list of dictionaries containing combined data for all matches.
    """
    # Get the current date and schedule
    date = get_date()
    schedule = get_schedule_by_date(date)

    # Build the list of matches
    list_of_matches = []
    for x in schedule:
        match_dict = {"away": x.get('away_name'), "home": x.get('home_name')}
        list_of_matches.append(match_dict)

    # Read team data from JSON files
    team_data = read_json_file('data/team_data.json')
    other_team_data = read_json_file('data/all_team_data.json')

    # Generate team analysis
    beans = generate_team_analysis_dict(other_team_data, team_data)

    # Combine the data
    combined_data = combine_dicts_for_data(beans, list_of_matches, team_data)

    return combined_data

def process_match_data(combined_data):
    """
    Generates an HTML table summarizing match data.

    Args:
        combined_data (list): A list of dictionaries containing combined match data,
                              with 'away' and 'home' keys for each match.

    Returns:
        str: An HTML table as a string.
    """
    # Define the table headers
    headers = [
        "Win", "Loss", "Team (W,L,%)", "vs Team (W,L,%)",
        "Venue", "VS Record Against", "Current Streak",
        "Average Win Streak", "Average Lose Streak",
        "Record"
    ]

    # Start the HTML table
    html_output = ["<table border='1'>"]
    # html_output.append("<thead>")
    html_output.append("<tr>")
    for header in headers:
        html_output.append(f"<th>{header}</th>")
    html_output.append("</tr>")
    # html_output.append("</thead>")
    # html_output.append("<tbody>")

    # Populate the table rows with match data
    for match in combined_data:
        for team_type in ["away", "home"]:  # Process both away and home teams
            team_data = match.get(team_type, {})
            opponent_data = match.get("home" if team_type == "away" else "away", {})

            # Generate the inline graph for the streak distribution
            streak_graph = team_data.get('streak_distribution_graph', 'N/A')

            # Add a row for the team
            html_output.append("<tr>")
            html_output.append(f"<td><input type='checkbox'></td>")
            html_output.append(f"<td><input type='checkbox'></td>")
            html_output.append(f"<td>{team_data.get('team_name', 'N/A')} <b>({team_data.get('wins', 'N/A')},{team_data.get('losses', 'N/A')},{team_data.get('win_percentage', 'N/A')}%)</b></td>")
            html_output.append(f"<td>{opponent_data.get('team_name', 'N/A')} <b>({opponent_data.get('wins', 'N/A')},{opponent_data.get('losses', 'N/A')},{opponent_data.get('win_percentage', 'N/A')})</b></td>")
            html_output.append(f"<td>{team_data.get('venue', 'N/A')}</td>")
            html_output.append(f"<td>{', '.join(team_data.get('vs_record', [])) or 'N/A'}</td>")
            html_output.append(f"<td>{team_data.get('current_streak', {}).get('streak_type', 'N/A')} ({team_data.get('current_streak', {}).get('streak_length', 'N/A')})</td>")
            html_output.append(f"<td>{team_data.get('streak_analysis', {}).get('average_win_streak_length', 'N/A')}</td>")
            html_output.append(f"<td>{team_data.get('streak_analysis', {}).get('average_lose_streak_length', 'N/A')}</td>")
            html_output.append(f"<td>{team_data.get('record', 'N/A')}</td>")
            html_output.append("</tr>")

    # Close the table
    # html_output.append("</tbody>")
    html_output.append("</table>")

    return "\n".join(html_output)

def process_match_data1(combined_data):
    """
    Processes combined match data and outputs a formatted summary for each match.

    Args:
        combined_data (list): A list of dictionaries containing combined match data, 
                              with 'away' and 'home' keys for each match.

    Returns:
        str: A formatted string summarizing the match data.
    """
    output = []

    for i, match in enumerate(combined_data, start=1):
        # Extract away and home team data
        away = match.get('away', {})
        home = match.get('home', {})

        # Format the match summary for the away team
        output.append(f"<input type='checkbox'>")
        output.append(f"<b>{away.get('team_name', 'N/A')}</b> (W:{away.get('wins', 'N/A')} L:{away.get('losses', 'N/A')} {away.get('win_percentage', 'N/A')}%)")
        output.append(f"vs {home.get('team_name', 'N/A')} (home) (W:{home.get('wins', 'N/A')} L:{home.get('losses', 'N/A')} {home.get('win_percentage', 'N/A')}%)")
        output.append(f"@  {away.get('venue', 'N/A')}")
        output.append(f"Record Against Opp: {', '.join(away.get('vs_record', [])) or 'N/A'}")
        output.append(f"Record: {away.get('record', 'N/A')}")  # Truncate long records for readability
        # output.append("--------------------------------------------------")
        output.append(away.get('streak_distribution_graph', 'N/A'))
        output.append("--------------------------------------------------")
        output.append(f"number of win streaks                   {away.get('streak_analysis', {}).get('number_of_win_streaks', 'N/A'):<10}")
        output.append(f"average win streak length               {away.get('streak_analysis', {}).get('average_win_streak_length', 'N/A'):<10}")
        output.append(f"number of lose streaks                  {away.get('streak_analysis', {}).get('number_of_lose_streaks', 'N/A'):<10}")
        output.append(f"average lose streak length              {away.get('streak_analysis', {}).get('average_lose_streak_length', 'N/A'):<10}")
        output.append(f"Current Streak:                         {away.get('current_streak', {}).get('streak_type', 'N/A')}, {away.get('current_streak', {}).get('streak_length', 'N/A')}")
        output.append(f"Predicted Next Outcome:                 {away.get('predicted_outcome', 'N/A'):<10}")
        output.append(f"markov prediction:                      {away.get('markov_predictions', {}).get('markov_prediction', 'N/A'):<10}")
        output.append(f"markov monte carlo:                     {away.get('markov_predictions', {}).get('markov_monte_carlo', 'N/A'):<10}")
        output.append(f"markov monte carlo certainty:           {away.get('markov_predictions', {}).get('markov_monte_carlo_certainty', 'N/A'):<10}")
        output.append("")

        # Format the match summary for the home team
        output.append(f"<input type='checkbox'>")
        output.append(f"<b>{home.get('team_name', 'N/A')}</b> (W:{home.get('wins', 'N/A')} L:{home.get('losses', 'N/A')} {home.get('win_percentage', 'N/A')}%)")
        output.append(f"vs {away.get('team_name', 'N/A')} (away) (W:{away.get('wins', 'N/A')} L:{away.get('losses', 'N/A')} {away.get('win_percentage', 'N/A')}%)")
        output.append(f"@  {home.get('venue', 'N/A')}")
        output.append(f"Record Against Opp: {', '.join(home.get('vs_record', [])) or 'N/A'}")
        output.append(f"Record: {home.get('record', 'N/A')[:100]} ... etc")  # Truncate long records for readability
        # output.append("--------------------------------------------------")
        output.append(home.get('streak_distribution_graph', 'N/A'))
        output.append("--------------------------------------------------")
        output.append(f"number of win streaks                   {home.get('streak_analysis', {}).get('number_of_win_streaks', 'N/A'):<10}")
        output.append(f"average win streak length               {home.get('streak_analysis', {}).get('average_win_streak_length', 'N/A'):<10}")
        output.append(f"number of lose streaks                  {home.get('streak_analysis', {}).get('number_of_lose_streaks', 'N/A'):<10}")
        output.append(f"average lose streak length              {home.get('streak_analysis', {}).get('average_lose_streak_length', 'N/A'):<10}")
        output.append(f"Current Streak:                         {home.get('current_streak', {}).get('streak_type', 'N/A')}, {home.get('current_streak', {}).get('streak_length', 'N/A')}")
        output.append(f"Predicted Next Outcome:                 {home.get('predicted_outcome', 'N/A'):<10}")
        output.append(f"markov prediction:                      {home.get('markov_predictions', {}).get('markov_prediction', 'N/A'):<10}")
        output.append(f"markov monte carlo:                     {home.get('markov_predictions', {}).get('markov_monte_carlo', 'N/A'):<10}")
        output.append(f"markov monte carlo certainty:           {home.get('markov_predictions', {}).get('markov_monte_carlo_certainty', 'N/A'):<10}")
        output.append("")

    return "\n".join(output)

# filepath: /workspaces/zenithcobra.github.io/scripts/merge_schedule_teamstats.py
import re
from typing import Dict, Any, Tuple, List

POSITION_ORDER = {
    "C": 1, "1B": 2, "2B": 3, "3B": 4, "SS": 5,
    "LF": 6, "CF": 7, "RF": 8, "OF": 9,
    "DH": 10, "UTIL": 11, "PH": 12, "PR": 13
}

def _position_sort_key(p):
    pos = p.get("position", "").upper().strip()
    return POSITION_ORDER.get(pos, 99), p.get("player_name","")

SCHEDULE_LINE_RE = re.compile(
    r'^(?P<dt>\d{4}-\d{2}-\d{2} \d{2}:\d{2} [AP]M [A-Z]+)\s+-\s+'
    r'(?P<away>.+?)\s+@\s+(?P<home>.+?)\s+\((?P<status>[^)]+)\)\s*$'
)

TEAM_CELL_RE = re.compile(r'^\s*(?P<name>.+?)\s*<b>\((?P<rec>[^)]+)\)</b>\s*$')

def parse_schedule_text(schedule_text: str) -> List[Dict[str, str]]:
    games = []
    for line in schedule_text.strip().splitlines():
        line = line.rstrip()
        if not line:
            continue
        m = SCHEDULE_LINE_RE.match(line)
        if not m:
            continue
        d = m.groupdict()
        # Normalize team names (strip double spaces)
        d["away"] = re.sub(r'\s+', ' ', d["away"]).strip()
        d["home"] = re.sub(r'\s+', ' ', d["home"]).strip()
        games.append(d)
    return games

def parse_teams_table(html: str) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Returns structure:
    data[team][opponent] = {
        'team_record': str,
        'opp_record': str,
        'venue': str,
        'vs_record_against': str,
        'current_streak': str,
        'avg_win_streak': str,
        'avg_lose_streak': str,
        'record_sequence': str
    }
    """
    # Extract rows between <tr> ... </tr>
    rows = re.findall(r'<tr>(.*?)</tr>', html, flags=re.DOTALL | re.IGNORECASE)
    data: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for r in rows:
        # Extract all <td> contents
        tds = re.findall(r'<td>(.*?)</td>', r, flags=re.DOTALL | re.IGNORECASE)
        if len(tds) < 10:
            continue  # skip header or malformed
        team_cell = tds[2]
        vs_cell = tds[3]
        venue = re.sub(r'\s+', ' ', tds[4].strip())
        vs_record_against = re.sub(r'\s+', ' ', tds[5].strip())
        current_streak = re.sub(r'\s+', ' ', tds[6].strip())
        avg_win_streak = re.sub(r'\s+', ' ', tds[7].strip())
        avg_lose_streak = re.sub(r'\s+', ' ', tds[8].strip())
        record_sequence = re.sub(r'\s+', ' ', tds[9].strip())

        tm_match = TEAM_CELL_RE.match(team_cell)
        vs_match = TEAM_CELL_RE.match(vs_cell)
        if not (tm_match and vs_match):
            continue
        team_name = re.sub(r'\s+', ' ', tm_match.group('name').strip())
        team_record = tm_match.group('rec').strip()
        opp_name = re.sub(r'\s+', ' ', vs_match.group('name').strip())
        opp_record = vs_match.group('rec').strip()


        vs_record_against = '-'.join(part.strip() for part in vs_record_against.split(','))

        data.setdefault(team_name, {})
        data[team_name][opp_name] = {
            "team_record": team_record,
            "opp_record": opp_record,
            "venue": venue,
            "vs_record_against": vs_record_against,
            "current_streak": current_streak,
            "avg_win_streak": avg_win_streak,
            "avg_lose_streak": avg_lose_streak,
            "record_sequence": record_sequence
        }
    return data


def _normalize_team_name(name: str) -> str:
    """
    Light normalization to help match pitcher team names to schedule/team table names.
    Adjust mapping as needed.
    """
    name = name.strip()
    # Map shortened / alternate forms
    aliases = {
        "Athletics": "Oakland Athletics",
        "D-backs": "Arizona Diamondbacks",
    }
    return aliases.get(name, name)

def build_pitcher_map(pitcher_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Returns { normalized_team_name : pitcher_entry }.
    If multiple pitchers per team appear, the first is kept (customize if needed).
    """
    m = {}
    for p in pitcher_data:
        team = p.get("pitchers_team")
        if not team:
            continue
        key = _normalize_team_name(team)
        # Keep first (assumed probable starter); replace logic if you prefer latest.
        m.setdefault(key, p)
    return m

def build_batter_map(batter_data):
    """
    Returns: { team_name : [ { 'player_name': ..., 'position': ..., 'hr_seq': ... }, ... ] }
    Adds a trimmed HR sequence (first 10 tokens of HR_record) under key 'hr_seq'.
    """
    team_map = {}
    for entry in batter_data or []:
        if not isinstance(entry, dict):
            continue
        name = entry.get("player_name")
        hr_full = (entry.get("HR_record") or "").strip()
        # Build trimmed hr sequence: first 10 dash-separated tokens
        tokens = [t for t in hr_full.split('-') if t != '']
        trimmed_hr = '-'.join(tokens[:12])
        if trimmed_hr:  # ensure something present
            trimmed_hr = trimmed_hr  # keep as is (no trailing dash)
        hr_val = entry.get("HR")
        hr24_val = entry.get("HR24",0)
        try:
            hr_int = int(hr_val) if hr_val is not None else 0
        except Exception:
            hr_int = 0
        hr_int = str(hr_int) + " " + str(hr24_val)
        hr_display = f"{hr_int:>2}"  # right pad to 2 width (space + digit) for <10
        pos_raw = entry.get("position") or ""
        # If single char position, prepend underscore for alignment like your sample
        if len(pos_raw.strip()) == 1:
            pos_raw = '_' + pos_raw.strip()
        pos_combined = f"{pos_raw} {hr_display}"
        team = entry.get("team")
        if not (name and pos_combined and team):
            continue
        team_norm = re.sub(r'\s+', ' ', team).strip()
        team_map.setdefault(team_norm, []).append({
            "player_name": name.strip(),
            "position": pos_combined.strip(),
            "hr_seq": trimmed_hr
        })
    for t, roster in team_map.items():
        roster.sort(key=_position_sort_key)
    return team_map

def format_matchup_block(game: Dict[str, str],
                         stats_a: Dict[str, Any],
                         stats_b: Dict[str, Any],
                         width_team: int,
                         width_recseq: int,
                         pitcher_map: Dict[str, Dict[str, Any]],
                         batter_map: Dict[str, list]) -> str:
    """
    Extended: adds pitcher lines (pp / era / s09 / hr9 / h9 / w / l) if found.
    """
    away = game['away']
    home = game['home']
    status = game['status']
    dt = game['dt']
    venue = stats_a.get('venue') or stats_b.get('venue') or ''

    away_rec = f"{stats_a.get('team_record','')}"
    home_rec = f"{stats_b.get('team_record','')}"

    away_seq = stats_a.get('record_sequence', '')[:28]
    home_seq = stats_b.get('record_sequence', '')[:28]

    # Team stats
    cs_away = stats_a.get('current_streak', '')
    cs_home = stats_b.get('current_streak', '')
    aws_away = stats_a.get('avg_win_streak', '')
    aws_home = stats_b.get('avg_win_streak', '')
    als_away = stats_a.get('avg_lose_streak', '')
    als_home = stats_b.get('avg_lose_streak', '')
    pgh_away = stats_a.get('vs_record_against', '')
    pgh_home = stats_b.get('vs_record_against', '')

    # Pitchers
    away_pitcher_entry = pitcher_map.get(_normalize_team_name(away), {}) or {}
    home_pitcher_entry = pitcher_map.get(_normalize_team_name(home), {}) or {}

    away_stats = away_pitcher_entry.get("stats", {}) or {}
    home_stats = home_pitcher_entry.get("stats", {}) or {}

    away_pitcher = away_pitcher_entry.get("pitcher", "")
    home_pitcher = home_pitcher_entry.get("pitcher", "")
    away_era = away_pitcher_entry.get("ERA", away_stats.get("era", ""))
    home_era = home_pitcher_entry.get("ERA", home_stats.get("era", ""))
    away_so9 = away_pitcher_entry.get("SO9", away_stats.get("strikeoutsPer9Inn", ""))
    home_so9 = home_pitcher_entry.get("SO9", home_stats.get("strikeoutsPer9Inn", ""))

    # New metrics
    away_hr9 = away_stats.get("homeRunsPer9", "")
    home_hr9 = home_stats.get("homeRunsPer9", "")
    away_h9 = away_stats.get("hitsPer9Inn", "")
    home_h9 = home_stats.get("hitsPer9Inn", "")
    away_wins = away_stats.get("wins", "")
    home_wins = home_stats.get("wins", "")
    away_losses = away_stats.get("losses", "")
    home_losses = home_stats.get("losses", "")

    indent = "      "
    label_field_width = len(indent)

    def pad(s, w):
        return f"{s:<{w}}"

    def unlabeled_line(left, right, gap="    "):
        return f"{indent}{pad(left, width_team)}{gap}{pad(right, width_team)}"

    def stat_line(label, left_val, right_val):
        prefix = (label + ":").ljust(label_field_width)
        return f"{prefix}{pad(str(left_val), width_team)}         {pad(str(right_val), width_team)}"

    # Core lines
    line_status = f"{indent}({status})"
    line_dt = f"{indent}{dt}     @       {venue}"
    line_names = f"{indent}{pad(away, width_team)} @       {pad(home, width_team)}"
    line_records = unlabeled_line(away_rec, home_rec, gap="         ")
    line_seq = unlabeled_line(away_seq, home_seq, gap="        ")

    lines = [
        line_status,
        line_dt,
        line_names,
        line_records,
        line_seq,
        stat_line("cs", cs_away, cs_home),
        stat_line("aws", aws_away, aws_home),
        stat_line("als", als_away, als_home),
        stat_line("pgh", pgh_away, pgh_home),
    ]

    # Pitcher lines (only if any pitcher present)
    if any([away_pitcher, home_pitcher]):
        lines.append(stat_line("pp", away_pitcher, home_pitcher))
        lines.append(stat_line("era", away_era, home_era))
        lines.append(stat_line("s09", away_so9, home_so9))
        lines.append(stat_line("hr9", away_hr9, home_hr9))
        lines.append(stat_line("h9", away_h9, home_h9))
        lines.append(stat_line("w", away_wins, home_wins))
        lines.append(stat_line("l", away_losses, home_losses))

    # ---------------- Roster lines ----------------
    away_roster = batter_map.get(_normalize_team_name(away), []) or batter_map.get(away, [])
    home_roster = batter_map.get(_normalize_team_name(home), []) or batter_map.get(home, [])

    if away_roster or home_roster:
        name_field = max(
            [len(p["player_name"]) for p in away_roster] +
            [len(p["player_name"]) for p in home_roster] +
            [10]
        )
        max_name_allowed = max(16, width_team + 5)
        name_field = min(name_field, max_name_allowed)

        def fmt_player(entry):
            if not entry:
                return ""
            name1 = entry["player_name"] + '  '
            return f'{name1:<{name_field}}{entry["position"]}'

        def fmt_hr_seq(entry):
            if not entry:
                return ""
            return entry.get("hr_seq", "")
        gap = "       "  # keep same gap as stat_line

        max_rows = max(len(away_roster), len(home_roster))
        for i in range(max_rows):
            left_entry = away_roster[i] if i < len(away_roster) else None
            right_entry = home_roster[i] if i < len(home_roster) else None

            # Player line
            left_txt = fmt_player(left_entry)
            right_txt = fmt_player(right_entry)
            left_padded = f"{left_txt:<{width_team}}"
            right_padded = f"  {right_txt:<{width_team}}"
            lines.append(f"{indent}{left_padded}{gap}{right_padded}")

            # HR sequence line (under each player)
            left_hr = f"{fmt_hr_seq(left_entry):<{width_team}}"
            right_hr = f"{fmt_hr_seq(right_entry):<{width_team}}"
            # Only add if at least one side has content
            if left_entry or right_entry:
                lines.append(f"{indent}{left_hr}{gap}  {right_hr}")

    lines.append("")  # separator
    return "\n".join(lines)

def build_schedule_view(schedule_text: str,
                        teams_table_html: str,
                        pitcher_data: List[Dict[str, Any]] = None,
                        batter_data: List[Dict[str, Any]] = None,
                        max_record_seq_chars: int = 70) -> str:
    games = parse_schedule_text(schedule_text)
    stats_map = parse_teams_table(teams_table_html)
    pitcher_map = build_pitcher_map(pitcher_data or [])
    batter_map = build_batter_map(batter_data or [])
    all_team_names = [g['away'] for g in games] + [g['home'] for g in games]
    if not all_team_names:
        return ""
    width_team = max(len(name) for name in all_team_names) + 6
    width_recseq = max_record_seq_chars

    blocks = []
    for g in games:
        away = g['away']
        home = g['home']
        stats_a = stats_map.get(away, {}).get(home, {})
        stats_b = stats_map.get(home, {}).get(away, {})
        # block = format_matchup_block(g, stats_a, stats_b, width_team, width_recseq, pitcher_map)
        block = format_matchup_block(g, stats_a, stats_b, width_team, width_recseq, pitcher_map, batter_map)
        blocks.append(block)
    return "\n".join(blocks)

def format_schedule(schedule_path="data/schedule_text.txt",
                    teams_table_path="data/teams_table.html.txt",
                    pitcher_path="data/pitcher_data.json",
                    batter_path="data/batter_data.json") -> str:
    with open(schedule_path, "r", encoding="utf-8") as f:
        sched = f.read()
    with open(teams_table_path, "r", encoding="utf-8") as f:
        table_html = f.read()
    import json
    try:
        with open(pitcher_path, "r", encoding="utf-8") as f:
            p_data = json.load(f)
    except Exception:
        p_data = []
    try:
        with open(batter_path, "r", encoding="utf-8") as f:
            b_data = json.load(f)
    except Exception:
        b_data = []
    return build_schedule_view(sched, table_html, p_data, b_data)

# import re
# from html import escape

# def schedule_text_to_html(raw: str) -> str:
#     """
#     Convert the plain text schedule_view.txt.txt content into simple HTML
#     with:
#       - Monospace preserved formatting (wrapped in <pre class="schedule-view">)
#       - Player names bolded ( <b>Name</b> ) when they appear in roster lines
#         directly before a position code (RF, 1B, _C, SS, LF, CF, DH, etc.).
#       - Stat / recent-result sequences like 0-1-0-0-0-0-0-0-0-0 (5+ tokens)
#         italicized + grey via a span: <span class="seq"><i>...</i></span>

#     Heuristics:
#       - A "player name" here is 1–4 capitalized words (allowing accents,
#         apostrophes, periods) immediately followed (after 2+ spaces) by a
#         position code of 1–3 chars (letters, digits, or leading underscore).
#       - Sequence detection: any pattern of at least 5 numeric tokens separated
#         by hyphens: d(-d){4,} with optional trailing hyphen.

#     You can embed the returned HTML into a page; includes a minimal <style>
#     block for convenience. Adjust CSS as desired.
#     """
#     if not raw:
#         return "<div>(no data)</div>"

#     # Regex for player names (lookahead ensures a position code follows)
#     name_pattern = re.compile(
#         r'(?P<name>'
#         r'[A-Z][A-Za-zÀ-ÖØ-öø-ÿ\'\.]+'
#         r'(?: [A-Z][A-Za-zÀ-ÖØ-öø-ÿ\'\.]+){0,3}'
#         r')'
#         r'(?=\s{2,}(?:_[A-Z]|[A-Z0-9]{1,2})\b)'
#     )

#     # Regex for stat / recent-result sequences (≥5 tokens)
#     seq_pattern = re.compile(r'\b\d(?:-\d){4,}\b-?')

#     html_lines = []
#     for line in raw.splitlines():
#         # Preserve original indentation; operate on the raw line (not escaped yet)
#         original_line = line

#         # Escape first (so inserted tags are only ours)
#         esc = escape(original_line)

#         # Bold player names
#         def repl_name(m: re.Match) -> str:
#             nm = m.group('name')
#             return f"<b>{nm}</b>"

#         esc = name_pattern.sub(repl_name, esc)

#         # Italicize sequences
#         def repl_seq(m: re.Match) -> str:
#             seq = m.group(0)
#             return f'<span class="seq"><i>{seq}</i></span>'

#         esc = seq_pattern.sub(repl_seq, esc)

#         html_lines.append(esc)

#     styled = (
#         "<style>\n"
#         ".schedule-view { font-family: monospace; white-space: pre; line-height:1.1; }\n"
#         ".schedule-view .seq { color:#777; font-style:italic; }\n"
#         ".schedule-view b { color:#FFF200; }\n"
#         "</style>\n"
#         "<pre class=\"schedule-view\">"
#         + "\n".join(html_lines) +
#         "</pre>"
#     )
#     return styled

# ```python
# // filepath: [script.py](http://_vscodecontentref_/0)
# ...existing imports above...
import re
from html import escape

def schedule_text_to_html(raw: str) -> str:
    """
    Enhanced HTML styling for the plain-text schedule view.

    Adds:
      - Italic status line ( (Scheduled) )
      - Bold game time and park capacity number
      - Bold team names on the matchup line
      - Italic full W/L record-sequence line
      - Italic pgh (previous games head‑to‑head) sequences
      - Bold pitcher names (pp line)
      - Bold ERA numbers (era line)
      - Italic numeric values on s09 / hr9 / h9 / w / l lines
      - Existing: bold player names; italic grey recent stat sequences (0-1-0...)
    """
    if not raw:
        return "<div>(no data)</div>"

    # Player name (already on roster lines) before a position block
    name_pattern = re.compile(
        r'(?P<name>'
        r'[A-Z][A-Za-zÀ-ÖØ-öø-ÿ\'\.]+'
        r'(?: [A-Z][A-Za-zÀ-ÖØ-öø-ÿ\'\.]+){0,3}'
        r')(?=\s{2,}(?:_[A-Z]|[A-Z0-9]{1,2})\b)'
    )
    # Numeric dash sequences (already handled)
    num_seq_pattern = re.compile(r'\b\d(?:-\d){4,}\b-?')
    # W/L dash sequences (team record sequences)
    wl_seq_pattern = re.compile(r'\bWL{3,}\b-?')

    # Date line: capture date, time, venue, capacity
    date_line_pattern = re.compile(
        r'^(\s*\d{4}-\d{2}-\d{2})\s+'
        r'(\d{2}:\d{2} [AP]M [A-Z]+)(\s+@\s+.+?\()(\d+)(\))\s*$'
    )
    # Matchup (team names) line: Team A @ Team B
    team_line_pattern = re.compile(
        r'^(\s*)([A-Za-z0-9 .\'\-&]+?)(\s+@+\s+)([A-Za-z0-9 .\'\-&]+?)(\s*)$'
    )
    # Pitcher line
    pp_line_pattern = re.compile(r'^\s*pp:\s*(.*)$', re.IGNORECASE)
    # ERA line
    era_line_pattern = re.compile(r'^\s*era:\s*(.*)$', re.IGNORECASE)
    # Lines where numeric columns should be italic
    italic_num_labels = {'s09:', 'hr9:', 'h9:', 'w:', 'l:'}

    def bold_numbers(segment: str) -> str:
        return re.sub(r'(?<![\w>])(\d+(?:\.\d+)?)(?![\w<])', r'<b>\1</b>', segment)

    def italic_numbers(segment: str) -> str:
        return re.sub(r'(?<![\w>])(\d+(?:\.\d+)?)(?![\w<])', r'<i>\1</i>', segment)

    html_lines = []
    for line in raw.splitlines():
        original = line
        esc = escape(original)

        # 1. Status line => italic whole line if it is only "(Something)"
        if original.strip().startswith("(") and original.strip().endswith(")") and original.strip().count("(") == 1:
            esc = f"<i>{esc}</i>"
            html_lines.append(esc)
            continue

        # 2. Date line (time bold, capacity bold)
        m_date = date_line_pattern.match(original)
        if m_date:
            g1, g2, g3, g4_num, g5 = m_date.groups()
            esc = (
                f"{escape(g1)} <b>{escape(g2)}</b>"
                f"{escape(g3)}<b>{escape(g4_num)}</b>{escape(g5)}"
            )
            html_lines.append(esc)
            continue

        # 3. Team names line
        m_team = team_line_pattern.match(original)
        if m_team and '@' in original:
            indent, left_team, mid, right_team, tail = m_team.groups()
            esc = f"{escape(indent)}<b>{escape(left_team.rstrip())}</b>{escape(mid)}<b>{escape(right_team.rstrip())}</b>{escape(tail)}"
            html_lines.append(esc)
            continue

        # 4. Record sequence line (two WL sequences) => italic WL sequences
        if wl_seq_pattern.search(original) and original.strip().startswith(('W','L')):
            def wl_wrap(m):
                return f"<i>{m.group(0)}</i>"
            esc = wl_seq_pattern.sub(wl_wrap, esc)
            html_lines.append(esc)
            continue

        # 5. pgh line: italic WL sequences after the label
        if original.lstrip().lower().startswith("pgh:"):
            def wl_wrap(m):
                return f"<i>{m.group(0)}</i>"
            esc = wl_seq_pattern.sub(wl_wrap, esc)
            html_lines.append(esc)
            continue

        # 6. Pitcher line: bold each pitcher name token cluster (non-numeric text columns)
        if pp_line_pattern.match(original):
            # After label, bold contiguous non-space spans that contain letters
            parts = esc.split(':', 1)
            if len(parts) == 2:
                label, rest = parts
                rest = re.sub(r'([A-Za-zÀ-ÖØ-öø-ÿ\'\.][A-Za-zÀ-ÖØ-öø-ÿ\'\. ]+)',
                              lambda m: f"<b>{m.group(1).rstrip()}</b>", rest)
                esc = f"{label}:{rest}"
            html_lines.append(esc)
            continue

        # 7. ERA line: bold numbers only (two columns)
        if era_line_pattern.match(original):
            esc = bold_numbers(esc)
            html_lines.append(esc)
            continue

        # 8. Italic numeric columns for certain labels
        stripped = original.lstrip()
        prefix = stripped[:stripped.find(':')+1] if ':' in stripped else ''
        if prefix.lower() in italic_num_labels:
            esc = italic_numbers(esc)
            html_lines.append(esc)
            continue

        # (Existing roster styling) ---------------------------------

        # Bold player names on roster lines
        esc = name_pattern.sub(lambda m: f"<b>{m.group('name')}</b>", esc)
        # Italic numeric dash sequences
        esc = num_seq_pattern.sub(lambda m: f'<span class="seq"><i>{m.group(0)}</i></span>', esc)

        html_lines.append(esc)

    styled = (
        "<style>\n"
        ".schedule-view { font-family: monospace; white-space: pre; line-height:1.1; }\n"
        ".schedule-view .seq { color:#777; font-style:italic; }\n"
        ".schedule-view b { color:#FFF200; }\n"
        ".schedule-view i { color:#B0B0B0; }\n"
        "</style>\n"
        "<pre class=\"schedule-view\">"
        + "\n".join(html_lines) +
        "</pre>"
    )
    return styled

# ...rest of file unchanged...

def extract_first_int(s: str):
    """
    Return the first integer found in the string, else None.
    Example: 'American Family Field (146)' -> 146
    """
    import re
    m = re.search(r'\d+', s or '')
    return int(m.group()) if m else None


def extract_all_ints(s: str):
    """
    Return list of all integers (as ints) in the string.
    Example: 'Park 146 Row 12 Seat 7' -> [146, 12, 7]
    """
    import re
    return [int(x) for x in re.findall(r'\d+', s or '')]



def abbreviate_venue(venue: str) -> str:
    """
    Abbreviate a ballpark / venue string.

    Rules:
      - Preserve trailing capacity in parentheses: "(123)"
      - Split name from capacity.
      - If the word 'at' appears (case-insensitive) and is not first/last token:
            Left side letters + '@' + Right side letters
        (each side = first letter of each word, all caps)
      - Otherwise: first letter of every word (all caps)
      - Words keep only alphanumerics when taking the initial (so "Daikin"->D, "O'Hara"->O)

    Examples:
        'American Family Field (146)' -> 'AFF (146)'
        'Oriole Park at Camden Yards (202)' -> 'OP@CY (202)'
        'Busch Stadium (125)' -> 'BS (125)'
        'Rate Field (149)' -> 'RF (149)'

    Returns original string if it cannot parse.
    """
    import re

    if not venue or not venue.strip():
        return venue

    venue = venue.strip()

    # Extract capacity "(###)" if present
    m = re.search(r'\s*\((\d+)\)\s*$', venue)
    capacity = None
    if m:
        capacity = m.group(1)
        name_part = venue[:m.start()].strip()
    else:
        name_part = venue

    if not name_part:
        return venue  # nothing to abbreviate

    tokens = name_part.split()
    if not tokens:
        return venue

    # Locate 'at'
    at_index = None
    for i, tok in enumerate(tokens):
        if tok.lower() == 'at':
            at_index = i
            break

    def initials(words):
        chars = []
        for w in words:
            # Keep only alphanumerics for initial choice
            m = re.search(r'[A-Za-z0-9]', w)
            if m:
                chars.append(m.group(0).upper())
        return ''.join(chars)

    if at_index is not None and 0 < at_index < len(tokens) - 1:
        left = tokens[:at_index]
        right = tokens[at_index + 1:]
        left_abbr = initials(left)
        right_abbr = initials(right)
        abbr = f"{left_abbr}@{right_abbr}" if left_abbr and right_abbr else initials(tokens)
    else:
        abbr = initials(tokens)

    if not abbr:
        return venue  # fallback

    return f"{abbr} ({capacity})" if capacity else abbr



def make_index():
    # get date for later
    date = datetime.now().strftime("%Y-%m-%d")
    
    # Ensure the "docs" folder exists
    os.makedirs("docs", exist_ok=True)

    # FILE PATHS
    ## output
    output_html_path = "docs/index.html"

    ## text
    parlay_banned_list_path = "data/parlay_banned_list.txt" 
    yesterdays_report_path = "data/yesterdays_report_text.txt"
    standings_path = "data/standings_text.txt"
    todays_schedule_path = "data/schedule_text.txt"


    ## Read the contents of the text files
    with open(parlay_banned_list_path, "r") as parlay_banned_file:
        parlay_banned_list_content = parlay_banned_file.read()

    with open(yesterdays_report_path, "r") as yesterdays_report_file:
        yesterdays_report_content = yesterdays_report_file.read()

    with open(standings_path, "r") as standings_file:
        standings_content = standings_file.read()

    with open(todays_schedule_path, "r") as todays_schedule_file:
        todays_schedule_content = todays_schedule_file.read()

    ## data
    yesterday_home_run_data_path = "data/yesterday_home_run_data.json"
    yesterday_home_run_data = read_json_file(yesterday_home_run_data_path)
    yesterday_home_run_table = generate_yesterday_home_run_html_table(yesterday_home_run_data)
    # save_to_text(yesterday_home_run_table, "yesterdays_homers_table.html")
    
    team_list_path = 'data/teams_playing_today_data.json'
    team_list = read_json_file(team_list_path)
    team_list_table = generate_team_list_html_table(team_list)
    # save_to_text(team_list_table, 'team_list_table.html')

    team_data_path = "data/team_data.json"
    team_data = read_json_file(team_data_path)
    ballpark_data_path = "data/ballpark_data.json"
    ballpark_data = read_json_file(ballpark_data_path)
    schedule_data_path = 'data/schedule_data.json'
    schedule_data = read_json_file(schedule_data_path)
    team_data_table = generate_team_html_table(team_data, ballpark_data, schedule_data)
    # save_to_text(team_data_table,'team_data_table')
    team_table_data = parse_html_table(team_data_table)
    save_to_json(team_table_data, "all_team_data")
    # team_analysis_string = generate_team_analysis_string(team_table_data, team_data)
    # Call the method to get the combined data
    combined_data = get_combined_team_data()
    # Call the method with the combined data
    team_analysis_string = process_match_data(combined_data)
    save_to_text(team_analysis_string,"teams_table.html")

    new_schedule_view = format_schedule()
    save_to_text(new_schedule_view, "schedule_view.txt")
    styled_schedule = schedule_text_to_html(new_schedule_view)
    save_to_text(styled_schedule, "styled_schedule_view.html")
    new_schedule_view = styled_schedule

    pitcher_data_path = "data/pitcher_data.json"
    pitcher_data = read_json_file(pitcher_data_path)
    pitcher_table = generate_pitcher_html_table(pitcher_data)
    # save_to_text(pitcher_table,"pitcher_table.html")
    
    batter_data_path = "data/batter_data.json"
    batter_data = read_json_file(batter_data_path)
    batter_table = generate_batter_html_table(batter_data,schedule_data,ballpark_data)
    # save_to_text(batter_table, 'batter_table.html')
    
    bvp_data_path = "data/batter_vs_pitcher_data.json"
    bvp_data = read_json_file(bvp_data_path)
    bvp_table = generate_bvp_html_table(bvp_data, schedule_data, ballpark_data)
    # save_to_text(bvp_table, "bvp_table.html")
    
    dh_batter_data_path = "data/dh_batter_data.json"
    dh_batter_data = read_json_file(dh_batter_data_path)
    dh_batter_table = generate_dh_batter_html_table(dh_batter_data, schedule_data, ballpark_data)
    # save_to_text(dh_batter_table, "dh_batter_table.html")

    leader_data_path1 = "data/ERA_leader_data.json"
    leader_data_path2 = "data/SO9_leader_data.json"
    leader_data_path3 = "data/HR_leader_data.json"
    leader_data1 = read_json_file(leader_data_path1)
    leader_data2 = read_json_file(leader_data_path2)
    leader_data3 = read_json_file(leader_data_path3)
    leaders_table = generate_leaders_table(leader_data1,leader_data2,leader_data3)

    # HTML PART
    # Create the HTML content with a sticky navbar
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MLB Report</title>
<style>
                body {{
                    margin: 0;
                    font-family: 'Fira Code', monospace; /* Use a coding font for a terminal-like feel */
                    color: #BBBBBB;
                    background-color: black; /* Dark background for better contrast */
                }}
                h1, h2, h3, h4, h5, h6 {{
                color: #14B37D;
                }}
                .navbar {{
                    position: sticky;
                    top: 0;
                    background-color: #333;
                    overflow: hidden;
                    z-index: 1000;
                    white-space: nowrap; /* Prevent wrapping */
                }}

                .navbar a {{
                    float: left;
                    display: block;
                    color: white;
                    text-align: center;
                    padding: 8px 10px; /* Reduced padding */
                    font-size: 12px; /* Smaller font size */
                    text-decoration: none;
                }}

                .navbar a:hover {{
                    background-color: #ddd;
                    color: black;
                }}

                .content {{
                    padding: 20px;
                }}

                .highlight {{
                    background-color: #363B44; /* Highlight color */
                }}
                th {{
                    background-color: #363B44; /* Accent color for headers */
                    color: #2A8EEA;
                }}
                a {{
                    color: #3A75C4; /* Cyan color */
                    text-decoration: none; /* Removes underline */
                }}
                .number-highlight {{
                    color: #F2F27A; /* Example color for numbers */
                    font-weight: bold; /* Optional: Make numbers bold */
                    }}
                .non-number-highlight {{
                    color: #50fa7b;
                    }}
            </style>
    </head>
    <body>
        <div class="navbar">
            <a href="#useful-links">Links</a>
            <a href="#parlay-banned-list">Banned</a>
            <a href="#yesterdays-report">History</a>
            <a href="#standings">Standings</a>
            <a href="#todays-schedule">Schedule</a>
            <a href="#teams">Select Teams</a>
            <a href="#records">Teams</a>
            <a href="#leaders">Leaders</a>
            <a href="#match-overviews-pitchers">Pitchers</a>
            <a href="#match-overviews-batters">Players</a>
            <a href="#dh-batters">DH's</a>
            <a href="#bvp-stats">BvP</a>
            <a href="#checked-section">Checked</a>
        </div>
        <div class="content">
            <h1 id="useful-links">Useful Links</h1>
            <ul>
            <li><a href='https://www.fantasyalarm.com/mlb/lineups'>BVP checker</a></li>
            <li><a href='https://www.baseball-reference.com'>baseball-reference</a></li>
            <li><a href='https://baseballsavant.mlb.com'>baseball-savant</a></li>
            <li><a href='https://www.fangraphs.com'>fangraphs</a></li>
            <li><a href='https://www.statmuse.com/mlb'>Stat muse</a></li>
            <li><a href='https://www.baseballmusings.com/cgi-bin/CurStreak.py'>Baseball Musings</a></li>
            <li><a href='https://www.teamrankings.com'>Team Rankings</a></li>
            <li><a href='https://www.onlyhomers.com/ballparks'>Only Homers</a></li>
            </ul>
            <h2>MLB Report {date}</h2>
            <h2 id="parlay-banned-list">Parlay Banned List</h2>
            <pre>{parlay_banned_list_content}</pre>
            <h2 id="yesterdays-report">Yesterdays History</h2>
            <pre>{yesterdays_report_content}</pre>
            <h2 id="standings">Standings</h2>
            <pre>{standings_content}</pre>
            <h2 id="todays-schedule">Today's Schedule</h2>
            <pre>{new_schedule_view}</pre>
            <h2 id="teams">Filter Teams</h2>
            <pre>{team_list_table}</pre>
            <h2 id="records">Team Records</h2>
            <pre>{team_analysis_string}</pre>
            <h2 id="yesterdays-homers">Yesterdays Home Runs</h2>
            <pre>{yesterday_home_run_table}</pre>
            <h2 id="leaders">League Leaders</h2>
            <pre>{leaders_table}</pre>
            <h2 id="match-overviews-pitchers">Probable Pitchers</h2>
            <pre>{pitcher_table}</pre>
            <h2 id="match-overviews-batters">Players</h2>
            <pre>{batter_table}</pre>
            <h2 id="dh-batters">DH Batters</h2>
            <pre>{dh_batter_table}</pre>
            <h2 id="bvp-stats">BVP</h2>
            <pre>{bvp_table}</pre>
            

        </div>
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    let currentlyHighlightedRow = null;
            
                    // Add click event listener to all table rows
                    document.querySelectorAll('table tr').forEach(row => {{
                        row.addEventListener('click', function() {{
                            // Remove highlight from the previously highlighted row
                            if (currentlyHighlightedRow) {{
                                currentlyHighlightedRow.classList.remove('highlight');
                            }}
                            // Highlight the clicked row
                            this.classList.add('highlight');
                            currentlyHighlightedRow = this;
                        }});
                    }});
                }});
            
                document.addEventListener('DOMContentLoaded', function () {{
                    // Find all text nodes in the document
                    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
            
                    let node;
                    while ((node = walker.nextNode())) {{
                        const parent = node.parentNode;
            
                        // Skip script and style tags
                        if (parent.tagName === 'SCRIPT' || parent.tagName === 'STYLE') continue;
            
                        // Replace numbers with a span wrapping them
                        const replacedHTML = node.nodeValue.replace(/(\\d+)/g, '<span class="number-highlight">$1</span>');
                        if (replacedHTML !== node.nodeValue) {{
                            const tempDiv = document.createElement('div');
                            tempDiv.innerHTML = replacedHTML;
            
                            // Replace the text node with the new HTML
                            while (tempDiv.firstChild) {{
                                parent.insertBefore(tempDiv.firstChild, node);
                            }}
                            parent.removeChild(node);
                        }}
                    }}
                }});
            
            </script>
    </body>
    </html>
    """

    # # Write the HTML content to the output file
    # with open(output_html_path, "w") as output_file:
    #     output_file.write(html_content)

    # print(f"HTML file saved to {output_html_path}")

    return html_content

def process_html(html_as_string):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_as_string, "html.parser")

    # Find all tables in the HTML
    tables = soup.find_all("table")

    # Add a "Checked" section at the bottom of the page
    checked_section = soup.new_tag("div", id="checked-section")
    checked_heading = soup.new_tag("h2")
    checked_heading.string = "Checked"
    checked_section.append(checked_heading)

    # Create a <pre> tag to wrap the table
    pre_tag = soup.new_tag("pre")
    checked_table = soup.new_tag("table", id="checked-table", border="1")
    pre_tag.append(checked_table)  # Add the table inside the <pre> tag
    checked_section.append(pre_tag)  # Add the <pre> tag to the section

    soup.body.append(checked_section)

    # Add JavaScript to handle saving checkbox states and copying rows
    script = soup.new_tag("script")
    script.string = """
    document.addEventListener('DOMContentLoaded', function() {
        // Function to handle checkbox clicks
        function handleCheckboxClick(checkbox) {
            const row = checkbox.closest('tr');
            const checkedTable = document.getElementById('checked-table');

            if (checkbox.checked) {
                // Clone the row and add it to the "Checked" table
                const clonedRow = row.cloneNode(true);
                clonedRow.querySelectorAll('input[type="checkbox"]').forEach(cb => {
                    cb.disabled = true; // Disable checkboxes in the cloned row
                });
                checkedTable.appendChild(clonedRow);
            } else {
                // Remove the row from the "Checked" table if it exists
                const rows = Array.from(checkedTable.querySelectorAll('tr'));
                rows.forEach(checkedRow => {
                    const originalRowContent = Array.from(row.cells).map(cell => cell.innerText).join('');
                    const checkedRowContent = Array.from(checkedRow.cells).map(cell => cell.innerText).join('');
                    if (originalRowContent === checkedRowContent) {
                        checkedRow.remove();
                    }
                });
            }
        }

        // Attach the event listener to all checkboxes
        document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('click', function() {
                handleCheckboxClick(this);
            });
        });
    });
    """
    soup.body.append(script)

    # Add JavaScript to handle row highlighting
    highlight_script = soup.new_tag("script")
    script.highlight_string = """
    document.addEventListener('DOMContentLoaded', function() {
        let currentlyHighlightedRow = null;

        document.querySelectorAll('table').forEach(table => {
            table.addEventListener('click', function(event) {
                const cell = event.target.closest('td, th'); // Check if the clicked element is a cell
                if (cell) {
                    const row = cell.closest('tr'); // Get the row of the clicked cell
                    if (currentlyHighlightedRow) {
                        currentlyHighlightedRow.classList.remove('highlight'); // Remove highlight from the previous row
                    }
                    row.classList.add('highlight'); // Highlight the new row
                    currentlyHighlightedRow = row; // Update the currently highlighted row
                }
            });
        });
    });

    // Add CSS for the highlight class
    const style = document.createElement('style');
    style.innerHTML = `
        .highlight {
            background-color: #363B44; /* Highlight color */
        }
    `;
    document.head.appendChild(style);
    """
    soup.body.append(highlight_script)

    # Add the sortable script to the HTML
    sortable_script = """
    document.addEventListener('DOMContentLoaded', function() {
        const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;

        const comparer = (idx, asc) => (a, b) => ((v1, v2) =>
            v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)
        )(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

        document.querySelectorAll('th').forEach(th => th.addEventListener('click', (() => {
            const table = th.closest('table');
            Array.from(table.querySelectorAll('tr:nth-child(n+2)'))
                .sort(comparer(Array.from(th.parentNode.children).indexOf(th), this.asc = !this.asc))
                .forEach(tr => table.appendChild(tr) );
        })));
    });
    """
    sortable_script_tag = soup.new_tag("script")
    sortable_script_tag.string = sortable_script
    soup.body.append(sortable_script_tag)

    # --------------------------------
    sticky_style = soup.new_tag("style")
    sticky_style.string = """
    body {
        margin: 0;
        font-family: Arial, sans-serif;
    }

    .navbar {
        position: fixed; /* Ensures the navbar stays fixed at the top */
        top: 0;
        left: 0;
        width: 100%; /* Makes the navbar span the full width of the page */
        background-color: #333; /* Sets the background color */
        z-index: 1000; /* Ensures the navbar stays above other content */
    }

    .navbar a {
        float: left;
        display: block;
        color: white;
        text-align: center;
        padding: 8px 10px; /* Adjust padding for better spacing */
        font-size: 12px; /* Adjust font size */
        text-decoration: none;
    }

    .navbar a:hover {
        background-color: #ddd;
        color: black;
    }

    .content {
        padding-top: 50px; /* Adds padding to prevent content from overlapping the navbar */
    }
    """
    soup.head.append(sticky_style)

    sticky_headers_script = soup.new_tag("script")
    sticky_headers_script.string = """
    document.addEventListener('DOMContentLoaded', function() {
        const navbarHeight = document.querySelector('.navbar').offsetHeight;

        document.querySelectorAll('table').forEach(table => {
            const headerRow = table.querySelector('tr:first-child');
            if (headerRow) {
                headerRow.style.top = `${navbarHeight}px`; // Set the sticky header below the navbar
            }
        });
    });
    """
    soup.body.append(sticky_headers_script)

    sticky_headers_style = soup.new_tag("style")
    sticky_headers_style.string = """
    table tr:first-child {
        position: sticky;
        top: 40px; /* Adjust this value to match the height of your navbar */
        background-color: #fff; /* Optional: Set background color for better visibility */
        z-index: 999; /* Ensure it stays below the navbar but above other content */
    }
    """
    soup.head.append(sticky_headers_style)

    # =================================
    # =================================
    # =================================
    
    # # Find all tables in the HTML
    # tables = soup.find_all("table")

    # # Add a "Checked" section at the bottom of the page
    # checked_section = soup.new_tag("div", id="checked-section")
    # checked_heading = soup.new_tag("h2")
    # checked_heading.string = "Checked"
    # checked_section.append(checked_heading)

    # # Create a <pre> tag to wrap the table
    # pre_tag = soup.new_tag("pre")
    # checked_table = soup.new_tag("table", id="checked-table", border="1")
    # pre_tag.append(checked_table)  # Add the table inside the <pre> tag
    # checked_section.append(pre_tag)  # Add the <pre> tag to the section

    # soup.body.append(checked_section)

    # # Add JavaScript to handle filtering rows based on radio selection
    # filter_script = soup.new_tag("script")
    # filter_string = """
    # document.addEventListener('DOMContentLoaded', function() {
    #     const radios = document.querySelectorAll('input[type="radio"]');
    #     const tables = document.querySelectorAll('table');

    #     function filterRows() {
    #         const selectedRadio = Array.from(radios).find(radio => radio.checked);
    #         const filterText = selectedRadio ? selectedRadio.closest('tr').querySelector('td:last-child').innerText : null;

    #         tables.forEach(table => {
    #             const rows = table.querySelectorAll('tr');
    #             rows.forEach((row, index) => {
    #                 if (index === 0) {
    #                     // Always show the header row
    #                     row.style.display = '';
    #                 } else {
    #                     const rowText = row.innerText.toLowerCase();
    #                     if (!filterText || rowText.includes(filterText.toLowerCase())) {
    #                         row.style.display = '';
    #                     } else {
    #                         row.style.display = 'none';
    #                     }
    #                 }
    #             });
    #         });
    #     }

    #     // Attach event listeners to all radio buttons
    #     radios.forEach(radio => {
    #         radio.addEventListener('change', filterRows);
    #     });

    #     // Show all rows by default
    #     filterRows();
    # });
    # """
    # soup.body.append(filter_script)

    # # Add CSS for better visibility
    # style_tag = soup.new_tag("style")
    # style_tag.string = """
    # table {
    #     width: 100%;
    #     border-collapse: collapse;
    # }
    # th, td {
    #     padding: 8px;
    #     text-align: left;
    #     border: 1px solid #ddd;
    # }
    # tr:nth-child(even) {
    #     background-color: #f9f9f9;
    # }
    # tr:hover {
    #     background-color: #f1f1f1;
    # }
    # """
    # soup.head.append(style_tag)
    # =================================
    # =================================
    # =================================
    
    # # Add buttons for filtering and resetting
    # button_container = soup.new_tag("div", id="button-container")
    # filter_button = soup.new_tag("button", id="filter-button")
    # filter_button.string = "Filter"
    # reset_button = soup.new_tag("button", id="reset-button")
    # reset_button.string = "Reset"
    # button_container.append(filter_button)
    # button_container.append(reset_button)
    # soup.body.insert(0, button_container)  # Add buttons at the top of the body

    # Add buttons for filtering and resetting
    button_container = soup.new_tag("div", id="button-container")
    filter_button = soup.new_tag("button", id="filter-button")
    filter_button.string = "Filter"
    reset_button = soup.new_tag("button", id="reset-button")
    reset_button.string = "Reset"
    button_container.append(filter_button)
    button_container.append(reset_button)

    # Find the "Filter Teams" heading and insert the buttons below it
    filter_heading = soup.find("h2", string="Filter Teams")
    if filter_heading:
        filter_heading.insert_after(button_container)  # Insert the buttons after the heading


    # Add JavaScript for filtering and resetting
    filter_script = soup.new_tag("script")
    filter_script.string = """
    document.addEventListener('DOMContentLoaded', function() {
        const filterButton = document.getElementById('filter-button');
        const resetButton = document.getElementById('reset-button');
        const radios = document.querySelectorAll('input[type="radio"]');
        const tables = document.querySelectorAll('table');

        // Function to filter rows based on selected radio buttons
        function filterRows() {
            const selectedRadios = Array.from(radios).filter(radio => radio.checked);
            const filterTexts = selectedRadios.map(radio => 
                radio.closest('tr').querySelector('td:last-child').innerText.toLowerCase()
            );

            tables.forEach(table => {
                const rows = table.querySelectorAll('tr');
                rows.forEach((row, index) => {
                    if (index === 0) {
                        // Always show the header row
                        row.style.display = '';
                    } else {
                        const rowText = row.innerText.toLowerCase();
                        if (filterTexts.length === 0 || filterTexts.some(filterText => rowText.includes(filterText))) {
                            row.style.display = '';
                        } else {
                            row.style.display = 'none';
                        }
                    }
                });
            });
        }

        // Function to reset all radio buttons and show all rows
        function resetFilters() {
            radios.forEach(radio => radio.checked = false);
            tables.forEach(table => {
                const rows = table.querySelectorAll('tr');
                rows.forEach(row => {
                    row.style.display = '';
                });
            });
        }

        // Attach event listeners to buttons
        filterButton.addEventListener('click', filterRows);
        resetButton.addEventListener('click', resetFilters);
    });
    """
    soup.body.append(filter_script)

    # =================================
    # =================================
    # =================================

    return str(soup)
