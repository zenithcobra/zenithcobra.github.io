import importlib
import script
import NHL_script

# Reload the script after making changes
importlib.reload(script)

# RUNNING THE SCRIPT
print('script getting date')
# DATES
date = script.get_date()


print('script getting schedule')
# SCHEDULE INFO
script.update_picture()

NHL_script.process_schedule()
NHL_script.process_yesterdays_scores_to_report()
NHL_script.process_raw_skaters_html_table()