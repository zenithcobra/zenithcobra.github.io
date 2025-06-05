import statsapi
import mlbstatsapi
from datetime import datetime, timedelta


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
    """
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

# GET ALL THE MATCHES TODAY LOTS OF API
def get_matches_today_data():
    mlb_date = get_date()    # get the proper formatted date
    schedule = get_schedule_by_date(mlb_date)    # get the schedule as a dictionary for today
    processed_schedule = process_the_schedule(schedule)    # Process the schedule


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
                    dict2 = {'bvp_stats': split.stat.__dict__} #dict of stats from the bvp stats
                    dict2.update({'bvp_matchup': bvp_matchup})
                    dict2.update({'pitcher': p_id.__dict__.get('fullname')})
                    dict2.update({'batter': b_id.__dict__.get('fullname')})
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
                    dict2.update({'bvp_matchup': bvp_matchup})
                    dict2.update({'pitcher': p_id.__dict__.get('fullname')})
                    dict2.update({'batter': b_id.__dict__.get('fullname')})
                    BvP.append(dict2)

            except KeyError as e:
                print(f"KeyError: {e}. Skipping this player. Stats: {stats}")
            except Exception as e:
                print(f"Unexpected error: {e}. Skipping this player.")
        
        # Add the BvP stats to the matches_today dictionary
        x.update({'BvP_stats': BvP})

    return matches_today


# import sys
# import os

# sys.stdout = open(os.devnull, 'w')

# Call your function
todays_matches = get_matches_today_data()

# # Restore output
# sys.stdout = sys.__stdout__

# print(todays_matches)

import os
import json
from datetime import datetime, timedelta

# Directory to save the JSON file
output_dir = "text_output"
os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

# File name for today's matches
today_date = datetime.now().strftime("%Y-%m-%d")
file_path = os.path.join(output_dir, f"todays_matches.json")

# Check if the file already exists
if os.path.exists(file_path):
    # Rename the existing file by appending yesterday's date
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    new_file_path = os.path.join(output_dir, f"todays_matches_{yesterday_date}.json")
    os.rename(file_path, new_file_path)

# Save today's matches to the JSON file
with open(file_path, "w") as json_file:
    json.dump(todays_matches, json_file, indent=4)

print(f"Today's matches saved to {file_path}")


