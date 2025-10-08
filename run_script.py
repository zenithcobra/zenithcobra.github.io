import importlib
import script
import NHL_script
import NHL_data_fetcher

# Reload the script after making changes
importlib.reload(script)

# RUNNING THE SCRIPT
print('script getting date')
# DATES
date = script.get_date()

print('script getting schedule')
# SCHEDULE INFO
script.update_picture()

NHL_script.make_todays_schedule()
NHL_script.process_yesterdays_scores_to_report()

NHL_data_fetcher.get_nhl_skaters()
NHL_data_fetcher.get_nhl_goalies()
NHL_data_fetcher.get_nhl_lines()
NHL_data_fetcher.get_nhl_teams()
