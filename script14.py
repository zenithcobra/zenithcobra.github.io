import os
import json
from bs4 import BeautifulSoup
import statsapi

html_file_path = "text_output/BVP.txt"

# Ensure the files exist
if not os.path.exists(html_file_path):
    raise FileNotFoundError(f"{html_file_path} does not exist.")

# Parse the HTML table and convert it into a list of lists
def parse_html_table_to_list(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()
    
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table")
    
    if not table:
        raise ValueError("No table found in the HTML file.")
    
    rows = []
    for tr in table.find_all("tr"):
        row = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        rows.append(row)
    
    return rows


html_table_as_list = parse_html_table_to_list(html_file_path)
players_bvp = html_table_as_list[1:]
# print(players_bvp)
