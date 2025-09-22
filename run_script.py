import importlib
import script
import NHL_todays_schedule

# Reload the script after making changes
importlib.reload(script)

# RUNNING THE SCRIPT 

print('script getting date')
# DATES
date = script.get_date()


print('script getting yesterdays report')
# YESTERDAYS REPORT
yesterdays_report = script.get_yesterdays_report()
script.save_list_to_text(yesterdays_report,'yesterdays_report_text')


print('script getting schedule')
# SCHEDULE INFO
schedule = script.get_schedule_by_date(date)
processed_schedule = script.process_the_schedule(schedule)
raw_schedule_text = script.get_schedule_text()
schedule_text = script.process_schedule_text(raw_schedule_text)
script.save_to_json(schedule,'schedule_data')
script.save_to_text(schedule_text, 'schedule_text')


print('script getting standings')
# STANDINGS
standings_text = script.get_standings_text()
script.save_to_text(standings_text, "standings_text")


print('script getting team info')
# TEAMS PLAYING TODAY and History and Records
teams_today = script.get_teams_playing_today_from_processed_schedule(processed_schedule)
team_history = script.get_team_history(teams_today)
team_wins = script.get_team_records(team_history)
ballparks = script.scrape_ballparks_table_to_json()
script.save_to_json(teams_today, 'teams_playing_today_data')
script.save_to_json(team_wins, 'team_data')
script.save_to_json(ballparks, 'ballpark_data')


print('script  getting pitchers')
# PITCHERS
pitchers_today = script.process_pitchers_from_processed_schedule(processed_schedule)
processed_pitchers = script.add_stats_to_pitchers(pitchers_today)
script.save_to_json(processed_pitchers,"pitcher_data")


print('script getting batters')
# BATTERS
rooster = script.process_players_from_roster_into_list(processed_schedule)
batters = script.add_stats_to_batters(rooster)
batters_with_streaks = script.process_batters(batters,team_history)
batter_vs_pitcher = script.old_batter_vs_pitchers_get()
batter_vs_pitcher_with_streaks = script.get_streaks_for_bvp(batter_vs_pitcher,batters_with_streaks)
todays_dh_batters = script.find_dh_batters_add_stats_streaks(schedule, batters_with_streaks)
yesterdays_home_runs = script.get_yesterdays_homers(batters_with_streaks)
script.save_to_json(batters_with_streaks, "batter_data")
script.save_to_json(batter_vs_pitcher_with_streaks,'batter_vs_pitcher_data')
script.save_to_json(todays_dh_batters, 'dh_batter_data')
script.save_to_json(yesterdays_home_runs,'yesterday_home_run_data')

# analysis of home runs
bvp_data = script.read_json_list('data/batter_vs_pitcher_data.json')

for a in bvp_data:
    hr = a.get('all_HR_record', '')
    hr_analysis_dict = script.analyze_score_sequence(hr)
    a.update({'all_HR_analysis': hr_analysis_dict})
    h = a.get('all_H_record', '')
    h_analysis_dict = script.analyze_score_sequence(h)
    a.update({'all_H_analysis': h_analysis_dict})
    rbi = a.get('all_RBI_record', '')
    rbi_analysis_dict = script.analyze_score_sequence(rbi)
    a.update({'all_RBI_analysis': rbi_analysis_dict})

script.save_to_json(bvp_data, "batter_vs_pitcher_data")

print('script getting league leaders')
# LEAGUE LEADERS
eras_leaders = script.league_leaders_era()
so9_leaders = script.league_leaders_strikeouts_per_9_innings()
hr_leaders = script.league_leaders_hrs()
script.save_to_json(eras_leaders, 'ERA_leader_data')
script.save_to_json(so9_leaders, 'SO9_leader_data')
script.save_to_json(hr_leaders, 'HR_leader_data')


print('make index')
index_html = script.make_index()
# script.save_to_text(index_html, 'raw_index')

# index_html = make_index()
# processed_html = script.process_html(index_html)
# print(processed_html)
# script.save_to_html(processed_html,'index')

NHL_todays_schedule.process_schedule()
