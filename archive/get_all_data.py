#
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

import importlib
import script

# Reload the script after making changes
importlib.reload(script)

#
# open teams list
team_id_list = script.read_json_list('data/mlb_teams.json')
# print(team_id_list)

beans = {}
for a in team_id_list:
    roster = script.get_roster_names(a)
    beans.update({a:{"roster": roster, "list_of_players": []}})


for a in beans:
    new_yellow = {a:[]}
    for b in beans[a]["roster"]:
        # print(b)
        yellow = script.get_id_for_player(b)
        player = {"team": a, "name": b, "id": yellow}
        beans[a]["list_of_players"].append({"team": a, "name": b, "id": yellow})
        

script.save_to_json(beans, "a_players")
        

#
list1 = script.read_json_dictionary('data/a_players.json')

# add stats from players
for a in list1:
    list_of_players = list1[a]["list_of_players"]
       
    pitchers = []
    hitters = []
    for x in list_of_players:
        player_id = x["id"]
        player_name = x["name"]
        team = x["team"]
        print(player_id, player_name, team)
        print(player_name,',',player_id)
        try:
            player_stats = script.get_player_stats_2025("hitting", player_id)
            # print(player_stats)
            if player_stats:
                # script.save_to_json(player_stats, f"data/player_stats/{player_id}.json")
                # print(player_stats)
                # add to hitters_list
                hitters.append({
                                    "team":team,
                                    "player_name":player_name,
                                    "player_id":player_id,
                                    "player_stats":player_stats
                                    })

            else:
                player_stats = script.get_player_stats_2025("pitching", player_id)
                if player_stats:
                    # print(player_stats)
                    # add to pitchers_list
                    pitchers.append({
                        "team":team,
                        "player_name":player_name,
                        "player_id":player_id,
                        "player_stats":player_stats
                        })
                else:
                    print('even no pitching stats')
                    print(f"No stats found for {player_name} ({player_id}) from {team}")
        except Exception as e:
            print(f"Error fetching stats for {player_name} ({player_id}): {e}")
    list1[a].update({"pitchers":pitchers,"hitters":hitters})


script.save_to_json(list1, "b_players")


#
list1 = script.read_json_dictionary('data/b_players.json')

for a in list1:
    print(a)
    list_of_past_games = script.get_gameid_team_history(a)
    list1[a].update({"team_gameid_history":list_of_past_games})

script.save_to_json(list1, "c_players")

#
list1 = script.read_json_dictionary('data/c_players.json')

# Initialize the MLB StatsAPI client
mlb = mlbstatsapi.Mlb()

for a in list1:
    # Get the team object using the team ID
    team_data = mlb.get_team(a)
    print(team_data)
    # Extract the team name from the returned data
    if team_data:
        team_name = team_data.name
        list1[a].update({"team_name": team_name, "team_id":a})
        # print(f"The team name for ID {team_id} is: {team_name}")
    else:
        print(f"No team found for ID {team_id}")

script.save_to_json(list1, "d_players")

#
importlib.reload(script)
list1 = script.read_json_dictionary('data/d_players.json')

for a in list1:
    team_name = list1[a]['team_name']
    game_history = list1[a]['team_gameid_history']
    game_history_info = script.get_team_records_new(game_history, team_name)
    list1[a].update({"history_data": game_history_info})

script.save_to_json(list1, "e_players")


#
importlib.reload(script)
list1 = script.read_json_dictionary('data/e_players.json')

for a in list1:
    # print(list1[a]["history_data"])
    for key, value in list1[a].items():
        print(f"{key}: {value}")
    print('- - - - - - - -')



#
importlib.reload(script)
list1 = script.read_json_dictionary('data/e_players.json')

for a in list1:
    # Example structure of the lists
    list_of_players = list1[a].get("list_of_players", [])
    pitchers = list1[a].get("pitchers", [])
    hitters = list1[a].get("hitters", [])

    # Iterate through pitchers and add stats to the corresponding player in list_of_players
    for pitcher in pitchers:
        for player in list_of_players:
            if str(player['id']) == str(pitcher['player_id']):
                player['type'] = 'pitcher'
                player['player_stats'] = pitcher['player_stats']

    # Iterate through hitters and add stats to the corresponding player in list_of_players
    for hitter in hitters:
        for player in list_of_players:
            if str(player['id']) == str(hitter['player_id']):
                player['type'] = 'hitter'
                player['player_stats'] = hitter['player_stats']

# for a in list1:
#     for key, player in list1[a].items():
#         print(key, player)
for a in list1:
    # Collect keys to remove
    keys_to_remove = ["pitchers", "hitters"]
    for key in keys_to_remove:
        list1[a].pop(key, None)  # Safely remove the key if it exists

# Save the updated list back to the JSON file
script.save_to_json(list1, "f_players")

# # Print the updated list_of_players for verification
# for player in list_of_players:
#     print(player)

#
# importlib.reload(script)
# list1 = script.read_json_dictionary('data/f_players.json')

# for a in list1:
#     team_gameid_history = list1[a]['team_gameid_history']
#     list_of_players = list1[a]['list_of_players']

#     for q in list_of_players:
#         q['player_stats'].update({"past_games_stats":[]})

#     for b in team_gameid_history:
#         boxscore = script.get_boxscore(b)
#         # print(boxscore['home']['players'])
#         boxscore_home_id = boxscore['teamInfo']['home']['id']
#         # print(boxscore_home_id)
#         boxscore_away_id = boxscore['teamInfo']['away']['id']
#         # print(boxscore_away_id)
#         boxscore_home_stats = boxscore['homeBatters']
#         boxscore_away_stats = boxscore['awayBatters']
#         date = ''
#         for s in boxscore['gameBoxInfo']:
#             is_date = script.contains_date(s['label'])
#             if is_date:
#                 date = s['label']
#         venue = ''
#         for s in boxscore['gameBoxInfo']:
#             if s['label'] == 'Venue':
#                 venue = s['value']

#         for c in list_of_players:
#             team_id = c["team"]
#             # print('team id', team_id)
#             player_id = c["id"]
#             player_game_stats = {}

#             if int(team_id) == int(boxscore_home_id):
#                 home = True
#                 # print('true')
#                 # print('home', boxscore_home_id)
#             else:
#                 home = False
#                 # print('false')
#                 # print('away', boxscore_away_id)

#             if home == True:
#                 for d in boxscore_home_stats:
#                     if player_id == boxscore_home_stats[d]['id']:
#                     # pitching or batting or both
#                     # if boxscore_home_stats[d]['stats']['pitching']:
#                         player_game_stats.update({
#                             "game_id": b,
#                             "venue": venue,
#                             "date": date,
#                             "vs_team": boxscore_away_id,
#                             "position": boxscore_home_stats[d]['position']['abbreviation'],
#                             "stats": boxscore_home_stats[d]
#                         })
#                     if boxscore_home_stats[d]['stats']['batting']:
#                         player_game_stats.update({
#                             "game_id": b,
#                             "venue": venue,
#                             "date": date,
#                             "vs_team": boxscore_away_id,
#                             "position": boxscore_home_stats[d]['position']['abbreviation'],
#                             "batting_stats": boxscore_home_stats[d]['stats']['batting']
#                         })
#             if home == False:
#                 for d in boxscore_away_stats:
#                     # pitching or batting or both
#                     # if boxscore_away_stats[d]['stats']['pitching']:
#                     #     player_game_stats.update({
#                     #         "game_id": b,
#                     #         "venue": venue,
#                     #         "date": date,
#                     #         "vs_team": boxscore_home_id,
#                     #         "position": boxscore_away_stats[d]['position']['abbreviation'],
#                     #         "pitching_stats": boxscore_away_stats[d]['stats']['pitching']
#                     #     })
#                     if boxscore_away_stats[d]['stats']['batting']:
#                         player_game_stats.update({
#                             "game_id": b,
#                             "venue": venue,
#                             "date": date,
#                             "vs_team": boxscore_home_id,
#                             "position": boxscore_away_stats[d]['position']['abbreviation'],
#                             "batting_stats": boxscore_away_stats[d]['stats']['batting']
#                         })    
#             c['player_stats']['past_games_stats'].append(player_game_stats)        

# # print(list1)
# script.save_to_json(list1, "g_players")



#
importlib.reload(script)
list1 = script.read_json_dictionary('data/f_players.json')

for a in list1:
    team_gameid_history = list1[a]['team_gameid_history']
    list_of_players = list1[a]['list_of_players']

    for q in list_of_players:
        q['player_stats'].update({"past_games_stats":[]})

    for b in team_gameid_history:
        boxscore = script.get_boxscore(b)
        # print(boxscore['home']['players'])
        boxscore_home_id = boxscore['teamInfo']['home']['id']
        # print(boxscore_home_id)
        boxscore_away_id = boxscore['teamInfo']['away']['id']
        # print(boxscore_away_id)
        boxscore_home_stats = boxscore['home']['players']
        boxscore_away_stats = boxscore['away']['players']
        date = ''
        for s in boxscore['gameBoxInfo']:
            is_date = script.contains_date(s['label'])
            if is_date:
                date = s['label']
        venue = ''
        for s in boxscore['gameBoxInfo']:
            if s['label'] == 'Venue':
                venue = s['value']

        for c in list_of_players:
            team_id = c["team"]
            # print('team id', team_id)
            player_id = c["id"]
            player_game_stats = {}

            if int(team_id) == int(boxscore_home_id):
                home = True
                # print('true')
                # print('home', boxscore_home_id)
            else:
                home = False
                # print('false')
                # print('away', boxscore_away_id)

            if home == True:
                for d in boxscore_home_stats:
                    if player_id == boxscore_home_stats[d]['person']['id']:
                        # pitching or batting or both
                        if boxscore_home_stats[d]['stats']['pitching']:
                            player_game_stats.update({
                                "game_id": b,
                                "venue": venue,
                                "date": date,
                                "vs_team": boxscore_away_id,
                                "position": boxscore_home_stats[d]['position']['abbreviation'],
                                "pitching_stats": boxscore_home_stats[d]['stats']['pitching']
                            })
                        if boxscore_home_stats[d]['stats']['batting']:
                            player_game_stats.update({
                                "game_id": b,
                                "venue": venue,
                                "date": date,
                                "vs_team": boxscore_away_id,
                                "position": boxscore_home_stats[d]['position']['abbreviation'],
                                "batting_stats": boxscore_home_stats[d]['stats']['batting']
                            })
            if home == False:
                for d in boxscore_away_stats:
                    if player_id == boxscore_away_stats[d]['person']['id']:
                        # pitching or batting or both
                        if boxscore_away_stats[d]['stats']['pitching']:
                            player_game_stats.update({
                                "game_id": b,
                                "venue": venue,
                                "date": date,
                                "vs_team": boxscore_home_id,
                                "position": boxscore_away_stats[d]['position']['abbreviation'],
                                "pitching_stats": boxscore_away_stats[d]['stats']['pitching']
                            })
                        if boxscore_away_stats[d]['stats']['batting']:
                            player_game_stats.update({
                                "game_id": b,
                                "venue": venue,
                                "date": date,
                                "vs_team": boxscore_home_id,
                                "position": boxscore_away_stats[d]['position']['abbreviation'],
                                "batting_stats": boxscore_away_stats[d]['stats']['batting']
                            })    
            c['player_stats']['past_games_stats'].append(player_game_stats)        

# print(list1)
script.save_to_json(list1, "g_players")



#
# importlib.reload(script)
# list1 = script.read_json_dictionary('data/g_players.json')

# for a in list1:
#     for key, value in list1[a].items():
#         list1[a].pop("pitchers",None)
#         list1[a].pop("hitters",None)
#         # for player in list1[a]['list_of_players']:
#         #     game_stats = player['player_stats']['past_games_stats']
#         #     # Filter out empty dictionaries
#         #     filtered_game_stats = [entry for entry in game_stats if entry]
#         #     player['player_stats'].update({"past_games_stats": filtered_game_stats})

# # Save the updated list back to the JSON file
# script.save_to_json(list1, "h_players")

importlib.reload(script)
list1 = script.read_json_dictionary('data/g_players.json')

for a in list1:
    # Uncomment and use this block if you want to filter out empty dictionaries
    for player in list1[a]['list_of_players']:
        game_stats = player['player_stats']['past_games_stats']
        # Filter out empty dictionaries
        filtered_game_stats = [entry for entry in game_stats if entry]
        player['player_stats'].update({"past_games_stats": filtered_game_stats})

# Save the updated list back to the JSON file
script.save_to_json(list1, "h_players")


