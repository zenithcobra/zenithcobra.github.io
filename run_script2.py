import importlib
import script
import NHL_script
import NHL_data

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
