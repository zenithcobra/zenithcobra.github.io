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

# for x in all_names:
#     print(x)

# --------------
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# # List of names to match
# all_names = ["John Doe", "Jane Smith"]  # Replace with your actual list of names

# File paths
input_file_path = "text_output/match_overviews-BATTERS.txt"
output_file_path = "text_output/DH_BATTERS.txt"

# Check if the output file exists
if os.path.exists(output_file_path):
    # Rename the existing file with yesterday's date
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    renamed_file_path = f"text_output/DH_BATTERS_{yesterday_date}.txt"
    os.rename(output_file_path, renamed_file_path)

# Read the input HTML file
with open(input_file_path, "r", encoding="utf-8") as file:
    html_content = file.read()

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Find the table in the HTML
table = soup.find("table")

# Create a new table for matching rows with a border of 1
new_table = BeautifulSoup('<table border="1"></table>', "html.parser").table

if table:
    # Copy the header row to the new table
    header_row = table.find("tr")
    if header_row:
        new_table.append(header_row)

    # Iterate through rows and find matches
    rows = table.find_all("tr")[1:]  # Skip the header row
    for row in rows:
        player_name_cell = row.find("td")  # Assuming the player's name is in the first column
        if player_name_cell:
            player_name = player_name_cell.text.strip()
            if player_name.startswith("(DH)"):
                # Prefix the name with "(DH)"
                player_name_cell.string = f"{player_name}"
                # Append the row to the new table
                new_table.append(row)

# Add the sortable script to the HTML
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

# Save the new table to the output file
with open(output_file_path, "w", encoding="utf-8") as file:
    file.write(str(new_table))
    file.write(sortable_script)

print(f"Filtered table saved to {output_file_path}")
# --------------

from bs4 import BeautifulSoup

# File path for the HTML table
file_path = "text_output/match_overviews-BATTERS.txt"

# Read the HTML file
with open(file_path, "r", encoding="utf-8") as file:
    html_content = file.read()

# -----------
# # Parse the HTML content using BeautifulSoup
# soup = BeautifulSoup(html_content, "html.parser")


# # Find the table in the HTML
# table = soup.find("table")

# if table:
#     # Add a new header cell for "DH"
#     header_row = table.find("tr")
#     if header_row:
#         dh_header = soup.new_tag("th")
#         dh_header.string = "DH"
#         header_row.append(dh_header)

#     # Add a new cell to each row for the "DH" column
#     rows = table.find_all("tr")[1:]  # Skip the header row
#     for row in rows:
#         player_name = row.find("td").text.strip()  # Assuming the player's name is in the first column
#         dh_cell = soup.new_tag("td")
#         if player_name in all_names:
#             dh_cell.string = "DH"
#         row.append(dh_cell)

# # Save the modified HTML back to the file
# with open(file_path, "w", encoding="utf-8") as file:
#     file.write(str(soup))

# print(f"Updated table saved to {file_path}")

# ---------------

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Find all table cells (assuming names are in <td> tags)
table_cells = soup.find_all("td")

# Modify names in the table if they appear in the all_names list
for cell in table_cells:
    if cell.text.strip() in all_names:  # Check if the name is in the all_names list
        cell.string = f"(DH) {cell.text.strip()}"  # Append "(DH)" to the name

# Save the modified HTML back to the file
with open(file_path, "w", encoding="utf-8") as file:
    file.write(str(soup))

print(f"Updated table saved to {file_path}")