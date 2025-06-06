import statsapi
import mlbstatsapi
from datetime import datetime, timedelta
import csv


# get date
def get_date():
    """
    Gets the current date in the format required by 'statsapi'.
    Returns:
        str: The current date formatted as 'MM/DD/YYYY'.
    """
    return datetime.now().strftime("%m/%d/%Y")


# get yesterdays date
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


# Roster Method
def get_roster_names(team_id):
    """
    This method gets a list of just names of the players in the roster.
    Args:
        team_id (int): The ID of the team whose roster is to be fetched.
    Returns:
        list: A list of player names in the roster.
    """
    roster_string = statsapi.roster(team_id)
    roster_list_unprocessed = roster_string.split('\n')
    roster_list = []
    
    for x in roster_list_unprocessed:
        roster_line = ''
        for y in x.split(' ')[4:]:  # Skip the first 4 elements to get the name
            roster_line = roster_line + y + ' '
        roster_list.append(roster_line.lstrip())  # Remove leading whitespace
    
    return roster_list


# HR leaders
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
    print(date)
    # Get the schedule as a dictionary for the provided date
    schedule = statsapi.schedule(start_date=date, end_date=date)
    return schedule


# process the schedule
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
        date = get_date

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


def extract_probable_pitchers_from_processed_schedule(processed_schedule):
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


def get_id_for_player(player_name):
    """
    Returns a player's ID based on their name.

    Args:
        player_name (str): The name of the player.

    Returns:
        int: The player's ID if found, otherwise None.
    """
    mlb = mlbstatsapi.Mlb()
    player_id = mlb.get_people_id(player_name)
    
    # Validate pitcher_ids
    if not player_id:
        print(f"Warning: No player ID found for {player_id}")
        return None
    
    # Safely access the first element
    return player_id[0]


def get_pitcher_name(player_id):
    """
    Returns the full name of a pitcher based on their ID.

    Args:
        pitcher_id (int): The ID of the pitcher.

    Returns:
        str: The full name of the pitcher.
    """
    mlb = mlbstatsapi.Mlb()
    player_name = mlb.get_person(player_id).__dict__.get('fullname')

    if not player_name:
        print(f"Warning: No player ID found for {player_id}")
        return None
    
    return player_name


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
        print(f"Warning: No player name found for ID {player_id}")
        return None
    
    return player_name


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
        print(f"KeyError: {e}. Skipping this player. Stats: {stats}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}. Skipping this player.")
        return None

    return BvP[0]


# batter vs pitcher data list
def get_batter_vs_pitcher_stats(processed_schedule):
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

        # get then Validate pitcher_ids
        away_pitcher_id = get_id_for_player(away_probable_pitcher)
        if away_pitcher_id is None:  # Check if pitcher_ids is None
            print(f"Could not find ID for {away_probable_pitcher}")
            continue  # Skip to the next iteration of the loop
        
        # get pitcher name and validate
        away_pitcher_name = get_player_name(away_pitcher_id)
        if away_pitcher_name is None:
            print(f"Warning: No player name found for ID {away_pitcher_id}")
            continue

        # get away team_id
        away_pitcher_team_id = x.get('away_id')

        # get away pitcher name
        away_pitcher_team = get_team_from_id(away_pitcher_team_id)
        if away_pitcher_team is None:
            print(f"Warning: No team found for ID {away_pitcher_team_id}")
            continue
        
        # Process home team batters
        for y in x.get('home_team_roster', []):  # Default to an empty list if key is missing
            
            # get and validate batter id
            home_batter_id = get_id_for_player(y)
            if home_batter_id is None:  # Check if batter_id is None
                print(f"Could not find ID for batter {y}")
                continue  # Skip to the next iteration of the loop

            # get batter name and validate
            home_batter_name = get_player_name(home_batter_id)
            if home_batter_name is None:
                print(f"Warning: No player name found for ID {home_batter_id}")
                continue

            #batter team id
            home_batter_team_id = x.get('home_id')

            # get home batter name
            home_batter_team = get_team_from_id(home_batter_team_id)
            if home_batter_team is None:
                print(f"Warning: No team found for ID {home_batter_team_id}")
                continue
            
            # get bvp stats
            batter_vs_pitcher_stats = get_bvp_stats(home_batter_id, away_pitcher_id)

            bvp_dict = {
                "batter": home_batter_name,
                "batter_id": home_batter_id,
                "team": home_batter_team,
                "pitcher": away_pitcher_name,
                "pitcher_id": away_pitcher_id,
                "pitcher_team": away_pitcher_team,
                "pitcher_team_id": away_pitcher_team_id,
                "AB": batter_vs_pitcher_stats.get('atbats'),
                "H": batter_vs_pitcher_stats.get('hits'),
                "HR": batter_vs_pitcher_stats.get('homeruns'),
                "AVG": batter_vs_pitcher_stats.get('avg'),
                "RBI": batter_vs_pitcher_stats.get('rbi'),
                "OBP": batter_vs_pitcher_stats.get('obp'),
                "OPS": batter_vs_pitcher_stats.get('ops')
            }

            returned_list.append(bvp_dict)

        # get home pitcher and validate
        home_probable_pitcher = x.get('home_probable_pitcher')
        if home_probable_pitcher is None:
            print(f"Warning: Missing away_probable_pitcher for game: {x}")
            continue

        # get then Validate pitcher_ids
        home_pitcher_id = get_id_for_player(home_probable_pitcher)
        if home_pitcher_id is None:  # Check if pitcher_ids is None
            print(f"Could not find ID for {home_probable_pitcher}")
            continue  # Skip to the next iteration of the loop
        
        # get pitcher name and validate
        home_pitcher_name = get_player_name(home_pitcher_id)
        if home_pitcher_name is None:
            print(f"Warning: No player name found for ID home_pitcher name{home_pitcher_id}")
            continue

        # get away team_id
        home_pitcher_team_id = x.get('home_id')

        # get away pitcher name
        home_pitcher_team = get_team_from_id(home_pitcher_team_id)
        if home_pitcher_team is None:
            print(f"Warning: No team found for ID home pitcher team id {home_pitcher_team_id}")
            continue
        
        # Process home team batters
        for z in x.get('away_team_roster', []):  # Default to an empty list if key is missing
            
            # get and validate batter id
            away_batter_id = get_id_for_player(z)
            if away_batter_id is None:  # Check if batter_id is None
                print(f"Could not find ID foraway  batter id {z}")
                continue  # Skip to the next iteration of the loop

            # get batter name and validate
            away_batter_name = get_player_name(away_batter_id)
            if away_batter_name is None:
                print(f"Warning: No player name found for ID away batter name{away_batter_id}")
                continue

            #batter team id
            away_batter_team_id = x.get('away_id')

            # get home batter name
            away_batter_team = get_team_from_id(away_batter_team_id)
            if away_batter_team is None:
                print(f"Warning: No team found for ID away batter team id {away_batter_team_id}")
                continue
            
            # get bvp stats
            batter_vs_pitcher_stats = get_bvp_stats(away_batter_id, home_pitcher_id)

            bvp_dict = {
                "batter": home_batter_name,
                "batter_id": home_batter_id,
                "team": home_batter_team,
                "pitcher": away_pitcher_name,
                "pitcher_id": away_pitcher_id,
                "pitcher_team": away_pitcher_team,
                "pitcher_team_id": away_pitcher_team_id,
                "AB": batter_vs_pitcher_stats.get('atbats'),
                "H": batter_vs_pitcher_stats.get('hits'),
                "HR": batter_vs_pitcher_stats.get('homeruns'),
                "AVG": batter_vs_pitcher_stats.get('avg'),
                "RBI": batter_vs_pitcher_stats.get('rbi'),
                "OBP": batter_vs_pitcher_stats.get('obp'),
                "OPS": batter_vs_pitcher_stats.get('ops')
            }

            returned_list.append(bvp_dict)

    return returned_list

date = get_date()
print(date)
schedule = get_schedule_by_date(date)
processed_schedule = process_the_schedule(schedule)
pitcher_today = extract_probable_pitchers_from_processed_schedule(processed_schedule)
batter_vs_pitcher_stats = get_batter_vs_pitcher_stats(processed_schedule)

print(batter_vs_pitcher_stats)




# # ------------------------------
# # ------------------------------
# # ------------------------------

# mlb_date = get_date()    # get the proper formatted date
# schedule = get_schedule_by_date(mlb_date)    # get the schedule as a dictionary for today
# processed_schedule = process_the_schedule(schedule)    # Process the schedule
# pitchers_today = extract_probable_pitchers_from_processed_schedule(processed_schedule)








# # import sys
# # import os

# # sys.stdout = open(os.devnull, 'w')

# # Call your function
# todays_matches = get_matches_today_data()

# # # Restore output
# # sys.stdout = sys.__stdout__

# # print(todays_matches)

# import os
# import json
# from datetime import datetime, timedelta

# # Directory to save the JSON file
# output_dir = "text_output"
# os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

# # File name for today's matches
# today_date = datetime.now().strftime("%Y-%m-%d")
# file_path = os.path.join(output_dir, f"todays_matches.json")

# # Check if the file already exists
# if os.path.exists(file_path):
#     # Rename the existing file by appending yesterday's date
#     yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
#     new_file_path = os.path.join(output_dir, f"todays_matches_{yesterday_date}.json")
#     os.rename(file_path, new_file_path)

# # Save today's matches to the JSON file
# with open(file_path, "w") as json_file:
#     json.dump(todays_matches, json_file, indent=4)

# print(f"Today's matches saved to {file_path}")


