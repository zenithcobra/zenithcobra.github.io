# %%
## WRITE EVERYTHING TO INDEX.html
import os
from datetime import datetime

date = datetime.now().strftime("%Y-%m-%d")
 
# Ensure the "docs" folder exists
os.makedirs("docs", exist_ok=True)

# File paths
parlay_banned_list_path = "text_output/parlay_banned_list.txt" 
yesterdays_report_path = "text_output/Yesterdays_Report.txt"
standings_path = "text_output/standings.txt"
today_schedule_path = "text_output/todays_schedule.txt"
match_overview_pitchers_path = "text_output/match_overviews-PITCHERS.txt"
match_overview_batters_path = "text_output/match_overviews-BATTERS.txt"
dh_batters_path = "text_output/DH_BATTERS.txt"
bvp_path = "text_output/BVP2.txt"
streaks_path = "text_output/streaks.txt"

output_html_path = "docs/index2.html"

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

with open(dh_batters_path, "r") as dh_batters_file:
    dh_batters_content = dh_batters_file.read()

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
        <a href="#dh-batters">DH's</a>
        <a href="#bvp-stats">BvP</a>
        <a href="#streaks">Streaks</a>
        <a href="#checked-section">Checked</a>
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
        <h2>MLB Report {date}</h2>
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
        <h2 id="dh-batters">DH Batters</h2>
        <pre>{dh_batters_content}</pre>
        <h2 id="bvp-stats">Batter vs Pitcher Stats</h2>
        <pre>{bvp_content}</pre>
        <h2 id="streaks">Streaks</h2>
        <pre>{streaks_content}</pre>

    </div>
</body>
</html>
"""

# Write the HTML content to the output file
with open(output_html_path, "w") as output_file:
    output_file.write(html_content)

print(f"HTML file saved to {output_html_path}")

# --------------------------------------------------------
# PArt 2: Add checkboxes to the tables in index2.html
# --------------------------------------------------------

# from bs4 import BeautifulSoup

# # Read the input HTML file
# with open("docs/index2.html", "r", encoding="utf-8") as file:
#     soup = BeautifulSoup(file, "html.parser")

# # Find all tables in the HTML
# tables = soup.find_all("table")

# # Add a checkbox column and unique IDs to each table
# for table_index, table in enumerate(tables):
#     # Add a unique ID to the table
#     table['id'] = f"table_{table_index}"

#     # Add a header for the checkbox column
#     header_row = table.find("tr")
#     if header_row:
#         checkbox_header = soup.new_tag("th")
#         checkbox_header.string = "Select"
#         header_row.insert(0, checkbox_header)

#     # Add a checkbox to each row
#     rows = table.find_all("tr")[1:]  # Skip the header row
#     for row_index, row in enumerate(rows):
#         checkbox_cell = soup.new_tag("td")
#         checkbox = soup.new_tag("input", type="checkbox", onclick="saveCheckboxState(this)")
#         checkbox_cell.append(checkbox)
#         row.insert(0, checkbox_cell)

# # Add JavaScript to handle saving checkbox states in cookies
# script = soup.new_tag("script")
# script.string = """
# function saveCheckboxState(checkbox) {
#     const table = checkbox.closest('table');
#     const tableId = table.id;
#     const rowIndex = Array.from(checkbox.closest('tr').parentNode.children).indexOf(checkbox.closest('tr'));
#     const checkboxState = checkbox.checked ? '1' : '0';

#     // Set cookie with 1-day expiration
#     const expirationDate = new Date();
#     expirationDate.setDate(expirationDate.getDate() + 1); // 1 day from now
#     document.cookie = `${tableId}_row_${rowIndex}=${checkboxState}; path=/; expires=${expirationDate.toUTCString()}`;
# }

# function loadCheckboxStates() {
#     const cookies = document.cookie.split('; ');
#     cookies.forEach(cookie => {
#         const [key, value] = cookie.split('=');
#         if (key.includes('_row_')) {
#             const [tableId, _, rowIndex] = key.split('_');
#             const table = document.getElementById(tableId);
#             if (table) {
#                 const row = table.querySelectorAll('tr')[rowIndex];
#                 if (row) {
#                     const checkbox = row.querySelector('input[type="checkbox"]');
#                     if (checkbox) {
#                         checkbox.checked = value === '1';
#                     }
#                 }
#             }
#         }
#     });
# }

# window.onload = loadCheckboxStates;
# """
# soup.body.append(script)

# # Write the modified HTML to a new file
# with open("docs/index.html", "w", encoding="utf-8") as file:
#     file.write(str(soup))

from bs4 import BeautifulSoup

# Read the input HTML file
with open("docs/index2.html", "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "html.parser")

# Find all tables in the HTML
tables = soup.find_all("table")

# # Add a checkbox column and unique IDs to each table
# for table_index, table in enumerate(tables):
#     # Add a unique ID to the table
#     table['id'] = f"table_{table_index}"

#     # Add a header for the checkbox column
#     header_row = table.find("tr")
#     if header_row:
#         checkbox_header = soup.new_tag("th")
#         checkbox_header.string = "Select"
#         header_row.insert(0, checkbox_header)

#     # Add a checkbox to each row
#     rows = table.find_all("tr")[1:]  # Skip the header row
#     for row_index, row in enumerate(rows):
#         checkbox_cell = soup.new_tag("td")
#         checkbox = soup.new_tag("input", type="checkbox", onclick="handleCheckboxClick(this)")
#         checkbox_cell.append(checkbox)
#         row.insert(0, checkbox_cell)

# # # Add a "Checked" section at the bottom of the page
# # checked_section = soup.new_tag("div", id="checked-section")
# # checked_heading = soup.new_tag("h2")
# # checked_heading.string = "Checked"
# # checked_section.append(checked_heading)
# # checked_table = soup.new_tag("table", id="checked-table", border="1")
# # checked_section.append(checked_table)
# # soup.body.append(checked_section)
# # Add a "Checked" section at the bottom of the page
# checked_section = soup.new_tag("div", id="checked-section")
# checked_heading = soup.new_tag("h2")
# checked_heading.string = "Checked"
# checked_section.append(checked_heading)

# # Create a <pre> tag to wrap the table
# pre_tag = soup.new_tag("pre")
# checked_table = soup.new_tag("table", id="checked-table", border="1")
# pre_tag.append(checked_table)  # Add the table inside the <pre> tag
# checked_section.append(pre_tag)  # Add the <pre> tag to the section

# soup.body.append(checked_section)
# para_tag = soup.new_tag("pre")
# para_tag.string = "\n\n\n\n\n\n\n\n"
# soup.body.append(para_tag)
# # Locate the "Streaks" section in the HTML
# # streaks_section = soup.find("h2", id="streaks")

# # # Add a "Checked" section after the "Streaks" section
# # checked_section = soup.new_tag("div", id="checked-section")
# # checked_heading = soup.new_tag("h2")
# # checked_heading.string = "Checked"
# # checked_section.append(checked_heading)

# # # Create a <pre> tag to wrap the table
# # pre_tag = soup.new_tag("pre")
# # checked_table = soup.new_tag("table", id="checked-table", border="1")
# # pre_tag.append(checked_table)  # Add the table inside the <pre> tag
# # checked_section.append(pre_tag)  # Add the <pre> tag to the section

# # # Insert the "Checked" section after the "Streaks" section
# # if streaks_section:
# #     streaks_section.insert_after(checked_section)
# # else:
# #     # If "Streaks" section is not found, append "Checked" section to the body
# #     soup.body.append(checked_section)
# # # Add JavaScript to handle copying rows to the "Checked" section
# # script = soup.new_tag("script")
# # script.string = """
# # function handleCheckboxClick(checkbox) {
# #     const row = checkbox.closest('tr');
# #     const checkedTable = document.getElementById('checked-table');

# #     if (checkbox.checked) {
# #         // Clone the row and add it to the "Checked" table
# #         const clonedRow = row.cloneNode(true);
# #         clonedRow.querySelector('input[type="checkbox"]').remove(); // Remove the checkbox from the cloned row
# #         checkedTable.appendChild(clonedRow);
# #     } else {
# #         // Remove the row from the "Checked" table if it exists
# #         const rows = checkedTable.querySelectorAll('tr');
# #         rows.forEach(checkedRow => {
# #             if (checkedRow.isEqualNode(row.cloneNode(true))) {
# #                 checkedRow.remove();
# #             }
# #         });
# #     }
# # }

# # function loadCheckboxStates() {
# #     const cookies = document.cookie.split('; ');
# #     cookies.forEach(cookie => {
# #         const [key, value] = cookie.split('=');
# #         if (key.includes('_row_')) {
# #             const [tableId, _, rowIndex] = key.split('_');
# #             const table = document.getElementById(tableId);
# #             if (table) {
# #                 const row = table.querySelectorAll('tr')[rowIndex];
# #                 if (row) {
# #                     const checkbox = row.querySelector('input[type="checkbox"]');
# #                     if (checkbox) {
# #                         checkbox.checked = value === '1';
# #                         if (checkbox.checked) {
# #                             const checkedTable = document.getElementById('checked-table');
# #                             const clonedRow = row.cloneNode(true);
# #                             clonedRow.querySelector('input[type="checkbox"]').remove();
# #                             checkedTable.appendChild(clonedRow);
# #                         }
# #                     }
# #                 }
# #             }
# #         }
# #     });
# # }

# # window.onload = loadCheckboxStates;
# # """
# # soup.body.append(script)

# # Add JavaScript to handle saving checkbox states in localStorage
# script = soup.new_tag("script")
# script.string = """
# function handleCheckboxClick(checkbox) {
#     const row = checkbox.closest('tr');
#     const table = checkbox.closest('table');
#     const tableId = table.id;
#     const rowIndex = Array.from(table.querySelectorAll('tr')).indexOf(row);
#     const checkedTable = document.getElementById('checked-table');

#     if (checkbox.checked) {
#         // Save the checkbox state in localStorage
#         localStorage.setItem(`${tableId}_row_${rowIndex}`, '1');

#         // Clone the row and add it to the "Checked" table
#         const clonedRow = row.cloneNode(true);
#         clonedRow.querySelector('input[type="checkbox"]').remove(); // Remove the checkbox from the cloned row
#         checkedTable.appendChild(clonedRow);
#     } else {
#         // Remove the checkbox state from localStorage
#         localStorage.removeItem(`${tableId}_row_${rowIndex}`);

#         // Remove the row from the "Checked" table if it exists
#         const rows = checkedTable.querySelectorAll('tr');
#         rows.forEach(checkedRow => {
#             if (checkedRow.isEqualNode(row.cloneNode(true))) {
#                 checkedRow.remove();
#             }
#         });
#     }
# }

# function loadCheckboxStates() {
#     // Iterate through all keys in localStorage
#     for (let i = 0; i < localStorage.length; i++) {
#         const key = localStorage.key(i);
#         if (key.includes('_row_')) {
#             const [tableId, _, rowIndex] = key.split('_');
#             const table = document.getElementById(tableId);
#             if (table) {
#                 const row = table.querySelectorAll('tr')[rowIndex];
#                 if (row) {
#                     const checkbox = row.querySelector('input[type="checkbox"]');
#                     if (checkbox) {
#                         checkbox.checked = localStorage.getItem(key) === '1';
#                         if (checkbox.checked) {
#                             const checkedTable = document.getElementById('checked-table');
#                             const clonedRow = row.cloneNode(true);
#                             clonedRow.querySelector('input[type="checkbox"]').remove();
#                             checkedTable.appendChild(clonedRow);
#                         }
#                     }
#                 }
#             }
#         }
#     }
# }

# window.onload = loadCheckboxStates;
# """
# soup.body.append(script)

# Find all tables in the HTML
tables = soup.find_all("table")

# Add three checkbox columns and unique IDs to each table
for table_index, table in enumerate(tables):
    # Add a unique ID to the table
    table['id'] = f"table_{table_index}"

    # Add headers for the checkbox columns
    header_row = table.find("tr")
    h_r_names = ['HRS','H','RBI']
    if header_row:
        for i in range(3):  # Add three checkbox headers
            checkbox_header = soup.new_tag("th")
            checkbox_header.string = f"{h_r_names[i]}"
            header_row.insert(0, checkbox_header)

    # Add three checkboxes to each row
    rows = table.find_all("tr")[1:]  # Skip the header row
    for row_index, row in enumerate(rows):
        for i in range(3):  # Add three checkboxes per row
            checkbox_cell = soup.new_tag("td")
            checkbox = soup.new_tag("input", type="checkbox", onclick="handleCheckboxClick(this)")
            checkbox['data-checkbox-index'] = i  # Add a data attribute to identify the checkbox
            checkbox_cell.append(checkbox)
            row.insert(0, checkbox_cell)

# Add a "Checked" section at the bottom of the page
checked_section = soup.new_tag("div", id="checked-section")
checked_heading = soup.new_tag("h2")
checked_heading.string = "Checked"
checked_section.append(checked_heading)

# Create a <pre> tag to wrap the table
pre_tag = soup.new_tag("pre")
checked_table = soup.new_tag("table", id="checked-table", border="1")
pre_tag.append(checked_table)  # Add the table inside the <pre> tag
checked_section.append(pre_tag)  # Add the <pre> tag to the section

soup.body.append(checked_section)

# Add JavaScript to handle saving checkbox states and copying rows
script = soup.new_tag("script")
script.string = """
function handleCheckboxClick(checkbox) {
    const row = checkbox.closest('tr');
    const table = checkbox.closest('table');
    const tableId = table.id;
    const rowIndex = Array.from(table.querySelectorAll('tr')).indexOf(row);
    const checkboxIndex = checkbox.getAttribute('data-checkbox-index');
    const checkedTable = document.getElementById('checked-table');

    // Save the checkbox state in localStorage
    const checkboxKey = `${tableId}_row_${rowIndex}_checkbox_${checkboxIndex}`;
    if (checkbox.checked) {
        localStorage.setItem(checkboxKey, '1');

        // Clone the row and add it to the "Checked" table
        const clonedRow = row.cloneNode(true);
        clonedRow.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            cb.disabled = true; // Disable checkboxes in the cloned row
        });
        checkedTable.appendChild(clonedRow);
    } else {
        localStorage.removeItem(checkboxKey);

        // Remove the row from the "Checked" table if it exists
        const rows = checkedTable.querySelectorAll('tr');
        rows.forEach(checkedRow => {
            if (checkedRow.isEqualNode(row.cloneNode(true))) {
                checkedRow.remove();
            }
        });
    }
}

function loadCheckboxStates() {
    // Iterate through all keys in localStorage
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key.includes('_checkbox_')) {
            const [tableId, _, rowIndex, checkboxIndex] = key.split('_');
            const table = document.getElementById(tableId);
            if (table) {
                const row = table.querySelectorAll('tr')[rowIndex];
                if (row) {
                    const checkbox = row.querySelector(`input[data-checkbox-index="${checkboxIndex}"]`);
                    if (checkbox) {
                        checkbox.checked = localStorage.getItem(key) === '1';
                    }
                }
            }
        }
    }
}

window.onload = loadCheckboxStates;
"""
soup.body.append(script)

# Add JavaScript to handle row highlighting
highlight_script = soup.new_tag("script")
highlight_script.string = """
document.addEventListener('DOMContentLoaded', function() {
    let currentlyHighlightedRow = null;

    document.querySelectorAll('table').forEach(table => {
        table.addEventListener('click', function(event) {
            const cell = event.target.closest('td, th'); // Check if the clicked element is a cell
            if (cell) {
                const row = cell.closest('tr'); // Get the row of the clicked cell
                if (currentlyHighlightedRow) {
                    currentlyHighlightedRow.classList.remove('highlight'); // Remove highlight from the previous row
                }
                row.classList.add('highlight'); // Highlight the new row
                currentlyHighlightedRow = row; // Update the currently highlighted row
            }
        });
    });
});

// Add CSS for the highlight class
const style = document.createElement('style');
style.innerHTML = `
    .highlight {
        background-color: yellow; /* Highlight color */
    }
`;
document.head.appendChild(style);
"""
soup.body.append(highlight_script)

# --------------------------------
sticky_style = soup.new_tag("style")
sticky_style.string = """
body {
    margin: 0;
    font-family: Arial, sans-serif;
}

.navbar {
    position: fixed; /* Ensures the navbar stays fixed at the top */
    top: 0;
    left: 0;
    width: 100%; /* Makes the navbar span the full width of the page */
    background-color: #333; /* Sets the background color */
    z-index: 1000; /* Ensures the navbar stays above other content */
}

.navbar a {
    float: left;
    display: block;
    color: white;
    text-align: center;
    padding: 8px 10px; /* Adjust padding for better spacing */
    font-size: 12px; /* Adjust font size */
    text-decoration: none;
}

.navbar a:hover {
    background-color: #ddd;
    color: black;
}

.content {
    padding-top: 50px; /* Adds padding to prevent content from overlapping the navbar */
}
"""
soup.head.append(sticky_style)
# ------------------------


sticky_headers_script = soup.new_tag("script")
sticky_headers_script.string = """
document.addEventListener('DOMContentLoaded', function() {
    const navbarHeight = document.querySelector('.navbar').offsetHeight;

    document.querySelectorAll('table').forEach(table => {
        const headerRow = table.querySelector('tr:first-child');
        if (headerRow) {
            headerRow.style.top = `${navbarHeight}px`; // Set the sticky header below the navbar
        }
    });
});
"""
soup.body.append(sticky_headers_script)

sticky_headers_style = soup.new_tag("style")
sticky_headers_style.string = """
table tr:first-child {
    position: sticky;
    top: 40px; /* Adjust this value to match the height of your navbar */
    background-color: #fff; /* Optional: Set background color for better visibility */
    z-index: 999; /* Ensure it stays below the navbar but above other content */
}
"""
soup.head.append(sticky_headers_style)





# # Write the modified HTML to a new file
# with open("docs/index.html", "w", encoding="utf-8") as file:
#     file.write(str(soup))
import os
   
# File path for the HTML file
file_path = "docs/index.html"

# Check if the file exists
if os.path.exists(file_path):
    # Get the current date and time
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Create a new name for the existing file
    renamed_file_path = f"docs/index_{current_time}.html"
    
    # Rename the existing file
    os.rename(file_path, renamed_file_path)
    print(f"Existing file renamed to {renamed_file_path}")

# Write the modified HTML to a new file
with open(file_path, "w", encoding="utf-8") as file:
    file.write(str(soup))
    print(f"New file saved to {file_path}")
