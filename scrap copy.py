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


def build_bvp_batter_map(bvp_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Map batter team -> list of batter_vs_pitcher entries.
    We store as-is; ordering can later be customized (e.g., by all_HR desc).
    """
    m: Dict[str, List[Dict[str, Any]]] = {}
    for e in bvp_data or []:
        team = e.get("batter_team")
        if not team:
            continue
        m.setdefault(team, []).append(e)
    return m

def build_fallback_batter_map(fallback_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Fallback map if no bvp data available for a team.
    Expect each record to contain at least a 'team' or 'batter_team' plus
    optional stat sequences. (Adjust to your real schema.)
    """
    m: Dict[str, List[Dict[str, Any]]] = {}
    for e in fallback_data or []:
        team = e.get("batter_team") or e.get("team")
        if not team:
            continue
        m.setdefault(team, []).append(e)
    return m

def _seq_short(seq: str, max_len: int = 70) -> str:
    if not seq:
        return ""
    if len(seq) <= max_len:
        return seq
    return seq[:max_len]

def _format_bvp_line(entry: Dict[str, Any]) -> str:
    """
    Build the compact 'bvp:' summary.
    Expected keys inside entry:
      bvp_stats: { atbats, hits, rbi, homeruns }  (if missing defaults blank)
      all_HR, all_HR24
    Output example: '3ab 2h 1rbi 0hr 24hr25 9hr24'
    """
    bvp_stats = entry.get("bvp_stats") or {}
    ab = bvp_stats.get("atbats")
    h = bvp_stats.get("hits")
    rbi = bvp_stats.get("rbi")
    hr = bvp_stats.get("homeruns")
    hr25 = entry.get("all_HR")
    hr24 = entry.get("all_HR24")
    parts = []
    if ab is not None: parts.append(f"{ab}ab")
    if h is not None: parts.append(f"{h}h")
    if rbi is not None: parts.append(f"{rbi}rbi")
    if hr is not None: parts.append(f"{hr}hr")
    if hr25 is not None: parts.append(f"{hr25}hr25")
    if hr24 is not None: parts.append(f"{hr24}hr24")
    return " ".join(parts)

def _extract_batter_sequences(entry: Dict[str, Any]) -> Dict[str, str]:
    """
    Return standardized keys: hr, h, rbi.
    For bvp entries: use all_HR_record / all_H_record / all_RBI_record
    For fallback entries: HR_record / H_record / RBI_record
    """
    return {
        "hr": entry.get("all_HR_record") or entry.get("HR_record") or "",
        "h": entry.get("all_H_record") or entry.get("H_record") or "",
        "rbi": entry.get("all_RBI_record") or entry.get("RBI_record") or ""
    }

def _batter_display_name(entry: Dict[str, Any]) -> str:
    return entry.get("batter") or entry.get("player") or entry.get("name") or ""

def _format_batter_pair_lines(away_entry: Dict[str, Any] | None,
                              home_entry: Dict[str, Any] | None,
                              width_team: int,
                              indent: str) -> List[str]:
    """
    Produce lines for one pair of batters (away/home) including:
      name line
      hr:
      bvp: (only if either side has bvp_stats)
      h:
      rbi:
    """
    lines = []
    pad = lambda s: f"{s:<{width_team}}"
    if not (away_entry or home_entry):
        return lines

    away_name = _batter_display_name(away_entry) if away_entry else ""
    home_name = _batter_display_name(home_entry) if home_entry else ""
    lines.append(f"{indent}{pad(away_name)}{pad(home_name)}")

    # sequences
    if away_entry:
        away_seq = _extract_batter_sequences(away_entry)
    else:
        away_seq = {"hr": "", "h": "", "rbi": ""}

    if home_entry:
        home_seq = _extract_batter_sequences(home_entry)
    else:
        home_seq = {"hr": "", "h": "", "rbi": ""}

    label_w = len(indent)  # reuse indent width for alignment like other stat_line
    def stat_row(label: str, left: str, right: str):
        prefix = (label + ":").ljust(label_w)
        return f"{prefix}{pad(_seq_short(left))}{pad(_seq_short(right))}"

    lines.append(stat_row("hr", away_seq["hr"], home_seq["hr"]))

    # bvp line only if at least one side has real bvp stats (we detect via bvp_stats key)
    away_bvp_line = _format_bvp_line(away_entry) if (away_entry and away_entry.get("bvp_stats")) else ""
    home_bvp_line = _format_bvp_line(home_entry) if (home_entry and home_entry.get("bvp_stats")) else ""
    if away_bvp_line or home_bvp_line:
        lines.append(stat_row("bvp", away_bvp_line, home_bvp_line))

    lines.append(stat_row("h", away_seq["h"], home_seq["h"]))
    lines.append(stat_row("rbi", away_seq["rbi"], home_seq["rbi"]))
    return lines

# Modify existing format_matchup_block signature to accept batter maps
def format_matchup_block(game: Dict[str, str],
                         stats_a: Dict[str, Any],
                         stats_b: Dict[str, Any],
                         width_team: int,
                         width_recseq: int,
                         pitcher_map: Dict[str, Dict[str, Any]],
                         bvp_batter_map: Dict[str, List[Dict[str, Any]]] = None,
                         fallback_batter_map: Dict[str, List[Dict[str, Any]]] = None,
                         max_batters: int = 12) -> str:
    """
    Extended: adds pitcher lines (pp / era / s09 / hr9 / h9 / w / l) + batter pairs with sequences.
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

    cs_away = stats_a.get('current_streak', '')
    cs_home = stats_b.get('current_streak', '')
    aws_away = stats_a.get('avg_win_streak', '')
    aws_home = stats_b.get('avg_win_streak', '')
    als_away = stats_a.get('avg_lose_streak', '')
    als_home = stats_b.get('avg_lose_streak', '')
    pgh_away = stats_a.get('vs_record_against', '')
    pgh_home = stats_b.get('vs_record_against', '')

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

    if any([away_pitcher, home_pitcher]):
        lines.append(stat_line("pp", away_pitcher, home_pitcher))
        lines.append(stat_line("era", away_era, home_era))
        lines.append(stat_line("s09", away_so9, home_so9))
        lines.append(stat_line("hr9", away_hr9, home_hr9))
        lines.append(stat_line("h9", away_h9, home_h9))
        lines.append(stat_line("w", away_wins, home_wins))
        lines.append(stat_line("l", away_losses, home_losses))

    # Batter integration
    bvp_batter_map = bvp_batter_map or {}
    fallback_batter_map = fallback_batter_map or {}
    away_batters = bvp_batter_map.get(away) or fallback_batter_map.get(away) or []
    home_batters = bvp_batter_map.get(home) or fallback_batter_map.get(home) or []

    # Optionally sort (example: keep existing order; you can customize)
    # Truncate
    if max_batters:
        away_batters = away_batters[:max_batters]
        home_batters = home_batters[:max_batters]

    # Pair up (zip longest)
    max_rows = max(len(away_batters), len(home_batters))
    for i in range(max_rows):
        a_entry = away_batters[i] if i < len(away_batters) else None
        h_entry = home_batters[i] if i < len(home_batters) else None
        pair_lines = _format_batter_pair_lines(a_entry, h_entry, width_team, indent)
        lines.extend(pair_lines)

    lines.append("")
    return "\n".join(lines)

def build_schedule_view(schedule_text: str,
                        teams_table_html: str,
                        pitcher_data: List[Dict[str, Any]] = None,
                        bvp_batter_data: List[Dict[str, Any]] = None,
                        fallback_batter_data: List[Dict[str, Any]] = None,
                        max_record_seq_chars: int = 70) -> str:
    games = parse_schedule_text(schedule_text)
    stats_map = parse_teams_table(teams_table_html)
    pitcher_map = build_pitcher_map(pitcher_data or [])
    bvp_batter_map = build_bvp_batter_map(bvp_batter_data or [])
    fallback_batter_map = build_fallback_batter_map(fallback_batter_data or [])

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
        block = format_matchup_block(
            g, stats_a, stats_b, width_team, width_recseq,
            pitcher_map,
            bvp_batter_map=bvp_batter_map,
            fallback_batter_map=fallback_batter_map
        )
        blocks.append(block)
    return "\n".join(blocks)

def format_schedule(schedule_path="data/schedule_text.txt",
                    teams_table_path="data/teams_table.html.txt",
                    pitcher_path="data/pitcher_data.json",
                    bvp_batter_path="data/batter_vs_pitcher_data.json",
                    fallback_batter_path="data/batter_data.json") -> str:
    with open(schedule_path, "r", encoding="utf-8") as f:
        sched = f.read()
    with open(teams_table_path, "r", encoding="utf-8") as f:
        table_html = f.read()
    try:
        with open(pitcher_path, "r", encoding="utf-8") as f:
            p_data = json.load(f)
    except Exception:
        p_data = []
    try:
        with open(bvp_batter_path, "r", encoding="utf-8") as f:
            bvp_data = json.load(f)
    except Exception:
        bvp_data = []
    try:
        with open(fallback_batter_path, "r", encoding="utf-8") as f:
            fb_data = json.load(f)
    except Exception:
        fb_data = []
    return build_schedule_view(sched, table_html, p_data, bvp_data, fb_data)



