# server/utils.py
from datetime import datetime, timedelta
from typing import Tuple, Optional

def parse_date_range(date_range: str) -> Tuple[str, str]:
    """
    Parse various date range formats into start and end dates
    
    Accepts:
    - 'last7days', 'last30days', 'last90days'
    - 'thismonth', 'lastmonth'
    - 'specific:YYYY-MM-DD:YYYY-MM-DD' for a specific range
    
    Returns tuple of (start_date, end_date) in YYYY-MM-DD format
    """
    today = datetime.now()
    
    if date_range.startswith("last"):
        days = int(date_range[4:-4])  # Extract number from 'lastXdays'
        start_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    
    elif date_range == "thismonth":
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    
    elif date_range == "lastmonth":
        last_month = today.replace(day=1) - timedelta(days=1)
        start_date = last_month.replace(day=1).strftime("%Y-%m-%d")
        end_date = last_month.strftime("%Y-%m-%d")
    
    elif date_range.startswith("specific:"):
        parts = date_range.split(":")
        if len(parts) != 3:
            raise ValueError("Invalid date range format. Use 'specific:YYYY-MM-DD:YYYY-MM-DD'")
        start_date = parts[1]
        end_date = parts[2]
    
    else:
        raise ValueError("Invalid date range format")
    
    return start_date, end_date


def format_csv_data(headers: list, rows: list) -> str:
    """Format data as CSV text"""
    result = [",".join(headers)]
    for row in rows:
        result.append(",".join(str(cell) for cell in row))
    
    return "\n".join(result)