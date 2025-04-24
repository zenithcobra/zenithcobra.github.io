import statsapi
from datetime import datetime, timedelta
from collections import defaultdict



def get_yesterday_date():
    """Get yesterday's date in YYYY-MM-DD format."""
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

def get_current_date():
    import datetime
    """Get the current date in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")

def fetch_schedule(date):
    """Fetch the MLB schedule for a given date."""
    return statsapi.schedule(start_date=date, end_date=date)

def fetch_standings(date):
    """Fetch MLB standings for a given date."""
    return (
        statsapi.standings(leagueId=103, date=date) +
        statsapi.standings(leagueId=104, date=date)
    )

def fetch_player_stats(categories, years, limit=75):
    """Fetch player stats for given categories and years."""
    stats = defaultdict(list)
    for category, label in categories:
        for year in years:
            beans = statsapi.league_leader_data(category, season=year, limit=limit, statGroup='hitting')
            for x in beans:
                stats[(category, year)].append((x[1], x[2], x[3]))  # (Player Name, Team, Value)
    return stats

def format_stats(stats):
    """Format stats into a readable string."""
    formatted = []
    for (category, year), players in stats.items():
        formatted.append(f"\n{category.upper()} {year}:\n")
        for name, team, value in sorted(players, key=lambda x: (x[0], x[1])):
            formatted.append(f"{name:<20} {team:<25} {value}")
    return "\n".join(formatted)