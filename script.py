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

def get_yesterdays_report():
    
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

def get_yesterdays_homers():
    
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
        
        try:
            beans2 = statsapi.player_stat_data(next(x['id'] for x in statsapi.get('sports_players',{'season':2024,'gameType':'W'})['people'] if x['fullName']==z), 'hitting', 'season') 
        except StopIteration:
            print(f"No player found with the name '{z}'.")
            beans2 = None  # Set beans to None or handle it appropriately
        except Exception as e:
            print(f"An error occurred: {e}")
            beans2 = None  # Set beans to None or handle it appropriately


        new_list_with_stats = {}
        if beans:  # Only proceed if a matching player is found
            name = z
            new_list_with_stats.update({'name':name})
            team_name = beans.get('current_team')    
            new_list_with_stats.update({'team': team_name})
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

    return stat_homers

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

def get_team_records(teams_history):
    list_of_lists = []
    for a in teams_history:
        team_id = a.get('team_id')
        team_name = a.get('team_name')
        team_history = a.get('last_games')
        team_record = ''
        list_of_previous_games = team_history
        for x in list_of_previous_games:
            schedule1 = statsapi.schedule(game_id=x)
            if schedule1[0].get('winning_team') == team_name:
                team_record = team_record + 'W-'
            else:
                team_record = team_record + 'L-'
        a.update({'team_record': team_record})

    return teams_history

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

def get_team_history(teams_playing_today):
    
    date = get_date()
    mlb_date = get_yesterday(date)

    new_team_list = []
    for a in teams_playing_today:
        team_dict = {}
        # how to get the last 15 games for a team
        team_id = a.get("team_id")
        team_name = a.get("team_name")
        sched = statsapi.schedule(start_date='01/01/2025',end_date=mlb_date,team=team_id)
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
            # Get the stats for the away probable pitcher
            stats2 = get_player_stats_2024('hitting',player_id)
            if stats2 is None:
                print(f"2025 process batters could not get stats for batter id {player_id}")
                x.update({
                    "HR24": '',
                    "HR24pg": '',
                    "fHR24pg": '' 
                })
                continue
            else:
                # print('stats')
                hrs2 = float(int(stats.get('homeRuns')))
                games_played2 = float(int(stats.get('gamesPlayed')))
                hrs_per_game4 = round((hrs2 / games_played2), 2)
                hrs_per_game3 = str(Fraction(round((hrs2 / games_played2), 2)).limit_denominator(7))
                x.update({
                    "HR24": hrs2,
                    "HR24pg": hrs_per_game4,
                    "fHR24pg": hrs_per_game3 
                })

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

        
    return list_of_players

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
        for xx in batters_with_streaks:
            if z == xx.get('player_name'):
                # add all the stats
                player_dict = xx

        if player_dict:
            try:
                beans = statsapi.player_stat_data(next(x['id'] for x in statsapi.get('sports_players',{'season':2025,'gameType':'W'})['people'] if x['fullName']==z), 'hitting', 'season') 
            except StopIteration:
                print(f"No player found with the name '{z}'.")
                beans = None  # Set beans to None or handle it appropriately
            except Exception as e:
                print(f"An error occurred: {e}")
                beans = None  # Set beans to None or handle it appropriately
            try:
                beans2 = statsapi.player_stat_data(next(x['id'] for x in statsapi.get('sports_players',{'season':2024,'gameType':'W'})['people'] if x['fullName']==z), 'hitting', 'season') 
            except StopIteration:
                print(f"No player found with the name beans2'{z}'.")
                beans2 = None  # Set beans to None or handle it appropriately
            except Exception as e:
                print(f"An error occurred: {e}")
                beans2 = None  # Set beans to None or handle it appropriately

            new_list_with_stats = []
            if beans:  # Only proceed if a matching player is found
                name = z
                new_list_with_stats.append(name)
                team_name = beans.get('current_team')    
                new_list_with_stats.append(team_name)
                for a in beans.get('stats'):
                    games_played = float(int(a.get('stats').get('gamesPlayed')))
                    # hits = float(int(a.get('stats').get('hits')))
                    # new_list_with_stats.append(f"{hits}")
                    hrs = float(int(a.get('stats').get('homeRuns')))
                    new_list_with_stats.append(f"{int(hrs)}")
                    # rbi = float(int(a.get('stats').get('rbi')))
                    # new_list_with_stats.append(f"{rbi}")
                    hrs_per_game = round((hrs / games_played), 2)
                    new_list_with_stats.append(f"{hrs_per_game}")
                    hrs_per_game2 = str(Fraction(round((hrs / games_played), 2)).limit_denominator(7))
                    #str(Fraction(round(float(x[18])/float(x[6]),2)).limit_denominator(5))
                    new_list_with_stats.append(f"{hrs_per_game2}")
                    # hits_per_game = round((hits / games_played), 3)
                    # new_list_with_stats.append(f"{hits_per_game}")
                    # rbis_per_game = round((rbi / games_played), 3)
                    # new_list_with_stats.append(f"{rbis_per_game}")
            if beans2:
                beans2_id = beans2.get('id')
                beans3 = statsapi.player_stat_data(beans2_id, group="hitting", type="season", sportId=1, season=2024)
            
                for b in beans3.get('stats'):
                    hrs2 = float(int(b.get('stats').get('homeRuns')))
                    # print(hrs2)
                    games_played2 = float(int(b.get('stats').get('gamesPlayed')))
                    hrs_per_game4 = round((hrs2 / games_played2), 2)
                    hrs_per_game3 = str(Fraction(round((hrs2 / games_played2), 2)).limit_denominator(7))
                
                    new_list_with_stats.append(f"{int(hrs2)}")          
                    new_list_with_stats.append(f"{hrs_per_game4}")  
                    new_list_with_stats.append(f"{hrs_per_game3}")    
            else:
                new_list_with_stats.append(0)
                new_list_with_stats.append(0)
                new_list_with_stats.append(0)
            
            
            stat_homers.append(new_list_with_stats)

    return stat_homers

# Get Dates
date = get_date()

# Get Schedule and process
schedule = get_schedule_by_date(date)
processed_schedule = process_the_schedule(schedule)

# Get Yesterdays Report
yesterdays_report = get_yesterdays_report()

# Get Homers Yesterday
y_homers = get_yesterdays_homers()

# Get Teams today
teams_today = get_teams_playing_today_from_processed_schedule(processed_schedule)

# Get Pitchers today
pitchers_today = process_pitchers_from_processed_schedule(processed_schedule)
processed_pitchers = add_stats_to_pitchers(pitchers_today)

# Get Batter vs Pitcher stats
batter_vs_pitcher_stats = process_batter_vs_pitcher_stats(processed_schedule)

# Get Streak Data
# # streaks_data = get_streaks_data() # TODO fix this

# Get Upcoming Schedule as Text
schedule_text = get_schedule_text()
standings_text = get_standings_text()

# Get the Roster then prosses the batters out from roster
rooster = process_players_from_roster_into_list(processed_schedule)
batters = add_stats_to_batters(rooster)

# Get Team History
team_history = get_team_history(teams_today)
team_wins = get_team_records(team_history)

# Add streaks to batters
batters_with_streaks = process_batters(batters,team_history)

# Add streaks to bvp
bvp_with_streaks = get_streaks_for_bvp(batter_vs_pitcher_stats,batters_with_streaks)

# get Bvp
batter_vs_pitcher = old_batter_vs_pitchers_get()

# Get League Leaders
eras_leaders = league_leaders_era()
so9_leaders = league_leaders_strikeouts_per_9_innings()
hr_leaders = league_leaders_hrs()

# Save File
save_list_to_text(yesterdays_report,'yesterdays_report')
save_to_json(y_homers,'ace_yesterdays_homers')
save_to_json(teams_today, 'ace_teams_playing_today')
save_to_json(pitchers_today,'pitchers')
save_to_json(batter_vs_pitcher_stats,'ace_batter_vs_pitcher')
save_to_json(batter_vs_pitcher, 'ace_bvp')
# save_to_json(streaks_data, 'hitting_streaks')
save_to_text(schedule_text, 'ace_schedule_text')
save_to_json(processed_batters, "batters")
save_to_json(processed_pitchers,"ace_pitchers_with_stats")
save_to_text(standings_text, "ace_standings")
save_to_json(team_history, "team_histories")
save_to_json(team_wins,"ace_team_wins")
save_to_json(batters_with_streaks,"ace_batters_with_streaks")
save_to_json(bvp_with_streaks,"ace_bvp_with_streaks")

# TODO
# then when you add DH to batters you can grab the stats from the batters file
# make index