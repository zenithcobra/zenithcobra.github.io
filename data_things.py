from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from fractions import Fraction
import csv
import json
import mlbstatsapi
import os
import pytz
import re
import requests
import statsapi
import requests
from bs4 import BeautifulSoup
import json
import numpy as np
import matplotlib.pyplot as plt


def detect_current_streak(sequence):
    """
    Detects the current streak (value and length) in the sequence.

    Args:
        sequence (list): A list of 1s and 0s representing wins and losses.

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


def predict_streak_continuation(current_streak, stats):
    """
    Predicts whether the current streak will continue or transition.

    Args:
        current_streak (tuple): A tuple containing the current streak value (1 or 0) and its length.
        stats (dict): A dictionary containing streak statistics.

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

def parse_html_table(html_content):
    """
    Parses an HTML table into a list of dictionaries, excluding checkbox columns.

    Args:
        html_content (str): The HTML content as a string.

    Returns:
        list: A list of dictionaries where each dictionary represents a row of the table.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')  # Find the first table in the HTML

    if not table:
        # raise ValueError("No table found in the provided HTML content.")
        return {}
    # Identify columns with checkboxes by inspecting the first data row
    first_data_row = table.find_all('tr')[1]  # Skip the header row
    checkbox_columns = []
    for i, td in enumerate(first_data_row.find_all('td')):
        if td.find('input', {'type': 'checkbox'}):
            checkbox_columns.append(i)

    # Extract headers, excluding checkbox columns
    headers = []
    for i, th in enumerate(table.find('tr').find_all('th')):
        if i not in checkbox_columns:
            headers.append(th.text.strip())

    # Extract rows, excluding checkbox columns
    rows = []
    for tr in table.find_all('tr')[1:]:  # Skip the header row
        row_data = []
        for i, td in enumerate(tr.find_all('td')):
            if i not in checkbox_columns:
                row_data.append(td.get_text(strip=True))
        if len(row_data) == len(headers):  # Ensure row matches header length
            rows.append(dict(zip(headers, row_data)))

    return rows

