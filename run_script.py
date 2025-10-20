import importlib
import script
import NHL_script

# Reload the script after making changes
importlib.reload(script)

# RUNNING THE SCRIPT
print("script getting date")

# DATES
date = script.get_date()

print("script getting schedule")
# SCHEDULE INFO
script.update_picture()

# NHL SCHEDULE
NHL_script.make_todays_schedule()

# NHL YESTERDAYS SCORES FROM NHL_API
# NHL_script.process_yesterdays_scores_to_report()

# NHL DATA SCRAPE FROM MONEYPUCK
NHL_script.get_nhl_skaters()
NHL_script.get_nhl_goalies()
NHL_script.get_nhl_lines()
NHL_script.get_nhl_teams()

# Process Data
# NHL_data.process_nhl_data_and_generate_html()
NHL_script.combine_and_save_skaters(1, 'NHL_data/SOG_per_game.csv')
NHL_script.csv_to_html('NHL_data/SOG_per_game.csv')
