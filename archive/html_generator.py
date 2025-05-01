import os

def generate_html_from_text(file_path, output_dir):
    """Generate an HTML file from a text file."""
    if not os.path.exists(file_path):
        print(f"File {file_path} not found, skipping.")
        return None

    with open(file_path, "r") as file:
        content = file.read()

    html_filename = os.path.splitext(os.path.basename(file_path))[0] + ".html"
    html_filepath = os.path.join(output_dir, html_filename)

    with open(html_filepath, "w") as html_file:
        html_file.write(f"<!DOCTYPE html>\n<html>\n<head>\n<title>{file_path}</title>\n</head>\n<body>\n")
        html_file.write(f"<pre>{content}</pre>\n")
        html_file.write(f"<a href='index.html'>Back to Index</a>\n</body>\n</html>")

    return html_filename

def generate_index_html(html_files, output_dir):
    """Generate an index HTML file linking to all other HTML files."""
    index_filepath = os.path.join(output_dir, "index.html")
    with open(index_filepath, "w") as index_file:
        index_file.write(f"<!DOCTYPE html>\n<html>\n<head>\n<title>Index</title>\n</head>\n<body>\n")
        index_file.write("<h1>Index</h1>\n<ul>\n")
        for html_file in html_files:
            index_file.write(f"<li><a href='{html_file}'>{html_file}</a></li>\n")
        index_file.write(f"<li><a href='https://www.fantasyalarm.com/mlb/lineups'>BVP checker</a></li>\n")
        index_file.write(f"<li><a href='https://www.baseball-reference.com'>baseball-reference</a></li>\n")
        index_file.write(f"<li><a href='https://baseballsavant.mlb.com'>baseball-savant</a></li>\n")
        index_file.write(f"<li><a href='https://www.fangraphs.com'>fangraphs</a></li>\n")
        index_file.write(f"<li><a href='https://www.statmuse.com/mlb'>Stat muse</a></li>\n")
        index_file.write("</ul>\n</div>\n</body>\n</html>")
        index_file.write("</ul>\n</body>\n</html>")