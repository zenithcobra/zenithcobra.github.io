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
import statsapi
from datetime import datetime, timedelta
import os
from datetime import datetime
import pytz

# Ensure the "text_output" folder exists
os.makedirs("text_output", exist_ok=True)

# Get yesterday's date
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# File paths
file_name = "Yesterdays_Report.txt"
report_file_path = f"text_output/{file_name}"
backup_file_path = f"text_output/Yesterdays_Report_{yesterday}.txt"

# Check if Todays_Report.txt exists and rename it
if os.path.exists(report_file_path):
    os.rename(report_file_path, backup_file_path)

# Get yesterday's schedule
oneday = timedelta(days=1)
yesterday_date = datetime.now().date() - oneday
yschedule = statsapi.schedule(start_date=yesterday_date, end_date=yesterday_date)

# Separate entries with "Toronto" in the "summary" key
entries_with_toronto = [x for x in yschedule if "summary" in x and "Toronto" in x["summary"]]

# Separate entries without "Toronto" in the "summary" key
entries_without_toronto = [x for x in yschedule if not ("summary" in x and "Toronto" in x["summary"])]

# Combine the two lists, bringing entries with "Toronto" to the top
sorted_list = entries_with_toronto + entries_without_toronto

yesterdays_content = []
for x in sorted_list:
    
    # Example UTC datetime string
    utc_datetime_str = x.get("game_datetime")

    # Parse the UTC datetime string
    utc_datetime = datetime.strptime(utc_datetime_str, '%Y-%m-%dT%H:%M:%SZ')

    # Define the UTC and Eastern Time zones
    utc_zone = pytz.utc
    eastern_zone = pytz.timezone('US/Eastern')

    # Localize the datetime to UTC
    utc_datetime = utc_zone.localize(utc_datetime)

    # Convert to Eastern Time
    eastern_datetime = utc_datetime.astimezone(eastern_zone)

    # Format the datetime in a readable format
    readable_format = eastern_datetime.strftime('%Y-%m-%d %I:%M %p %Z')

    # print(readable_format)
    # print(x)
    # print(x)
    x.update({"time_scheduled": readable_format})
    x.update({"scoring_plays": statsapi.game_scoring_plays(x.get("game_id"))})
    yesterdays_content.append(
        f"{x.get('time_scheduled')}\n"
        # f"Status: {x.get('')}\n"
        f"{x.get('away_name'):<22} {x.get('away_score')}    @\n"
        f"{x.get('home_name'):<22} {x.get('home_score')}\n\n"
        f"{x.get('scoring_plays')}\n\n"
        f"NEXT GAME:\n"
    )


# Write content to the new Todays_Report.txt file
with open(report_file_path, "w") as file:
    for content in yesterdays_content:
        file.write(content)


print(f"New report saved to {report_file_path}")
if os.path.exists(backup_file_path):
    print(f"Existing report renamed to {backup_file_path}")


# %%
# GET TODAYS SCHEDULE

import statsapi
from datetime import datetime, timedelta
import os
import pytz

# Ensure the "text_output" folder exists
os.makedirs("text_output", exist_ok=True)

# Get yesterday's date
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# File paths
file_name = "todays_schedule.txt"
report_file_path = f"text_output/{file_name}"

# Get today's date
mlb_date = datetime.now().strftime("%m/%d/%Y")
schedule = statsapi.schedule(start_date=mlb_date, end_date=mlb_date)

# -----------------------------------
for x in schedule:
    # Example UTC datetime string
    utc_datetime_str = x.get("game_datetime")

    # Parse the UTC datetime string
    utc_datetime = datetime.strptime(utc_datetime_str, '%Y-%m-%dT%H:%M:%SZ')

    # Define the UTC and Eastern Time zones
    utc_zone = pytz.utc
    eastern_zone = pytz.timezone('US/Eastern')

    # Localize the datetime to UTC
    utc_datetime = utc_zone.localize(utc_datetime)

    # Convert to Eastern Time
    eastern_datetime = utc_datetime.astimezone(eastern_zone)

    # Format the datetime in a readable format
    readable_format = eastern_datetime.strftime('%Y-%m-%d %I:%M %p %Z')

    beans = x.get('summary').split('-')
    new_beans = readable_format + " - " + beans[3].strip()
    x.update({"summary": new_beans})
# -----------------------------------


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



# %%
# GET THE MATCH OVERVIEW PART OF THE TEXT FILE TO BE ADDED TO THE INDEX.html file
import statsapi
import os
from datetime import datetime, timedelta
import json

# Path to the JSON file
file_path = "text_output/todays_matches.json"

# Check if the file exists
if os.path.exists(file_path):
    # Read the JSON file
    with open(file_path, "r") as json_file:
        todays_matches = json.load(json_file)


# ----------------------
pitchers = []
batters = []

for y in todays_matches:
    
    # start the dictionary
    player = {}

    # print(f"Match: AWAY: {y['away_name']} vs HOME: {y['home_name']}\n\n")
    # print(f"Away Probable Pitcher: {y['away_probable_pitcher']}\n")
    player.update({"type": "pitcher", "name": y['away_probable_pitcher'], "team": y['away_name']})


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
            # print(f"    ERA: {era1}\n")
            player.update({"ERA": era1})
            strikeouts1 = beans['stats'][0]['stats']['strikeoutsPer9Inn']
            # print(f"    Strikeouts per 9 Innings: {strikeouts1}\n\n")
            player.update({"SO9": strikeouts1})
        else:
            era1 = None
    else:
        era1 = None
    if player.get("name") != '':    
        pitchers.append(player)
    player2 = {}


    # print(f"Home Probable Pitcher: {y['home_probable_pitcher']}\n")
    player2.update({"type": "pitcher", "name": y['home_probable_pitcher'], "team": y['home_name']})

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
            
            # print(f"    ERA: {era2}\n")
            player2.update({"ERA": era2})
            
            strikeouts2 = beans2['stats'][0]['stats']['strikeoutsPer9Inn']
            # print(f"    Strikeouts per 9 Innings: {strikeouts2}\n\n")
            player2.update({"SO9": strikeouts2})

        else:
            era2 = None
    else:
        era2 = None

    # pitchers.append(player2)
    if player2.get("name") != '':    
        pitchers.append(player2)
    
    batter = {}
    # print("Away Team Home Run Leaders:\n")
    for leader in y['away_team_leaders_hr']:
        # print(f"  - {leader['name']}: {leader['homeRuns']} HR\n")
        batter = {}
        batter.update({"type": "batter", "name": leader['name'], "team": y['away_name'], "HR": leader['homeRuns']})
        batters.append(batter)
    # print("\nHome Team Home Run Leaders:\n")
    for leader in y['home_team_leaders_hr']:
        # print(f"  - {leader['name']}: {leader['homeRuns']} HR\n")
        batter = {}
        batter.update({"type": "batter", "name": leader['name'], "team": y['home_name'], "HR": leader['homeRuns']})
        batters.append(batter)

    # print("\n")
    


# for x in pitchers:
#     print(x)

# Generate an HTML table from the pitchers list
# html_output = "<html>\n<head>\n<title>Pitchers Overview</title>\n</head>\n<body>\n"
html_output = "<h1>Pitchers Overview</h1>\n"
html_output += "<table border='1'>\n"

# Add table headers
html_output += "<tr>\n"
html_output += "<th>NAME</th>\n"
html_output += "<th>TEAM</th>\n"
html_output += "<th>ERA</th>\n"
html_output += "<th>SO9</th>\n"
html_output += "</tr>\n"

# Add table rows
for pitcher in pitchers:
    html_output += "<tr>\n"
    html_output += f"<td>{pitcher.get('name', 'N/A')}</td>\n"
    html_output += f"<td>{pitcher.get('team', 'N/A')}</td>\n"
    html_output += f"<td>{pitcher.get('ERA', 'N/A')}</td>\n"
    html_output += f"<td>{pitcher.get('SO9', 'N/A')}</td>\n"
    html_output += "</tr>\n"

# Close the table and HTML tags
html_output += "</table>\n"
# html_output += "</body>\n</html>"

# Ensure the "text_output" folder exists
os.makedirs("text_output", exist_ok=True)

# Get yesterday's date
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# File paths
file_name = "match_overviews-PITCHERS.txt"
file_path = f"text_output/{file_name}"
backup_file_path = f"text_output/match_overviews-PITCHERS_{yesterday}.txt"


# Check if match_overviews.txt exists and rename it
if os.path.exists(file_path):
    os.rename(file_path, backup_file_path)

# Open the new match_overviews.txt file in write mode
with open(file_path, "w") as file:
    file.write(html_output)    

print(f"New match overview-PITCHERS saved to {file_path}")
if os.path.exists(backup_file_path):
    print(f"Existing match overview renamed to {backup_file_path}")




# for x in batters:
#     print(x)


# Generate an HTML table from the pitchers list
# html_output2 = "<html>\n<head>\n<title>Pitchers Overview</title>\n</head>\n<body>\n"
html_output2 = "<h1>Batters Overview</h1>\n"
html_output2 += "<table border='1'>\n"

# Add table headers
html_output2 += "<tr>\n"
html_output2 += "<th>NAME</th>\n"
html_output2 += "<th>TEAM</th>\n"
html_output2 += "<th>HRs</th>\n"
html_output2 += "</tr>\n"

# Add table rows
for batter in batters:
    html_output2 += "<tr>\n"
    html_output2 += f"<td>{batter.get('name', 'N/A')}</td>\n"
    html_output2 += f"<td>{batter.get('team', 'N/A')}</td>\n"
    html_output2 += f"<td>{batter.get('HR', 'N/A')}</td>\n"
    html_output2 += "</tr>\n"

# Close the table and HTML tags
html_output2 += "</table>\n"
# html_output2 += "</body>\n</html>"

# Ensure the "text_output" folder exists
os.makedirs("text_output", exist_ok=True)

# Get yesterday's date
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# File paths
file_name2 = "match_overviews-BATTERS.txt"
file_path2 = f"text_output/{file_name2}"
backup_file_path2 = f"text_output/match_overviews-BATTERS_{yesterday}.txt"


# Check if match_overviews.txt exists and rename it
if os.path.exists(file_path2):
    os.rename(file_path2, backup_file_path2)

# Open the new match_overviews.txt file in write mode
with open(file_path2, "w") as file:
    file.write(html_output2)    

print(f"New match overview-BATTERS saved to {file_path2}")
if os.path.exists(backup_file_path2):
    print(f"Existing match overview renamed to {backup_file_path2}")



# --------------

# Read the HTML files
with open("text_output/match_overviews-BATTERS.txt", "r") as file:
    batters_html = file.read()

with open("text_output/match_overviews-PITCHERS.txt", "r") as file:
    pitchers_html = file.read()

# JavaScript for making tables sortable
sortable_script = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;

    const comparer = (idx, asc) => (a, b) => ((v1, v2) =>
        v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)
    )(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

    document.querySelectorAll('th').forEach(th => th.addEventListener('click', (() => {
        const table = th.closest('table');
        Array.from(table.querySelectorAll('tr:nth-child(n+2)'))
            .sort(comparer(Array.from(th.parentNode.children).indexOf(th), this.asc = !this.asc))
            .forEach(tr => table.appendChild(tr) );
    })));
});
</script>
"""

# Add the script to the HTML content
batters_html_sortable = f"{batters_html}\n{sortable_script}"
pitchers_html_sortable = f"{pitchers_html}\n{sortable_script}"

# Save the updated HTML files
with open("text_output/match_overviews-BATTERS.txt", "w") as file:
    file.write(batters_html_sortable)

with open("text_output/match_overviews-PITCHERS.txt", "w") as file:
    file.write(pitchers_html_sortable)

print("Sortable HTML tables saved.")



# %%


# %%



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
backup_file_path = f"text_output/standings_{yesterday}.txt"

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


# %%

import os
from datetime import datetime, timedelta
import json
from collections import defaultdict

# Path to the JSON file
file_path = "text_output/todays_matches.json"

# Check if the file exists
if os.path.exists(file_path):
    # Read the JSON file
    with open(file_path, "r") as json_file:
        todays_matches = json.load(json_file)
        
# Ensure the "text_output" folder exists
os.makedirs("text_output", exist_ok=True)

# Get yesterday's date
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# File paths
bvp_file_path = "text_output/BVP.txt"
backup_file_path = f"text_output/BVP_{yesterday}.txt"

# Check if BVP.html exists and rename it
if os.path.exists(bvp_file_path):
    os.rename(bvp_file_path, backup_file_path)

# Group batter stats by pitcher
pitcher_data = defaultdict(list)

for match in todays_matches:
    if 'BvP_stats' in match:
        for bvp in match['BvP_stats']:
            away = match['away_probable_pitcher']
            home = match['home_probable_pitcher']
            if bvp['pitcher'] == away:
                pitcher_heading = f"Away Pitcher: {bvp['pitcher']} {match['away_name']}"
                batter_team = match['home_name']
            elif bvp['pitcher'] == home:
                pitcher_heading = f"Home Pitcher: {bvp['pitcher']} {match['home_name']}"
                batter_team = match['away_name']
            else:
                continue

            # Append batter stats to the corresponding pitcher
            pitcher_data[pitcher_heading].append({
                "batter": f"{bvp['batter']} ({batter_team})",
                "atbats": bvp['bvp_stats'].get('atbats', 'N/A'),
                "hits": bvp['bvp_stats'].get('hits', 'N/A'),
                "homeruns": bvp['bvp_stats'].get('homeruns', 'N/A'),
                "avg": bvp['bvp_stats'].get('avg', 'N/A'),
                "rbi": bvp['bvp_stats'].get('rbi', 'N/A'),
                "obp": bvp['bvp_stats'].get('obp', 'N/A'),
                "ops": bvp['bvp_stats'].get('ops', 'N/A'),
            })


# JavaScript for making tables sortable
sortable_script = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;

    const comparer = (idx, asc) => (a, b) => ((v1, v2) =>
        v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)
    )(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

    document.querySelectorAll('th').forEach(th => th.addEventListener('click', (() => {
        const table = th.closest('table');
        Array.from(table.querySelectorAll('tr:nth-child(n+2)'))
            .sort(comparer(Array.from(th.parentNode.children).indexOf(th), this.asc = !this.asc))
            .forEach(tr => table.appendChild(tr) );
    })));
});
</script>
"""

# Open the new BVP.html file in write mode
with open(bvp_file_path, "w") as file:
    # Write the opening HTML tags
    file.write("<h1>Batter vs Pitcher Stats</h1>\n")

    # Write data for each pitcher
    for pitcher_heading, batters in pitcher_data.items():
        # Write the heading for the pitcher
        file.write(f"<h3>{pitcher_heading}</h3>\n")

        # Start the table
        file.write("<table border='1'>\n")
        file.write("<tr>\n")
        file.write("<th>Batter</th>\n")
        file.write("<th>AB</th>\n")
        file.write("<th>H</th>\n")
        file.write("<th>HR</th>\n")
        file.write("<th>AVG</th>\n")
        file.write("<th>RBI</th>\n")
        file.write("<th>OBP</th>\n")
        file.write("<th>OPS</th>\n")
        file.write("</tr>\n")

        # Write the batter stats
        for batter in batters:
            file.write("<tr>\n")
            file.write(f"<td>{batter['batter']}</td>\n")
            file.write(f"<td>{batter['atbats']}</td>\n")
            file.write(f"<td>{batter['hits']}</td>\n")
            file.write(f"<td>{batter['homeruns']}</td>\n")
            file.write(f"<td>{batter['avg']}</td>\n")
            file.write(f"<td>{batter['rbi']}</td>\n")
            file.write(f"<td>{batter['obp']}</td>\n")
            file.write(f"<td>{batter['ops']}</td>\n")
            file.write("</tr>\n")

        # Close the table
        file.write("</table>\n")
        file.write("<br>\n")  # Add a line break for better readability
        file.write(sortable_script)

    # Write the closing HTML tags
    file.write("</body>\n</html>\n")

print(f"New BVP file saved to {bvp_file_path}")
if os.path.exists(backup_file_path):
    print(f"Existing BVP file renamed to {backup_file_path}")


# %%
# READ THE CSV DATA FROM THE FILE AND CONVERT IT TO HTML TABLE SAVE TO STREAKS.TXT


import csv
import os
import json
from datetime import datetime, timedelta
from rapidfuzz import fuzz

# Read the CSV file into a list
with open("text_output/hitting-streak.csv", "r", encoding="utf-8") as file:
    csv_data = list(csv.reader(file))

# Extract the first line as table_labels
table_labels = csv_data.pop(0)

# Filter out any lines that match the labels
players_on_a_streak = [row for row in csv_data if row != table_labels]

# -------------------------------

# # open all_players_with_teams.csv and read the data into a list
# with open("text_output/all_players_with_teams.csv", "r", encoding="utf-8") as file:
#     all_players_data = list(csv.reader(file))

# # Compare the players_on_a_streak with all_players_data and add team names to players_on_a_streak
# for player in players_on_a_streak:
#     player_name = player[0]  # Assuming the player's name is in the first column
#     team_name = None
#     best_match_score = 0  # Track the best match score
#     best_match_team = None  # Track the team name of the best match

#     # Search for the player's team in all_players_data using fuzzy matching
#     for all_player in all_players_data:
#         all_player_name = all_player[0]  # Assuming the player's name is in the first column of all_players_data
#         match_score = fuzz.ratio(player_name, all_player_name)  # Calculate the similarity score

#         if match_score > best_match_score:  # Update the best match if the score is higher
#             best_match_score = match_score
#             best_match_team = all_player[1]  # Assuming the team name is in the second column of all_players_data

#     # If the best match score is above a threshold, use the matched team name
#     if best_match_score >= 80:  # Adjust the threshold as needed (e.g., 80 for high confidence)
#         team_name = best_match_team
#     else:
#         team_name = "Unknown Team"  # If no good match is found, add a placeholder

#     # Add the team name to the player's data
#     player.insert(1, team_name)

# table_labels.insert(1,"Team")  # Add the new column label for team names
# # -------------------------------
# # Load the list of teams playing today from the JSON file
# with open("text_output/teams_playing_today.json", "r", encoding="utf-8") as file:
#     teams_playing_today = json.load(file)

# # Filter out rows in players_on_a_streak that don't match the teams playing today
# filtered_players_on_a_streak = []
# for player in players_on_a_streak:
#     player_team = player[1]  # Assuming the team name is in the second column
#     best_match_score = 0
#     best_match_team = None

#     # Search for the player's team in teams_playing_today using fuzzy matching
#     for team in teams_playing_today:
#         match_score = fuzz.ratio(player_team, team)  # Calculate the similarity score

#         if match_score > best_match_score:  # Update the best match if the score is higher
#             best_match_score = match_score
#             best_match_team = team

#     # If the best match score is above a threshold, keep the player
#     if best_match_score >= 80:  # Adjust the threshold as needed
#         filtered_players_on_a_streak.append(player)

# # Replace the original players_on_a_streak with the filtered list
# players_on_a_streak = filtered_players_on_a_streak
# # -------------------------------

# JavaScript for making tables sortable
sortable_script = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;

    const comparer = (idx, asc) => (a, b) => ((v1, v2) =>
        v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)
    )(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

    document.querySelectorAll('th').forEach(th => th.addEventListener('click', (() => {
        const table = th.closest('table');
        Array.from(table.querySelectorAll('tr:nth-child(n+2)'))
            .sort(comparer(Array.from(th.parentNode.children).indexOf(th), this.asc = !this.asc))
            .forEach(tr => table.appendChild(tr) );
    })));
});
</script>
"""

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
html_table += sortable_script  # Add the JavaScript for sorting

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
match_overview_pitchers_path = "text_output/match_overviews-PITCHERS.txt"
match_overview_batters_path = "text_output/match_overviews-BATTERS.txt"
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

with open(match_overview_pitchers_path, "r") as match_overview_pitchers_file:
    match_overview_pitchers_content = match_overview_pitchers_file.read()
    
with open(match_overview_batters_path, "r") as match_overview_batters_file:
    match_overview_batters_content = match_overview_batters_file.read()

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
        <a href="#match-overviews-pitchers">Pitchers</a>
        <a href="#match-overviews-batters">Batters</a>
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
        <h2 id="match-overviews-pitchers">Pitcher Match Overviews</h2>
        <pre>{match_overview_pitchers_content}</pre>
        <h2 id="match-overviews-batters">Batter Match Overviews</h2>
        <pre>{match_overview_batters_content}</pre>
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


