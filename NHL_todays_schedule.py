from datetime import datetime
from pathlib import Path
import file_operations
from cache_manager import CacheManager

# Initialize CacheManager
cache = CacheManager()

# File paths
csv_path = 'NHL_data/nhl_schedule.csv'
output_file = 'NHL_data/NHL_todays_schedule.txt'

# Function to format the schedule into the desired text format
def format_schedule(schedule):
    formatted_lines = []
    for row in schedule:
        date, time, away, home = row
        formatted_line = f"{date} {time:<8} EDT - {away:<20} @ {home:<20}"
        formatted_lines.append(formatted_line)
    return formatted_lines

# Main function to handle the schedule processing
def process_schedule():
    # Check if the cache is valid for today
    if cache.is_cache_valid(output_file, expiry_hours=24):
        print(f"Today's schedule is already cached: {output_file}")
        return

    # Archive the old file if it exists
    if Path(output_file).exists():
        cache._archive_existing_file(output_file)

    # Read the schedule CSV
    nhl_schedule = file_operations.read_csv(csv_path)

    # Get today's date in the format "YYYY-MM-DD"
    today = datetime.now().strftime("%Y-%m-%d")

    # Filter the schedule to include only today's games
    todays_games = [row for row in nhl_schedule[1:] if row[0] == today]

    # Format the schedule
    formatted_schedule = format_schedule(todays_games)

    # Save the formatted schedule to the text file
    file_operations.save_text(formatted_schedule, 'NHL_todays_schedule')
