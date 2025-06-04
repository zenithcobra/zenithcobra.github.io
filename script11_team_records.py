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

json_file_path2 = "text_output/teams_playing_today.json"
# Ensure the file exists
if not os.path.exists(json_file_path2):
    raise FileNotFoundError(f"{json_file_path2} does not exist.")

# Read the JSON file into a dictionary
with open(json_file_path2, "r", encoding="utf-8") as file:
    teams_playing_today = json.load(file)

csv_file_path = "text_output/all_all_teams_with_ids.csv"
# Ensure the file exists
if not os.path.exists(csv_file_path):
    raise FileNotFoundError(f"{csv_file_path} does not exist.")

# Read the csv file into a list of lists
import csv
with open(csv_file_path, "r", encoding="utf-8") as file:
    csv_reader = csv.reader(file)
    all_teams_with_ids = [row for row in csv_reader]

teams_with_ids_list = []
for y in teams_playing_today:
    for x in all_teams_with_ids:
        if y == x[3]:
            teams_with_ids_list.append([x[0],y])

# remove duplicates
teams_with_ids_list = list(set(tuple(x) for x in teams_with_ids_list))
# Convert back to list of lists
teams_with_ids_list = [list(x) for x in teams_with_ids_list]



# print(team_name,' -> ',team_record)

list_of_lists = []
for a in teams_with_ids_list:
    # print(a[1])
    # for x in teams_last_10_games.get(a[0]):
    # print(a[0],a[1],x)
    team_dict_key = a[0]
    team_name = a[1]
    team_record = ''
    list_of_previous_games = teams_last_10_games.get(team_dict_key, [])
    for x in list_of_previous_games:
        schedule1 = statsapi.schedule(game_id=x)
        if schedule1[0].get('winning_team') == team_name:
            team_record = team_record + 'W-'
        else:
            team_record = team_record + 'L-'
    list_of_lists.append([team_dict_key, team_name, team_record])

# Get yesterday's date
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# File paths
bvp_file_path = "text_output/teams_record.txt"
backup_file_path = f"text_output/teams_record_{yesterday}.txt"

# Check if BVP.html exists and rename it
if os.path.exists(bvp_file_path):
    os.rename(bvp_file_path, backup_file_path)


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
    # file.write("<h1>Batter vs Pitcher Stats</h1>\n")

    # Write the heading for the pitcher
    # file.write(f"<h3>{pitcher_heading}</h3>\n")

    # Start the table
    file.write("<table border='1'>\n")
    file.write("<tr>\n")
    file.write("<th>Team</th>\n")
    file.write("<th>Record</th>\n")
    file.write("</tr>\n")

    # Write data for each pitcher
    for b in list_of_lists:
        file.write("<tr>\n")
        file.write(f"<td>{b[1]}</td>\n")
        file.write(f"<td>{b[2]}</td>\n")
        file.write("</tr>\n")

    # Close the table
    file.write("</table>\n")
    file.write("<br>\n")  # Add a line break for better readability
    file.write(sortable_script)

    # Write the closing HTML tags
    # file.write("</body>\n</html>\n")

print(f"New BVP file saved to {bvp_file_path}")
if os.path.exists(backup_file_path):
    print(f"Existing BVP file renamed to {backup_file_path}")
