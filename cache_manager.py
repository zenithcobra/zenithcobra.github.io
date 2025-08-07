"""
Cache management for MLB data to reduce API calls and improve performance.
"""
import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import config


class CacheManager:
    """Manages caching of MLB data to reduce API calls."""
    
    def __init__(self):
        config.ensure_directories()
    
    def is_cache_valid(self, file_path: str, expiry_hours: int = config.CACHE_EXPIRY_HOURS) -> bool:
        """Check if cached file is still valid based on modification time."""
        if not os.path.exists(file_path):
            return False
        
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        expiry_time = datetime.now() - timedelta(hours=expiry_hours)
        
        return file_mod_time > expiry_time
    
    def get_cached_data(self, file_path: str, expiry_hours: int = config.CACHE_EXPIRY_HOURS) -> Optional[Any]:
        """Get cached data if it's still valid."""
        if self.is_cache_valid(file_path, expiry_hours):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    if file_path.endswith('.json'):
                        return json.load(file)
                    else:
                        return file.read()
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error reading cached file {file_path}: {e}")
                return None
        return None
    
    def save_data(self, data: Any, file_path: str, archive_existing: bool = True) -> None:
        """Save data to file with optional archiving of existing file."""
        if archive_existing and os.path.exists(file_path):
            self._archive_existing_file(file_path)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                if file_path.endswith('.json'):
                    json.dump(data, file, indent=4)
                else:
                    if isinstance(data, list):
                        file.writelines(data)
                    else:
                        file.write(str(data))
            print(f"Data saved to {file_path}")
        except (IOError, TypeError) as e:
            print(f"Error saving data to {file_path}: {e}")
    
    def _archive_existing_file(self, file_path: str) -> None:
        """Archive existing file with yesterday's date."""
        yesterday_date = (datetime.now() - timedelta(days=1)).strftime(config.DATE_FORMAT_FILE)
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        archived_filename = f"{name}_{yesterday_date}{ext}"
        archived_path = os.path.join(config.ARCHIVED_DATA_DIR, archived_filename)
        
        if not os.path.exists(archived_path):
            try:
                os.rename(file_path, archived_path)
                print(f"Archived existing file to {archived_path}")
            except OSError as e:
                print(f"Error archiving file {file_path}: {e}")
        else:
            print(f"Archived file already exists: {archived_path}")
    
    def save_json(self, data: List[Dict], filename: str) -> None:
        """Save data as JSON with automatic archiving."""
        file_path = os.path.join(config.DATA_DIR, f"{filename}.json")
        self.save_data(data, file_path)
    
    def save_text(self, content: str, filename: str) -> None:
        """Save content as text file."""
        file_path = os.path.join(config.DATA_DIR, f"{filename}.txt")
        self.save_data(content, file_path)
    
    def save_html(self, content: str, filename: str) -> None:
        """Save content as HTML file."""
        file_path = os.path.join(config.DOCS_DIR, f"{filename}.html")
        self.save_data(content, file_path, archive_existing=False)
    
    def load_json(self, filename: str, expiry_hours: int = config.CACHE_EXPIRY_HOURS) -> Optional[List[Dict]]:
        """Load JSON data from cache if valid."""
        file_path = os.path.join(config.DATA_DIR, f"{filename}.json")
        return self.get_cached_data(file_path, expiry_hours)
    
    def load_text(self, filename: str, expiry_hours: int = config.CACHE_EXPIRY_HOURS) -> Optional[str]:
        """Load text data from cache if valid."""
        file_path = os.path.join(config.DATA_DIR, f"{filename}.txt")
        return self.get_cached_data(file_path, expiry_hours)
    
    def get_or_fetch(self, cache_key: str, fetch_function, *args, **kwargs) -> Any:
        """Get data from cache or fetch it using the provided function."""
        cached_data = self.load_json(cache_key)
        if cached_data is not None:
            print(f"Using cached data for {cache_key}")
            return cached_data
        
        print(f"Fetching fresh data for {cache_key}")
        data = fetch_function(*args, **kwargs)
        self.save_json(data, cache_key)
        return data
    
    def clear_cache(self, pattern: Optional[str] = None) -> None:
        """Clear cached files, optionally matching a pattern."""
        for filename in os.listdir(config.DATA_DIR):
            if pattern is None or pattern in filename:
                file_path = os.path.join(config.DATA_DIR, filename)
                try:
                    os.remove(file_path)
                    print(f"Removed cached file: {file_path}")
                except OSError as e:
                    print(f"Error removing file {file_path}: {e}")


# Global cache manager instance
cache = CacheManager()