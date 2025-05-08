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
        away_leaders = statsapi.team_leader_data(x.get('away_id'), 'homeRuns', season=2025, leaderGameTypes="R", limit=10)
        for z in away_leaders:
            away_team_leaders_hr.append({'name': z[1],'homeRuns': z[2]})

        game_data.update({'away_team_leaders_hr': away_team_leaders_hr})

        home_team_leaders_hr = []
        # add top away team guys here
        home_leaders = statsapi.team_leader_data(x.get('home_id'), 'homeRuns', season=2025, leaderGameTypes="R", limit=10)
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

print(todays_matches)


# %%
# WRITE BVP TO A FILE

import os
from datetime import datetime, timedelta

# Ensure the "text_output" folder exists
os.makedirs("text_output", exist_ok=True)

# Get yesterday's date
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# File paths
bvp_file_path = "text_output/BVP.txt"
backup_file_path = f"text_output/BVP_{yesterday}.txt"

# Check if BVP.txt exists and rename it
if os.path.exists(bvp_file_path):
    os.rename(bvp_file_path, backup_file_path)

# Open the new BVP.txt file in write mode
with open(bvp_file_path, "w") as file:
    for match in todays_matches:

        if 'BvP_stats' in match:

            file.write("Batter vs Pitcher Stats:\n")
            for bvp in match['BvP_stats']:
                file.write("\n")
                away = match['away_probable_pitcher']
                home = match['home_probable_pitcher']
                batter_name = bvp['bvp_matchup']
                if bvp['pitcher'] == away:
                    file.write(f"Away Pitcher:  {bvp['pitcher']:<17} {match['away_name']:<25}\n")
                    beans = 'away'
                elif bvp['pitcher'] == home:
                    file.write(f"Home Pitcher:  {bvp['pitcher']:<17} {match['home_name']:<25}\n")
                    beans = 'home'
                if beans == 'away':
                    file.write(f"Home  Batter:  {bvp['batter']:<17} {match['home_name']:<25}\n")
                elif beans == 'home':
                    file.write(f"Away  Batter:  {bvp['batter']:<17} {match['away_name']:<25}\n")
                file.write(f" AB: {bvp['bvp_stats'].get('atbats', 'N/A'):>7}\n")
                file.write(f"  H: {bvp['bvp_stats'].get('hits', 'N/A'):>7}\n")
                file.write(f" HR: {bvp['bvp_stats'].get('homeruns', 'N/A'):>7}\n")
                file.write(f"AVG: {bvp['bvp_stats'].get('avg', 'N/A'):>7}\n")
                file.write(f"RBI: {bvp['bvp_stats'].get('rbi', 'N/A'):>7}\n")
                file.write(f"obp: {bvp['bvp_stats'].get('obp', 'N/A'):>7}\n")
                file.write(f"ops: {bvp['bvp_stats'].get('ops', 'N/A'):>7}\n")
                file.write("\n")

            file.write("\n")  # Write a newline for better readability between matches

print(f"New BVP file saved to {bvp_file_path}")
if os.path.exists(backup_file_path):
    print(f"Existing BVP file renamed to {backup_file_path}")

# %%
# GET THE STANDINGS AND SCHEDULED GAMES AND ADD TO TEXT FILE
import statsapi
from datetime import datetime, timedelta
import os

# Ensure the "text_output" folder exists
os.makedirs("text_output", exist_ok=True)

# Get yesterday's date
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# File paths
file_name = "Yesterdays_Report.txt"
report_file_path = f"text_output/{file_name}"
backup_file_path = f"text_output/Old_Report_{yesterday}.txt"

# Check if Todays_Report.txt exists and rename it
if os.path.exists(report_file_path):
    os.rename(report_file_path, backup_file_path)

# Get yesterday's schedule
oneday = timedelta(days=1)
yesterday_date = datetime.now().date() - oneday
yschedule = statsapi.schedule(start_date=yesterday_date, end_date=yesterday_date)

# Get today's schedule
mlb_date = datetime.now().strftime("%m/%d/%Y")

# Prepare content to write schedule plus line scoring plays
yesterday_schedule_content = "\nYesterday's Schedule:\n" + "\n".join(
    f'{x.get("summary")}\n\n{statsapi.linescore(x.get("game_id"))}\n\n{statsapi.game_scoring_plays(x.get("game_id"))}\n\n-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*\n' for x in yschedule
)

# Combine all content
full_content = (
    yesterday_schedule_content
)

# Write content to the new Todays_Report.txt file
with open(report_file_path, "w") as file:
    file.write(full_content)

print(f"New report saved to {report_file_path}")
if os.path.exists(backup_file_path):
    print(f"Existing report renamed to {backup_file_path}")

# %%
# GET TODAYS STANDINGS
import statsapi
from datetime import datetime, timedelta
import os

# Ensure the "text_output" folder exists
os.makedirs("text_output", exist_ok=True)

# Get yesterday's date
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# File paths
file_name = "standings.txt"
report_file_path = f"text_output/{file_name}"
backup_file_path = f"text_output/Old_standings_{yesterday}.txt"

# Check if standings.txt exists and rename it
if os.path.exists(report_file_path):
    os.rename(report_file_path, backup_file_path)

# ---------------------------
# Get today's date for api call
mlb_date = datetime.now().strftime("%m/%d/%Y")
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

# Write content to the new Todays_Report.txt file
with open(report_file_path, "w") as file:
    file.write(full_content)

print(f"New report saved to {report_file_path}")
if os.path.exists(backup_file_path):
    print(f"Existing report renamed to {backup_file_path}")

# %%
# GET TODAYS SCHEDULE
import statsapi
from datetime import datetime, timedelta
import os

# Ensure the "text_output" folder exists
os.makedirs("text_output", exist_ok=True)

# Get yesterday's date
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# File paths
file_name = "todays_schedule.txt"
report_file_path = f"text_output/{file_name}"
backup_file_path = f"text_output/Old_schedule_{yesterday}.txt"

# Check if standings.txt exists and rename it
if os.path.exists(report_file_path):
    os.rename(report_file_path, backup_file_path)
# ----------------------------------
import statsapi
from datetime import datetime, timedelta
import os
# Get today's date
mlb_date = datetime.now().strftime("%m/%d/%Y")
schedule = statsapi.schedule(start_date=mlb_date, end_date=mlb_date)
today_schedule_content = "Today's Schedule:\n" + "\n".join(
    f'{x.get("summary")}' for x in schedule
)
# ----------------------------------
# Combine all content
full_content = (
    today_schedule_content
)

# Write content to the new Todays_Report.txt file
with open(report_file_path, "w") as file:
    file.write(full_content)

print(f"New report saved to {report_file_path}")
if os.path.exists(backup_file_path):
    print(f"Existing report renamed to {backup_file_path}")

# %%
# GET THE MATCH OVERVIEW PART OF THE TEXT FILE TO BE ADDED TO THE INDEX.html file
import statsapi
import os
from datetime import datetime, timedelta

# Ensure the "text_output" folder exists
os.makedirs("text_output", exist_ok=True)

# Get yesterday's date
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# File paths
file_name = "match_overviews.txt"
file_path = f"text_output/{file_name}"
backup_file_path = f"text_output/match_overviews_{yesterday}.txt"

# Check if match_overviews.txt exists and rename it
if os.path.exists(file_path):
    os.rename(file_path, backup_file_path)

# Open the new match_overviews.txt file in write mode
with open(file_path, "w") as file:
    for y in todays_matches:
        file.write(f"Match: AWAY: {y['away_name']} vs HOME: {y['home_name']}\n\n")
        file.write(f"Away Probable Pitcher: {y['away_probable_pitcher']}\n")
        
        # Get the stats for the away probable pitcher
        try:
            beans = statsapi.player_stat_data(
                next(x['id'] for x in statsapi.get('sports_players', {'season': 2025, 'gameType': 'W'})['people'] if x['fullName'] == y.get('away_probable_pitcher')),
                'pitching',
                'career'
            )
        except StopIteration:
            print(f"Error: Could not find player ID for away probable pitcher: {y.get('away_probable_pitcher')}")
            beans = None
        except Exception as e:
            print(f"An error occurred while fetching player stats: {e}")
            beans = None
        # Query the ERA stat
        # era1 = beans['stats'][0]['stats']['era']
        # Safely access the nested 'era' key
        if beans is not None and 'stats' in beans:
            stats_list = beans.get('stats', [{}])  # Get 'stats' or default to a list with an empty dictionary
            if isinstance(stats_list, list) and len(stats_list) > 0 and isinstance(stats_list[0], dict):
                era1 = stats_list[0].get('stats', {}).get('era', None)
                file.write(f"    ERA: {era1}\n")
                strikeouts1 = beans['stats'][0]['stats']['strikeoutsPer9Inn']
                file.write(f"    Strikeouts per 9 Innings: {strikeouts1}\n\n")
            else:
                era1 = None
        else:
            era1 = None

        
        file.write(f"Home Probable Pitcher: {y['home_probable_pitcher']}\n")
        
        # Get the stats for the home probable pitcher
        try:
            beans2 = statsapi.player_stat_data(
                next(x['id'] for x in statsapi.get('sports_players', {'season': 2025, 'gameType': 'W'})['people'] if x['fullName'] == y.get('home_probable_pitcher')),
                'pitching',
                'career'
            )
        except StopIteration:
            print(f"Error: Could not find player ID for home probable pitcher: {y.get('home_probable_pitcher')}")
            beans2 = None
        except Exception as e:
            print(f"An error occurred while fetching player stats for home probable pitcher: {e}")
            beans2 = None
        
        if beans2 is not None and 'stats' in beans2:
            stats_list2 = beans2.get('stats', [{}])  # Get 'stats' or default to a list with an empty dictionary
            if isinstance(stats_list2, list) and len(stats_list2) > 0 and isinstance(stats_list2[0], dict):
                era2 = stats_list2[0].get('stats', {}).get('era', None)
                file.write(f"    ERA: {era2}\n")
                strikeouts2 = beans2['stats'][0]['stats']['strikeoutsPer9Inn']
                file.write(f"    Strikeouts per 9 Innings: {strikeouts2}\n\n")
            else:
                era2 = None
        else:
            era2 = None


        
        file.write("Away Team Home Run Leaders:\n")
        for leader in y['away_team_leaders_hr']:
            file.write(f"  - {leader['name']}: {leader['homeRuns']} HR\n")
        
        file.write("\nHome Team Home Run Leaders:\n")
        for leader in y['home_team_leaders_hr']:
            file.write(f"  - {leader['name']}: {leader['homeRuns']} HR\n")
        
        file.write("\n")

print(f"New match overview saved to {file_path}")
if os.path.exists(backup_file_path):
    print(f"Existing match overview renamed to {backup_file_path}")

# %%
## WRITE EVERYTHING TO INDEX.html
import os

# Ensure the "docs" folder exists
os.makedirs("docs", exist_ok=True)

# File paths
parlay_banned_list_path = "text_output/parlay_banned_list.txt" 
todays_report_path = "text_output/Todays_Report.txt"
match_overview_path = "text_output/match_overviews.txt"
bvp_path = "text_output/BVP.txt"
output_html_path = "docs/index.html"

# Read the contents of the text files
with open(parlay_banned_list_path, "r") as parlay_banned_file:
    parlay_banned_list_content = parlay_banned_file.read()

with open(todays_report_path, "r") as todays_report_file:
    todays_report_content = todays_report_file.read()

with open(match_overview_path, "r") as match_overview_file:
    match_overview_content = match_overview_file.read()

with open(bvp_path, "r") as bvp_file:
    bvp_content = bvp_file.read()

# Create the HTML content
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MLB Report</title>
</head>
<body>
    <ul>
    <li><a href='https://www.fantasyalarm.com/mlb/lineups'>BVP checker</a></li>
    <li><a href='https://www.baseball-reference.com'>baseball-reference</a></li>
    <li><a href='https://baseballsavant.mlb.com'>baseball-savant</a></li>
    <li><a href='https://www.fangraphs.com'>fangraphs</a></li>
    <li><a href='https://www.statmuse.com/mlb'>Stat muse</a></li>
    <li><a href='https://www.baseballmusings.com/cgi-bin/CurStreak.py'>Baseball Musings</a></li>
    </ul>
    <h1>MLB Report</h1>
    <h2>Parlay Banned List</h2>
    <pre>{parlay_banned_list_content}</pre>
    <h2>Today's Report</h2>
    <pre>{todays_report_content}</pre>
    <h2>MAtch Overviews</h2>
    <pre>{match_overview_content}</pre>
    <h2>Batter vs Pitcher Stats</h2>
    <pre>{bvp_content}</pre>
</body>
</html>
"""

# Write the HTML content to the output file
with open(output_html_path, "w") as output_file:
    output_file.write(html_content)

print(f"HTML file saved to {output_html_path}")

# %%
# GET THE STREAKS DATA FROM THE WEB

import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime, timedelta

# Ensure the "text_output" folder exists
os.makedirs("text_output", exist_ok=True)

# Get yesterday's date
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# File paths
file_name = "hitting-streak.csv"
file_path = f"text_output/{file_name}"
backup_file_path = f"text_output/hitting-streak_{yesterday}.csv"

# Check if the file already exists and rename it
if os.path.exists(file_path):
    os.rename(file_path, backup_file_path)

# URL of the webpage
url = "https://www.baseballmusings.com/cgi-bin/CurStreak.py"

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the table in the HTML
    table = soup.find('table')
    
    if table:
        # Extract table rows
        rows = table.find_all('tr')
        
        # Extract table data
        table_data = []
        for row in rows:
            cells = row.find_all(['td', 'th'])  # Include both header and data cells
            table_data.append([cell.get_text(strip=True) for cell in cells])
        
        # Write the table data to a CSV file
        with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(table_data[2:])
        
        print(f"New file saved to {file_path}")
        if os.path.exists(backup_file_path):
            print(f"Existing file renamed to {backup_file_path}")
    else:
        print("No table found on the page.")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")

# %%
# READ THE CSV DATA FROM THE FILE AND CONVERT IT TO HTML TABLE

import csv
import os
from datetime import datetime, timedelta

# Read the CSV file into a list
with open("text_output/hitting-streak.csv", "r", encoding="utf-8") as file:
    csv_data = list(csv.reader(file))

# Extract the first line as table_labels
table_labels = csv_data.pop(0)

# Filter out any lines that match the labels
players_on_a_streak = [row for row in csv_data if row != table_labels]

# -------------------------------

# open all_players_with_teams.csv and read the data into a list
with open("text_output/all_players_with_teams.csv", "r", encoding="utf-8") as file:
    all_players_data = list(csv.reader(file))

# compare the players_on_a_streak with all_players_data and add team names to players_on_a_streak
for player in players_on_a_streak:
    player_name = player[0]  # Assuming the player's name is in the first column
    team_name = None
    
    # Search for the player's team in all_players_data
    for all_player in all_players_data:
        if all_player[0] == player_name:  # Assuming the player's name is in the first column of all_players_data
            team_name = all_player[1]  # Assuming the team name is in the second column of all_players_data
            break
    
    # If a team name was found, add it to the player's data
    if team_name:
        player.insert(1,team_name)
    else:
        player.insert(1,"Unknown Team")  # If no team found, add a placeholder

table_labels.insert(1,"Team")  # Add the new column label for team names
# -------------------------------


# Convert the data into an HTML table
html_table = "<table border='1'>\n"

# Add the table headers
html_table += "  <tr>\n"
for label in table_labels:
    html_table += f"    <th>{label}</th>\n"
html_table += "  </tr>\n"

# Add the table rows
for player in players_on_a_streak:
    html_table += "  <tr>\n"
    for value in player:
        html_table += f"    <td>{value}</td>\n"
    html_table += "  </tr>\n"

html_table += "</table>"

# File paths
output_dir = "text_output"
streaks_file = os.path.join(output_dir, "streaks.txt")

# Check if the file already exists
if os.path.exists(streaks_file):
    # Get yesterday's date
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    # Rename the existing file
    renamed_file = os.path.join(output_dir, f"streaks_{yesterday}.txt")
    os.rename(streaks_file, renamed_file)

# Write the HTML table to the new streaks.txt file
with open(streaks_file, "w", encoding="utf-8") as file:
    file.write(html_table)

print(f"HTML table saved to {streaks_file}")

# %%
## WRITE EVERYTHING TO INDEX.html
import os

# Ensure the "docs" folder exists
os.makedirs("docs", exist_ok=True)

# File paths
parlay_banned_list_path = "text_output/parlay_banned_list.txt" 
yesterdays_report_path = "text_output/Yesterdays_Report.txt"
standings_path = "text_output/standings.txt"
today_schedule_path = "text_output/todays_schedule.txt"
match_overview_path = "text_output/match_overviews.txt"
bvp_path = "text_output/BVP.txt"
streaks_path = "text_output/streaks.txt"
output_html_path = "docs/index.html"

# Read the contents of the text files
with open(parlay_banned_list_path, "r") as parlay_banned_file:
    parlay_banned_list_content = parlay_banned_file.read()

with open(yesterdays_report_path, "r") as yesterdays_report_file:
    yesterdays_report_content = yesterdays_report_file.read()

with open(standings_path, "r") as standings_file:
    standings_content = standings_file.read()

with open(today_schedule_path, "r") as today_schedule_file:
    today_schedule_content = today_schedule_file.read()

with open(match_overview_path, "r") as match_overview_file:
    match_overview_content = match_overview_file.read()

with open(bvp_path, "r") as bvp_file:
    bvp_content = bvp_file.read()

with open(streaks_path, "r") as streaks_file:
    streaks_content = streaks_file.read()
# ...existing code...

# Create the HTML content with a sticky navbar
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MLB Report</title>
<style>
        body {{
            margin: 0;
            font-family: Arial, sans-serif;
        }}
        .navbar {{
            position: sticky;
            top: 0;
            background-color: #333;
            overflow: hidden;
            # overflow-x: auto;
            z-index: 1000;
            white-space: nowrap; /* Prevent wrapping */
        }}
        .navbar a {{
            float: left;
            display: block;
            color: white;
            text-align: center;
            padding: 8px 10px; /* Reduced padding */
            font-size: 12px; /* Smaller font size */
            text-decoration: none;
        }}
        .navbar a:hover {{
            background-color: #ddd;
            color: black;
        }}
        .content {{
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="navbar">
        <a href="#useful-links">Links</a>
        <a href="#parlay-banned-list">Banned</a>
        <a href="#yesterdays-report">History</a>
        <a href="#standings">Standings</a>
        <a href="#todays-schedule">Schedule</a>
        <a href="#match-overviews">Matchups</a>
        <a href="#bvp-stats">BvP</a>
        <a href="#streaks">Streaks</a>
    </div>
    <div class="content">
        <h1 id="useful-links">Useful Links</h1>
        <ul>
        <li><a href='https://www.fantasyalarm.com/mlb/lineups'>BVP checker</a></li>
        <li><a href='https://www.baseball-reference.com'>baseball-reference</a></li>
        <li><a href='https://baseballsavant.mlb.com'>baseball-savant</a></li>
        <li><a href='https://www.fangraphs.com'>fangraphs</a></li>
        <li><a href='https://www.statmuse.com/mlb'>Stat muse</a></li>
        <li><a href='https://www.baseballmusings.com/cgi-bin/CurStreak.py'>Baseball Musings</a></li>
        <li><a href='https://www.teamrankings.com'>Team Rankings</a></li>
        </ul>
        <h2>MLB Report</h2>
        <h2 id="parlay-banned-list">Parlay Banned List</h2>
        <pre>{parlay_banned_list_content}</pre>
        <h2 id="yesterdays-report">Yesterdays History</h2>
        <pre>{yesterdays_report_content}</pre>
        <h2 id="standings">Standings</h2>
        <pre>{standings_content}</pre>
        <h2 id="todays-schedule">Today's Schedule</h2>
        <pre>{today_schedule_content}</pre>
        <h2 id="match-overviews">Match Overviews</h2>
        <pre>{match_overview_content}</pre>
        <h2 id="bvp-stats">Batter vs Pitcher Stats</h2>
        <pre>{bvp_content}</pre>
        <h2 id="streaks">Streaks</h2>
        {streaks_content}
    </div>
</body>
</html>
"""

# Write the HTML content to the output file
with open(output_html_path, "w") as output_file:
    output_file.write(html_content)

print(f"HTML file saved to {output_html_path}")


