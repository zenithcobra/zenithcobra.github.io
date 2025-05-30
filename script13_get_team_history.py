import os
import json
from bs4 import BeautifulSoup
import statsapi
from datetime import datetime

# File paths
json_file_path = "text_output/teams_playing_today.json"

if not os.path.exists(json_file_path):
    raise FileNotFoundError(f"{json_file_path} does not exist.")

# Read the JSON file into a list
def read_json_to_list(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    if not isinstance(data, list):
        raise ValueError("The JSON file does not contain a list.")
    
    return data

teams_playing_today = read_json_to_list(json_file_path)

team_ids = []
for team in teams_playing_today:
    # print(team)
    team_ids.append(statsapi.lookup_team(team)[0].get('id'))

# print(team_ids)

# get the proper formatted date
mlb_date = datetime.now().strftime("%m/%d/%Y")

# new_team_list = []
team_dict = {}
for a in team_ids:
    # how to get the last 15 games for a team
    sched = statsapi.schedule(start_date='01/01/2025',end_date=mlb_date,team=a)
    newlist = sorted(sched, key = lambda k: k["game_date"], reverse=True)
    game_data_list = []
    for game in newlist[0:15]:
    #     # beans = statsapi.get("game", {"gamePk": game.get('game_id')})
    #     beans = statsapi.get("game", {"gamePk": game.get('gamePk')})
        game_data_list.append(game.get('game_id'))
        # print(f"{a} -> {}")
    team_dict.update({a:game_data_list})
    # new_team_list.append(team_dict)

# save the new team list to a JSON file
output_json_path = "text_output/teams_last_10_games.json"
with open(output_json_path, "w", encoding="utf-8") as output_file:
    json.dump(team_dict, output_file, indent=4)
print(f"Teams' last 10 games saved to {output_json_path}")



# for x in new_team_list:
#     print(x)