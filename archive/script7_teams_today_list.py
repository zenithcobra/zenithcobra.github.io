# %%
# READ TODAYS_MATCHES AND MAKE A TEAMS TODAY LIST AND SAVE THAT TO JSON
import os
import json

from datetime import datetime, timedelta

# Path to the JSON file
file_path = "text_output/todays_matches.json"

# Check if the file exists
if os.path.exists(file_path):
    # Read the JSON file
    with open(file_path, "r") as json_file:
        todays_matches = json.load(json_file)
    
    # Extract the list of teams playing today
    teams_playing_today = []
    for match in todays_matches:
        if 'away_name' in match:
            teams_playing_today.append(match['away_name'])
        if 'home_name' in match:
            teams_playing_today.append(match['home_name'])
    
    # print("Teams playing today:", teams_playing_today)
    # Path for the teams file
    teams_file_path = "text_output/teams_playing_today.json"

    # Check if the teams file already exists
    if os.path.exists(teams_file_path):
        # Rename the existing file by appending yesterday's date
        yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        old_teams_file_path = f"text_output/teams_playing_today_{yesterday_date}.json"
        os.rename(teams_file_path, old_teams_file_path)

    # Save the new list of teams to teams_playing_today.json
    with open(teams_file_path, "w") as teams_json_file:
        json.dump(teams_playing_today, teams_json_file, indent=4)
    print(f"Teams playing today saved to {teams_file_path}")

else:
    print(f"File {file_path} does not exist.")


