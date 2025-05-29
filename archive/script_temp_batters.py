# open batters list to a csv file
import os
import csv
import statsapi

# Ensure the "text_output" folder exists
os.makedirs("text_output", exist_ok=True)

# File path for the CSV file
csv_file_path = "text_output/batters_today.csv"


# Initialize an empty list to store the batters
list_of_batters = []

# Read the CSV file
with open(csv_file_path, mode="r", newline="", encoding="utf-8") as file:
    reader = csv.reader(file)
    
    # Skip the header row
    next(reader)
    
    # Append each row to the list
    for row in reader:
        list_of_batters.append(row)

new_list_with_stats = []
for z in list_of_batters:
    new_list_with_stats.append(z[0])  # name
    new_list_with_stats.append(z[1])  # team
    new_list_with_stats.append(z[2])  # hrs

    # Get player ID for the current name
    players = statsapi.get('sports_players', {'season': 2025, 'gameType': 'W'})['people']
    player = next((x for x in players if x['fullName'] == z[0]), None)  # Use None as fallback if no match is found

    if player:  # Only proceed if a matching player is found
        p_id = player['id']
        beans = statsapi.player_stat_data(p_id, 'hitting', 'season')
        for a in beans.get('stats'):
            games_played = float(int(a.get('stats').get('gamesPlayed')))
            hits = float(int(a.get('stats').get('hits')))
            new_list_with_stats.append(hits)
            hrs = float(int(a.get('stats').get('homeRuns')))
            rbi = float(int(a.get('stats').get('rbi')))
            new_list_with_stats.append(rbi)
            hrs_per_game = round((hrs / games_played), 3)
            new_list_with_stats.append(hrs_per_game)
            hits_per_game = round((hits / games_played), 3)
            new_list_with_stats.append(hits_per_game)
            rbis_per_game = round((rbi / games_played), 3)
            new_list_with_stats.append(rbis_per_game)

        # Fetch stats for 2024
        players_2024 = statsapi.get('sports_players', {'season': 2024, 'gameType': 'W'})['people']
        player_2024 = next((x for x in players_2024 if x['fullName'] == z[0]), None)

        if player_2024:  # Only proceed if a matching player is found for 2024
            p_id_2024 = player_2024['id']
            beans2 = statsapi.player_stat_data(p_id_2024, 'hitting', 'season')
            for b in beans2.get('stats'):
                bhrs = float(int(b.get('stats').get('homeRuns')))
                new_list_with_stats.append(bhrs)
    else:
        print(f"Player '{z[0]}' not found in the sports_players list.")

# Write the new list with stats to a CSV file
output_file_path = "text_output/updated_batters_with_stats.csv"
with open(output_file_path, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    # Write the header
    writer.writerow(["Name", "Team", "Hrs", "Hits", "RBI", "HRpg","Hpg", "RBIpg", "HR24"])
    
    # Write the data
    for i in range(0, len(new_list_with_stats), 9):
        writer.writerow(new_list_with_stats[i:i + 9])
print(f"Updated batters with stats written to {output_file_path}")