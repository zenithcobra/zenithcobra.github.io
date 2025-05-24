import statsapi

import json

# Read the JSON file
with open("text_output/teams_playing_today.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Ensure the data is a list
if isinstance(data, list):
    teams_list = data
else:
    raise ValueError("The JSON file does not contain a list.")

# Print the list to verify
# print(teams_list)

import statsapi
from datetime import datetime, timedelta
import os


# Get today's date
mlb_date = datetime.now().strftime("%m/%d/%Y")
schedule = statsapi.schedule(start_date=mlb_date, end_date=mlb_date)

# statsapi.get("game", {"gamePk": 633611})
# json_string = statsapi.get("game", {"gamePk": 777815})
# print(json_string.get('livedata'))


import json
import statsapi

# Fetch the JSON string
json_string = statsapi.get("game", {"gamePk": 777815})
livedata = json_string.get('liveData').get('boxscore').get('teams')
for x in livedata.get('away'):
    print(x)

# print(type(json_string))
# for key, value in json_string.items():
#     print(f"{key}")
# # Parse the JSON string into a Python dictionary
# if json_string:
#     json_data = json.loads(json_string)  # Convert JSON string to dictionary

#     # Access the 'livedata' key
#     livedata = json_data.get('liveData')
#     print(livedata)
# else:
#     print("No data returned from statsapi.get()")

# -----------------------------------
# for x in schedule:
#     game_json = statsapi.get("game", {"gamePk": x['game_id']})
#     print(game_json.get('boxscore').get('boxscore').get('teams'))
# #{livedata{boxscore{teams{







import json
import statsapi

# Fetch the JSON string
json_string = statsapi.get("game", {"gamePk": 777815})

# Pretty-print the JSON
pretty_json = json.dumps(json_string, indent=4)
print(pretty_json)


example_dh_json = """{livedata{boxscore{teams{away{ID683002": {
                            "person": {
                                "id": 683002,
                                "fullName": "Gunnar Henderson",
                                "link": "/api/v1/people/683002"
                            },
                            "jerseyNumber": "2",
                            "position": {
                                "code": "10",
                                "name": "Designated Hitter",
                                "type": "Hitter",
                                "abbreviation": "DH"
"""

# next go through and get the last games for each of the teams in teams_playing_today.json file

