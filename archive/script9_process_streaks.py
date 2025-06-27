# %%
# READ THE CSV DATA FROM THE FILE AND CONVERT IT TO HTML TABLE SAVE TO STREAKS.TXT


import csv
import os
import json
import statsapi
from datetime import datetime, timedelta
from rapidfuzz import fuzz

# Read the CSV file into a list
with open("text_output/hitting-streak.csv", "r", encoding="utf-8") as file:
    csv_data = list(csv.reader(file))

# Extract the first line as table_labels
table_labels = csv_data.pop(0)
table_labels.insert(1, "team")

# Filter out any lines that match the labels
players_on_a_streak = [row for row in csv_data if row != table_labels]

holder = []
for z in players_on_a_streak:
    filtered = []
    try:
        team = statsapi.lookup_team(statsapi.lookup_player(z[0])[0].get('currentTeam').get('id'))[0].get('name')
        for a in z:
            filtered.append(a)
        filtered.insert(1, team)
        print(team)
    except Exception as e:
        print(f"Error processing player {z[0]}: {e}")
        # Handle the error as needed (e.g., log it, skip the player, etc.)
        team = "..."
        for a in z:
            filtered.append(a)
        filtered.insert(1, "Unknown Team")
    holder.append(filtered)
players_on_a_streak = holder
# -------------------------------

# # open all_players_with_teams.csv and read the data into a list
# with open("text_output/all_players_with_teams.csv", "r", encoding="utf-8") as file:
#     all_players_data = list(csv.reader(file))

# # Compare the players_on_a_streak with all_players_data and add team names to players_on_a_streak
# for player in players_on_a_streak:
#     player_name = player[0]  # Assuming the player's name is in the first column
#     tea)
m_name = None
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
with open("text_output/teams_playing_today.json", "r", encoding="utf-8") as file:
    teams_playing_today = json.load(file)

# Filter out rows in players_on_a_streak that don't match the teams playing today
filtered_players_on_a_streak = []
for player in players_on_a_streak:
    player_team = player[1]  # Assuming the team name is in the second column
    best_match_score = 0
    best_match_team = None

    # Search for the player's team in teams_playing_today using fuzzy matching
    for team in teams_playing_today:
        match_score = fuzz.ratio(player_team, team)  # Calculate the similarity score

        if match_score > best_match_score:  # Update the best match if the score is higher
            best_match_score = match_score
            best_match_team = team

    # If the best match score is above a threshold, keep the player
    if best_match_score >= 80:  # Adjust the threshold as needed
        filtered_players_on_a_streak.append(player)

# Replace the original players_on_a_streak with the filtered list
players_on_a_streak = filtered_players_on_a_streak
# -------------------------------

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


