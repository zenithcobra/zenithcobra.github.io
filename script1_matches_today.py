# %%
# GET ALL THE MATCHES TODAY LOTS OF API
def get_matches_today_data():
    import statsapi
    import mlbstatsapi
    from datetime import datetime

    # Get today's schedule
    matches_today = []

    # get the proper formatted date
    mlb_date = datetime.now().strftime("%m/%d/%Y")

    # get the schedule as a dictionary for today
    schedule = statsapi.schedule(start_date=mlb_date, end_date=mlb_date)

    # iterate through each game of the schedule
    # building game_data dictionary
    for x in schedule:

        # initialize game data dictionary
        game_data = {}
        game_id = x.get('game_id')
        away_name = x.get('away_name')
        home_name = x.get('home_name')
        away_id = x.get('away_id')
        home_id = x.get('home_id')
        home_probable_pitcher = x.get('home_probable_pitcher')
        away_probable_pitcher = x.get('away_probable_pitcher')
        
        # game_id
        game_data.update({'game_id': game_id})

        # away_name
        game_data.update({'away_name': away_name}) 
        
        # home_name
        game_data.update({'home_name': home_name})
        
        # away_id
        game_data.update({'away_id': away_id})

        # get scheduled batters for game
        away_team_batters = []
        
        # add top away team guys here
        away_leaders = statsapi.team_leader_data(x.get('away_id'), 'homeRuns', season=2025, leaderGameTypes="R", limit=10)
        for z in away_leaders:
            away_team_batters.append({'name': z[1],'homeRuns': z[2]})

        game_data.update({'away_team_batters': away_team_batters})

        home_team_batters = []
        # add top away team guys here
        home_leaders = statsapi.team_leader_data(x.get('home_id'), 'homeRuns', season=2025, leaderGameTypes="R", limit=10)
        for z in home_leaders:
            home_team_batters.append({'name': z[1],'homeRuns': z[2]})

        game_data.update({'home_team_batters': home_team_batters})

        # home_id
        game_data.update({'home_id': home_id})
        # home_probable_pitcher
        game_data.update({'home_probable_pitcher': home_probable_pitcher})
        # away_probable_pitcher
        game_data.update({'away_probable_pitcher': away_probable_pitcher})

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


