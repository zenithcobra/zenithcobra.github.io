# filepath: /workspaces/zenithcobra.github.io/scripts/merge_schedule_teamstats.py
import re
from typing import Dict, Any, Tuple, List

POSITION_ORDER = {
    "C": 1, "1B": 2, "2B": 3, "3B": 4, "SS": 5,
    "LF": 6, "CF": 7, "RF": 8, "OF": 9,
    "DH": 10, "UTIL": 11, "PH": 12, "PR": 13
}

def _position_sort_key(p):
    pos = p.get("position", "").upper().strip()
    return POSITION_ORDER.get(pos, 99), p.get("player_name","")

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


def _normalize_team_name(name: str) -> str:
    """
    Light normalization to help match pitcher team names to schedule/team table names.
    Adjust mapping as needed.
    """
    name = name.strip()
    # Map shortened / alternate forms
    aliases = {
        "Athletics": "Oakland Athletics",
        "D-backs": "Arizona Diamondbacks",
    }
    return aliases.get(name, name)

def build_pitcher_map(pitcher_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Returns { normalized_team_name : pitcher_entry }.
    If multiple pitchers per team appear, the first is kept (customize if needed).
    """
    m = {}
    for p in pitcher_data:
        team = p.get("pitchers_team")
        if not team:
            continue
        key = _normalize_team_name(team)
        # Keep first (assumed probable starter); replace logic if you prefer latest.
        m.setdefault(key, p)
    return m

def build_batter_map(batter_data):
    """
    Returns: { team_name : [ { 'player_name': ..., 'position': ... }, ... ] }
    Filters out malformed entries (many in your file only have RBI_record).
    """
    team_map = {}
    for entry in batter_data or []:
        if not isinstance(entry, dict):
            continue
        name = entry.get("player_name")
        hr_record = entry.get("HR_record")
        hr_record = hr_record[:18]
        hrz = int(entry.get("HR"))
        if int(hrz) < 10:
            hrz = ' ' + str(hrz)
        pos2 = entry.get("position")
        if len(pos2.strip()) == 1:
            pos2 = '_' + pos2
        pos = str(pos2) + '  ' + str(hrz)
        team = entry.get("team")
        if not (name and pos and team):
            continue
        # Normalize spacing
        team_norm = re.sub(r'\s+', ' ', team).strip()
        pos_norm = pos.strip()
        team_map.setdefault(team_norm, []).append({
            "player_name": name.strip(),
            "position": pos_norm
        })
    # Sort rosters
    for t, roster in team_map.items():
        roster.sort(key=_position_sort_key)
    return team_map

def format_matchup_block(game: Dict[str, str],
                         stats_a: Dict[str, Any],
                         stats_b: Dict[str, Any],
                         width_team: int,
                         width_recseq: int,
                         pitcher_map: Dict[str, Dict[str, Any]],
                         batter_map: Dict[str, list]) -> str:
    """
    Extended: adds pitcher lines (pp / era / s09 / hr9 / h9 / w / l) if found.
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

    # Team stats
    cs_away = stats_a.get('current_streak', '')
    cs_home = stats_b.get('current_streak', '')
    aws_away = stats_a.get('avg_win_streak', '')
    aws_home = stats_b.get('avg_win_streak', '')
    als_away = stats_a.get('avg_lose_streak', '')
    als_home = stats_b.get('avg_lose_streak', '')
    pgh_away = stats_a.get('vs_record_against', '')
    pgh_home = stats_b.get('vs_record_against', '')

    # Pitchers
    away_pitcher_entry = pitcher_map.get(_normalize_team_name(away), {}) or {}
    home_pitcher_entry = pitcher_map.get(_normalize_team_name(home), {}) or {}

    away_stats = away_pitcher_entry.get("stats", {}) or {}
    home_stats = home_pitcher_entry.get("stats", {}) or {}

    away_pitcher = away_pitcher_entry.get("pitcher", "")
    home_pitcher = home_pitcher_entry.get("pitcher", "")
    away_era = away_pitcher_entry.get("ERA", away_stats.get("era", ""))
    home_era = home_pitcher_entry.get("ERA", home_stats.get("era", ""))
    away_so9 = away_pitcher_entry.get("SO9", away_stats.get("strikeoutsPer9Inn", ""))
    home_so9 = home_pitcher_entry.get("SO9", home_stats.get("strikeoutsPer9Inn", ""))

    # New metrics
    away_hr9 = away_stats.get("homeRunsPer9", "")
    home_hr9 = home_stats.get("homeRunsPer9", "")
    away_h9 = away_stats.get("hitsPer9Inn", "")
    home_h9 = home_stats.get("hitsPer9Inn", "")
    away_wins = away_stats.get("wins", "")
    home_wins = home_stats.get("wins", "")
    away_losses = away_stats.get("losses", "")
    home_losses = home_stats.get("losses", "")

    indent = "      "
    label_field_width = len(indent)

    def pad(s, w):
        return f"{s:<{w}}"

    def unlabeled_line(left, right, gap="    "):
        return f"{indent}{pad(left, width_team)}{gap}{pad(right, width_team)}"

    def stat_line(label, left_val, right_val):
        prefix = (label + ":").ljust(label_field_width)
        return f"{prefix}{pad(str(left_val), width_team)}     {pad(str(right_val), width_team)}"

    # Core lines
    line_status = f"{indent}({status})"
    line_dt = f"{indent}{dt}     @   {venue}"
    line_names = f"{indent}{pad(away, width_team)} @   {pad(home, width_team)}"
    line_records = unlabeled_line(away_rec, home_rec, gap="     ")
    line_seq = unlabeled_line(away_seq, home_seq)

    lines = [
        line_status,
        line_dt,
        line_names,
        line_records,
        line_seq,
        stat_line("cs", cs_away, cs_home),
        stat_line("aws", aws_away, aws_home),
        stat_line("als", als_away, als_home),
        stat_line("pgh", pgh_away, pgh_home),
    ]

    # Pitcher lines (only if any pitcher present)
    if any([away_pitcher, home_pitcher]):
        lines.append(stat_line("pp", away_pitcher, home_pitcher))
        lines.append(stat_line("era", away_era, home_era))
        lines.append(stat_line("s09", away_so9, home_so9))
        lines.append(stat_line("hr9", away_hr9, home_hr9))
        lines.append(stat_line("h9", away_h9, home_h9))
        lines.append(stat_line("w", away_wins, home_wins))
        lines.append(stat_line("l", away_losses, home_losses))

    # ---------------- Roster lines ----------------
    away_roster = batter_map.get(_normalize_team_name(away), []) or batter_map.get(away, [])
    home_roster = batter_map.get(_normalize_team_name(home), []) or batter_map.get(home, [])

    if away_roster or home_roster:
        # Determine padding for name so positions align reasonably inside the width
        # Reserve at least 3 chars for a position (like "C") + spaces.
        # We'll aim for: Name padded to (width_team - 4), then 1 space + position.
        name_field = max(
            [len(p["player_name"]) for p in away_roster] +
            [len(p["player_name"]) for p in home_roster] +
            [10]  # minimum
        )
        # But cap so we don't overflow the column
        max_name_allowed = max(8, width_team - 5)  # leave room for space + pos
        name_field = min(name_field, max_name_allowed)

        def fmt_player(entry):
            if not entry:
                return ""
            return f'{entry["player_name"]:<{name_field}} {entry["position"]}'

        max_rows = max(len(away_roster), len(home_roster))
        for i in range(max_rows):
            left_entry = away_roster[i] if i < len(away_roster) else None
            right_entry = home_roster[i] if i < len(home_roster) else None
            left_txt = fmt_player(left_entry)
            right_txt = fmt_player(right_entry)
            # Pad each side to the team column width
            left_padded = f"{left_txt:<{width_team}}"
            right_padded = f"{right_txt:<{width_team}}"
            lines.append(f"{indent}{left_padded}     {right_padded}")    

    lines.append("")  # separator
    return "\n".join(lines)

def build_schedule_view(schedule_text: str,
                        teams_table_html: str,
                        pitcher_data: List[Dict[str, Any]] = None,
                        batter_data: List[Dict[str, Any]] = None,
                        max_record_seq_chars: int = 70) -> str:
    games = parse_schedule_text(schedule_text)
    stats_map = parse_teams_table(teams_table_html)
    pitcher_map = build_pitcher_map(pitcher_data or [])
    batter_map = build_batter_map(batter_data or [])
    all_team_names = [g['away'] for g in games] + [g['home'] for g in games]
    if not all_team_names:
        return ""
    width_team = max(len(name) for name in all_team_names) + 6
    width_recseq = max_record_seq_chars

    blocks = []
    for g in games:
        away = g['away']
        home = g['home']
        stats_a = stats_map.get(away, {}).get(home, {})
        stats_b = stats_map.get(home, {}).get(away, {})
        # block = format_matchup_block(g, stats_a, stats_b, width_team, width_recseq, pitcher_map)
        block = format_matchup_block(g, stats_a, stats_b, width_team, width_recseq, pitcher_map, batter_map)
        blocks.append(block)
    return "\n".join(blocks)

def format_schedule(schedule_path="data/schedule_text.txt",
                    teams_table_path="data/teams_table.html.txt",
                    pitcher_path="data/pitcher_data.json",
                    batter_path="data/batter_data.json") -> str:
    with open(schedule_path, "r", encoding="utf-8") as f:
        sched = f.read()
    with open(teams_table_path, "r", encoding="utf-8") as f:
        table_html = f.read()
    import json
    try:
        with open(pitcher_path, "r", encoding="utf-8") as f:
            p_data = json.load(f)
    except Exception:
        p_data = []
    try:
        with open(batter_path, "r", encoding="utf-8") as f:
            b_data = json.load(f)
    except Exception:
        b_data = []
    return build_schedule_view(sched, table_html, p_data, b_data)
