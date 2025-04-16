# Standing and schedule into text file
import statsapi
from datetime import datetime, timedelta

# Get current date
mlb_date = datetime.now().strftime("%m/%d/%Y")
file_date = datetime.now().strftime("%Y-%m-%d")
import os
from datetime import datetime, timedelta
import statsapi

# File name with current date
file_date = datetime.now().strftime("%Y-%m-%d")
file_name = f"MLB STANDINGS AND SCHEDULE.txt"

# Get yesterday's schedule
oneday = timedelta(days=1)
yesterday = datetime.now().date() - oneday
yschedule = statsapi.schedule(start_date=yesterday, end_date=yesterday)

# Get today's schedule
mlb_date = datetime.now().strftime("%m/%d/%Y")
schedule = statsapi.schedule(start_date=mlb_date, end_date=mlb_date)

# Prepare content to write
yesterday_schedule_content = "\nYesterday's Schedule:\n" + "\n".join(
    f'{x.get("game_id")} -> {x.get("summary")}' for x in yschedule
)
standings_content = (
    "MLB Standings:\n"
    + statsapi.standings(leagueId=103, date=mlb_date)
    + statsapi.standings(leagueId=104, date=mlb_date)
)
today_schedule_content = "Today's Schedule:\n" + "\n".join(
    f'{x.get("game_id")} -> {x.get("summary")}' for x in schedule
)

new_content = (
    standings_content + "\n" + today_schedule_content + "\n" + yesterday_schedule_content
)

# Check if the file exists
if os.path.exists(file_name):
    with open(file_name, "r") as file:
        existing_content = file.read()

    # Prepend only if new content is not already in the file
    if new_content not in existing_content:
        with open(file_name, "w") as file:
            file.write(new_content + "\n" + existing_content)
else:
    # Write new content if the file doesn't exist
    with open(file_name, "w") as file:
        file.write(new_content)

print(f"Output written to {file_name}")

# update split into 2 jays text files 1 for past game highlights and 1 for future game stats

# JAYS INFO NEW TEXT FILE

import datetime
import os

oneday = datetime.timedelta(days=1)
yesterday = datetime.date.today() - oneday

# HIGHLIGHTS BY GAME ID
import statsapi
yschedule = statsapi.schedule(start_date=yesterday, end_date=yesterday)

# File to store the report
file_name = "BLUE JAYS HISTORY.txt"

# Collect all outputs in a list
output_lines = []

for x in yschedule:
    if 'Toronto' in x.get('summary'):
        game_id = x.get('game_id')

        output_lines.append(statsapi.roster(141))
        output_lines.append('HomeRuns')
        output_lines.append(statsapi.team_leaders(141,'homeRuns',limit=25,season=2025))
        output_lines.append('Batting')
        output_lines.append(statsapi.team_leaders(141,'battingAverage',limit=25,season=2025))
        output_lines.append('On Base Plus Slugging')
        output_lines.append(statsapi.team_leaders(141,'onBasePlusSlugging',limit=25,season=2025))
        output_lines.append('Walks')
        output_lines.append(statsapi.team_leaders(141,'walks',limit=25,season=2025))
        output_lines.append(statsapi.game_highlights(statsapi.next_game(141)))
        output_lines.append(statsapi.boxscore(statsapi.next_game(141)))
        for keys, values in x.items():
            output_lines.append(f'{str(keys):<25} -> {str(values)}')
        
        output_lines.append(' ')
        output_lines.append(statsapi.linescore(game_id))
        output_lines.append(' ')
        output_lines.append(statsapi.game_scoring_plays(game_id))  # enter game id
        output_lines.append(' ')
        output_lines.append(statsapi.boxscore(game_id))  # enter game id
        output_lines.append(' ')
        output_lines.append(statsapi.game_highlights(game_id))  # enter game id



# Combine all outputs into a single string
output_text = "\n".join(map(str, output_lines))

# Check if the file exists
if os.path.exists(file_name):
    # Read the existing content
    with open(file_name, "r") as file:
        existing_content = file.read()
    # Prepend the new content to the existing content
    new_content = output_text + "\n\n" + existing_content
else:
    # If the file doesn't exist, just use the new content
    new_content = output_text

# Write the updated content back to the file
with open(file_name, "w") as file:
    file.write(new_content)

print(f"Output written to {file_name}")
# import statsapi
# import pandas as pd

# # Get roster data
# x = statsapi.roster(141)
# y = x.splitlines()

# list_of_players_in_r = []
# for z in y:
#     line = z.split('  ')
#     list_of_players_in_r.append(line[2].strip())

# # List to store player stats dictionaries
# player_stats = []

# for a in list_of_players_in_r:
#     # Get player stats dictionary
#     player_id = next(x['id'] for x in statsapi.get('sports_players', {'season': 2025, 'gameType': 'W'})['people'] if x['fullName'] == a)
#     stats = statsapi.player_stat_data(player_id, 'hitting', 'career')
#     player_stats.append(stats)

# # Convert list of dictionaries to a pandas DataFrame
# df = pd.DataFrame(player_stats)

# # Write the DataFrame to an Excel file
# output_file = "MLB_Player_Stats.xlsx"
# df.to_excel(output_file, index=False)

# print(f"Player stats written to {output_file}")

import stats_helper
import statsapi
import os

# Get current and yesterday's date
date_time_str = stats_helper.get_current_date()
yesterdays_date_str = stats_helper.get_yesterday_date()

# File name
file_name = "GAME REPORTS.txt"

# Collect the new content to write
new_content = []
all_mlb_teams_yesterday = stats_helper.mlb_teams_for_day_list(yesterdays_date_str)

for x in all_mlb_teams_yesterday:
    new_content.append("->-<->-<->-<->-<->-<->-<-")
    for keys, values in x.items():
        new_content.append(f"{keys} -> {values}")
    new_content.append("   -   ")
    new_content.append(statsapi.linescore(x.get('game_id')))
    new_content.append("   -   ")
    new_content.append(statsapi.boxscore(x.get('game_id')))
    new_content.append(statsapi.game_highlights(x.get('game_id')))
new_content = "\n".join(new_content)

# Check if the file exists
if os.path.exists(file_name):
    with open(file_name, "r") as f:
        existing_content = f.read()

    # Prepend only if new content is not already in the file
    if new_content not in existing_content:
        with open(file_name, "w") as f:
            f.write(new_content + "\n" + existing_content)
else:
    # Write new content if the file doesn't exist
    with open(file_name, "w") as f:
        f.write(new_content)

print(f"Output written to {file_name}")

import os
import statsapi
import stats_helper
from datetime import datetime

# File name
file_name = "LEAGUE LEADERS.txt"

# Collect the new content to write
mlb_games_today = []
mlb_date = datetime.now().strftime("%m/%d/%Y")
sched = statsapi.schedule(start_date=mlb_date, end_date=mlb_date)
for x in sched:
    mlb_games_today.append(x.get('away_name'))
    mlb_games_today.append(x.get('home_name'))

beans = statsapi.league_leader_data('battingAverage', season=2025, limit=50, statGroup='hitting')
stats = []
names = []
for x in beans:
    if x[2] in mlb_games_today:
        stringy = str(x[1]) + "-" + str(x[2]) + "-AVG 2025-" + str(x[3])
        stats.append(stringy)
        names.append(x[1])

# Collect stats for other categories and years
categories = [
    ('battingAverage', 'AVG'),
    ('homeRuns', 'HR'),
    ('gamesPlayed', 'aGP'),
    ('onBasePlusSlugging', 'OBPS'),
    ('strikeOuts', 'SO'),
    ('hits', 'HITS'),
]
years = [2025, 2024]

for category, label in categories:
    for year in years:
        beans = statsapi.league_leader_data(category, season=year, limit=75, statGroup='hitting')
        for x in beans:
            if x[1] in names:
                stringy = f"{x[1]}-{x[2]}-{label} {year}-{x[3]}"
                stats.append(stringy)

# Sort stats
stats.sort()

# Format the stats for writing
formatted_stats = "\n".join(
    f"{x.split('-')[0]:<20} {x.split('-')[1]:<20} {x.split('-')[2]:<12} {x.split('-')[3]:<5}" for x in stats
)

# Check if the file exists
if os.path.exists(file_name):
    with open(file_name, "r") as file:
        existing_content = file.read()

    # Prepend only if new content is not already in the file
    if formatted_stats not in existing_content:
        with open(file_name, "w") as file:
            file.write(formatted_stats + "\n\n" + existing_content)
else:
    # Write new content if the file doesn't exist
    with open(file_name, "w") as file:
        file.write(mlb_date + "\n")
        file.write(formatted_stats)

print(f"Output written to {file_name}")

from collections import defaultdict
import os
from datetime import datetime

# File path
file_path = "LEAGUE LEADERS.txt"
mlb_date_str = datetime.now().strftime("%m/%d/%Y")

# Data structure to store player stats
player_stats = defaultdict(lambda: defaultdict(list))

# Read the file and parse the data
with open(file_path, "r") as file:
    for line in file:
        parts = line.strip().split()
        if len(parts) < 6:
            continue  # Skip invalid lines
        
        # Extract data
        name = " ".join(parts[:2])  # First and last name
        team = " ".join(parts[2:-3])  # Team name
        stat_type = parts[-3]  # Statistic type (e.g., AVG, HR)
        year = parts[-2]  # Year
        value = parts[-1]  # Statistic value
        
        # Store the data
        player_stats[name][stat_type].append((year, value))

# Function to calculate a player's performance score (example: based on AVG and OBPS)
def calculate_score(stats):
    avg = max(float(v[1]) for v in stats.get("AVG", [("0", "0")]))
    obps = max(float(v[1]) for v in stats.get("OBPS", [("0", "0")]))
    return avg + obps  # Example scoring formula

# Rank players based on their performance score
ranked_players = sorted(player_stats.items(), key=lambda x: calculate_score(x[1]), reverse=True)

# Prepare the output
line_str = "Top 5 Players: " + mlb_date_str
output_lines = [line_str]
for i, (player, stats) in enumerate(ranked_players[:5], start=1):
    output_lines.append(f"{i}. {player}")
    for stat_type, values in stats.items():
        output_lines.append(f"   {stat_type}: {', '.join([f'{v[0]}: {v[1]}' for v in values])}")
output_lines.append("")  # Add a blank line at the end

# File to write the output
output_file = "TOP LEAGUE LEADERS.txt"

# Prepend the data to the file if it exists
if os.path.exists(output_file):
    with open(output_file, "r") as file:
        existing_content = file.read()
    with open(output_file, "w") as file:
        file.write("\n".join(output_lines) + "\n" + existing_content)
else:
    with open(output_file, "w") as file:
        file.write("\n".join(output_lines) + "\n")

print(f"Output written to {output_file}")

import os

# List of text files to convert
text_files = ["LEAGUE LEADERS.txt", "BLUE JAYS HISTORY.txt","GAME REPORTS.txt", "TOP LEAGUE LEADERS.txt", "MLB STANDINGS AND SCHEDULE.txt"]

# Directory to store the generated HTML files
output_dir = "html_output"
os.makedirs(output_dir, exist_ok=True)

# Flexbox CSS for stretchable text
flexbox_css = """
<style>
    
</style>
"""

# Generate HTML files for each text file
html_files = []
for text_file in text_files:
    if not os.path.exists(text_file):
        print(f"File {text_file} not found, skipping.")
        continue

    # Read the content of the text file
    with open(text_file, "r") as file:
        content = file.read()

    # Create an HTML file
    html_filename = os.path.splitext(text_file)[0] + ".html"
    html_filepath = os.path.join(output_dir, html_filename)
    html_files.append(html_filename)

    # Write the HTML content
    with open(html_filepath, "w") as html_file:
        html_file.write(f"<!DOCTYPE html>\n<html>\n<head>\n<title>{text_file}</title>\n{flexbox_css}</head>\n<body>\n")
        html_file.write(f"<div class='content'>\n<pre>{content}</pre>\n</div>\n")
        html_file.write(f"<a href='index.html'>Back to Index</a>\n</body>\n</html>")

# Generate the index.html file
index_filepath = os.path.join(output_dir, "index.html")
with open(index_filepath, "w") as index_file:
    index_file.write(f"<!DOCTYPE html>\n<html>\n<head>\n<title>Index</title>\n{flexbox_css}</head>\n<body>\n")
    index_file.write("<div class='content'>\n<h1>Index</h1>\n<ul>\n")
    for html_file in html_files:
        index_file.write(f"<li><a href='{html_file}'>{html_file}</a></li>\n")
    index_file.write("</ul>\n</div>\n</body>\n</html>")

print(f"HTML files have been generated in the '{output_dir}' directory.")