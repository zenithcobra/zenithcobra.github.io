import os
import json

def json_to_html_table(json_data, table_title):
    """
    Converts a list of dictionaries into an HTML table.
    
    Args:
        json_data (list): A list of dictionaries.
        table_title (str): The title of the table (e.g., the JSON file name).
    
    Returns:
        str: An HTML string representing the table.
    """
    if not json_data:
        return f"<h2>{table_title}</h2><p>No data available</p>"

    # Extract headers from the keys of the first dictionary
    headers = json_data[0].keys()

    # Start the HTML table
    html = f"<h2>{table_title}</h2>\n<table border='1'>\n<tr>"
    html += "".join(f"<th>{header}</th>" for header in headers)
    html += "</tr>\n"

    # Add rows for each dictionary
    for row in json_data:
        html += "<tr>"
        html += "".join(f"<td>{row.get(header, '')}</td>" for header in headers)
        html += "</tr>\n"

    html += "</table>\n"
    return html

def generate_html_from_json_files(directory, output_file):
    """
    Reads all JSON files in a directory, converts them to HTML tables, 
    and writes them to a single HTML file.
    
    Args:
        directory (str): The path to the directory containing JSON files.
        output_file (str): The path to the output HTML file.
    """
    all_tables = "<html><body>\n"

    # Iterate through all JSON files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            with open(file_path, "r", encoding="utf-8") as json_file:
                try:
                    json_data = json.load(json_file)
                    if isinstance(json_data, list) and all(isinstance(item, dict) for item in json_data):
                        table_html = json_to_html_table(json_data, table_title=filename)
                        all_tables += table_html + "<br>\n"
                    else:
                        print(f"Skipping {filename}: Not a list of dictionaries.")
                except json.JSONDecodeError:
                    print(f"Skipping {filename}: Invalid JSON format.")

    all_tables += "</body></html>"

    # Write the combined HTML to the output file
    with open(output_file, "w", encoding="utf-8") as output:
        output.write(all_tables)

    print(f"HTML file generated: {output_file}")

# Example usage
directory_path = "data/"  # Replace with the path to your JSON files
output_html_file = "output.html"       # Replace with the desired output file name
generate_html_from_json_files(directory_path, output_html_file)