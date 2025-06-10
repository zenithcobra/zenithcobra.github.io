# # GET TODAYS SCHEDULE

# import statsapi
# from datetime import datetime, timedelta
# import os
# import pytz

# # Ensure the "text_output" folder exists
# os.makedirs("text_output", exist_ok=True)

# # Get yesterday's date
# yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# # File paths
# file_name = "todays_schedule.txt"
# report_file_path = f"text_output/{file_name}"

# # Get today's date
# mlb_date = datetime.now().strftime("%m/%d/%Y")
# schedule = statsapi.schedule(start_date=mlb_date, end_date=mlb_date)

# # -----------------------------------
# for x in schedule:
#     # Example UTC datetime string
#     utc_datetime_str = x.get("game_datetime")

#     # Parse the UTC datetime string
#     utc_datetime = datetime.strptime(utc_datetime_str, '%Y-%m-%dT%H:%M:%SZ')

#     # Define the UTC and Eastern Time zones
#     utc_zone = pytz.utc
#     eastern_zone = pytz.timezone('US/Eastern')

#     # Localize the datetime to UTC
#     utc_datetime = utc_zone.localize(utc_datetime)

#     # Convert to Eastern Time
#     eastern_datetime = utc_datetime.astimezone(eastern_zone)

#     # Format the datetime in a readable format
#     readable_format = eastern_datetime.strftime('%Y-%m-%d %I:%M %p %Z')

#     beans = x.get('summary').split('-')
#     new_beans = readable_format + " - " + beans[3].strip()
#     x.update({"summary": new_beans})
# # -----------------------------------


# today_schedule_content = "Today's Schedule:\n" + "\n".join(
#     f'{x.get("summary")}' for x in schedule
# )
# # ----------------------------------

# # Combine all content
# full_content = (
#     today_schedule_content
# )

# # Write content to the new Todays_Report.txt file
# with open(report_file_path, "w") as file:
#     file.write(full_content)

# print(f"New report saved to {report_file_path}")



