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
sorted_list = entries_without_toronto

# get the toronto game
toronto_content = []
toronto_game = entries_with_toronto[0]
if "Toronto" in toronto_game.get('summary'):
    # Example UTC datetime string
    utc_datetime_str = toronto_game.get("game_datetime")
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
    # scoring_plays = statsapi.game_scoring_plays(x.get("game_id"))
    # new_scoring_plays = ""
    # Get scoring plays as a string

    scoring_plays = statsapi.game_scoring_plays(toronto_game.get("game_id"))
    # Convert the scoring plays string into a list of lines
    scoring_plays_list = scoring_plays.split("\n")
    # Filter the lines to only include those that contain "homers"
    filtered_plays = [line for line in scoring_plays_list if "homers" in line]
    # Process each kept line to only include the part before the first ")"
    processed_plays = [line.split(")")[0] + ")" for line in filtered_plays if ")" in line]
    # Join the processed lines back into a string if needed
    new_scoring_plays = "\n".join(processed_plays)
    highlights = statsapi.game_highlights(toronto_game.get("game_id"))

    toronto_game.update({"time_scheduled": readable_format})
    toronto_game.update({"scoring_plays": new_scoring_plays})
    toronto_content.append(
        f"{toronto_game.get('time_scheduled')}\n"
        # f"Status: {x.get('')}\n"
        f"{toronto_game.get('away_name'):<22} {toronto_game.get('away_score')}    @\n"
        f"{toronto_game.get('home_name'):<22} {toronto_game.get('home_score')}\n\n"
        f"{toronto_game.get('scoring_plays')}\n\n"
        f"HIGHLIGHTS\n\n"
        f"{highlights}\n\n"
        f"NEXT GAME:\n"
    )

yesterdays_content = []
homers = []
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
    # scoring_plays = statsapi.game_scoring_plays(x.get("game_id"))
    # new_scoring_plays = ""
    # Get scoring plays as a string
    scoring_plays = statsapi.game_scoring_plays(x.get("game_id"))

    # Convert the scoring plays string into a list of lines
    scoring_plays_list = scoring_plays.split("\n")

    # Filter the lines to only include those that contain "homers"
    filtered_plays = [line for line in scoring_plays_list if "homers" in line]

    # Process each kept line to only include the part before the first ")"
    processed_plays = [line.split(")")[0] + ")" for line in filtered_plays if ")" in line]

    # Join the processed lines back into a string if needed
    # new_scoring_plays = "\n".join(processed_plays)

    x.update({"time_scheduled": readable_format})
    # x.update({"scoring_plays": new_scoring_plays})
    homers.append(processed_plays)
    yesterdays_content.append(
        f"GAME:\n"
        f"{x.get('time_scheduled')}\n"
        # f"Status: {x.get('')}\n"
        f"{x.get('away_name'):<22} {x.get('away_score')}    @\n"
        f"{x.get('home_name'):<22} {x.get('home_score')}\n\n"
        # f"{x.get('scoring_plays')}\n\n"
    )
new_homers = []
for x in homers:
    for y in x:
        new_homers.append(y)

# Write content to the new Todays_Report.txt file
with open(report_file_path, "w") as file:
    for tcontent in toronto_content:
        file.write(tcontent)
    for content in yesterdays_content:
        file.write(content)
    file.write("<h3>Yesterdays Homers</h3>\n")
    for contents in new_homers:
        file.write(contents)


print(f"New report saved to {report_file_path}")
if os.path.exists(backup_file_path):
    print(f"Existing report renamed to {backup_file_path}")


