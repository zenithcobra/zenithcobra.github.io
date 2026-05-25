# GET THE MATCH OVERVIEW PART OF THE TEXT FILE TO BE ADDED TO THE INDEX.html file
import statsapi
import os
from datetime import datetime, timedelta
import json
from fractions import Fraction

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
    

# save batters list to a csv file
import csv
import os

# Ensure the "text_output" folder exists
os.makedirs("text_output", exist_ok=True)

# File path for the CSV file
csv_file_path = "text_output/batters_today.csv"

# # Save the batters list to a CSV file
# with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
#     # Define the CSV field names (keys from the batter dictionaries)
#     fieldnames = ["type", "name", "team", "HR"]
    
#     # Create a CSV writer object
#     writer = csv.DictWriter(file, fieldnames=fieldnames)
    
#     # Write the header row
#     writer.writeheader()
    
#     # Write the rows for each batter
#     writer.writerows(batters)

# print(f"Batters saved to {csv_file_path}")

# Save the batters list to a CSV file
with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
    # Define the CSV field names (keys from the batter dictionaries)
    fieldnames = ["type", "name", "team", "HR"]
    
    # Create a CSV writer object
    writer = csv.writer(file)
    
    # Write the header row
    writer.writerow(fieldnames[1:])  # Exclude "type" from the header
    
    # Write the rows for each batter as lists
    for batter in batters:
        writer.writerow([batter["name"], batter["team"], batter["HR"]])

print(f"Batters saved to {csv_file_path}")

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

# -----------------------------
# open batters list to a csv file
import os
import csv
import statsapi

# Ensure the "text_output" folder exists
os.makedirs("text_output", exist_ok=True)

# File path for the CSV file
csv_file_path = "text_output/batters_today.csv"


# Initialize an empty list to store the batters
list_of_batters = []

# Read the CSV file
with open(csv_file_path, mode="r", newline="", encoding="utf-8") as file:
    reader = csv.reader(file)
    
    # Skip the header row
    next(reader)
    
    # Append each row to the list
    for row in reader:
        list_of_batters.append(row)

# for x in list_of_batters:
#     print(x)

holder_of_stats = []
for z in list_of_batters:
    new_list_with_stats = []
    new_list_with_stats.append(z[0])  # name
    new_list_with_stats.append(z[1])  # team
    new_list_with_stats.append(f"{z[2]}")  # hrs

    # Get player ID for the current name
    # players = statsapi.get('sports_players', {'season': 2025, 'gameType': 'W'})['people']
    # player = next((x for x in players if x['fullName'] == z[0]), None)  # Use None as fallback if no match is found
    # beans = statsapi.player_stat_data(next(x['id'] for x in statsapi.get('sports_players',{'season':2025,'gameType':'W'})['people'] if x['fullName']==z[0]), 'hitting', 'season') 

    try:
        beans = statsapi.player_stat_data(next(x['id'] for x in statsapi.get('sports_players',{'season':2025,'gameType':'W'})['people'] if x['fullName']==z[0]), 'hitting', 'season') 
    except StopIteration:
        print(f"No player found with the name '{z}'.")
        beans = None  # Set beans to None or handle it appropriately
    except Exception as e:
        print(f"An error occurred: {e}")
        beans = None  # Set beans to None or handle it appropriately
    try:
        beans2 = statsapi.player_stat_data(next(x['id'] for x in statsapi.get('sports_players',{'season':2024,'gameType':'W'})['people'] if x['fullName']==z[0]), 'hitting', 'season') 
    except StopIteration:
        print(f"No player found with the name '{z}'.")
        beans2 = None  # Set beans to None or handle it appropriately
    except Exception as e:
        print(f"An error occurred: {e}")
        beans2 = None  # Set beans to None or handle it appropriately


    if beans:  # Only proceed if a matching player is found
        # print(beans)    
        for a in beans.get('stats'):
            games_played = float(int(a.get('stats').get('gamesPlayed')))
            hits = float(int(a.get('stats').get('hits')))
            new_list_with_stats.append(f"{int(hits)}")
            hrs = float(int(a.get('stats').get('homeRuns')))
            rbi = float(int(a.get('stats').get('rbi')))
            new_list_with_stats.append(f"{int(rbi)}")
            hrs_per_game = round((hrs / games_played), 3)
            new_list_with_stats.append(f"{hrs_per_game}")
            fhrs_per_game = str(Fraction(round((hrs / games_played), 2)).limit_denominator(7))
            new_list_with_stats.append(f"{fhrs_per_game}")
            hits_per_game = round((hits / games_played), 3)
            new_list_with_stats.append(f"{hits_per_game}")
            fhits_per_game = str(Fraction(round((hits / games_played), 2)).limit_denominator(7))
            new_list_with_stats.append(f"{fhits_per_game}")
            rbis_per_game = round((rbi / games_played), 3)
            new_list_with_stats.append(f"{rbis_per_game}")
            frbis_per_game = str(Fraction(round((rbi / games_played), 2)).limit_denominator(7))
            new_list_with_stats.append(f"{frbis_per_game}")



    if beans2:
        beans2_id = beans2.get('id')
        beans3 = statsapi.player_stat_data(beans2_id, group="hitting", type="season", sportId=1, season=2024)
    
        for b in beans3.get('stats'):
            hrs2 = float(int(b.get('stats').get('homeRuns')))
            games_played2 = float(int(b.get('stats').get('gamesPlayed')))
            hrs_per_game4 = round((hrs2 / games_played2), 2)
            hrs_per_game3 = str(Fraction(round((hrs2 / games_played2), 2)).limit_denominator(7))
            
            new_list_with_stats.append(f"{int(hrs2)}")  
            new_list_with_stats.append(f"{hrs_per_game4}")  
            new_list_with_stats.append(f"{hrs_per_game3}")  
            # print(hrs2)
            # new_list_with_stats.append(f"{int(hrs2)}")  
        
    else:
        print(f"Player '{z[0]}' not found in the sports_players list.")
        new_list_with_stats.append("0")  # Append "0" if player not found
        new_list_with_stats.append("0")  # Append "0" if player not found
        new_list_with_stats.append("0")  # Append "0" if player not found
        
    holder_of_stats.append(new_list_with_stats)

for x in holder_of_stats:
    print(x[11])

# Write the new list with stats to a CSV file
output_file_path = "text_output/updated_batters_with_stats.csv"
with open(output_file_path, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    # Write the header
    writer.writerow(["Name", "Team", "Hrs", "Hits", "RBI", "HRpg", "fHRpg","Hpg", "fHpg", "RBIpg", "fRBIpg", "HR24","HR24pg","fHR24pg"])
    
    # Write the data
    for i in holder_of_stats:
        writer.writerow(i)
print(f"Updated batters with stats written to {output_file_path}")
# -----------------------------



# Generate an HTML table from the pitchers list
# html_output2 = "<html>\n<head>\n<title>Pitchers Overview</title>\n</head>\n<body>\n"
html_output2 = "<h1>Batters Overview</h1>\n"
html_output2 += "<table border='1'>\n"

# Add table headers
html_output2 += "<tr>\n"
html_output2 += "<th>NAME</th>\n"
html_output2 += "<th>TEAM</th>\n"
html_output2 += "<th>HRs</th>\n"
html_output2 += "<th>HITS</th>\n"
html_output2 += "<th>RBI</th>\n"
html_output2 += "<th>HRpg</th>\n"
html_output2 += "<th>fHRpg</th>\n"
html_output2 += "<th>Hpg</th>\n"
html_output2 += "<th>fHpg</th>\n"
html_output2 += "<th>RBIpg</th>\n"
html_output2 += "<th>fRBIpg</th>\n"
html_output2 += "<th>HR24</th>\n"
html_output2 += "<th>HR24pg</th>\n"
html_output2 += "<th>fHR24pg</th>\n"
html_output2 += "</tr>\n"

# Add table rows
for batter in holder_of_stats:
    html_output2 += "<tr>\n"
    html_output2 += f"<td>{batter[0]}</td>\n"
    html_output2 += f"<td>{batter[1]}</td>\n"
    html_output2 += f"<td>{batter[2]}</td>\n"
    html_output2 += f"<td>{batter[3]}</td>\n"
    html_output2 += f"<td>{batter[4]}</td>\n"
    html_output2 += f"<td>{batter[5]}</td>\n"
    html_output2 += f"<td>{batter[6]}</td>\n"
    html_output2 += f"<td>{batter[7]}</td>\n"
    html_output2 += f"<td>{batter[8]}</td>\n"
    html_output2 += f"<td>{batter[9]}</td>\n"
    html_output2 += f"<td>{batter[10]}</td>\n"
    html_output2 += f"<td>{batter[11]}</td>\n"
    html_output2 += f"<td>{batter[12]}</td>\n"
    html_output2 += f"<td>{batter[13]}</td>\n"
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


