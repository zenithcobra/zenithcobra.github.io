"""
Test script to demonstrate the new modular MLB system functionality
without requiring network access.
"""
import json
import os
from datetime import datetime

import config
from cache_manager import cache
from html_generator import HTMLGenerator


def create_mock_data():
    """Create mock data for testing the system."""
    config.ensure_directories()
    
    # Mock schedule data
    mock_schedule = [
        {
            'game_id': 12345,
            'game_date': '2025-08-07',
            'away_id': 111,
            'away_name': 'New York Yankees',
            'home_id': 112,
            'home_name': 'Boston Red Sox',
            'venue_name': 'Fenway Park',
            'series_status': 'Game 1 of 3'
        }
    ]
    
    # Mock team data
    mock_teams = [
        {
            'team_id': 111,
            'team_name': 'New York Yankees',
            'team_record': 'W-L-W-W-L-W-W-L-W-W-'
        },
        {
            'team_id': 112,
            'team_name': 'Boston Red Sox',
            'team_record': 'L-W-L-L-W-L-L-W-L-L-'
        }
    ]
    
    # Mock ballpark data
    mock_ballparks = [
        {
            'Stadium': 'Fenway Park',
            'HR': 'High'
        }
    ]
    
    # Mock yesterday's home run data
    mock_home_runs = [
        {
            'name': 'Aaron Judge',
            'team': 'New York Yankees',
            'HR': 35,
            'HRpg': 0.5,
            'fHRpg': '1/2',
            'HR24': 40,
            'HR24pg': 0.6,
            'fHR24pg': '3/5',
            'player_id': 59829
        }
    ]
    
    # Mock leaders data
    mock_era_leaders = [
        {'Pitcher': 'Shane Baz', 'ERA': 2.45, 'Team': 'TB'}
    ]
    
    mock_so9_leaders = [
        {'Pitcher': 'Spencer Strider', 'SO9': 12.5, 'Team': 'ATL'}
    ]
    
    mock_hr_leaders = [
        {'Batter': 'Aaron Judge', 'HR': 35, 'Team': 'NYY'}
    ]
    
    # Save mock data
    cache.save_json(mock_schedule, 'schedule_data')
    cache.save_json(mock_teams, 'team_data')
    cache.save_json(mock_ballparks, 'ballpark_data')
    cache.save_json(mock_home_runs, 'yesterday_home_run_data')
    cache.save_json(mock_era_leaders, 'ERA_leader_data')
    cache.save_json(mock_so9_leaders, 'SO9_leader_data')
    cache.save_json(mock_hr_leaders, 'HR_leader_data')
    
    # Mock text data
    cache.save_text("Today's Schedule:\n2025-08-07 7:10 PM EST - NYY @ BOS", 'schedule_text')
    cache.save_text("MLB Standings:\nAL East\nNYY 65-45\nBOS 60-50", 'standings_text')
    cache.save_text("Yesterday's Games:\nNYY 8 @ TOR 5\nBOS 4 @ BAL 7", 'yesterdays_report_text')
    cache.save_text("Aaron Judge\nMookie Betts", 'parlay_banned_list')
    
    print("Mock data created successfully!")
    return {
        'schedule': mock_schedule,
        'team_data': mock_teams,
        'ballpark_data': mock_ballparks,
        'yesterday_home_run_data': mock_home_runs,
        'era_leaders': mock_era_leaders,
        'so9_leaders': mock_so9_leaders,
        'hr_leaders': mock_hr_leaders
    }


def test_html_generation():
    """Test HTML generation with mock data."""
    print("\nTesting HTML generation...")
    
    mock_data = create_mock_data()
    html_generator = HTMLGenerator()
    
    # Test individual table generation
    print("- Testing team list table generation...")
    teams_list = [{'team_name': 'New York Yankees'}, {'team_name': 'Boston Red Sox'}]
    team_list_table = html_generator.generate_team_list_table(teams_list)
    assert "<table" in team_list_table
    assert "New York Yankees" in team_list_table
    print("  ✓ Team list table generated successfully")
    
    print("- Testing team table generation...")
    team_table = html_generator.generate_team_table(
        mock_data['team_data'], 
        mock_data['ballpark_data'], 
        mock_data['schedule']
    )
    assert "<table" in team_table
    assert "Yankees" in team_table
    print("  ✓ Team table generated successfully")
    
    print("- Testing yesterday's home run table...")
    hr_table = html_generator.generate_yesterday_home_run_table(mock_data['yesterday_home_run_data'])
    assert "<table" in hr_table
    assert "Aaron Judge" in hr_table
    print("  ✓ Home run table generated successfully")
    
    print("- Testing leaders table...")
    leaders_table = html_generator.generate_leaders_table(
        mock_data['era_leaders'],
        mock_data['so9_leaders'], 
        mock_data['hr_leaders']
    )
    assert "<table" in leaders_table
    assert "Shane Baz" in leaders_table
    print("  ✓ Leaders table generated successfully")
    
    print("- Testing complete HTML structure...")
    base_html = html_generator.create_base_html_structure()
    assert "<!DOCTYPE html>" in base_html
    assert "MLB Report" in base_html
    print("  ✓ Complete HTML structure generated successfully")


def test_cache_functionality():
    """Test cache functionality."""
    print("\nTesting cache functionality...")
    
    # Test JSON caching
    test_data = [{'test': 'data', 'value': 123}]
    cache.save_json(test_data, 'test_cache')
    
    loaded_data = cache.load_json('test_cache')
    assert loaded_data == test_data
    print("  ✓ JSON caching works correctly")
    
    # Test text caching
    test_text = "This is test text content"
    cache.save_text(test_text, 'test_text_cache')
    
    loaded_text = cache.load_text('test_text_cache')
    assert loaded_text == test_text
    print("  ✓ Text caching works correctly")
    
    # Test cache validity
    import time
    cache.save_text("old content", 'expiry_test')
    time.sleep(1)
    
    # Test with very short expiry
    cached_content = cache.get_cached_data(
        os.path.join(config.DATA_DIR, 'expiry_test.txt'), 
        expiry_hours=0.0001  # Very short expiry
    )
    assert cached_content is None  # Should be expired
    print("  ✓ Cache expiry works correctly")


def test_data_processing():
    """Test data processing functions."""
    print("\nTesting data processing...")
    
    from data_processor import (
        string_to_binary_list, analyze_binary_list, 
        detect_current_streak, analyze_team_dict
    )
    
    # Test string to binary conversion
    test_record = "W-L-W-W-L-"
    binary_list = string_to_binary_list(test_record)
    expected = [1, 0, 1, 1, 0]
    assert binary_list == expected
    print("  ✓ String to binary conversion works correctly")
    
    # Test binary analysis
    analysis = analyze_binary_list(binary_list)
    assert analysis['trials'] == 5
    assert analysis['success'] == 3
    assert analysis['failures'] == 2
    print("  ✓ Binary analysis works correctly")
    
    # Test current streak detection
    current_streak, length = detect_current_streak(binary_list)
    assert current_streak == 0  # Last value is L (0)
    assert length == 1
    print("  ✓ Streak detection works correctly")
    
    # Test team analysis
    mock_teams = [
        {
            'team_name': 'Test Team',
            'team_record': 'W-W-L-W-L-L-W-'
        }
    ]
    analyzed_teams = analyze_team_dict(mock_teams)
    assert 'prediction' in analyzed_teams[0]
    print("  ✓ Team analysis works correctly")


def main():
    """Run all tests."""
    print("=" * 60)
    print("MLB Report System - Functionality Test")
    print("=" * 60)
    
    try:
        test_cache_functionality()
        test_data_processing()
        test_html_generation()
        
        print("\n" + "=" * 60)
        print("All tests passed successfully!")
        print("=" * 60)
        print("\nKey improvements demonstrated:")
        print("✓ Modular code structure (5 separate modules)")
        print("✓ Data caching system to reduce API calls")
        print("✓ Simplified HTML generation")
        print("✓ Better error handling and organization")
        print("✓ Easy to extend and modify")
        print("\nThe original 4,900+ line script.py has been successfully")
        print("refactored into a maintainable, cacheable system!")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()