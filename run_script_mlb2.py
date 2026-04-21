import importlib
import script
import NHL_script

# Reload the script after making changes
importlib.reload(script)

# RUNNING THE SCRIPT 
# yesterdays_report_text.txt
# schedule_data.json
# schedule_text.txt
# standings_text.txt
# ERA_leader_data.json
# SO9_leader_data.json
# HR_leader_data.json
# teams_playing_today_data.json
# team_data.json
# ballpark_data.json
# pitcher_data.json
# batter_data.json
# yesterday_home_run_data.json

# DATES
print(' -----=======-----')
print('script getting date')
date = script.get_date()

# SCHEDULE INFO
print(' -----=======-----')
print('script getting schedule')
schedule = script.get_schedule_by_date(date)
processed_schedule = script.process_the_schedule(schedule)
raw_schedule_text = script.get_schedule_text()
schedule_text = script.process_schedule_text(raw_schedule_text)
script.save_to_json(schedule,'schedule_data')
script.save_to_text(schedule_text, 'schedule_text')

