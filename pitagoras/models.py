# pitagoras/models.py
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class Manager:
    name: str
    user_id: str


@dataclass
class Account:
    account_id: str
    name: str
    provider: str
    login_customer_id: Optional[str] = None  # For Google Ads
    property_id: Optional[str] = None  # For Google Analytics
    credential_email: Optional[str] = None  # For Google Analytics


@dataclass
class Customer:
    id: str
    name: str
    accounts: List[Account]
    status: str