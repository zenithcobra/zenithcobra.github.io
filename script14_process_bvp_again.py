
import os
import json
from bs4 import BeautifulSoup
import statsapi
from datetime import datetime, timedelta
from fractions import Fraction

# -------

# File path for the JSON file
json_file_path = "text_output/teams_last_10_games.json"

# Ensure the file exists
if not os.path.exists(json_file_path):
    raise FileNotFoundError(f"{json_file_path} does not exist.")

# Read the JSON file into a dictionary
with open(json_file_path, "r", encoding="utf-8") as file:
    teams_last_10_games = json.load(file)


# ---------


html_file_path = "text_output/BVP.txt"

# Ensure the files exist
if not os.path.exists(html_file_path):
    raise FileNotFoundError(f"{html_file_path} does not exist.")

# Parse the HTML table and convert it into a list of lists
def parse_html_table_to_list(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()
    
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table")
    
    if not table:
        raise ValueError("No table found in the HTML file.")
    
    rows = []
    for tr in table.find_all("tr"):
        row = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        rows.append(row)
    
    return rows


html_table_as_list = parse_html_table_to_list(html_file_path)
players_bvp = html_table_as_list[1:]

for x in players_bvp:
    # print(x[0])
    player = statsapi.lookup_player(x[0])
    x.append(player[0]['id'])
    x.append(player[0]['currentTeam']['id'])

for q in players_bvp:
    player_id = q[10]
    team_id = q[11]
    last_games_list = teams_last_10_games.get(str(team_id), [])
    hr_record = ''
    hits_record = ''
    rbi_record = ''
    for game in last_games_list:
        boxscore = statsapi.boxscore_data(game, timecode=None)
        for x in boxscore.get('awayBatters'):
            if player_id == x.get('personId'):
                hr_record = hr_record + x.get('hr') + '-'
                hits_record = hits_record + x.get('h') + '-'
                rbi_record = rbi_record + x.get('rbi') + '-'
        for x in boxscore.get('homeBatters'):
            if player_id == x.get('personId'):
                hr_record = hr_record + x.get('hr') + '-'
                hits_record = hits_record + x.get('h') + '-'
                rbi_record = rbi_record + x.get('rbi') + '-'
    q.append(hr_record)
    q.append(hits_record)
    q.append(rbi_record)

for w in players_bvp:
    name = w[0]
    player_id = w[10]
    # ------------------
    # ------------------
    try:
        beans = statsapi.player_stat_data(next(x['id'] for x in statsapi.get('sports_players',{'season':2025,'gameType':'W'})['people'] if x['fullName']==name), 'hitting', 'season') 
    except StopIteration:
        print(f"No player found with the name '{z}'.")
        beans = None  # Set beans to None or handle it appropriately
    except Exception as e:
        print(f"An error occurred: {e}")
        beans = None  # Set beans to None or handle it appropriately
    try:
        beans2 = statsapi.player_stat_data(next(x['id'] for x in statsapi.get('sports_players',{'season':2024,'gameType':'W'})['people'] if x['fullName']==name), 'hitting', 'season') 
    except StopIteration:
        print(f"No player found with the name '{name}'.")
        beans2 = None  # Set beans to None or handle it appropriately
    except Exception as e:
        print(f"An error occurred: {e}")
        beans2 = None  # Set beans to None or handle it appropriately
    # ------------------
    # ------------------
    # beans = statsapi.player_stat_data(next(x['id'] for x in statsapi.get('sports_players',{'season':2025,'gameType':'W'})['people'] if x['fullName']==name), 'hitting', 'season') 

    if beans:  # Only proceed if a matching player is found
        # print(beans)    
        for a in beans.get('stats'):
            games_played = float(int(a.get('stats').get('gamesPlayed')))
            hrs = float(int(a.get('stats').get('homeRuns')))
            hits = float(int(a.get('stats').get('hits')))
            rbi = float(int(a.get('stats').get('rbi')))
            hrs_per_game = round((hrs / games_played), 3)
            fhrs_per_game = str(Fraction(round((hrs / games_played), 2)).limit_denominator(7))
            hits_per_game = round((hits / games_played), 3)
            fhits_per_game = str(Fraction(round((hits / games_played), 2)).limit_denominator(7))
            rbis_per_game = round((rbi / games_played), 3)
            frbis_per_game = str(Fraction(round((rbi / games_played), 2)).limit_denominator(7))
            w.append(int(hrs))
            w.append(f"{hrs_per_game}")
            w.append(f"{fhrs_per_game}")
            w.append(f"{int(hits)}")
            w.append(f"{hits_per_game}")
            w.append(f"{fhits_per_game}")
            w.append(f"{int(rbi)}")
            w.append(f"{rbis_per_game}")
            w.append(f"{frbis_per_game}")

        # # Fetch stats for 2024
        # beans2 = statsapi.player_stat_data(next(x['id'] for x in statsapi.get('sports_players',{'season':2025,'gameType':'W'})['people'] if x['fullName']==name), 'hitting', 'season') 

        # if beans2:  # Only proceed if a matching player is found for 2024
        #     # print(beans2)
        #     for b in beans2.get('stats'):
        #         # bhrs = float(int(b.get('stats').get('homeRuns')))
        #         bhrs = int(b.get('stats').get('homeRuns'))
        #         # bbhrs = bhrs + 0.24
        #         w.append(f"{bhrs}")
        # else:
        #     w.append('n/a')  # If no stats found for 2024, append 0
    if beans2:
        beans2_id = beans2.get('id')
        beans3 = statsapi.player_stat_data(beans2_id, group="hitting", type="season", sportId=1, season=2024)
    
        for b in beans3.get('stats'):
            hrs2 = float(int(b.get('stats').get('homeRuns')))
            # print(hrs2)
            games_played2 = float(int(b.get('stats').get('gamesPlayed')))
            hrs_per_game4 = round((hrs2 / games_played2), 2)
            hrs_per_game3 = str(Fraction(round((hrs2 / games_played2), 2)).limit_denominator(7))
            
            w.append(f"{int(hrs2)}") 
            w.append(f"{hrs_per_game4}")  
            w.append(f"{hrs_per_game3}")  

    else:
        w.append('n/a')  # If no stats found for 2024, append 0
        w.append('n/a')  # If no stats found for 2024, append 0
        w.append('n/a')  # If no stats found for 2024, append 0
        print(f"Player '{name}' not found in the sports_players list.")
    # ------------------



# ---------------save new html

# Get yesterday's date
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# File paths
bvp_file_path = "text_output/BVP2.txt"
backup_file_path = f"text_output/BVP2_{yesterday}.txt"

# Check if BVP.html exists and rename it
if os.path.exists(bvp_file_path):
    os.rename(bvp_file_path, backup_file_path)


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

# Open the new BVP.html file in write mode
with open(bvp_file_path, "w") as file:
    # Write the opening HTML tags
    # file.write("<h1>Batter vs Pitcher Stats</h1>\n")

    # Write the heading for the pitcher
    # file.write(f"<h3>{pitcher_heading}</h3>\n")

    # Start the table
    file.write("<table border='1'>\n") 
    file.write("<tr>\n") 
    file.write("<th>Batter</th>\n") #0
    file.write("<th>Team</th>\n") #1
    file.write("<th>Pitcher</th>\n") #2
    file.write("<th>AB</th>\n") #3
    file.write("<th>H</th>\n") #4
    file.write("<th>HR</th>\n") #5
    file.write("<th>AVG</th>\n") #6
    file.write("<th>RBI</th>\n") #7
    file.write("<th>OBP</th>\n") #8
    file.write("<th>OPS</th>\n") #9
    file.write("<th>HR25</th>\n") #15
    file.write("<th>HRpg25</th>\n") #16
    file.write("<th>fHRpg25</th>\n") #17
    file.write("<th>HR24</th>\n") #24
    file.write("<th>HR24pg</th>\n") #25
    file.write("<th>fHR24pg</th>\n") #26
    file.write("<th>PAST HRS</th>\n") #12
    file.write("<th>PAST HITS</th>\n") #13
    file.write("<th>PAST RBIS</th>\n") #14
    file.write("<th>H25</th>\n") #18
    file.write("<th>Hpg25</th>\n") #19
    file.write("<th>fHpg25</th>\n") #20
    file.write("<th>RBI25</th>\n") #21
    file.write("<th>RBIpg25</th>\n") #22
    file.write("<th>fRBIpg25</th>\n") #23
    file.write("</tr>\n")

    # Write data for each pitcher
    for b in players_bvp:
        file.write("<tr>\n")
        file.write(f"<td>{b[0]}</td>\n")
        file.write(f"<td>{b[1]}</td>\n")
        file.write(f"<td>{b[2]}</td>\n")
        file.write(f"<td>{b[3]}</td>\n")
        file.write(f"<td>{b[4]}</td>\n")
        file.write(f"<td>{b[5]}</td>\n")
        file.write(f"<td>{b[6]}</td>\n")
        file.write(f"<td>{b[7]}</td>\n")
        file.write(f"<td>{b[8]}</td>\n")
        file.write(f"<td>{b[9]}</td>\n")
        file.write(f"<td>{b[15]}</td>\n")
        file.write(f"<td>{b[16]}</td>\n")
        file.write(f"<td>{b[17]}</td>\n")
        file.write(f"<td>{b[24]}</td>\n")
        file.write(f"<td>{b[25]}</td>\n")
        file.write(f"<td>{b[26]}</td>\n")
        file.write(f"<td>{b[12]}</td>\n")
        file.write(f"<td>{b[13]}</td>\n")
        file.write(f"<td>{b[14]}</td>\n")
        file.write(f"<td>{b[18]}</td>\n")
        file.write(f"<td>{b[19]}</td>\n")
        file.write(f"<td>{b[20]}</td>\n")
        file.write(f"<td>{b[21]}</td>\n")
        file.write(f"<td>{b[22]}</td>\n")
        file.write(f"<td>{b[23]}</td>\n")
        file.write("</tr>\n")

    # Close the table
    file.write("</table>\n")
    file.write("<br>\n")  # Add a line break for better readability
    file.write(sortable_script)

    # Write the closing HTML tags
    # file.write("</body>\n</html>\n")

print(f"New BVP file saved to {bvp_file_path}")
if os.path.exists(backup_file_path):
    print(f"Existing BVP file renamed to {backup_file_path}")



