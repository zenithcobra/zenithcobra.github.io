# Import necessary modules
import os  # For file and directory operations
import datetime  # For working with dates and times
from shutil import move  # For moving files between directories

# List of files to check and process
file_names = [
    "MLB STANDINGS AND SCHEDULE.txt",  # File for MLB standings and schedule
    "BLUE JAYS HISTORY.txt",  # File for Blue Jays historical data
    "GAME REPORTS.txt",  # File for game reports
    "LEAGUE LEADERS.txt",  # File for league leaders
    "TOP LEAGUE LEADERS.txt"  # File for top league leaders
]

# Folder where the processed files will be moved
reports_folder = "mlb_reports"

# Ensure the folder exists; create it if it doesn't
os.makedirs(reports_folder, exist_ok=True)

# Get the current date in YYYY-MM-DD format for appending to file names
current_date = datetime.datetime.now().strftime("%Y-%m-%d")

# Iterate through the list of files to check if they exist
for file_name in file_names:
    if os.path.exists(file_name):  # Check if the file exists
        # Create a new file name by appending the current date
        new_file_name = f"{os.path.splitext(file_name)[0]}-{current_date}{os.path.splitext(file_name)[1]}"
        # Move the file to the reports folder with the new name
        move(file_name, os.path.join(reports_folder, new_file_name))

# Import the statsapi module for fetching MLB data
import statsapi
from datetime import datetime, timedelta  # For date manipulation

# Get the current date in MM/DD/YYYY format for MLB API queries
mlb_date = datetime.now().strftime("%m/%d/%Y")
file_date = datetime.now().strftime("%Y-%m-%d")  # File date in YYYY-MM-DD format

# File name for storing MLB standings and schedule
file_name = f"MLB STANDINGS AND SCHEDULE.txt"

# Get yesterday's date for fetching previous day's schedule
oneday = timedelta(days=1)
yesterday = datetime.now().date() - oneday
yschedule = statsapi.schedule(start_date=yesterday, end_date=yesterday)  # Fetch yesterday's schedule

# Get today's schedule
schedule = statsapi.schedule(start_date=mlb_date, end_date=mlb_date)

# Prepare content for writing to the file
yesterday_schedule_content = "\nYesterday's Schedule:\n" + "\n".join(
    f'{x.get("game_id")} -> {x.get("summary")}' for x in yschedule
)
standings_content = (
    "MLB Standings:\n"
    + statsapi.standings(leagueId=103, date=mlb_date)  # Standings for American League
    + statsapi.standings(leagueId=104, date=mlb_date)  # Standings for National League
)
today_schedule_content = "Today's Schedule:\n" + "\n".join(
    f'{x.get("game_id")} -> {x.get("summary")}' for x in schedule
)

# Combine all content into a single string
new_content = (
    standings_content + "\n" + today_schedule_content + "\n" + yesterday_schedule_content
)

# Check if the file exists
if os.path.exists(file_name):
    with open(file_name, "r") as file:
        existing_content = file.read()  # Read the existing content

    # Prepend new content only if it doesn't already exist in the file
    if new_content not in existing_content:
        with open(file_name, "w") as file:
            file.write(new_content + "\n" + existing_content)
else:
    # Write new content if the file doesn't exist
    with open(file_name, "w") as file:
        file.write(new_content)

print(f"Output written to {file_name}")  # Notify the user that the file has been updated

# Update Blue Jays-specific data into a separate file
import datetime
import os

# Calculate yesterday's date
oneday = datetime.timedelta(days=1)
yesterday = datetime.date.today() - oneday

# Fetch yesterday's schedule
yschedule = statsapi.schedule(start_date=yesterday, end_date=yesterday)

# File to store Blue Jays history
file_name = "BLUE JAYS HISTORY.txt"

# Collect all outputs in a list
output_lines = []

# Iterate through yesterday's schedule to find Blue Jays games
for x in yschedule:
    if 'Toronto' in x.get('summary'):  # Check if the game involves the Toronto Blue Jays
        game_id = x.get('game_id')  # Get the game ID

        # Append various stats and highlights for the Blue Jays
        output_lines.append(statsapi.roster(141))  # Blue Jays roster
        output_lines.append('HomeRuns')
        output_lines.append(statsapi.team_leaders(141, 'homeRuns', limit=25, season=2025))
        output_lines.append('Batting')
        output_lines.append(statsapi.team_leaders(141, 'battingAverage', limit=25, season=2025))
        output_lines.append('On Base Plus Slugging')
        output_lines.append(statsapi.team_leaders(141, 'onBasePlusSlugging', limit=25, season=2025))
        output_lines.append('Walks')
        output_lines.append(statsapi.team_leaders(141, 'walks', limit=25, season=2025))
        output_lines.append(statsapi.game_highlights(statsapi.next_game(141)))  # Highlights for the next game
        output_lines.append(statsapi.boxscore(statsapi.next_game(141)))  # Boxscore for the next game
        for keys, values in x.items():
            output_lines.append(f'{str(keys):<25} -> {str(values)}')  # Add game details
        
        output_lines.append(' ')
        output_lines.append(statsapi.linescore(game_id))  # Linescore for the game
        output_lines.append(' ')
        output_lines.append(statsapi.game_scoring_plays(game_id))  # Scoring plays for the game
        output_lines.append(' ')
        output_lines.append(statsapi.boxscore(game_id))  # Boxscore for the game
        output_lines.append(' ')
        output_lines.append(statsapi.game_highlights(game_id))  # Highlights for the game

# Combine all outputs into a single string
output_text = "\n".join(map(str, output_lines))

# Check if the file exists
if os.path.exists(file_name):
    # Read the existing content
    with open(file_name, "r") as file:
        existing_content = file.read()
    # Prepend the new content to the existing content
    new_content = output_text + "\n\n" + existing_content
else:
    # If the file doesn't exist, just use the new content
    new_content = output_text

# Write the updated content back to the file
with open(file_name, "w") as file:
    file.write(new_content)

print(f"Output written to {file_name}")  # Notify the user that the file has been updated