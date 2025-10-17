"""
HTML generation functions for MLB reports.
Extracted from script.py to improve organization and simplify modification.
"""
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

import notebooks.config as config
from cache_manager import cache


class HTMLGenerator:
    """Handles HTML generation for MLB reports."""
    
    def __init__(self):
        self.date = datetime.now().strftime("%Y-%m-%d")
    
    def generate_team_list_table(self, team_list: List[Dict[str, str]]) -> str:
        """Generate HTML table for team list filtering."""
        if not team_list:
            return "<p>No team data available</p>"
        
        headers = ["filter", "Team"]
        
        html = "<table border='1'>\n<tr>"
        html += "".join(f"<th>{header}</th>" for header in headers)
        html += "</tr>\n"
        
        for team in team_list:
            html += "<tr>"
            html += "<td><input type='radio'></td>"
            html += f"<td>{team.get('team_name', '')}</td>"
            html += "</tr>\n"
        
        html += "</table>\n"
        return html
    
    def generate_team_table(self, team_data: List[Dict[str, Any]], 
                           ball_park_data: List[Dict[str, Any]], 
                           schedule_data: List[Dict[str, Any]]) -> str:
        """Generate HTML table for team data."""
        if not all([team_data, ball_park_data, schedule_data]):
            return "<h2>Team Data</h2><p>No data available</p>"
        
        # Process ballpark names
        for park in ball_park_data:
            stadium = park.get('Stadium')
            if stadium == 'Guaranteed Rate Field':
                park.update({'Stadium': 'Rate Field'})
            elif stadium == 'Minute Maid Park':
                park.update({'Stadium': 'Daikin Park'})
        
        # Merge team data with schedule and ballpark data
        processed_teams = self._merge_team_schedule_data(team_data, schedule_data, ball_park_data)
        
        headers = [
            "Win", "Loss", "Team", "vs_Team", "Series", "Venue",
            "WLmc?", "WLmmc?", "WLmmc%?", "Team Record"
        ]
        
        html = "<table border='1'>\n<tr>"
        html += "".join(f"<th>{header}</th>" for header in headers)
        html += "</tr>\n"
        
        for team in processed_teams:
            html += "<tr>"
            html += "<td><input type='checkbox'></td>"
            html += "<td><input type='checkbox'></td>"
            html += f"<td>{team.get('team_name', '')}</td>"
            html += f"<td>{team.get('vs_team', '')}</td>"
            html += f"<td>{team.get('series_info', '')}</td>"
            html += f"<td>{team.get('venue', '')}</td>"
            html += f"<td>{team.get('prediction', '')}</td>"
            html += f"<td>{team.get('wl_mmp', '')}</td>"
            
            value = team.get('wl_mmpp', '')
            html += f"<td>{round(float(value), 2) if value else ''}</td>"
            html += f"<td>{team.get('team_record', '')}</td>"
            html += "</tr>\n"
        
        html += "</table>\n"
        return html
    
    def generate_yesterday_home_run_table(self, yesterday_home_run_data: List[Dict[str, Any]]) -> str:
        """Generate HTML table for yesterday's home run data."""
        if not yesterday_home_run_data:
            return "<h2>Yesterdays Home Run Data</h2><p>No data available</p>"
        
        headers = [
            "RBI", "H", "HR", "Batter", "Team", "HR", "HRpg", "fHRpg",
            "HR24", "HR24pg", "fHR24pg", "HRmc?", "HRmmc?", "HRmmc%?",
            "HR_record only shows if they are playing today"
        ]
        
        html = "<table border='1'>\n<tr>"
        html += "".join(f"<th>{header}</th>" for header in headers)
        html += "</tr>\n"
        
        for player in yesterday_home_run_data:
            html += "<tr>"
            html += "<td><input type='checkbox'></td>"
            html += "<td><input type='checkbox'></td>"
            html += "<td><input type='checkbox'></td>"
            html += f"<td>{player.get('name', '')}</td>"
            html += f"<td>{player.get('team', '')}</td>"
            html += f"<td>{player.get('HR', '')}</td>"
            html += f"<td>{player.get('HRpg', '')}</td>"
            html += f"<td>{player.get('fHRpg', '')}</td>"
            html += f"<td>{player.get('HR24', '')}</td>"
            html += f"<td>{player.get('HR24pg', '')}</td>"
            html += f"<td>{player.get('fHR24pg', '')}</td>"
            html += f"<td>{player.get('prediction', '')}</td>"
            html += f"<td>{player.get('hr_mmp', '')}</td>"
            
            value = player.get('hr_mmpp', '')
            html += f"<td>{round(float(value), 2) if value else ''}</td>"
            html += f"<td>{player.get('HR_record', '')}</td>"
            html += "</tr>\n"
        
        html += "</table>\n"
        return html
    
    def generate_leaders_table(self, era_leaders: List[Dict[str, Any]], 
                              so9_leaders: List[Dict[str, Any]], 
                              hr_leaders: List[Dict[str, Any]]) -> str:
        """Generate HTML tables for league leaders."""
        def make_table(data: List[Dict[str, Any]], title: str) -> str:
            if not data or not isinstance(data, list) or not data[0]:
                return f"<h3>{title}</h3><p>No data available</p>"
            
            headers = data[0].keys()
            html = f"<h3>{title}</h3><table border='1'><tr>"
            html += "".join(f"<th>{h}</th>" for h in headers)
            html += "</tr>\n"
            
            for row in data:
                html += "<tr>"
                html += "".join(f"<td>{row.get(h, '')}</td>" for h in headers)
                html += "</tr>\n"
            
            html += "</table>\n"
            return html
        
        html = ""
        html += make_table(era_leaders, "ERA")
        html += make_table(so9_leaders, "SO9")
        html += make_table(hr_leaders, "HR")
        return html
    
    def generate_pitcher_table(self, pitcher_data: List[Dict[str, Any]]) -> str:
        """Generate HTML table for pitcher data."""
        if not pitcher_data:
            return "<h2>Pitcher Data</h2><p>No data available</p>"
        
        # This would contain the original pitcher table generation logic
        # For now, create a basic table
        html = "<table border='1'>\n"
        html += "<tr><th>Pitcher</th><th>Team</th><th>Stats</th></tr>\n"
        
        for pitcher in pitcher_data:
            html += "<tr>"
            html += f"<td>{pitcher.get('pitcher', '')}</td>"
            html += f"<td>{pitcher.get('team', '')}</td>"
            html += f"<td>{pitcher.get('stats', '')}</td>"
            html += "</tr>\n"
        
        html += "</table>\n"
        return html
    
    def generate_batter_table(self, batter_data: List[Dict[str, Any]], 
                             schedule_data: List[Dict[str, Any]], 
                             ballpark_data: List[Dict[str, Any]]) -> str:
        """Generate HTML table for batter data."""
        if not batter_data:
            return "<h2>Batter Data</h2><p>No data available</p>"
        
        # This would contain the original batter table generation logic
        html = "<table border='1'>\n"
        html += "<tr><th>Batter</th><th>Team</th><th>Stats</th></tr>\n"
        
        for batter in batter_data:
            html += "<tr>"
            html += f"<td>{batter.get('batter', '')}</td>"
            html += f"<td>{batter.get('team', '')}</td>"
            html += f"<td>{batter.get('stats', '')}</td>"
            html += "</tr>\n"
        
        html += "</table>\n"
        return html
    
    def generate_bvp_table(self, bvp_data: List[Dict[str, Any]], 
                          schedule_data: List[Dict[str, Any]], 
                          ballpark_data: List[Dict[str, Any]]) -> str:
        """Generate HTML table for batter vs pitcher data."""
        if not bvp_data:
            return "<h2>BvP Data</h2><p>No data available</p>"
        
        html = "<table border='1'>\n"
        html += "<tr><th>Batter</th><th>Pitcher</th><th>Stats</th></tr>\n"
        
        for matchup in bvp_data:
            html += "<tr>"
            html += f"<td>{matchup.get('batter', '')}</td>"
            html += f"<td>{matchup.get('pitcher', '')}</td>"
            html += f"<td>{matchup.get('stats', '')}</td>"
            html += "</tr>\n"
        
        html += "</table>\n"
        return html
    
    def generate_dh_batter_table(self, dh_batter_data: List[Dict[str, Any]], 
                                schedule_data: List[Dict[str, Any]], 
                                ballpark_data: List[Dict[str, Any]]) -> str:
        """Generate HTML table for designated hitter data."""
        if not dh_batter_data:
            return "<h2>DH Batter Data</h2><p>No data available</p>"
        
        html = "<table border='1'>\n"
        html += "<tr><th>DH Batter</th><th>Team</th><th>Stats</th></tr>\n"
        
        for dh in dh_batter_data:
            html += "<tr>"
            html += f"<td>{dh.get('batter', '')}</td>"
            html += f"<td>{dh.get('team', '')}</td>"
            html += f"<td>{dh.get('stats', '')}</td>"
            html += "</tr>\n"
        
        html += "</table>\n"
        return html
    
    def _merge_team_schedule_data(self, team_data: List[Dict[str, Any]], 
                                 schedule_data: List[Dict[str, Any]], 
                                 ball_park_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge team data with schedule and ballpark information."""
        processed_teams = []
        
        for team in team_data:
            team_id = team.get('team_id')
            team_name = team.get('team_name')
            team_record = team.get('team_record')
            
            team_dict = {
                "team_id": team_id,
                "team_name": team_name,
                "team_record": team_record
            }
            
            # Find schedule info for this team
            for game in schedule_data:
                away_id = game.get('away_id')
                home_id = game.get('home_id')
                
                if team_id == away_id:
                    vs_team = game.get('home_name')
                    team_dict.update({
                        "vs_team": f"{vs_team} (<b>home</b>)",
                        "series_info": game.get("series_status")
                    })
                    
                    # Add venue info
                    venue = game.get('venue_name')
                    for park in ball_park_data:
                        if venue == park.get('Stadium'):
                            venue_hr = park.get('HR', '')
                            team_dict.update({
                                "venue": f"{venue} <b>({venue_hr})</b>"
                            })
                            break
                    
                elif team_id == home_id:
                    vs_team = game.get('away_name')
                    team_dict.update({
                        "vs_team": f"{vs_team} (<b>away</b>)",
                        "series_info": game.get("series_status")
                    })
                    
                    # Add venue info
                    venue = game.get('venue_name')
                    for park in ball_park_data:
                        if venue == park.get('Stadium'):
                            venue_hr = park.get('HR', '')
                            team_dict.update({
                                "venue": f"{venue} <b>({venue_hr})</b>"
                            })
                            break
            
            processed_teams.append(team_dict)
        
        return processed_teams
    
    def create_base_html_structure(self) -> str:
        """Create the base HTML structure with styling and navigation."""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MLB Report</title>
            {self._get_css_styles()}
        </head>
        <body>
            {self._get_navigation_bar()}
            <div class="content">
                <h1 id="useful-links">Useful Links</h1>
                {self._get_useful_links()}
                <h2>MLB Report {self.date}</h2>
                {{content}}
            </div>
            {self._get_javascript()}
        </body>
        </html>
        """
    
    def _get_css_styles(self) -> str:
        """Get CSS styles for the HTML page."""
        return """
        <style>
            body {
                margin: 0;
                font-family: 'Fira Code', monospace;
                color: #BBBBBB;
                background-color: black;
            }
            h1, h2, h3, h4, h5, h6 {
                color: #14B37D;
            }
            .navbar {
                position: sticky;
                top: 0;
                background-color: #333;
                overflow: hidden;
                z-index: 1000;
                white-space: nowrap;
            }
            .navbar a {
                float: left;
                display: block;
                color: white;
                text-align: center;
                padding: 8px 10px;
                font-size: 12px;
                text-decoration: none;
            }
            .navbar a:hover {
                background-color: #ddd;
                color: black;
            }
            .content {
                padding: 20px;
            }
            .highlight {
                background-color: #363B44;
            }
            th {
                background-color: #363B44;
                color: #2A8EEA;
            }
            a {
                color: #3A75C4;
                text-decoration: none;
            }
            .number-highlight {
                color: #F2F27A;
                font-weight: bold;
            }
            .non-number-highlight {
                color: #50fa7b;
            }
        </style>
        """
    
    def _get_navigation_bar(self) -> str:
        """Get the navigation bar HTML."""
        nav_items = [
            ("useful-links", "Links"),
            ("parlay-banned-list", "Banned"),
            ("yesterdays-report", "History"),
            ("standings", "Standings"),
            ("todays-schedule", "Schedule"),
            ("teams", "Select Teams"),
            ("records", "Teams"),
            ("leaders", "Leaders"),
            ("match-overviews-pitchers", "Pitchers"),
            ("HR", "HR's"),
            ("H", "H's"),
            ("RBI", "RBI's"),
            ("dh-batters", "DH's"),
            ("bvp-stats-HR", "BvP HR"),
            ("bvp-stats-H", "BvP H"),
            ("bvp-stats-RBI", "BvP RBI"),
            ("checked-section", "Checked")
        ]
        
        navbar = '<div class="navbar">'
        for anchor, text in nav_items:
            navbar += f'<a href="#{anchor}">{text}</a>'
        navbar += '</div>'
        
        return navbar
    
    def _get_useful_links(self) -> str:
        """Get useful links section."""
        links = [
            ("https://www.fantasyalarm.com/mlb/lineups", "BVP checker"),
            ("https://www.baseball-reference.com", "baseball-reference"),
            ("https://baseballsavant.mlb.com", "baseball-savant"),
            ("https://www.fangraphs.com", "fangraphs"),
            ("https://www.statmuse.com/mlb", "Stat muse"),
            ("https://www.baseballmusings.com/cgi-bin/CurStreak.py", "Baseball Musings"),
            ("https://www.teamrankings.com", "Team Rankings"),
            ("https://www.onlyhomers.com/ballparks", "Only Homers")
        ]
        
        html = "<ul>"
        for url, text in links:
            html += f'<li><a href="{url}">{text}</a></li>'
        html += "</ul>"
        
        return html
    
    def _get_javascript(self) -> str:
        """Get JavaScript for interactive features."""
        return """
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                // Row highlighting functionality
                let currentlyHighlightedRow = null;
                
                document.querySelectorAll('table tr').forEach(row => {
                    row.addEventListener('click', function() {
                        if (currentlyHighlightedRow) {
                            currentlyHighlightedRow.classList.remove('highlight');
                        }
                        this.classList.add('highlight');
                        currentlyHighlightedRow = this;
                    });
                });
                
                // Number highlighting
                const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
                let node;
                while ((node = walker.nextNode())) {
                    const parent = node.parentNode;
                    if (parent.tagName === 'SCRIPT' || parent.tagName === 'STYLE') continue;
                    
                    const replacedHTML = node.nodeValue.replace(/(\\d+)/g, '<span class="number-highlight">$1</span>');
                    if (replacedHTML !== node.nodeValue) {
                        const tempDiv = document.createElement('div');
                        tempDiv.innerHTML = replacedHTML;
                        
                        while (tempDiv.firstChild) {
                            parent.insertBefore(tempDiv.firstChild, node);
                        }
                        parent.removeChild(node);
                    }
                }
            });
        </script>
        """


def process_html_advanced_features(html_string: str) -> str:
    """Add advanced features like sorting, filtering, and checked section to HTML."""
    soup = BeautifulSoup(html_string, "html.parser")
    
    # Add checked section
    checked_section = soup.new_tag("div", id="checked-section")
    checked_heading = soup.new_tag("h2")
    checked_heading.string = "Checked"
    checked_section.append(checked_heading)
    
    pre_tag = soup.new_tag("pre")
    checked_table = soup.new_tag("table", id="checked-table", border="1")
    pre_tag.append(checked_table)
    checked_section.append(pre_tag)
    
    soup.body.append(checked_section)
    
    # Add JavaScript for checkbox functionality
    checkbox_script = soup.new_tag("script")
    checkbox_script.string = """
    document.addEventListener('DOMContentLoaded', function() {
        function handleCheckboxClick(checkbox) {
            const row = checkbox.closest('tr');
            const checkedTable = document.getElementById('checked-table');

            if (checkbox.checked) {
                const clonedRow = row.cloneNode(true);
                clonedRow.querySelectorAll('input[type="checkbox"]').forEach(cb => {
                    cb.disabled = true;
                });
                checkedTable.appendChild(clonedRow);
            } else {
                const rows = Array.from(checkedTable.querySelectorAll('tr'));
                rows.forEach(checkedRow => {
                    const originalRowContent = Array.from(row.cells).map(cell => cell.innerText).join('');
                    const checkedRowContent = Array.from(checkedRow.cells).map(cell => cell.innerText).join('');
                    if (originalRowContent === checkedRowContent) {
                        checkedRow.remove();
                    }
                });
            }
        }

        document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('click', function() {
                handleCheckboxClick(this);
            });
        });
    });
    """
    soup.body.append(checkbox_script)
    
    # Add table sorting functionality
    sort_script = soup.new_tag("script")
    sort_script.string = """
    document.addEventListener('DOMContentLoaded', function() {
        const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;
        const comparer = (idx, asc) => (a, b) => ((v1, v2) =>
            v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)
        )(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

        document.querySelectorAll('th').forEach(th => th.addEventListener('click', (() => {
            const table = th.closest('table');
            Array.from(table.querySelectorAll('tr:nth-child(n+2)'))
                .sort(comparer(Array.from(th.parentNode.children).indexOf(th), this.asc = !this.asc))
                .forEach(tr => table.appendChild(tr));
        })));
    });
    """
    soup.body.append(sort_script)
    
    return str(soup)