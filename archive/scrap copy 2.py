```python
// filepath: /workspaces/zenithcobra.github.io/scrap copy 2.py
import re
import json
from typing import Dict, Any, List, Optional

# =========================
# Parsing schedule & team table
# =========================

# === Column layout tuning ===
# Increase this to push the right (home) column farther right.
COLUMN_GAP = 8   # was 5

def _stat_line(indent: str, label: str, left: str, right: str, width_team: int) -> str:
    prefix = (label + ":").ljust(len(indent))
    return f"{prefix}{left:<{width_team}}{' ' * COLUMN_GAP}{right:<{width_team}}"

def _name_line(indent: str, left: str, right: str, width_team: int) -> str:
    return f"{indent}{left:<{width_team}}{' ' * COLUMN_GAP}{right:<{width_team}}"


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
        d["away"] = re.sub(r'\s+', ' ', d["away"]).strip()
        d["home"] = re.sub(r'\s+', ' ', d["home"]).strip()
        games.append(d)
    return games

def parse_teams_table(html: str) -> Dict[str, Dict[str, Dict[str, Any]]]:
    rows = re.findall(r'<tr>(.*?)</tr>', html, flags=re.DOTALL | re.IGNORECASE)
    data: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for r in rows:
        tds = re.findall(r'<td>(.*?)</td>', r, flags=re.DOTALL | re.IGNORECASE)
        if len(tds) < 10:
            continue
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
        vs_record_against_clean = '-'.join(part.strip() for part in vs_record_against.split(','))
        data.setdefault(team_name, {})
        data[team_name][opp_name] = {
            "team_record": team_record,
            "opp_record": opp_record,
            "venue": venue,
            "vs_record_against": vs_record_against_clean,
            "current_streak": current_streak,
            "avg_win_streak": avg_win_streak,
            "avg_lose_streak": avg_lose_streak,
            "record_sequence": record_sequence
        }
    return data

# =========================
# Normalization & maps
# =========================

def _normalize_team_name(name: str) -> str:
    name = (name or "").strip()
    aliases = {
        "Athletics": "Oakland Athletics",
        "D-backs": "Arizona Diamondbacks",
    }
    return aliases.get(name, name)

def build_pitcher_map(pitcher_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    m: Dict[str, Dict[str, Any]] = {}
    for p in pitcher_data or []:
        team = p.get("pitchers_team")
        if not team:
            continue
        key = _normalize_team_name(team)
        m.setdefault(key, p)
    return m

def build_bvp_batter_map(bvp_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    m: Dict[str, List[Dict[str, Any]]] = {}
    for e in bvp_data or []:
        team = e.get("batter_team")
        if not team:
            continue
        m.setdefault(team, []).append(e)
    return m

def build_fallback_batter_map(fallback_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    m: Dict[str, List[Dict[str, Any]]] = {}
    for e in fallback_data or []:
        team = e.get("batter_team") or e.get("team")
        if not team:
            continue
        m.setdefault(team, []).append(e)
    return m

# =========================
# Batter helpers
# =========================

BATTER_SEQ_MAX_TOKENS = 14  # 14 tokens -> trimmed pattern like example

def _batter_display_name(entry: Dict[str, Any]) -> str:
    return entry.get("batter") or entry.get("player") or entry.get("name") or ""

def _extract_batter_sequences(entry: Dict[str, Any]) -> Dict[str, str]:
    return {
        "hr": entry.get("all_HR_record") or entry.get("HR_record") or "",
        "h": entry.get("all_H_record") or entry.get("H_record") or "",
        "rbi": entry.get("all_RBI_record") or entry.get("RBI_record") or ""
    }

def _trim_sequence_tokens(seq: str, max_tokens: int = BATTER_SEQ_MAX_TOKENS) -> str:
    if not seq:
        return ""
    parts = [p for p in seq.split('-') if p != ""]
    if len(parts) <= max_tokens:
        return '-'.join(parts) + ('-' if parts else '')
    return '-'.join(parts[:max_tokens]) + '-'

def _format_bvp_line(entry: Dict[str, Any]) -> str:
    if not entry:
        return ""
    bvp_stats = entry.get("bvp_stats")
    all_hr = entry.get("all_HR")
    all_hr24 = entry.get("all_HR24")
    if bvp_stats:
        parts = []
        ab = bvp_stats.get("atbats")
        h = bvp_stats.get("hits")
        rbi = bvp_stats.get("rbi")
        hr = bvp_stats.get("homeruns")
        if ab is not None: parts.append(f"{ab}ab")
        if h is not None: parts.append(f"{h}h")
        if rbi is not None: parts.append(f"{rbi}rbi")
        if hr is not None: parts.append(f"{hr}hr")
        if all_hr is not None: parts.append(f"{all_hr}hr25")
        if all_hr24 is not None: parts.append(f"{all_hr24}hr24")
        return " ".join(parts)
    parts = []
    if all_hr is not None: parts.append(f"{all_hr}hr")
    if all_hr24 is not None: parts.append(f"{all_hr24}hr24")
    return " ".join(parts)

# =========================
# Core formatting
# =========================

def _stat_line(indent: str, label: str, left: str, right: str, width_team: int, gap: int = 5) -> str:
    prefix = (label + ":").ljust(len(indent))
    return f"{prefix}{left:<{width_team}}{' ' * gap}{right:<{width_team}}"

def _name_line(indent: str, left: str, right: str, width_team: int, gap: int = 5) -> str:
    return f"{indent}{left:<{width_team}}{' ' * gap}{right:<{width_team}}"

def _format_first_batter_pair(indent: str,
                              away_entry: Optional[Dict[str, Any]],
                              home_entry: Optional[Dict[str, Any]],
                              width_team: int) -> List[str]:
    lines: List[str] = []
    away_name = _batter_display_name(away_entry) if away_entry else ""
    home_name = _batter_display_name(home_entry) if home_entry else ""
    lines.append(_name_line(indent, away_name, home_name, width_team))

    # Sequences
    away_seq = _extract_batter_sequences(away_entry) if away_entry else {"hr": "", "h": "", "rbi": ""}
    home_seq = _extract_batter_sequences(home_entry) if home_entry else {"hr": "", "h": "", "rbi": ""}

    for key in ("hr", "h", "rbi"):
        away_seq[key] = _trim_sequence_tokens(away_seq[key])
        home_seq[key] = _trim_sequence_tokens(home_seq[key])

    # hr line
    lines.append(_stat_line(indent, "hr", away_seq["hr"], home_seq["hr"], width_team))
    # bvp line
    away_bvp = _format_bvp_line(away_entry) if away_entry else ""
    home_bvp = _format_bvp_line(home_entry) if home_entry else ""
    if away_bvp or home_bvp:
        lines.append(_stat_line(indent, "bvp", away_bvp, home_bvp, width_team))
    # h line
    lines.append(_stat_line(indent, "h", away_seq["h"], home_seq["h"], width_team))
    # rbi line
    lines.append(_stat_line(indent, "rbi", away_seq["rbi"], home_seq["rbi"], width_team))

    return lines

def _format_followup_batter_pair(indent: str,
                                 away_entry: Optional[Dict[str, Any]],
                                 home_entry: Optional[Dict[str, Any]],
                                 width_team: int) -> List[str]:
    lines: List[str] = []
    away_name = _batter_display_name(away_entry) if away_entry else ""
    home_name = _batter_display_name(home_entry) if home_entry else ""
    lines.append(_name_line(indent, away_name, home_name, width_team))
    return lines

def format_matchup_block(game: Dict[str, str],
                         stats_a: Dict[str, Any],
                         stats_b: Dict[str, Any],
                         width_team: int,
                         pitcher_map: Dict[str, Dict[str, Any]],
                         bvp_batter_map: Dict[str, List[Dict[str, Any]]],
                         fallback_batter_map: Dict[str, List[Dict[str, Any]]],
                         max_batters: int = 15) -> str:
    away = game['away']
    home = game['home']
    status = game['status']
    dt = game['dt']
    stats_a = stats_a or {}
    stats_b = stats_b or {}
    venue = stats_a.get('venue') or stats_b.get('venue') or ""

    away_seq = (stats_a.get('record_sequence') or "")[:28]
    home_seq = (stats_b.get('record_sequence') or "")[:28]

    indent = "      "  # 6 spaces like your example

    lines: List[str] = []
    lines.append(f"{indent}({status})")
    lines.append(f"{indent}{dt}     @    {venue}")

    lines.append(_name_line(indent, away, home, width_team))
    lines.append(_name_line(indent,
                            stats_a.get("team_record",""),
                            stats_b.get("team_record",""),
                            width_team))
    lines.append(_name_line(indent, away_seq, home_seq, width_team))
    lines.append(_stat_line(indent, "cs",
                            stats_a.get("current_streak",""),
                            stats_b.get("current_streak",""),
                            width_team))
    lines.append(_stat_line(indent, "aws",
                            stats_a.get("avg_win_streak",""),
                            stats_b.get("avg_win_streak",""),
                            width_team))
    lines.append(_stat_line(indent, "als",
                            stats_a.get("avg_lose_streak",""),
                            stats_b.get("avg_lose_streak",""),
                            width_team))
    lines.append(_stat_line(indent, "pgh",
                            stats_a.get("vs_record_against",""),
                            stats_b.get("vs_record_against",""),
                            width_team))

    # Pitchers
    away_pitcher_entry = pitcher_map.get(_normalize_team_name(away), {})
    home_pitcher_entry = pitcher_map.get(_normalize_team_name(home), {})
    away_stats_p = away_pitcher_entry.get("stats", {}) or {}
    home_stats_p = home_pitcher_entry.get("stats", {}) or {}

    def gv(entry, alt_stats, key1, key2=None):
        if key1 in entry:
            return entry.get(key1, "")
        if key2:
            return alt_stats.get(key2, "")
        return alt_stats.get(key1, "")

    away_pitcher = away_pitcher_entry.get("pitcher","")
    home_pitcher = home_pitcher_entry.get("pitcher","")
    away_era = gv(away_pitcher_entry, away_stats_p, "ERA", "era")
    home_era = gv(home_pitcher_entry, home_stats_p, "ERA", "era")
    away_so9 = gv(away_pitcher_entry, away_stats_p, "SO9", "strikeoutsPer9Inn")
    home_so9 = gv(home_pitcher_entry, home_stats_p, "SO9", "strikeoutsPer9Inn")
    away_hr9 = away_stats_p.get("homeRunsPer9","")
    home_hr9 = home_stats_p.get("homeRunsPer9","")
    away_h9 = away_stats_p.get("hitsPer9Inn","")
    home_h9 = home_stats_p.get("hitsPer9Inn","")
    away_w = away_stats_p.get("wins","")
    home_w = home_stats_p.get("wins","")
    away_l = away_stats_p.get("losses","")
    home_l = home_stats_p.get("losses","")

    if away_pitcher or home_pitcher:
        lines.append(_stat_line(indent, "pp", away_pitcher, home_pitcher, width_team))
        lines.append(_stat_line(indent, "era", away_era, home_era, width_team))
        lines.append(_stat_line(indent, "s09", away_so9, home_so9, width_team))
        lines.append(_stat_line(indent, "hr9", away_hr9, home_hr9, width_team))
        lines.append(_stat_line(indent, "h9", away_h9, home_h9, width_team))
        lines.append(_stat_line(indent, "w", away_w, home_w, width_team))
        lines.append(_stat_line(indent, "l", away_l, home_l, width_team))

    # Batters (BvP preferred; fallback otherwise)
    away_batters = bvp_batter_map.get(away) or fallback_batter_map.get(away) or []
    home_batters = bvp_batter_map.get(home) or fallback_batter_map.get(home) or []
    if max_batters:
        away_batters = away_batters[:max_batters]
        home_batters = home_batters[:max_batters]

    max_rows = max(len(away_batters), len(home_batters))
    if max_rows:
        for idx in range(max_rows):
            a_entry = away_batters[idx] if idx < len(away_batters) else None
            h_entry = home_batters[idx] if idx < len(home_batters) else None
            if idx == 0:
                lines.extend(_format_first_batter_pair(indent, a_entry, h_entry, width_team))
            else:
                # If only home batter remains, keep blank away column
                lines.extend(_format_followup_batter_pair(indent, a_entry, h_entry, width_team))

    lines.append("")  # blank line after block
    return "\n".join(lines)

# =========================
# Schedule view builder
# =========================

def _collect_all_name_lengths(games: List[Dict[str,str]],
                              pitcher_map: Dict[str, Dict[str, Any]],
                              bvp_batter_map: Dict[str,List[Dict[str,Any]]],
                              fallback_batter_map: Dict[str,List[Dict[str,Any]]]) -> int:
    names: List[str] = []
    for g in games:
        names.append(g['away'])
        names.append(g['home'])
        # pitchers
        for tm in (g['away'], g['home']):
            p = pitcher_map.get(_normalize_team_name(tm))
            if p and p.get("pitcher"):
                names.append(p["pitcher"])
        # batters
        for tm in (g['away'], g['home']):
            lst = bvp_batter_map.get(tm) or fallback_batter_map.get(tm) or []
            for e in lst:
                nm = _batter_display_name(e)
                if nm:
                    names.append(nm)
    if not names:
        return 30
    return max(len(n) for n in names) + 2

def build_schedule_view(schedule_text: str,
                        teams_table_html: str,
                        pitcher_data: List[Dict[str, Any]] = None,
                        bvp_batter_data: List[Dict[str, Any]] = None,
                        fallback_batter_data: List[Dict[str, Any]] = None) -> str:
    games = parse_schedule_text(schedule_text)
    stats_map = parse_teams_table(teams_table_html)
    pitcher_map = build_pitcher_map(pitcher_data or [])
    bvp_batter_map = build_bvp_batter_map(bvp_batter_data or [])
    fallback_batter_map = build_fallback_batter_map(fallback_batter_data or [])

    if not games:
        return ""

    width_team = _collect_all_name_lengths(games, pitcher_map, bvp_batter_map, fallback_batter_map)

    blocks = []
    for g in games:
        away = g['away']
        home = g['home']
        stats_a = (stats_map.get(away, {}) or {}).get(home, {})
        stats_b = (stats_map.get(home, {}) or {}).get(away, {})
        block = format_matchup_block(
            g,
            stats_a,
            stats_b,
            width_team,
            pitcher_map,
            bvp_batter_map,
            fallback_batter_map
        )
        blocks.append(block)
    return "\n".join(blocks)

# =========================
# Public API
# =========================

def format_schedule(schedule_path="data/schedule_text.txt",
                    teams_table_path="data/teams_table.html.txt",
                    pitcher_path="data/pitcher_data.json",
                    bvp_batter_path="data/batter_vs_pitcher_data.json",
                    fallback_batter_path="data/batter_data.json") -> str:
    try:
        with open(schedule_path, "r", encoding="utf-8") as f:
            sched = f.read()
    except Exception:
        sched = ""
    try:
        with open(teams_table_path, "r", encoding="utf-8") as f:
            table_html = f.read()
    except Exception:
        table_html = ""
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

# =========================
# CLI test
# =========================

if __name__ == "__main__":
    print(format_schedule())