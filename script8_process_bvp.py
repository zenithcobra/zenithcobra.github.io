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
    # file.write("</body>\n</html>\n")

print(f"New BVP file saved to {bvp_file_path}")
if os.path.exists(backup_file_path):
    print(f"Existing BVP file renamed to {backup_file_path}")


