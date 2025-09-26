from datetime import datetime
from pathlib import Path
import file_operations
import NHL_data_fetcher
import config
from cache_manager import CacheManager
import pandas as pd


# Function to format the schedule into the desired text format
# def format_schedule(schedule):
#     """
#     Takes the schedule and makes a array of lines formatted for a txt file.
#     """
#     formatted_lines = []
#     for row in schedule:
#         date, time, away, home = row
#         formatted_line = f"{date} {time:<8} EDT - {away:<22} @ {home:<25}"
#         formatted_lines.append(formatted_line)
    
    
#     return formatted_lines
def format_schedule(schedule):
    """
    Takes the schedule and makes an array of lines formatted for a txt file.
    If "Toronto Maple Leafs" exists in a line, it wraps it in a styled <b> tag.
    """
    formatted_lines = []
    for row in schedule:
        date, time, away, home = row
        formatted_line = f"{date} {time:<8} EDT - {away:<22} @ {home:<25}"
        
        # Wrap "Toronto Maple Leafs" with the styled <b> tag
        formatted_line = formatted_line.replace(
            "Toronto Maple Leafs", 
            '<b style="color: #5A62FF;">Toronto Maple Leafs</b>'
        )
        
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

def process_yesterdays_scores_to_report():
    nhl = NHL_data_fetcher.get_nhl_yesterdays_scores()

    import json
    from pathlib import Path

    # File paths
    # input_file = 'NHL_data/nhl_yesterdays_scores.json'
    output_dir = 'NHL_data/daily_scores'

    # Function to process the JSON data
    def process_scores(input_file, output_dir):
        data = input_file

        # Extract the date for the output file name
        # yesterdays_date = data.get("currentDate", "unknown_date")
        yesterdays_date = config.get_yesterday_NHL()

        # Prepare the output file path
        output_file = Path(output_dir) / f"NHL_scores_{yesterdays_date}.json"

        # Ensure the output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Extract and format the games data
        formatted_games = []
        for game in data.get("games", []):
            home_team = game["homeTeam"]["name"]["default"]
            away_team = game["awayTeam"]["name"]["default"]
            home_score = game["homeTeam"]["score"]
            away_score = game["awayTeam"]["score"]
            winner = home_team if home_score > away_score else away_team
            condensed_game = game.get("condensedGame", "")
            condensed_game = "https://www.nhl.com"+condensed_game

            # Extract goals data
            goals = []
            for goal in game.get("goals", []):
                goal_data = {
                    "player_id":goal['playerId'],
                    "name": f"{goal['firstName']['default']} {goal['lastName']['default']}",
                    "team": goal['teamAbbrev'],
                    "goals_to_date": goal.get("goalsToDate",None),
                    "assists": [
                        {
                            "name": assist["name"]["default"],
                            "assists_to_date": assist["assistsToDate"],
                            "player_id": assist["playerId"]
                        }
                        for assist in goal.get("assists", [])
                    ]
                }
                goals.append(goal_data)

            # Add the formatted game data
            formatted_games.append({
                "date": yesterdays_date,
                "home_team": home_team,
                "away_team": away_team,
                "home_score": home_score,
                "away_score": away_score,
                "winner": winner,
                "condensed_game": condensed_game,
                "goals": goals
            })

        # Save the formatted data to the output file
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(formatted_games, file, indent=4)

        print(f"Processed scores saved to {output_file}")

        return formatted_games

        
    def generate_hockey_reference_link(name):
        """
        Generates a Hockey Reference player link based on the player's name.

        Args:
            name (str): The player's full name in the format "FirstName LastName".

        Returns:
            str: The Hockey Reference player link.
        """
        # Split the name into first and last names
        try:
            first_name, last_name = name.split(" ")
        except ValueError:
            return "Invalid name format. Expected 'FirstName LastName'."

        # Extract the first letter of the last name
        last_name_initial = last_name[0].lower()

        # Extract the first two letters of the first name
        first_name_initials = first_name[:2].lower()

        # Format the link
        link = f"https://www.hockey-reference.com/players/{last_name_initial}/{last_name[:5].lower()}{first_name_initials}01.html"

        return link

    # def make_report(data):
    #     """
    #     Processes a JSON string of NHL scores and generates a text report.

    #     Args:
    #         json_string (str): JSON string containing NHL scores data.

    #     Returns:
    #         str: A formatted text report of the games and their details.
    #     """
    #     # import json

    #     # # Parse the JSON string
    #     # data = json.loads(json_string)

    #     # Initialize the report
    #     report_lines = []

    #     # Extract the date from the first game (assuming all games are from the same date)
    #     if data:
    #         report_lines.append(f"DATE: {data[0]['date']}")
    #     else:
    #         return "No games available to report."

        # # Process each game
        # for i, game in enumerate(data, start=1):
        #     report_lines.append(f"\nMATCH {i}:  <a target='_blank' rel='noopener noreferrer' href='{game['condensed_game']}'>Video</a>")
        #     report_lines.append(f"<b>{game['home_team']} {game['home_score']} vs {game['away_team']} {game['away_score']}</b>")
        #     report_lines.append("GOALS:")

        #     # Process each goal
        #     for goal in game.get("goals", []):
        #         player_link = generate_hockey_reference_link(goal['name'])
        #         report_lines.append(f"- Name: <a target='_blank' rel='noopener noreferrer' href='{player_link}'>{goal['name']}</a>")
        #         report_lines.append(f"  Team: {goal['team']}")
        #         report_lines.append(f"  Goals to date: {goal.get('goals_to_date', 'N/A')}")
        #         report_lines.append("  Assists to Goal:")
        #         for assist in goal.get("assists", []):
        #             report_lines.append(f"    - Name: {assist['name']}, Assists to date: {assist.get('assists_to_date', 'N/A')}")
        # Process each game
        # Process each game
        # for i, game in enumerate(data, start=1):
        #     # Add match header with video link
        #     report_lines.append(f"MATCH {i}:              Video")
        #     report_lines.append(f"{game['home_team']} {game['home_score']} vs {game['away_team']} {game['away_score']}\n")
        #     report_lines.append("  GOALS:\n")

        #     # Process each goal
        #     for goal in game.get("goals", []):
        #         # Add goal scorer details
        #         report_lines.append(f"  {goal['team'].ljust(3)} {goal['name'].ljust(20)} G2D: {str(goal.get('goals_to_date', 'N/A')).ljust(2)}")
        #         report_lines.append("  Assists")

        #         # Add assist details
        #         for assist in goal.get("assists", []):
        #             report_lines.append(f"    {assist['name'].ljust(20)} A2D: {assist.get('assists_to_date', 'N/A')}")

        #         # Add a blank line after each goal
        #         report_lines.append("")



        # # Join the report lines into a single string
        # return "\n".join(report_lines)

    def make_report(data):
        """
        Processes a JSON string of NHL scores and generates an HTML report.

        Args:
            data (list): List of games containing NHL scores data.

        Returns:
            str: A formatted HTML report of the games and their details.
        """
        # Initialize the report
        report_lines = []

        # Extract the date from the first game (assuming all games are from the same date)
        if data:
            report_lines.append(f"<h2>DATE: {data[0]['date']}</h2>")
        else:
            return "<p>No games available to report.</p>"

        # Process each game
        for i, game in enumerate(data, start=1):
            # Add match header with video link
            report_lines.append(f"<h2>MATCH {i}: <a target='_blank' rel='noopener noreferrer' href='{game['condensed_game']}'>Video</a></h2>")
            report_lines.append(f"<h2>{game['home_team']} {game['home_score']} vs {game['away_team']} {game['away_score']}</h2>")

            # Start the table
            report_lines.append("<table border='1' style='border-collapse: collapse; width: 100%;'>")
            report_lines.append("<tr><th>Team</th><th>Name</th><th>Assist1</th><th>Assist2</th></tr>")

            # Process each goal
            for goal in game.get("goals", []):
                # Extract assists
                assists = goal.get("assists", [])
                assist1 = f"{assists[0]['name']} ({assists[0].get('assists_to_date', 'N/A')})" if len(assists) > 0 else ""
                assist2 = f"{assists[1]['name']} ({assists[1].get('assists_to_date', 'N/A')})" if len(assists) > 1 else ""

                # Add a row for the goal
                report_lines.append(
                    f"<tr>"
                    f"<td>{goal['team']}</td>"
                    f"<td><a target='_blank' rel='noopener noreferrer' href='{generate_hockey_reference_link(goal['name'])}'>{goal['name']}</a> ({goal.get('goals_to_date', 'N/A')})</td>"
                    f"<td>{assist1}</td>"
                    f"<td>{assist2}</td>"
                    f"</tr>"
                )

            # End the table
            report_lines.append("</table>")
            report_lines.append("<br>")  # Add spacing between matches

        # Join the report lines into a single HTML string
        return "\n".join(report_lines)

    # Run the function
    yesterdays_scores = process_scores(nhl, output_dir)

    # Generate the report
    report = make_report(yesterdays_scores)

    # Print the report
    # print(report)

    # Optionally, save the report to a text file
    with open("NHL_data/NHL_yesterdays_scores.txt", "w") as file:
        file.write(report)
    print('report generated')


def process_raw_skaters_html_table():
    """
    Reads the NHL skaters CSV file and generates an HTML table.

    The HTML table only includes rows where the 'situation' column equals 'all'.
    The table is saved to the file path specified in `table_path`.

    File Paths:
    - Input: 'NHL_data/nhl_skaters_2024_2025_regular_latest.csv'
    - Output: 'NHL_data/skaters_table.html'
    """
    # File paths
    csv_path = "NHL_data/nhl_skaters_2024_2025_regular_latest.csv"
    table_path = "NHL_data/skaters_table.html"

    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_path)

    # Filter rows where 'situation' equals 'all'
    filtered_df = df[df['situation'] == 'all']

    # Generate the HTML table
    html_table = filtered_df.to_html(index=False, classes="table table-striped", border=0)

    # Save the HTML table to the specified file
    with open(table_path, "w", encoding="utf-8") as file:
        file.write(html_table)

    print(f"Filtered HTML table saved to {table_path}")