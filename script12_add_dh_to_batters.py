import statsapi
from datetime import datetime, timedelta

# Get today's date
mlb_date = datetime.now().strftime("%m/%d/%Y")
schedule = statsapi.schedule(start_date=mlb_date, end_date=mlb_date)

# yesterday = (datetime.now() - timedelta(days=9)).strftime("%Y-%m-%d")
# schedule = statsapi.schedule(start_date=yesterday, end_date=yesterday)

games = []
for x in schedule:
    json_string = statsapi.get("game", {"gamePk": x.get('game_id')})
    games.append(json_string)

# Fetch the JSON string
# json_string = statsapi.get("game", {"gamePk": 777807})
# json_string = games[1]  # Assuming we want the first game in the schedule
list_of_names = []
for x in games:
    beans = []
    json_string = x
    livedata = json_string.get('liveData').get('boxscore').get('teams')

    # Extract abbreviations for away team players
    # print("Away Team Abbreviations:")
    for player_id, player_data in livedata.get('away').get('players').items():
        full_name = player_data.get('person', {}).get('fullName', 'Unknown')
        abbreviation = player_data.get('position', {}).get('abbreviation', 'N/A')  # Default to 'N/A' if not found
        if abbreviation == 'DH':
            # print(f"Name: {full_name}, Player ID: {player_id}, Abbreviation: {abbreviation}")
            beans.append(full_name)
    # Extract team names
    # Extract abbreviations for home team players
    # print("\nHome Team Abbreviations:")
    for player_id, player_data in livedata.get('home').get('players').items():
        full_name = player_data.get('person', {}).get('fullName', 'Unknown')
        abbreviation = player_data.get('position', {}).get('abbreviation', 'N/A')  # Default to 'N/A' if not found
        if abbreviation == 'DH':
            # print(f"Name: {full_name}, Player ID: {player_id}, Abbreviation: {abbreviation}")
            beans.append(full_name)
    list_of_names.append(beans)

# for z in list_of_names:
#     print(z)

all_names = []
for x in list_of_names:
    for y in x:
        all_names.append(y)

from bs4 import BeautifulSoup

# File path for the HTML table
file_path = "text_output/match_overviews-BATTERS.txt"

# Read the HTML file
with open(file_path, "r", encoding="utf-8") as file:
    html_content = file.read()

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Find all table cells (assuming names are in <td> tags)
table_cells = soup.find_all("td")

# Modify names in the table if they appear in the all_names list
for cell in table_cells:
    if cell.text.strip() in all_names:  # Check if the name is in the all_names list
        cell.string = f"{cell.text.strip()} (DH)"  # Append "(DH)" to the name

# Save the modified HTML back to the file
with open(file_path, "w", encoding="utf-8") as file:
    file.write(str(soup))

print(f"Updated table saved to {file_path}")