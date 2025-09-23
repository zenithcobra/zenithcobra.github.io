from datetime import datetime
from pathlib import Path
import file_operations
from cache_manager import CacheManager


# Function to format the schedule into the desired text format
def format_schedule(schedule):
    """
    Takes the schedule and makes a array of lines formatted for a txt file.
    """
    formatted_lines = []
    for row in schedule:
        date, time, away, home = row
        formatted_line = f"{date} {time:<8} EDT - {away:<25} @ {home:<25}"
        formatted_lines.append(formatted_line)
    return formatted_lines


# Main function to handle the schedule processing
def process_schedule():
    """
    Processes the NHL schedule for today's games and saves it to a text file.

    This function reads the NHL schedule from a CSV file, filters the games to include only those
    scheduled for today's date, formats the schedule into a human-readable text format, and saves
    it to a text file. It uses a caching mechanism to avoid redundant processing if the schedule
    for today has already been generated within the last 4 hours.

    Workflow:
    1. Initializes the CacheManager to handle caching and archiving.
    2. Checks if the output file (`NHL_todays_schedule.txt`) is valid and up-to-date.
       - If valid, the function exits early without further processing.
    3. Archives the old schedule file if it exists and is outdated.
    4. Reads the NHL schedule from the CSV file (`nhl_schedule.csv`).
    5. Filters the schedule to include only games scheduled for today's date.
    6. Formats the filtered schedule into a readable text format.
    7. Saves the formatted schedule to the output file (`NHL_todays_schedule.txt`).

    File Paths:
    - Input: `NHL_data/nhl_schedule.csv` (CSV file containing the full NHL schedule).
    - Output: `NHL_data/NHL_todays_schedule.txt` (Text file containing today's games).

    Caching:
    - The CacheManager ensures that the schedule is only processed if the cache is invalid
      (i.e., the file is older than 4 hours or does not exist).

    Example Output (saved in `NHL_todays_schedule.txt`):
    ```
    2025-09-22 7:15 PM   EDT - Washington Capitals       @ Boston Bruins
    2025-09-22 9:40 PM   EDT - New York Rangers          @ Pittsburgh Penguins
    ```

    Dependencies:
    - [file_operations.read_csv](http://_vscodecontentref_/1): Reads the schedule from the CSV file.
    - [file_operations.save_text](http://_vscodecontentref_/2): Saves the formatted schedule to a text file.
    - [CacheManager](http://_vscodecontentref_/3): Handles caching and archiving of the output file.

    Raises:
    - FileNotFoundError: If the input CSV file does not exist.
    - ValueError: If the CSV file is improperly formatted.

    Notes:
    - The function assumes the CSV file has the following columns:
      `Date, Time, Away Team, Home Team`.
    - The date format in the CSV must be `YYYY-MM-DD`.

    """
    # Initialize CacheManager
    cache = CacheManager()
    # File paths
    csv_path = "NHL_data/nhl_schedule.csv"
    output_file = "NHL_data/NHL_todays_schedule.txt"
    # Check if the cache is valid for today
    if cache.is_cache_valid(output_file, expiry_hours=4):
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
    file_operations.save_text(formatted_schedule, "NHL_todays_schedule")
