
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