import os
from file_manager import move_files_to_folder, prepend_to_file, read_file, write_file
from stats_processor import (
    get_current_date, get_yesterday_date, fetch_schedule, fetch_standings, fetch_player_stats, format_stats
)
from html_generator import generate_html_from_text, generate_index_html

# Constants
REPORTS_FOLDER = "mlb_reports"
HTML_OUTPUT_DIR = "html_output"
FILE_NAMES = [
    "MLB STANDINGS AND SCHEDULE.txt",
    "BLUE JAYS HISTORY.txt",
    "GAME REPORTS.txt",
    "LEAGUE LEADERS.txt",
    "TOP LEAGUE LEADERS.txt"
]

# Ensure folders exist
os.makedirs(REPORTS_FOLDER, exist_ok=True)
os.makedirs(HTML_OUTPUT_DIR, exist_ok=True)

# Move old reports to the reports folder
current_date = get_current_date()
move_files_to_folder(FILE_NAMES, REPORTS_FOLDER, current_date)

# Generate MLB standings and schedule
mlb_date = get_current_date()
yesterday_date = get_yesterday_date()

schedule_today = fetch_schedule(mlb_date)
schedule_yesterday = fetch_schedule(yesterday_date)
standings = fetch_standings(mlb_date)

standings_content = f"MLB Standings:\n{standings}"
today_schedule_content = "Today's Schedule:\n" + "\n".join(
    f'{x["game_id"]} -> {x["summary"]}' for x in schedule_today
)
yesterday_schedule_content = "Yesterday's Schedule:\n" + "\n".join(
    f'{x["game_id"]} -> {x["summary"]}' for x in schedule_yesterday
)

standings_file_content = f"{standings_content}\n\n{today_schedule_content}\n\n{yesterday_schedule_content}"
write_file("MLB STANDINGS AND SCHEDULE.txt", standings_file_content)

# Generate league leaders
categories = [
    ('battingAverage', 'AVG'),
    ('homeRuns', 'HR'),
    ('gamesPlayed', 'aGP'),
    ('onBasePlusSlugging', 'OBPS'),
    ('strikeOuts', 'SO'),
    ('hits', 'HITS'),
]
years = [2025, 2024]
player_stats = fetch_player_stats(categories, years)
formatted_stats = format_stats(player_stats)
prepend_to_file("LEAGUE LEADERS.txt", formatted_stats)

# Generate HTML files
html_files = []
for file_name in FILE_NAMES:
    html_file = generate_html_from_text(file_name, HTML_OUTPUT_DIR)
    if html_file:
        html_files.append(html_file)

generate_index_html(html_files, HTML_OUTPUT_DIR)

print("All tasks completed successfully.")