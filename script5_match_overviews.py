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



