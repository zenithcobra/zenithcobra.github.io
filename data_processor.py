"""
Data processing and analysis functions for MLB data.
Extracted from script.py to improve organization.
"""
import json
import os
import re
import statsapi
from datetime import datetime, timedelta
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple

import config
from cache_manager import cache


def detect_current_streak(sequence: List[int]) -> Tuple[int, int]:
    """
    Detects the current streak (value and length) in the sequence.
    
    Args:
        sequence: A list of 1s and 0s representing wins and losses.
    
    Returns:
        tuple: A tuple containing the current streak value (1 or 0) and its length.
    """
    last_value = sequence[-1]
    streak_length = 0
    for value in reversed(sequence):
        if value == last_value:
            streak_length += 1
        else:
            break
    return last_value, streak_length


def predict_streak_continuation(current_streak: Tuple[int, int], stats: Dict[str, float]) -> int:
    """
    Predicts whether the current streak will continue or transition.
    
    Args:
        current_streak: A tuple containing the current streak value (1 or 0) and its length.
        stats: A dictionary containing streak statistics.
    
    Returns:
        int: The predicted next value (1 for win, 0 for loss).
    """
    streak_value, streak_length = current_streak

    if streak_value == 1:  # Current streak is a win streak
        if streak_length >= stats["longest_win_streak"]:
            return 0  # Predict a transition to a loss
        elif streak_length < stats["average_win_streak_length"]:
            return 1  # Predict continuation of the win streak
    elif streak_value == 0:  # Current streak is a loss streak
        if streak_length >= stats["longest_lose_streak"]:
            return 1  # Predict a transition to a win
        elif streak_length < stats["average_lose_streak_length"]:
            return 0  # Predict continuation of the loss streak

    # Default to continuation if no clear prediction can be made
    return streak_value


def string_to_binary_list(record_string: str) -> List[int]:
    """Convert a team record string (like 'W-L-W-L-') to binary list."""
    binary_list = []
    for char in record_string:
        if char == 'W':
            binary_list.append(1)
        elif char == 'L':
            binary_list.append(0)
    return binary_list


def analyze_binary_list(binary_list: List[int]) -> Dict[str, int]:
    """Analyze a binary list and return statistics."""
    trials = len(binary_list)
    success = sum(binary_list)
    failures = trials - success
    
    return {
        'trials': trials,
        'success': success,
        'failures': failures
    }


def find_streaks_with_analysis(binary_list: List[int]) -> Dict[str, Any]:
    """Find streaks in binary data and return analysis."""
    streaks = []
    if not binary_list:
        return {'streaks': []}
    
    current_value = binary_list[0]
    current_length = 1
    
    for i in range(1, len(binary_list)):
        if binary_list[i] == current_value:
            current_length += 1
        else:
            streaks.append({'value': current_value, 'length': current_length})
            current_value = binary_list[i]
            current_length = 1
    
    # Add the final streak
    streaks.append({'value': current_value, 'length': current_length})
    
    return {'streaks': streaks}


def analyze_streaks(streaks: List[Dict[str, int]]) -> Dict[str, float]:
    """Analyze streak data and return statistics."""
    win_streaks = [s['length'] for s in streaks if s['value'] == 1]
    lose_streaks = [s['length'] for s in streaks if s['value'] == 0]
    
    return {
        'number_of_win_streaks': len(win_streaks),
        'longest_win_streak': max(win_streaks) if win_streaks else 0,
        'average_win_streak_length': sum(win_streaks) / len(win_streaks) if win_streaks else 0,
        'number_of_lose_streaks': len(lose_streaks),
        'longest_lose_streak': max(lose_streaks) if lose_streaks else 0,
        'average_lose_streak_length': sum(lose_streaks) / len(lose_streaks) if lose_streaks else 0,
    }


def reverse_list(input_list: List[Any]) -> List[Any]:
    """Reverse a list."""
    return input_list[::-1]


def text_streak_distribution(streaks: List[Dict[str, int]]) -> str:
    """Create a text-based graph of streak distributions."""
    if not streaks:
        return "No streak data available"
    
    win_lengths = [s['length'] for s in streaks if s['value'] == 1]
    lose_lengths = [s['length'] for s in streaks if s['value'] == 0]
    
    max_length = max([s['length'] for s in streaks])
    
    graph_lines = []
    for length in range(1, min(max_length + 1, 11)):  # Limit to 10 for readability
        win_count = win_lengths.count(length)
        lose_count = lose_lengths.count(length)
        
        win_bar = 'W' * win_count
        lose_bar = 'L' * lose_count
        
        graph_lines.append(f"{length:2d}: {win_bar:<10} {lose_bar}")
    
    return '\n'.join(graph_lines)


def process_the_schedule(schedule: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process the raw schedule data into a more usable format."""
    processed_schedule = []
    
    for game in schedule:
        processed_game = {
            'game_id': game.get('game_id'),
            'game_date': game.get('game_date'),
            'game_datetime': game.get('game_datetime'),
            'away_id': game.get('away_id'),
            'away_name': game.get('away_name'),
            'away_probable_pitcher': game.get('away_probable_pitcher'),
            'home_id': game.get('home_id'),
            'home_name': game.get('home_name'),
            'home_probable_pitcher': game.get('home_probable_pitcher'),
            'venue_id': game.get('venue_id'),
            'venue_name': game.get('venue_name'),
            'status': game.get('status'),
            'series_status': game.get('series_status')
        }
        processed_schedule.append(processed_game)
    
    return processed_schedule


def get_teams_playing_today_from_processed_schedule(processed_schedule: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Extract teams playing today from processed schedule."""
    teams_today = []
    
    for game in processed_schedule:
        away_team = {'team_name': game.get('away_name'), 'team_id': game.get('away_id')}
        home_team = {'team_name': game.get('home_name'), 'team_id': game.get('home_id')}
        
        if away_team not in teams_today:
            teams_today.append(away_team)
        if home_team not in teams_today:
            teams_today.append(home_team)
    
    return teams_today


def get_team_history(teams_list: List[Dict[str, Any]], games_back: int = 10) -> List[Dict[str, Any]]:
    """Get recent game history for teams."""
    for team in teams_list:
        team_id = team.get('team_id')
        
        # Get recent games for this team
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)  # Look back 30 days to get enough games
        
        try:
            recent_games = statsapi.schedule(
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                team=team_id
            )
            
            # Get the last 'games_back' completed games
            completed_games = [g for g in recent_games if g.get('status') == 'Final']
            last_games = completed_games[-games_back:] if len(completed_games) >= games_back else completed_games
            
            team['last_games'] = [g.get('game_id') for g in last_games]
            
        except Exception as e:
            print(f"Error getting history for team {team.get('team_name')}: {e}")
            team['last_games'] = []
    
    return teams_list


def get_team_records(teams_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process team history to generate a record of wins and losses for each team."""
    for team in teams_history:
        team_id = team.get('team_id')
        team_name = team.get('team_name')
        team_history = team.get('last_games', [])
        team_record = ''
        list_of_results = []

        for game_id in team_history:
            try:
                schedule_data = statsapi.schedule(game_id=game_id)
                
                if not schedule_data or not schedule_data[0]:
                    print(f"Warning: No schedule data found for game_id {game_id}")
                    continue

                game_data = schedule_data[0]

                # Determine the winning team
                winning_team = game_data.get('winning_team')
                if not winning_team:
                    # Fallback: Determine the winner based on scores
                    away_score = game_data.get('away_score', 0)
                    home_score = game_data.get('home_score', 0)
                    away_team = game_data.get('away_name')
                    home_team = game_data.get('home_name')

                    if away_score > home_score:
                        winning_team = away_team
                    elif home_score > away_score:
                        winning_team = home_team
                    else:
                        print(f"Warning: Unable to determine winner for game_id {game_id}")
                        continue

                # Determine if the current team won or lost
                if winning_team == team_name:
                    team_record += 'W-'
                    vs_team = game_data.get('losing_team', 
                              game_data.get('home_name') if game_data.get('away_name') == team_name 
                              else game_data.get('away_name'))
                    result_info = {
                        'game_id': game_id,
                        'vs_team': vs_team,
                        'game_date': game_data.get('game_date'),
                        'result': 'W'
                    }
                else:
                    team_record += 'L-'
                    result_info = {
                        'game_id': game_id,
                        'vs_team': winning_team,
                        'game_date': game_data.get('game_date'),
                        'result': 'L'
                    }

                list_of_results.append(result_info)
                
            except Exception as e:
                print(f"Error processing game {game_id} for team {team_name}: {e}")
                continue

        # Update the team history with the record and detailed results
        team.update({
            'team_record': team_record, 
            'team_record_plus': list_of_results
        })

    return teams_history


def analyze_team_dict(team_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze team data and add predictions."""
    for team in team_data:
        team_record = team.get('team_record', '')
        
        # Convert record to binary for analysis
        binary_record = string_to_binary_list(team_record)
        
        if binary_record:
            # Analyze streaks
            streaks = find_streaks_with_analysis(binary_record)
            streak_stats = analyze_streaks(streaks.get('streaks', []))
            
            # Get current streak and predict
            current_streak, amount = detect_current_streak(reverse_list(binary_record))
            stats = {
                "longest_win_streak": streak_stats.get('longest_win_streak', 0),
                "average_win_streak_length": streak_stats.get('average_win_streak_length', 0),
                "longest_lose_streak": streak_stats.get('longest_lose_streak', 0),
                "average_lose_streak_length": streak_stats.get('average_lose_streak_length', 0),
            }
            
            predicted_outcome = predict_streak_continuation((current_streak, amount), stats)
            
            # Add predictions to team data
            team.update({
                'prediction': 'W' if predicted_outcome == 1 else 'L',
                'wl_mmp': f"{'W' if current_streak == 1 else 'L'}{amount}",
                'wl_mmpp': streak_stats.get('average_win_streak_length' if current_streak == 1 else 'average_lose_streak_length', 0)
            })
        else:
            team.update({
                'prediction': 'Unknown',
                'wl_mmp': 'No data',
                'wl_mmpp': 0
            })
    
    return team_data


def analyze_sequence_and_predict(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze sequence data and add predictions for home run data."""
    for item in data:
        # This would contain the original home run prediction logic
        # For now, add placeholder prediction data
        item.update({
            'prediction': 'Unknown',
            'hr_mmp': 'No data',
            'hr_mmpp': 0
        })
    
    return data


def get_yesterdays_homers(batters_with_streaks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Get yesterday's home run data with statistics."""
    # Get yesterday's schedule
    oneday = timedelta(days=1)
    yesterday_date = datetime.now().date() - oneday
    yschedule = statsapi.schedule(start_date=yesterday_date, end_date=yesterday_date)

    homers = []
    
    for game in yschedule:
        # Get scoring plays
        scoring_plays = statsapi.game_scoring_plays(game.get("game_id"))
        scoring_plays_list = scoring_plays.split("\n")
        
        # Filter for home runs
        filtered_plays = [line for line in scoring_plays_list if "homers" in line]
        processed_plays = [line.split(")")[0] + ")" for line in filtered_plays if ")" in line]
        
        homers.extend(processed_plays)

    # Extract player names and get stats
    new_homers = [homer.split("homers")[0].strip() for homer in homers if "(" in homer]
    
    stat_homers = []
    for player_name in new_homers:
        try:
            # Get current season stats
            player_stats = statsapi.player_stat_data(
                next(x['id'] for x in statsapi.get('sports_players', {
                    'season': str(config.CURRENT_SEASON), 
                    'gameType': 'W'
                })['people'] if x['fullName'] == player_name),
                'hitting', 'season'
            )
            
            player_data = {'name': player_name}
            
            if player_stats:
                team_name = player_stats.get('current_team')
                player_id = player_stats.get('id')
                
                player_data.update({
                    'team': team_name,
                    'player_id': player_id
                })
                
                for stat in player_stats.get('stats', []):
                    stats_dict = stat.get('stats', {})
                    games_played = float(stats_dict.get('gamesPlayed', 1))
                    hrs = float(stats_dict.get('homeRuns', 0))
                    
                    player_data.update({
                        'HR': int(hrs),
                        'HRpg': round(hrs / games_played, 2),
                        'fHRpg': str(Fraction(round(hrs / games_played, 2)).limit_denominator(7))
                    })
                
                # Get previous season stats
                try:
                    prev_stats = statsapi.player_stat_data(
                        player_id, group="hitting", type="season", 
                        sportId=1, season=config.CURRENT_SEASON - 1
                    )
                    
                    if prev_stats:
                        for stat in prev_stats.get('stats', []):
                            prev_stats_dict = stat.get('stats', {})
                            hrs2 = float(prev_stats_dict.get('homeRuns', 0))
                            games_played2 = float(prev_stats_dict.get('gamesPlayed', 1))
                            
                            player_data.update({
                                'HR24': int(hrs2),
                                'HR24pg': round(hrs2 / games_played2, 2),
                                'fHR24pg': str(Fraction(round(hrs2 / games_played2, 2)).limit_denominator(7))
                            })
                except:
                    player_data.update({'HR24': '', 'HR24pg': '', 'fHR24pg': ''})
            
            stat_homers.append(player_data)
            
        except Exception as e:
            print(f"Error getting stats for {player_name}: {e}")
            continue

    # Filter out empty entries and add streak data
    filtered_stat_homers = [
        player for player in stat_homers
        if not all(value == "" for value in player.values())
    ]
    
    # Add streak data from batters_with_streaks
    for player in filtered_stat_homers:
        player_id = player.get('player_id')
        for batter in batters_with_streaks:
            if batter.get('player_id') == player_id:
                player['HR_record'] = batter.get("HR_record", "")
                break

    return filtered_stat_homers