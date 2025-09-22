"""
Main orchestration script for MLB data analysis and report generation.
This replaces the monolithic script.py with a modular, cacheable approach.
"""
import os
from typing import Dict, List, Any

import config
from cache_manager import cache
from MLB_data_fetcher import (
    get_date, get_schedule_by_date, get_schedule_text, get_standings_text,
    get_yesterdays_report, scrape_ballparks_table_to_json
)
from data_processor import (
    process_the_schedule, get_teams_playing_today_from_processed_schedule,
    get_team_history, get_team_records, analyze_team_dict,
    get_yesterdays_homers, analyze_sequence_and_predict
)
from html_generator import HTMLGenerator, process_html_advanced_features


class MLBReportGenerator:
    """Main class for generating MLB reports with caching and modular structure."""
    
    def __init__(self):
        self.html_generator = HTMLGenerator()
        config.ensure_directories()
    
    def generate_full_report(self) -> str:
        """Generate the complete MLB report HTML."""
        print("Starting MLB report generation...")
        
        # Get current date
        date = get_date()
        print(f"Generating report for {date}")
        
        # Fetch or load cached data
        report_data = self._fetch_all_data(date)
        
        # Generate HTML content
        html_content = self._generate_html_content(report_data)
        
        # Process HTML with advanced features
        final_html = process_html_advanced_features(html_content)
        
        # Save the final HTML
        cache.save_html(final_html, "index")
        
        print("MLB report generation completed!")
        return final_html
    
    def _fetch_all_data(self, date: str) -> Dict[str, Any]:
        """Fetch all required data with caching."""
        print("Fetching data...")
        
        data = {}
        
        # Basic schedule and date data
        print("- Getting schedule data...")
        data['schedule'] = get_schedule_by_date(date)
        data['processed_schedule'] = process_the_schedule(data['schedule'])
        data['schedule_text'] = self._get_cached_or_fetch_text('schedule_text', get_schedule_text)
        
        # Standings
        print("- Getting standings...")
        data['standings_text'] = self._get_cached_or_fetch_text('standings_text', get_standings_text)
        
        # Yesterday's report
        print("- Getting yesterday's report...")
        yesterdays_report = get_yesterdays_report()
        data['yesterdays_report_text'] = '\n'.join(yesterdays_report)
        cache.save_text(data['yesterdays_report_text'], 'yesterdays_report_text')
        
        # Teams data
        print("- Getting teams data...")
        data['teams_today'] = get_teams_playing_today_from_processed_schedule(data['processed_schedule'])
        data['team_history'] = get_team_history(data['teams_today'])
        data['team_data'] = get_team_records(data['team_history'])
        data['ballpark_data'] = self._get_cached_or_fetch_json('ballpark_data', scrape_ballparks_table_to_json)
        
        # Yesterday's home runs (placeholder - would need batters_with_streaks)
        print("- Getting yesterday's home runs...")
        try:
            # This would normally require batter streak data
            data['yesterday_home_run_data'] = []  # get_yesterdays_homers([])
        except Exception as e:
            print(f"Error getting yesterday's home runs: {e}")
            data['yesterday_home_run_data'] = []
        
        # Leader data (placeholder - would implement actual fetching)
        print("- Getting leader data...")
        data['era_leaders'] = self._get_cached_or_fetch_json('ERA_leader_data', lambda: [])
        data['so9_leaders'] = self._get_cached_or_fetch_json('SO9_leader_data', lambda: [])
        data['hr_leaders'] = self._get_cached_or_fetch_json('HR_leader_data', lambda: [])
        
        # Additional data files (placeholders)
        data['pitcher_data'] = cache.load_json('pitcher_data') or []
        data['batter_data'] = cache.load_json('batter_data') or []
        data['bvp_data'] = cache.load_json('batter_vs_pitcher_data') or []
        data['dh_batter_data'] = cache.load_json('dh_batter_data') or []
        
        # Text files
        data['parlay_banned_list'] = cache.load_text('parlay_banned_list') or "No banned list available"
        
        # Save key data to cache
        cache.save_json(data['schedule'], 'schedule_data')
        cache.save_json(data['teams_today'], 'teams_playing_today_data')
        cache.save_json(data['team_data'], 'team_data')
        cache.save_json(data['ballpark_data'], 'ballpark_data')
        
        return data
    
    def _get_cached_or_fetch_text(self, cache_key: str, fetch_function) -> str:
        """Get text data from cache or fetch it fresh."""
        cached_data = cache.load_text(cache_key)
        if cached_data is not None:
            print(f"  Using cached {cache_key}")
            return cached_data
        
        print(f"  Fetching fresh {cache_key}")
        data = fetch_function()
        cache.save_text(data, cache_key)
        return data
    
    def _get_cached_or_fetch_json(self, cache_key: str, fetch_function) -> List[Dict[str, Any]]:
        """Get JSON data from cache or fetch it fresh."""
        cached_data = cache.load_json(cache_key)
        if cached_data is not None:
            print(f"  Using cached {cache_key}")
            return cached_data
        
        print(f"  Fetching fresh {cache_key}")
        data = fetch_function()
        cache.save_json(data, cache_key)
        return data
    
    def _generate_html_content(self, data: Dict[str, Any]) -> str:
        """Generate the complete HTML content."""
        print("Generating HTML content...")
        
        # Process team data with analysis
        processed_team_data = analyze_team_dict(data['team_data'])
        
        # Generate individual HTML sections
        team_list_table = self.html_generator.generate_team_list_table(data['teams_today'])
        team_table = self.html_generator.generate_team_table(
            processed_team_data, data['ballpark_data'], data['schedule']
        )
        yesterday_hr_table = self.html_generator.generate_yesterday_home_run_table(
            data['yesterday_home_run_data']
        )
        leaders_table = self.html_generator.generate_leaders_table(
            data['era_leaders'], data['so9_leaders'], data['hr_leaders']
        )
        pitcher_table = self.html_generator.generate_pitcher_table(data['pitcher_data'])
        batter_table = self.html_generator.generate_batter_table(
            data['batter_data'], data['schedule'], data['ballpark_data']
        )
        bvp_table = self.html_generator.generate_bvp_table(
            data['bvp_data'], data['schedule'], data['ballpark_data']
        )
        dh_batter_table = self.html_generator.generate_dh_batter_table(
            data['dh_batter_data'], data['schedule'], data['ballpark_data']
        )
        
        # Create the complete HTML content
        content_sections = f"""
            <h2 id="parlay-banned-list">Parlay Banned List</h2>
            <pre>{data['parlay_banned_list']}</pre>
            
            <h2 id="yesterdays-report">Yesterdays History</h2>
            <pre>{data['yesterdays_report_text']}</pre>
            
            <h2 id="standings">Standings</h2>
            <pre>{data['standings_text']}</pre>
            
            <h2 id="todays-schedule">Today's Schedule</h2>
            <pre>{data['schedule_text']}</pre>
            
            <h2 id="teams">Filter Teams</h2>
            <pre>{team_list_table}</pre>
            
            <h2 id="records">Team Records</h2>
            <pre>{team_table}</pre>
            
            <h2 id="yesterdays-homers">Yesterdays Home Runs</h2>
            <pre>{yesterday_hr_table}</pre>
            
            <h2 id="leaders">League Leaders</h2>
            <pre>{leaders_table}</pre>
            
            <h2 id="match-overviews-pitchers">Pitcher Match Overviews</h2>
            <pre>{pitcher_table}</pre>
            
            <h2 id="match-overviews-batters">Roster Overviews</h2>
            <pre>{batter_table}</pre>
            
            <h2 id="dh-batters">DH Batters</h2>
            <pre>{dh_batter_table}</pre>
            
            <h2 id="bvp-stats">Batter vs Pitcher Stats</h2>
            <pre>{bvp_table}</pre>
        """
        
        # Insert content into base HTML structure
        base_html = self.html_generator.create_base_html_structure()
        final_html = base_html.replace('{content}', content_sections)
        
        return final_html
    
    def run_quick_update(self) -> str:
        """Run a quick update using mostly cached data."""
        print("Running quick update with cached data...")
        
        # Force refresh only time-sensitive data
        date = get_date()
        schedule_text = get_schedule_text()
        cache.save_text(schedule_text, 'schedule_text')
        
        standings_text = get_standings_text()
        cache.save_text(standings_text, 'standings_text')
        
        # Use cached data for everything else
        report_data = self._fetch_all_data(date)
        html_content = self._generate_html_content(report_data)
        final_html = process_html_advanced_features(html_content)
        
        cache.save_html(final_html, "index")
        print("Quick update completed!")
        return final_html


def main():
    """Main entry point for the script."""
    generator = MLBReportGenerator()
    
    # Check if we should do a full refresh or quick update
    # This could be controlled by command line arguments
    html_result = generator.generate_full_report()
    
    print(f"Report generated and saved to {config.INDEX_HTML_FILE}")
    return html_result


if __name__ == "__main__":
    main()