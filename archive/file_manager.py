import os
from shutil import move

def ensure_folder_exists(folder_name):
    """Ensure a folder exists, create it if it doesn't."""
    os.makedirs(folder_name, exist_ok=True)

def move_files_to_folder(file_names, folder_name, date_suffix):
    """Move files to a folder with the current date appended."""
    ensure_folder_exists(folder_name)
    for file_name in file_names:
        if os.path.exists(file_name):
            new_file_name = f"{os.path.splitext(file_name)[0]}-{date_suffix}{os.path.splitext(file_name)[1]}"
            move(file_name, os.path.join(folder_name, new_file_name))

def read_file(file_path):
    """Read the content of a file."""
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return file.read()
    return ""

def write_file(file_path, content):
    """Write content to a file."""
    with open(file_path, "w") as file:
        file.write(content)

def prepend_to_file(file_path, content):
    """Prepend content to a file."""
    existing_content = read_file(file_path)
    write_file(file_path, content + "\n\n" + existing_content)