import importlib
import script
import NHL_script

# Reload the script after making changes
importlib.reload(script)

# RUNNING THE SCRIPT 
# =========================================
# *****************************************
# -----------------------------------------
#
# START HERE 
# basically you run scripts that make json files of of the info you provide
# then you convert those json scrits to html tables
# then you open those html tables or just plain text files in the index.html file when you are done
# -----------------------------------------
# *****************************************
# =========================================

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


# YESTERDAYS REPORT
print(' -----=======-----')
print('script getting yesterdays report')
yesterdays_report = script.get_yesterdays_report()
script.save_list_to_text(yesterdays_report,'yesterdays_report_text')


# SCHEDULE INFO
print(' -----=======-----')
print('script getting schedule')
schedule = script.get_schedule_by_date(date)
processed_schedule = script.process_the_schedule(schedule)
raw_schedule_text = script.get_schedule_text()
schedule_text = script.process_schedule_text(raw_schedule_text)
script.save_to_json(schedule,'schedule_data')
script.save_to_text(schedule_text, 'schedule_text')


# STANDINGS
print(' -----=======-----')
print('script getting schedule')
standings_text = script.get_standings_text()
script.save_to_text(standings_text, "standings_text")


# LEAGUE LEADERS
print(' -----=======-----')
print('script getting league leaders')
eras_leaders = script.league_leaders_era()
so9_leaders = script.league_leaders_strikeouts_per_9_innings()
hr_leaders = script.league_leaders_hrs()
hr_leaders = script.league_leaders_hrs_2day(processed_schedule)
script.save_to_json(eras_leaders, 'ERA_leader_data')
script.save_to_json(so9_leaders, 'SO9_leader_data')
script.save_to_json(hr_leaders, 'HR_leader_data')
script.save_to_json(hr_leaders, 'HR_leader_data_2day')


# TEAMS PLAYING TODAY and History and Records
print(' -----=======-----')
print('script getting team info')
teams_today = script.get_teams_playing_today_from_processed_schedule(processed_schedule)
team_history = script.get_team_history(teams_today)
team_wins = script.get_team_records(team_history)
ballparks = script.scrape_ballparks_table_to_json()
filtered_team_data = script.process_team_data(team_wins)
script.save_to_json(teams_today, 'teams_playing_today_data')
script.save_to_json(filtered_team_data, 'team_data')
script.save_to_json(ballparks, 'ballpark_data')


# PITCHERS
print(' -----=======-----')
print('script  getting pitchers')
pitchers_today = script.process_pitchers_from_processed_schedule(processed_schedule)
processed_pitchers = script.add_stats_to_pitchers(pitchers_today)
script.save_to_json(processed_pitchers,"pitcher_data")


# BATTERS
print(' -----=======-----')
print('script getting batters and yesterdays homers')
rooster = script.process_players_from_roster_into_list(processed_schedule)
batters = script.add_stats_to_batters(rooster)
script.save_to_json(batters,"batter_data")
yesterdays_home_runs = script.get_yesterdays_homers()
yesterday_home_runs_2day = script.yesterday_hrs_2day(processed_schedule, yesterdays_home_runs)
script.save_to_json(yesterday_home_runs_2day,'yesterday_home_run_data')


# CONVERTS
# json data
# 'data/yesterdays_report_text.txt'
# 'data/schedule_text.txt'
# 'data/standings_text.txt'
# 'data/schedule_data.json'
schedule_data = 'data/schedule_data.json'
script.save_to_html(script.json_to_html_table(schedule_data), "schedule_data")
era_leader = 'data/ERA_leader_data.json'
script.save_to_html(script.json_to_html_table(era_leader), "era_leader_text")
s09_leader = 'data/SO9_leader_data.json'
script.save_to_html(script.json_to_html_table(s09_leader), "s09_leader_text")
hr_leader = 'data/HR_leader_data.json'
script.save_to_html(script.json_to_html_table(hr_leader), "hr_leader_text")
teams_today = 'data/teams_playing_today_data.json'
script.save_to_html(script.json_to_html_table(teams_today), "teams_today_text")
team_data = 'data/team_data.json'
script.save_to_html(script.json_to_html_table(team_data), "team_data_text")
ballpark_data = 'data/ballpark_data.json'
script.save_to_html(script.json_to_html_table(ballpark_data), "ballpark_data_text")
pitcher_data = 'data/pitcher_data.json'
script.save_to_html(script.json_to_html_table(pitcher_data), "pitcher_data_text")
batter_data = 'data/batter_data.json'
script.save_to_html(script.json_to_html_table(batter_data), "batter_data_text")
yesterday_homerun_data = 'data/yesterday_home_run_data.json'
script.save_to_html(script.json_to_html_table(yesterday_homerun_data), "yesterday_homerun_data_text")


batter_data = 'data/batter_data.json'

batters = script.read_json_file(batter_data)
for x in batters:
    # print(x)

    stats_for_player = script.get_season_stats(x['player_id'])
    # print(stats_for_player)
    try:
        for key,value in stats_for_player.items():
            x.update({key:value})
    except:
        continue

flattened_list = [script.flatten_dict(entry) for entry in batters]

for x in flattened_list:
    link_name = script.name_to_baseball_reference_anchor(x['player_name'])
    x.update({'p_name':x['player_name']})
    x.update({'player_name':link_name})


batter_data2 = 'batter_data2'
script.save_to_json(flattened_list,batter_data2)
batter_s = 'data/batter_data2.json'
script.save_to_html(script.json_to_html_table(batter_s), "batter_s")
script.fix_escaped_links_in_file('data/batter_s.html')
