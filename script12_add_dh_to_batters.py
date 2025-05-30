import statsapi
from datetime import datetime, timedelta
from fractions import Fraction

# Get today's date
mlb_date = datetime.now().strftime("%m/%d/%Y")
print(mlb_date)
schedule = statsapi.schedule(start_date=mlb_date, end_date=mlb_date)

# yesterday = (datetime.now() - timedelta(days=9)).strftime("%Y-%m-%d")
# schedule = statsapi.schedule(start_date=yesterday, end_date=yesterday)

games = []
for x in schedule:
    json_string = statsapi.get("game", {"gamePk": x.get('game_id')})
    games.append(json_string)

# Fetch the JSON string
# json_string = statsapi.get("game", {"gamePk": 777807})
# json_string = games[1]  # Assuming we want the first game in the schedule
list_of_names = []
for x in games:
    beans = []
    json_string = x
    livedata = json_string.get('liveData').get('boxscore').get('teams')

    # Extract abbreviations for away team players
    # print("Away Team Abbreviations:")
    for player_id, player_data in livedata.get('away').get('players').items():
        full_name = player_data.get('person', {}).get('fullName', 'Unknown')
        abbreviation = player_data.get('position', {}).get('abbreviation', 'N/A')  # Default to 'N/A' if not found
        if abbreviation == 'DH':
            # print(f"Name: {full_name}, Player ID: {player_id}, Abbreviation: {abbreviation}")
            beans.append(full_name)
    # Extract team names
    # Extract abbreviations for home team players
    # print("\nHome Team Abbreviations:")
    for player_id, player_data in livedata.get('home').get('players').items():
        full_name = player_data.get('person', {}).get('fullName', 'Unknown')
        abbreviation = player_data.get('position', {}).get('abbreviation', 'N/A')  # Default to 'N/A' if not found
        if abbreviation == 'DH':
            # print(f"Name: {full_name}, Player ID: {player_id}, Abbreviation: {abbreviation}")
            beans.append(full_name)
    list_of_names.append(beans)

# for z in list_of_names:
#     print(z)

all_names = []
for x in list_of_names:
    for y in x:
        all_names.append(y)
    # print(x)

# for x in all_names:
#     print(x)
# remove duplicates from the list
all_names = list(set(all_names))
# Print the unique names
print("Unique DH Batter Names:")
for name in all_names:
    print(name)

# search homers for team name and hr stats
stat_homers = []
for z in all_names:
    # print(z)
    # beans = ''
    beans = statsapi.player_stat_data(next(x['id'] for x in statsapi.get('sports_players',{'season':2025,'gameType':'W'})['people'] if x['fullName']==z), 'hitting', 'season') 
    new_list_with_stats = []
    if beans:  # Only proceed if a matching player is found
        name = z
        new_list_with_stats.append(name)
        team_name = beans.get('current_team')    
        new_list_with_stats.append(team_name)
        for a in beans.get('stats'):
            games_played = float(int(a.get('stats').get('gamesPlayed')))
            # hits = float(int(a.get('stats').get('hits')))
            # new_list_with_stats.append(f"{hits}")
            hrs = float(int(a.get('stats').get('homeRuns')))
            new_list_with_stats.append(f"{int(hrs)}")
            # rbi = float(int(a.get('stats').get('rbi')))
            # new_list_with_stats.append(f"{rbi}")
            hrs_per_game = round((hrs / games_played), 2)
            new_list_with_stats.append(f"{hrs_per_game}")
            hrs_per_game2 = str(Fraction(round((hrs / games_played), 2)).limit_denominator(20))
            #str(Fraction(round(float(x[18])/float(x[6]),2)).limit_denominator(5))
            new_list_with_stats.append(f"{hrs_per_game2}")
            # hits_per_game = round((hits / games_played), 3)
            # new_list_with_stats.append(f"{hits_per_game}")
            # rbis_per_game = round((rbi / games_played), 3)
            # new_list_with_stats.append(f"{rbis_per_game}")
    stat_homers.append(new_list_with_stats)

# save all names to a csv file called "text_output/FOUND_DH_BATTERS.csv"
import csv
with open("text_output/FOUND_DH_BATTERS.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    for name in all_names:
        writer.writerow([name])

# JavaScript for making tables sortable
sortable_script = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;

    const comparer = (idx, asc) => (a, b) => ((v1, v2) =>
        v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)
    )(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

    document.querySelectorAll('th').forEach(th => th.addEventListener('click', (() => {
        const table = th.closest('table');
        Array.from(table.querySelectorAll('tr:nth-child(n+2)'))
            .sort(comparer(Array.from(th.parentNode.children).indexOf(th), this.asc = !this.asc))
            .forEach(tr => table.appendChild(tr) );
    })));
});
</script>
"""
dh_file_path = "text_output/DH_BATTERS.txt"
# Open the new BVP.html file in write mode
with open(dh_file_path, "w") as file:
    # Write the opening HTML tags
    # file.write("<h1>Batter vs Pitcher Stats</h1>\n")

    # Write the heading for the pitcher
    # file.write(f"<h3>{pitcher_heading}</h3>\n")

    # Start the table
    file.write("<table border='1'>\n")
    file.write("<tr>\n")
    file.write("<th>Batter</th>\n")
    file.write("<th>Team</th>\n")
    file.write("<th>HR</th>\n")
    file.write("<th>HRpg</th>\n")
    file.write("<th>fHRpg</th>\n")
    file.write("</tr>\n")

    # # Write data for each pitcher
    # for batter in all_names:
    #     file.write("<tr>\n")
    #     file.write(f"<td>{batter}</td>\n")
    #     file.write("</tr>\n")
    for contents in stat_homers:
        # file.write(f"{contents}\n")
        # Start the table
        file.write("<tr>\n")
        file.write(f"<td>{contents[0]}</td>\n")
        file.write(f"<td>{contents[1]}</td>\n")
        file.write(f"<td>{contents[2]}</td>\n")
        file.write(f"<td>{contents[3]}</td>\n")
        file.write(f"<td>{contents[4]}</td>\n")
        file.write("</tr>\n")
    # Close the table
    file.write("</table>\n")
    file.write("<br>\n")  # Add a line break for better readability
    file.write(sortable_script)

    # Write the closing HTML tags
    # file.write("</body>\n</html>\n")

print(f"New BVP file saved to {dh_file_path}")

