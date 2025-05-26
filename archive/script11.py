from bs4 import BeautifulSoup

# Read the input HTML file
with open("docs/index.html", "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "html.parser")

# Find all tables in the HTML
tables = soup.find_all("table")

# Add a checkbox column to each table
for table in tables:
    # Add a header for the checkbox column
    header_row = table.find("tr")
    if header_row:
        checkbox_header = soup.new_tag("th")
        checkbox_header.string = "Select"
        header_row.insert(0, checkbox_header)

    # Add a checkbox to each row
    rows = table.find_all("tr")[1:]  # Skip the header row
    for row in rows:
        checkbox_cell = soup.new_tag("td")
        checkbox = soup.new_tag("input", type="checkbox", onclick="saveCheckboxState(this)")
        checkbox_cell.append(checkbox)
        row.insert(0, checkbox_cell)

# Add JavaScript to handle saving checkbox states in cookies
script = soup.new_tag("script")
script.string = """
function saveCheckboxState(checkbox) {
    const tableIndex = Array.from(checkbox.closest('table').parentNode.children).indexOf(checkbox.closest('table'));
    const rowIndex = Array.from(checkbox.closest('tr').parentNode.children).indexOf(checkbox.closest('tr'));
    const checkboxState = checkbox.checked ? '1' : '0';
    document.cookie = `table_${tableIndex}_row_${rowIndex}=${checkboxState}; path=/`;
}

function loadCheckboxStates() {
    const cookies = document.cookie.split('; ');
    cookies.forEach(cookie => {
        const [key, value] = cookie.split('=');
        if (key.startsWith('table_')) {
            const [_, tableIndex, __, rowIndex] = key.split('_');
            const table = document.querySelectorAll('table')[tableIndex];
            if (table) {
                const row = table.querySelectorAll('tr')[rowIndex];
                if (row) {
                    const checkbox = row.querySelector('input[type="checkbox"]');
                    if (checkbox) {
                        checkbox.checked = value === '1';
                    }
                }
            }
        }
    });
}

window.onload = loadCheckboxStates;
"""
soup.body.append(script)

# Write the modified HTML to a new file
with open("docs/index2.html", "w", encoding="utf-8") as file:
    file.write(str(soup))