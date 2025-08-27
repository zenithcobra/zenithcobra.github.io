# filepath: /workspaces/zenithcobra.github.io/scripts/merge_schedule_teamstats.py
import re
from typing import Dict, Any, Tuple, List

SCHEDULE_LINE_RE = re.compile(
    r'^(?P<dt>\d{4}-\d{2}-\d{2} \d{2}:\d{2} [AP]M [A-Z]+)\s+-\s+'
    r'(?P<away>.+?)\s+@\s+(?P<home>.+?)\s+\((?P<status>[^)]+)\)\s*$'
)

TEAM_CELL_RE = re.compile(r'^\s*(?P<name>.+?)\s*<b>\((?P<rec>[^)]+)\)</b>\s*$')

def parse_schedule_text(schedule_text: str) -> List[Dict[str, str]]:
    games = []
    for line in schedule_text.strip().splitlines():
        line = line.rstrip()
        if not line:
            continue
        m = SCHEDULE_LINE_RE.match(line)
        if not m:
            continue
        d = m.groupdict()
        # Normalize team names (strip double spaces)
        d["away"] = re.sub(r'\s+', ' ', d["away"]).strip()
        d["home"] = re.sub(r'\s+', ' ', d["home"]).strip()
        games.append(d)
    return games

def parse_teams_table(html: str) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Returns structure:
    data[team][opponent] = {
        'team_record': str,
        'opp_record': str,
        'venue': str,
        'vs_record_against': str,
        'current_streak': str,
        'avg_win_streak': str,
        'avg_lose_streak': str,
        'record_sequence': str
    }
    """
    # Extract rows between <tr> ... </tr>
    rows = re.findall(r'<tr>(.*?)</tr>', html, flags=re.DOTALL | re.IGNORECASE)
    data: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for r in rows:
        # Extract all <td> contents
        tds = re.findall(r'<td>(.*?)</td>', r, flags=re.DOTALL | re.IGNORECASE)
        if len(tds) < 10:
            continue  # skip header or malformed
        team_cell = tds[2]
        vs_cell = tds[3]
        venue = re.sub(r'\s+', ' ', tds[4].strip())
        vs_record_against = re.sub(r'\s+', ' ', tds[5].strip())
        current_streak = re.sub(r'\s+', ' ', tds[6].strip())
        avg_win_streak = re.sub(r'\s+', ' ', tds[7].strip())
        avg_lose_streak = re.sub(r'\s+', ' ', tds[8].strip())
        record_sequence = re.sub(r'\s+', ' ', tds[9].strip())

        tm_match = TEAM_CELL_RE.match(team_cell)
        vs_match = TEAM_CELL_RE.match(vs_cell)
        if not (tm_match and vs_match):
            continue
        team_name = re.sub(r'\s+', ' ', tm_match.group('name').strip())
        team_record = tm_match.group('rec').strip()
        opp_name = re.sub(r'\s+', ' ', vs_match.group('name').strip())
        opp_record = vs_match.group('rec').strip()


        vs_record_against = '-'.join(part.strip() for part in vs_record_against.split(','))

        data.setdefault(team_name, {})
        data[team_name][opp_name] = {
            "team_record": team_record,
            "opp_record": opp_record,
            "venue": venue,
            "vs_record_against": vs_record_against,
            "current_streak": current_streak,
            "avg_win_streak": avg_win_streak,
            "avg_lose_streak": avg_lose_streak,
            "record_sequence": record_sequence
        }
    return data

def format_matchup_block(game: Dict[str, str],
                         stats_a: Dict[str, Any],
                         stats_b: Dict[str, Any],
                         width_team: int,
                         width_recseq: int) -> str:
    """
    Builds a text block with:
      - 6-space indent for header / team lines
      - Labeled stat lines (cs/aws/als/pgh) left, aligned so values start under headers
    """
    away = game['away']
    home = game['home']
    status = game['status']
    dt = game['dt']
    venue = stats_a.get('venue') or stats_b.get('venue') or ''

    away_rec = f"{stats_a.get('team_record','')}"
    home_rec = f"{stats_b.get('team_record','')}"

    away_seq = stats_a.get('record_sequence', '')[:28]
    home_seq = stats_b.get('record_sequence', '')[:28]

    # Values for labeled lines
    cs_away = stats_a.get('current_streak', '')
    cs_home = stats_b.get('current_streak', '')
    aws_away = stats_a.get('avg_win_streak', '')
    aws_home = stats_b.get('avg_win_streak', '')
    als_away = stats_a.get('avg_lose_streak', '')
    als_home = stats_b.get('avg_lose_streak', '')
    pgh_away = stats_a.get('vs_record_against', '')
    pgh_home = stats_b.get('vs_record_against', '')

    indent = "      "  # 6 spaces
    label_field_width = len(indent)  # so data columns align with indented lines

    def pad(s, w):
        return f"{s:<{w}}"

    def unlabeled_line(left, right):
        return f"{indent}{pad(left, width_team)}    {pad(right, width_team)}"
    
    def unlabeled_line2(left, right):
        return f"{indent}{pad(left, width_team)}     {pad(right, width_team)}"


    # For lines with '@' we customize
    line_status = f"{indent}({status})"
    line_dt = f"{indent}{dt}     @   {venue}"
    line_names = f"{indent}{pad(away + ' []', width_team)} @   {pad(home + ' []', width_team)}"
    line_records = unlabeled_line2(away_rec, home_rec)
    line_seq = unlabeled_line(away_seq, home_seq)

    # Labeled stat lines: label + space, then pad to label_field_width
    def stat_line(label, left_val, right_val):
        prefix = (label + ":").ljust(label_field_width)
        return f"{prefix}{pad(left_val, width_team)}     {pad(right_val, width_team)}"

    line_cs = stat_line("cs", cs_away, cs_home)
    line_aws = stat_line("aws", aws_away, aws_home)
    line_als = stat_line("als", als_away, als_home)
    line_pgh = stat_line("pgh", pgh_away, pgh_home)

    return "\n".join([
        line_status,
        line_dt,
        line_names,
        line_records,
        line_seq,
        line_cs,
        line_aws,
        line_als,
        line_pgh,
        ""
    ])

def build_schedule_view(schedule_text: str,
                        teams_table_html: str,
                        max_record_seq_chars: int = 70) -> str:
    games = parse_schedule_text(schedule_text)
    stats_map = parse_teams_table(teams_table_html)

    # Determine width for team column (same for away & home column)
    all_team_names = [g['away'] for g in games] + [g['home'] for g in games]
    width_team = max(len(name) for name in all_team_names) + 6  # padding
    width_recseq = max_record_seq_chars

    blocks = []
    for g in games:
        away = g['away']
        home = g['home']
        # Retrieve stats both perspectives
        stats_a = stats_map.get(away, {}).get(home, {})
        stats_b = stats_map.get(home, {}).get(away, {})
        block = format_matchup_block(g, stats_a, stats_b, width_team, width_recseq)
        blocks.append(block)
    return "\n".join(blocks)

# Example usage (adjust paths)
def format_schedule():
    schedule_path = "data/schedule_text.txt"
    table_path = "data/teams_table.html.txt"
    with open(schedule_path, "r", encoding="utf-8") as f:
        sched = f.read()
    with open(table_path, "r", encoding="utf-8") as f:
        table_html = f.read()
    view = build_schedule_view(sched, table_html)
    return view