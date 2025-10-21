import script
import NHL_script

# RUNNING THE SCRIPT
print("script getting schedule")

# MLB SCHEDULE INFO
script.update_picture()

# NHL SCHEDULE
NHL_script.make_todays_schedule()

# NHL yesterdays scoring report
NHL_script.process_yesterdays_scores_to_report()
