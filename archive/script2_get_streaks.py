# # GET THE STREAKS DATA FROM THE WEB

# import requests
# from bs4 import BeautifulSoup
# import csv
# import os
# from datetime import datetime, timedelta

# # Ensure the "text_output" folder exists
# os.makedirs("text_output", exist_ok=True)

# # Get yesterday's date
# yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# # File paths
# file_name = "hitting-streak.csv"
# file_path = f"text_output/{file_name}"
# backup_file_path = f"text_output/hitting-streak_{yesterday}.csv"

# # Check if the file already exists and rename it
# if os.path.exists(file_path):
#     os.rename(file_path, backup_file_path)

# # URL of the webpage
# url = "https://www.baseballmusings.com/cgi-bin/CurStreak.py"

# # Send a GET request to the URL
# response = requests.get(url)

# # Check if the request was successful
# if response.status_code == 200:
#     # Parse the HTML content of the page
#     soup = BeautifulSoup(response.content, 'html.parser')
    
#     # Find the table in the HTML
#     table = soup.find('table')
    
#     if table:
#         # Extract table rows
#         rows = table.find_all('tr')
        
#         # Extract table data
#         table_data = []
#         for row in rows:
#             cells = row.find_all(['td', 'th'])  # Include both header and data cells
#             table_data.append([cell.get_text(strip=True) for cell in cells])
        
#         # Write the table data to a CSV file
#         with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
#             writer = csv.writer(csv_file)
#             writer.writerows(table_data[2:])
        
#         print(f"New file saved to {file_path}")
#         if os.path.exists(backup_file_path):
#             print(f"Existing file renamed to {backup_file_path}")
#     else:
#         print("No table found on the page.")
# else:
#     print(f"Failed to retrieve the page. Status code: {response.status_code}")


