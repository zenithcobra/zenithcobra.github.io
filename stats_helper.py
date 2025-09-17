

import csv
import pathlib
import requests
import pandas as pd
import os
from os import listdir
from os.path import isfile, join
from datetime import datetime
from dateutil.parser import parse
from fractions import Fraction
import stats_helper
import statsapi



# INITIALIZE SOME VARIABLES AND RUN SCRIPT

CSV_URL = 'https://moneypuck.com/moneypuck/playerData/seasonSummary/2024/regular/skaters.csv'
CSV_URL2023 = 'https://moneypuck.com/moneypuck/playerData/seasonSummary/2023/regular/skaters.csv'
CSV_URL2022 = 'https://moneypuck.com/moneypuck/playerData/seasonSummary/2022/regular/skaters.csv'
CSV_TEAM_NAMES = 'static_data/team_names.csv'
ALL_PLAYERS = 'static_data/players.csv'
STATS_2022_CSV = 'static_data/skaters20212022.csv'
STATS_2023_CSV = 'static_data/skaters20222023.csv'
STATS_2024_CSV = 'static_data/skaters20232024.csv'
PLAYERS_INFO_CSV = 'static_data/player_info.csv'
NHL_SCHEDULE = 'static_data/nhl_schedule.csv'
NBA_STATS = 'nba_data/'


# DATES

# GET THE MLB format DATE
def get_current_date_mlb():
    # Get the current date and convert to yy/mm/dd
    return datetime.now().strftime("%m/%d/%Y")

# GET THE DATE
def get_current_date():
    # Get the current date and convert to yy/mm/dd
    #print(datetime.now().strftime("%y/%m/%d"))
    return datetime.now().strftime("%y/%m/%d")
# import datetime
# x = datetime.datetime.strptime("Mon Feb 15 2010", "%a %b %d %Y").strftime("%d/%m/%Y")
# print(x)
# 
# dt = parse('Mon Feb 15 2010')
# print(dt)
# # datetime.datetime(2010, 2, 15, 0, 0)
# print(dt.strftime('%d/%m/%Y'))
# # 15/02/2010

def get_last_jays_game(date = None):
    if date != None:
        game_data = statsapi.boxscore(date)
        print(game_data)
        return game_data
    else:
        last_game = statsapi.last_game(141)
        game_data = statsapi.boxscore(last_game)
        print(game_data)
        return game_data

def get_leaders_OPS():
    # print(statsapi.league_leaders('onBasePlusSlugging',statGroup='hitting',limit=25,season=2025))
    # print(statsapi.league_leaders('homeRuns',statGroup='hitting',limit=25,season=2025))
    # print(statsapi.league_leaders('homeRuns',statGroup='hitting',limit=25,season=2024))
    stats1 = statsapi.league_leaders('onBasePlusSlugging',statGroup='hitting',limit=25,season=2025)
    stats2 = statsapi.league_leaders('homeRuns',statGroup='hitting',limit=25,season=2025)
    stats3 = statsapi.league_leaders('homeRuns',statGroup='hitting',limit=25,season=2024)
    # stats1 = statsapi.league_leader_data('homeRuns', season=2025, limit=20, statGroup='hitting', leagueId=None, gameTypes=None, playerPool=None, sportId=1, statType=None)
    # stats2 = statsapi.league_leader_data('homeRuns', season=2024, limit=20, statGroup='hitting', leagueId=None, gameTypes=None, playerPool=None, sportId=1, statType=None)
    # stats3 = statsapi.league_leader_data('onBasePlusSlugging', season=2025, limit=20, statGroup='hitting', leagueId=None, gameTypes=None, playerPool=None, sportId=1, statType=None)
    for x in len(stats1):
        print(f'{stats1[x]:>30} -> {stats2[x]:<30} @ {stats3[x]}')
    
    # the next two lines makes the data so i could go through and filter for teams
    # # beans = statsapi.league_leader_data('homeRuns', season=2025, limit=25, statGroup=None, leagueId=None, gameTypes=None, playerPool=None, sportId=1, statType=None)
    # print(beans)

def get_yesterday_date():
    import datetime
    oneday = datetime.timedelta(days=1)
    yesterday = datetime.date.today() - oneday
    # print(str(datetime.date.today()))
    # print(yesterday)
    return str(yesterday)


# READ CSV TO LIST

def load_stats_from_csv_to_list(csv_file_path):
    with open(csv_file_path, mode='r') as file:
        return list(csv.reader(file))


# READ CSV TO A LIST OF LINES WHERE EACH LINE IS A DICT

def load_stats_from_csv_to_list_of_dict(csv_file_path):
    """Read the CSV file and load stats, returning a list of dictionaries."""
    stats = []
    with open(csv_file_path, mode='r') as file:
        stats_csv_file = csv.reader(file)
        # Read the header
        headers = next(stats_csv_file)
        # Load the data and create a list of dictionaries
        for row in stats_csv_file:
            # Create a dictionary for each row using headers as keys
            stats.append({headers[i]: row[i] for i in range(len(headers))})
    return stats


# READ NHL SCHEDULE AND PRODUCE LIST OF TEAMS FOR THE DAY

def teams_today(date_time_str):
    teams_today = []
    schedule20242025 = load_stats_from_csv_to_list(NHL_SCHEDULE)
    for row in schedule20242025:
        if row[0] == date_time_str:
            input_string = row[1]
            prefix = input_string.split(",")[0].strip() if "," in input_string else 'Invalid'
            game_from_row = f"{row[2]} vs {row[3]} @ {prefix}"
            print(game_from_row)
            teams_today.extend([row[2], row[3]])
    return teams_today

def teams_today_list(date_time_str):
    teams_today = []
    schedule20242025 = load_stats_from_csv_to_list(NHL_SCHEDULE)
    for row in schedule20242025:
        if row[0] == date_time_str:
            input_string = row[1]
            prefix = input_string.split(",")[0].strip() if "," in input_string else 'Invalid'
            game_from_row = f"{row[2]} vs {row[3]} @ {prefix}"
            #print(game_from_row)
            teams_today.extend([row[2], row[3]])
    return teams_today

def mlb_teams_today():
    mlb_games_today = []
    mlb_date = stats_helper.get_current_date_mlb()
    sched = statsapi.schedule(start_date=mlb_date,end_date=mlb_date)
    for x in sched:
        mlb_games_today.append(x.get('away_name'))
        mlb_games_today.append(x.get('home_name'))
        splitted = x.get('summary').split("@")
        #print(f'{x.get('game_id')} -> {splitted[0]:<40} @ {splitted[1]}')
    return mlb_games_today

def mlb_teams_today_data():
    mlb_games_today = []
    mlb_date = stats_helper.get_current_date_mlb()
    sched = statsapi.schedule(start_date=mlb_date,end_date=mlb_date)
    for x in sched:
        mlb_games_today.append(x)
    return mlb_games_today

def get_mlb_teams_today():
    mlb_games_today = []
    mlb_date = stats_helper.get_current_date_mlb()
    sched = statsapi.schedule(start_date=mlb_date,end_date=mlb_date)
    for x in sched:
        mlb_games_today.append(x.get('away_name'))
        mlb_games_today.append(x.get('home_name'))
        splitted = x.get('summary').split("@")
        #print(f'{x.get('game_id')} -> {splitted[0]:<40} @ {splitted[1]}')
    return mlb_games_today

def mlb_teams_for_day(string_date):
    mlb_games_today = []
    mlb_date = string_date
    sched = statsapi.schedule(start_date=mlb_date,end_date=mlb_date)
    for x in sched:
        mlb_games_today.append(x)
        splitted = x.get('summary').split("@")
        #print(f'{x.get("game_id")} -> {splitted[0]:<40} @ {splitted[1]}')
    return mlb_games_today

def mlb_teams_for_day_list(string_date):
    mlb_games_today = []
    mlb_date = string_date
    sched = statsapi.schedule(start_date=mlb_date,end_date=mlb_date)
    for x in sched:
        mlb_games_today.append(x)
        splitted = x.get('summary').split("@")
        #print(f'{x.get("game_id")} -> {splitted[0]:<40} @ {splitted[1]}')
    return mlb_games_today


# NBA TEAMS TODAY

def get_nba_teams_today():
    CSV_NBA_PATH = ''
    NBA_SCHEDULE = 'static_data/nba_schedule.csv'
    NBA_NAMES = 'static_data/nba_names.csv'

    nba_beans = load_stats_from_csv_to_list_of_dict(NBA_SCHEDULE)
    nba_names = load_stats_from_csv_to_list_of_dict(NBA_NAMES)
    teams_nba = []
    for x in nba_beans:
        yellow = datetime.strptime(x.get('Game Date'), "%a, %b %d, %Y").strftime("%y/%m/%d")
        date1 = get_current_date()
        
        if yellow == date1:
            for y in nba_names:
                if x.get('Visitor') == y.get('name'):
                    teams_nba.append(y.get('abr'))
                    x.update({'Visitor':y.get('abr')})
                    # print(y.get('abr'))
                if x.get('Home') == y.get('name'):
                    teams_nba.append(y.get('abr'))
                    x.update({'Home':y.get('abr')})
                    # print(y.get('abr'))
            print(x.get('Visitor') + ' vs ' + x.get('Home') + ' @ ' + x.get('Start'))
    return teams_nba


# GET AND READ SNAPSHOT DATA

def fetch_skaters_data(CSV_URL):
    time_str = get_current_date()
    path_string = f'data/skaters{time_str.replace("/", "")}.csv'
    if isfile(path_string):
        print('👊 Skaters file already exists')
        return list(csv.reader(open(path_string, mode='r')))
    else:
        with requests.Session() as s:
            download = s.get(CSV_URL)
            stats_today = list(csv.reader(download.content.decode('utf-8').splitlines()))
            header = stats_today.pop(0)
            with open(path_string, 'w', newline='') as f:
                csv.writer(f).writerows([header] + stats_today)
        return stats_today

# PROCESS STATS

def get_skater_history(int_shots_average, teams_today):

    current_path = str(pathlib.Path().resolve())
    data_path = join(current_path, 'data')
    csv_file_paths = [join(data_path, f) for f in listdir(data_path) if isfile(join(data_path, f)) and f.endswith(".csv")]
    sorted_csv_file_paths = sorted(csv_file_paths, reverse=True)
    if not sorted_csv_file_paths:
        return []
    
    skaters_from_today = load_stats_from_csv_to_list_of_dict(sorted_csv_file_paths[0])
    skaters_from_today_filtered_for_all = [player for player in skaters_from_today if player.get('situation') == 'all' and player.get('team') in teams_today]
    
    skaters_from_today_filtered_for_all_and_asog = [
        player for player in skaters_from_today_filtered_for_all
        if 'I_F_shotsOnGoal' in player and 'games_played' in player and float(player["games_played"]) > 0
        and (avg_sog := int(round(float(player["I_F_shotsOnGoal"]) / float(player["games_played"]))) > int_shots_average)
    ]
    
    for player in skaters_from_today_filtered_for_all_and_asog:
        player.update({
            "past_games": str(int(round(float(player.get('games_played'))))),
            "past_sog": str(int(round(float(player["I_F_shotsOnGoal"])))),
            "past_a_sog": str(int(round(float(player["I_F_shotsOnGoal"]) / float(player["games_played"])))),
            "past_e_shot": str(int(round(float(player["I_F_xOnGoal"])))),
            "past_goals": str(int(round(float(player["I_F_goals"])))),
            "past_a_goals": str(int(round(float(player["I_F_goals"]) / float(player["games_played"])))),
            "past_e_goals": str(int(round(float(player["I_F_xGoals"])))),
            "past_on_ice_goal": str(int(round(float(player["OnIce_F_goals"])))),
            "past_a_on_ice_goal": str(int(round(float(player["OnIce_F_goals"]) / float(player["games_played"])))),
            "past_assists1": str(int(round(float(player["I_F_primaryAssists"])))),
            "past_assists2": str(int(round(float(player["I_F_secondaryAssists"])))),
            "past_rebound_goals": str(int(round(float(player["I_F_reboundGoals"]))))
        })

    for file_path in sorted_csv_file_paths[1:]:
        additional_data = load_stats_from_csv_to_list_of_dict(file_path)
        for player in skaters_from_today_filtered_for_all_and_asog:
            for x in additional_data:
                if player.get('name') == x.get('name') and x.get('situation') == 'all':
                    player["past_games"] += ":" + str(int(round(float(x.get('games_played')))))
                    player["past_sog"] += ":" + str(int(round(float(x["I_F_shotsOnGoal"]))))
                    player["past_a_sog"] += ":" + str(int(round(float(x["I_F_shotsOnGoal"]) / float(x["games_played"]))))
                    player["past_e_shot"] += ":" + str(int(round(float(x["I_F_xOnGoal"]))))
                    player["past_goals"] += ":" + str(int(round(float(x["I_F_goals"]))))
                    player["past_a_goals"] += ":" + str(int(round(float(x["I_F_goals"]) / float(x["games_played"]))))
                    player["past_e_goals"] += ":" + str(int(round(float(x["I_F_xGoals"]))))
                    player["past_on_ice_goal"] += ":" + str(int(round(float(x["OnIce_F_goals"]))))
                    player["past_a_on_ice_goal"] += ":" + str(int(round(float(x["OnIce_F_goals"]) / float(x["games_played"]))))
                    player["past_assists1"] += ":" + str(int(round(float(x["I_F_primaryAssists"]))))
                    player["past_assists2"] += ":" + str(int(round(float(x["I_F_secondaryAssists"]))))
                    player["past_rebound_goals"] += ":" + str(int(round(float(x["I_F_reboundGoals"]))))
    
    stats_2022 = load_stats_from_csv_to_list_of_dict(STATS_2022_CSV)
    stats_2023 = load_stats_from_csv_to_list_of_dict(STATS_2023_CSV)
    stats_2024 = load_stats_from_csv_to_list_of_dict(STATS_2024_CSV)
    for player in skaters_from_today_filtered_for_all_and_asog:
        for x in stats_2022:
            if player.get('name') == x.get('name') and x.get('situation') == 'all':
                stats = {
                        "SOG_22": str(int(round(float(x["I_F_shotsOnGoal"])))),
                        "AVG_SOG_22": str(int(round(float(x["I_F_shotsOnGoal"]) / float(x["games_played"])))),
                        "GOALS_22": str(int(round(float(x["I_F_goals"])))),
                        "AVG_GOALS_22": str(int(round(float(x["I_F_goals"]) / float(x["games_played"])))),
                        "ASSISTS1_22": str(int(round(float(x["I_F_primaryAssists"])))),
                        "ASSISTS2_22": str(int(round(float(x["I_F_secondaryAssists"])))),
                        "AVG_ASSISTS_22": str(int(round((float(x["I_F_secondaryAssists"]) + float(x["I_F_primaryAssists"])) / float(x["games_played"])))),
                        "REBOUNDS_22": str(int(round(float(x["I_F_reboundGoals"])))),
                        "AVG_REBOUNDS_22": str(int(round(float(x["I_F_reboundGoals"]) / float(x["games_played"])))),
                        "ONICE_GOALS_22": str(int(round(float(x["OnIce_A_xGoals"]))))
                    }
                player.update(stats)
        for x in stats_2023:
            if player.get('name') == x.get('name') and x.get('situation') == 'all':
                stats = {
                        "SOG_23": str(int(round(float(x["I_F_shotsOnGoal"])))),
                        "AVG_SOG_23": str(int(round(float(x["I_F_shotsOnGoal"]) / float(x["games_played"])))),
                        "GOALS_23": str(int(round(float(x["I_F_goals"])))),
                        "AVG_GOALS_23": str(int(round(float(x["I_F_goals"]) / float(x["games_played"])))),
                        "ASSISTS1_23": str(int(round(float(x["I_F_primaryAssists"])))),
                        "ASSISTS2_23": str(int(round(float(x["I_F_secondaryAssists"])))),
                        "AVG_ASSISTS_23": str(int(round((float(x["I_F_secondaryAssists"]) + float(x["I_F_primaryAssists"])) / float(x["games_played"])))),
                        "REBOUNDS_23": str(int(round(float(x["I_F_reboundGoals"])))),
                        "AVG_REBOUNDS_23": str(int(round(float(x["I_F_reboundGoals"]) / float(x["games_played"])))),
                        "ONICE_GOALS_23": str(int(round(float(x["OnIce_A_xGoals"]))))
                    }
                player.update(stats)
        for x in stats_2024:
            if player.get('name') == x.get('name') and x.get('situation') == 'all':
                stats = {
                        "SOG_24": str(int(round(float(x["I_F_shotsOnGoal"])))),
                        "AVG_SOG_24": str(int(round(float(x["I_F_shotsOnGoal"]) / float(x["games_played"])))),
                        "GOALS_24": str(int(round(float(x["I_F_goals"])))),
                        "AVG_GOALS_24": str(int(round(float(x["I_F_goals"]) / float(x["games_played"])))),
                        "ASSISTS1_24": str(int(round(float(x["I_F_primaryAssists"])))),
                        "ASSISTS2_24": str(int(round(float(x["I_F_secondaryAssists"])))),
                        "AVG_ASSISTS_24": str(int(round((float(x["I_F_secondaryAssists"]) + float(x["I_F_primaryAssists"])) / float(x["games_played"])))),
                        "REBOUNDS_24": str(int(round(float(x["I_F_reboundGoals"])))),
                        "AVG_REBOUNDS_24": str(int(round(float(x["I_F_reboundGoals"]) / float(x["games_played"])))),
                        "ONICE_GOALS_24": str(int(round(float(x["OnIce_A_xGoals"]))))
                    }
                player.update(stats)

        # List of keys to process
        keys_to_process = [
        "past_games", 
        "past_sog", 
        "past_a_sog", 
        "past_e_shot", 
        "past_goals", 
        "past_a_goals", 
        "past_e_goals", 
        "past_on_ice_goal", 
        "past_a_on_ice_goal", 
        "past_assists1", 
        "past_assists2", 
        "past_rebound_goals"
        ]
    
        # Process each key
        for key in keys_to_process:
            string_to_split = str(player.get(key)).split(":")
            new_string_to_update = ":" + ":".join(string_to_split[:20])
            player.update({key: new_string_to_update})

        #print(player.get('name'))

    return skaters_from_today_filtered_for_all_and_asog


# Function to replace duplicates with '-'
def replace_duplicates(arr):
    result = []
    previous_value = None
    for value in arr:
        if value == previous_value:
            result.append('-')
        else:
            result.append(value)
        previous_value = value
    return result


def remove_redundancies_from_specific_data(specific_data_array):
    # TODO
    """
    Explanation:
    Splitting the Strings: We start by splitting the games_played and past_sog strings into lists using the split(":") method.
    Replace Duplicates Function: This function iterates over the list and checks if the current value is the same as the previous one. If it is, it appends '-' to the result list; otherwise, it appends the actual value.
    Processing Multiple Lists: After processing the games_played list, we iterate through it again and apply the same logic to past_sog based on the indices of processed_games_played.
    Joining to String: Finally, the processed lists are joined back into strings and printed out.
    This code will give you the desired transformation of both strings.
    """
    # add these things to the code in the player stat dict there is a array that looks like below intgrate it into your code please

    # Certainly! You can achieve this by iterating through the games_played list, checking for duplicated values, and replacing them with '-'. After processing games_played, you can use the same indices to modify the past_sog. Here is a sample code to achieve your requirements:


    for x in specific_data_array:


        
        # Process each key to be a shorter 20 game span
        string_to_split1 = str(x.get('past_games')).split(":")
        new_string_to_update1 = ":" + ":".join(string_to_split1[:20])
        #print(new_string_to_update1)
        x.update({'past_games': new_string_to_update1})
        
        # List of the next keys to process
        keys_to_process = [
        "past_sog", 
        "past_a_sog", 
        "past_e_shot", 
        "past_goals", 
        "past_a_goals", 
        "past_e_goals", 
        "past_on_ice_goal", 
        "past_a_on_ice_goal", 
        "past_assists1", 
        "past_assists2", 
        "past_rebound_goals"
        ]

        # Process each key to be a shorter 20 game span
        for key in keys_to_process:
            #print(x)
            string_to_split = str(x.get(key)).split(":")
            new_string_to_update = ":" + ":".join(string_to_split[:20])
            #print(new_string_to_update)
            x.update({key: new_string_to_update})

        # now remember you want the past games string to compare too 
        # get games played 
        past_games = x.get('past_games')

        # now convert this shit 
        # Original strings
        #games_played = ':52:52:52:51:51:49:48:48:46:45:38:38:37:36:35:33:32:32:31:31'
        #past_sog = ':190:190:190:186:186:178:178:173:161:158:128:128:123:122:120:114:113:113:108:108'

        # Convert strings to lists by splitting on ":"
        #array_from_string_to_split1 = games_played.split(":")
        array_from_string_to_split1 = past_games.split(":")
        #array_from_string_to_split2 = past_sog.split(":")

        for key in keys_to_process:
            array_from_string_to_split2 = str(x.get(key)).split(":")
            
            # Process games_played  
            processed_games_played = replace_duplicates(array_from_string_to_split1)

            # Process past_sog using the same indices as processed_games_played
            processed_past_sog = []
            for i, value in enumerate(processed_games_played):
                if value == '-':
                    processed_past_sog.append('-')
                else:  # Handle the case when it's not a duplicate
                    processed_past_sog.append(array_from_string_to_split2[i])

            # Convert the lists back to strings
            processed_games_played_str = ':' + ':'.join(processed_games_played)
            processed_past_sog_str = ':' + ':'.join(processed_past_sog)

            x.update({"past_games": processed_games_played_str})
            x.update({key: processed_past_sog_str})


        # # Output the results
        # print("Before games_played:", games_played)
        # print("After games_played:", processed_games_played_str)
        # print("Before past_sog:", past_sog)
        # print("After past_sog:", processed_past_sog_str)
    return specific_data_array

def make_report(data):
    date_time_str = get_current_date()
    # generate a report for 
    keys = data[0].keys()
    path_for_csv_file_to_save_to = 'reports/todays_report'+ date_time_str.replace('/','') +'.csv'
    with open(path_for_csv_file_to_save_to, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)