# %%
import statsapi
from datetime import datetime, timedelta
import os
from datetime import datetime
import pytz

# Ensure the "text_output" folder exists
os.makedirs("text_output", exist_ok=True)

# Get yesterday's date
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# File paths
file_name = "Yesterdays_Report.txt"
report_file_path = f"text_output/{file_name}"
backup_file_path = f"text_output/Yesterdays_Report_{yesterday}.txt"

# Check if Todays_Report.txt exists and rename it
if os.path.exists(report_file_path):
    os.rename(report_file_path, backup_file_path)

# Get yesterday's schedule
oneday = timedelta(days=1)
yesterday_date = datetime.now().date() - oneday
yschedule = statsapi.schedule(start_date=yesterday_date, end_date=yesterday_date)

# Separate entries with "Toronto" in the "summary" key
entries_with_toronto = [x for x in yschedule if "summary" in x and "Toronto" in x["summary"]]

# Separate entries without "Toronto" in the "summary" key
entries_without_toronto = [x for x in yschedule if not ("summary" in x and "Toronto" in x["summary"])]

# Combine the two lists, bringing entries with "Toronto" to the top
sorted_list = entries_with_toronto + entries_without_toronto

yesterdays_content = []
for x in sorted_list:
    
    # Example UTC datetime string
    utc_datetime_str = x.get("game_datetime")

    # Parse the UTC datetime string
    utc_datetime = datetime.strptime(utc_datetime_str, '%Y-%m-%dT%H:%M:%SZ')

    # Define the UTC and Eastern Time zones
    utc_zone = pytz.utc
    eastern_zone = pytz.timezone('US/Eastern')

    # Localize the datetime to UTC
    utc_datetime = utc_zone.localize(utc_datetime)

    # Convert to Eastern Time
    eastern_datetime = utc_datetime.astimezone(eastern_zone)

    # Format the datetime in a readable format
    readable_format = eastern_datetime.strftime('%Y-%m-%d %I:%M %p %Z')

    # print(readable_format)
    # print(x)
    # print(x)
    x.update({"time_scheduled": readable_format})
    x.update({"scoring_plays": statsapi.game_scoring_plays(x.get("game_id"))})
    yesterdays_content.append(
        f"{x.get('time_scheduled')}\n"
        # f"Status: {x.get('')}\n"
        f"{x.get('away_name'):<22} {x.get('away_score')}    @\n"
        f"{x.get('home_name'):<22} {x.get('home_score')}\n\n"
        f"{x.get('scoring_plays')}\n\n"
        f"NEXT GAME:\n"
    )


# Write content to the new Todays_Report.txt file
with open(report_file_path, "w") as file:
    for content in yesterdays_content:
        file.write(content)


print(f"New report saved to {report_file_path}")
if os.path.exists(backup_file_path):
    print(f"Existing report renamed to {backup_file_path}")


