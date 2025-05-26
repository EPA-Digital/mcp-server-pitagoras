# server/utils.py
from datetime import datetime, timedelta
from typing import Tuple, Optional, List, Dict

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


def parse_account_selection(selection: str, accounts: List[Dict]) -> List[Dict]:
    """Interpret a user selection string and return the matching accounts.

    Parameters
    ----------
    selection: str
        User provided string such as ``"1,3,id:123"``.
    accounts: list[dict]
        Available account objects. Each must contain an ``id`` or ``account_id`` field.

    Returns
    -------
    list[dict]
        Accounts corresponding to the selection. Supports numbers (1 based),
        ``id:<ID>``, raw IDs and the literal ``all``.
    """
    if not selection:
        return []

    tokens = [s.strip() for s in selection.split(',') if s.strip()]

    id_map = {}
    for account in accounts:
        acc_id = str(account.get('id') or account.get('account_id'))
        if acc_id:
            id_map[acc_id] = account

    selected: List[Dict] = []
    seen_ids = set()

    for token in tokens:
        low = token.lower()
        if low == 'all':
            return accounts

        if low.startswith('id:'):
            token_id = token.split(':', 1)[1]
            acc = id_map.get(token_id)
            if acc and token_id not in seen_ids:
                selected.append(acc)
                seen_ids.add(token_id)
            continue

        if token.isdigit():
            idx = int(token) - 1
            if 0 <= idx < len(accounts):
                acc = accounts[idx]
                acc_id = str(acc.get('id') or acc.get('account_id'))
                if acc_id not in seen_ids:
                    selected.append(acc)
                    seen_ids.add(acc_id)
            continue

        acc = id_map.get(token)
        if not acc:
            for a in accounts:
                if a.get('name', '').lower() == low:
                    acc = a
                    break
        if acc:
            acc_id = str(acc.get('id') or acc.get('account_id'))
            if acc_id not in seen_ids:
                selected.append(acc)
                seen_ids.add(acc_id)

    return selected
