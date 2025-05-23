import json

# Read the JSON file
with open("text_output/teams_playing_today.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Ensure the data is a list
if isinstance(data, list):
    teams_list = data
else:
    raise ValueError("The JSON file does not contain a list.")

# Print the list to verify
print(teams_list)