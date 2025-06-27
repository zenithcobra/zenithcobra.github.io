# %%
# GET TODAYS STANDINGS
import statsapi
from datetime import datetime, timedelta
import os

# Ensure the "text_output" folder exists
os.makedirs("text_output", exist_ok=True)

# Get yesterday's date
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# File paths
file_name = "standings.txt"
report_file_path = f"text_output/{file_name}"
backup_file_path = f"text_output/standings_{yesterday}.txt"

# Check if standings.txt exists and rename it
if os.path.exists(report_file_path):
    os.rename(report_file_path, backup_file_path)

# ---------------------------
# Get today's date for api call
mlb_date = datetime.now().strftime("%m/%d/%Y")
standings_content = (
    "MLB Standings:\n"
    + statsapi.standings(leagueId=103, date=mlb_date)
    + statsapi.standings(leagueId=104, date=mlb_date)
)
# -----------------------------
# Combine all content
full_content = (
    standings_content
)

# Write content to the new Todays_Report.txt file
with open(report_file_path, "w") as file:
    file.write(full_content)

print(f"New report saved to {report_file_path}")
if os.path.exists(backup_file_path):
    print(f"Existing report renamed to {backup_file_path}")


