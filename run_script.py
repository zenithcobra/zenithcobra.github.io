import NHL_script

# NHL DATA SCRAPE FROM MONEYPUCK
NHL_script.get_nhl_skaters()
NHL_script.get_nhl_goalies()
NHL_script.get_nhl_lines()
NHL_script.get_nhl_teams()

# Process Data
# NHL_data.process_nhl_data_and_generate_html()
NHL_script.combine_and_save_skaters(2, 'NHL_data/SOG_per_game.csv')
NHL_script.csv_to_html('NHL_data/SOG_per_game.csv')
# NHL_script.add_checkboxes_to_html('NHL_data/SOG_per_game.html')
# NHL_script.rename_csv_headers()
# NHL_script.make_nhl_report_today()
