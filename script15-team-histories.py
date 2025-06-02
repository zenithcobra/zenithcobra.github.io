
import os
import json
from bs4 import BeautifulSoup
import statsapi
from datetime import datetime, timedelta
from fractions import Fraction

# -------

# File path for the JSON file
json_file_path = "text_output/teams_last_10_games.json"

# Ensure the file exists
if not os.path.exists(json_file_path):
    raise FileNotFoundError(f"{json_file_path} does not exist.")

# Read the JSON file into a dictionary
with open(json_file_path, "r", encoding="utf-8") as file:
    teams_last_10_games = json.load(file)

    for game in last_games_list:
        boxscore = statsapi.boxscore_data(game, timecode=None)