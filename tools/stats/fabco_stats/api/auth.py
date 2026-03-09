"""OAuth2 authentication manager for Challonge API v2.1.

Reuses OAuth configuration from tools/challonge/oauth_config.json.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import requests

# Configuration paths - relative to the challonge tools directory
CHALLONGE_DIR = Path(__file__).parent.parent.parent.parent / "challonge"
OAUTH_CONFIG_PATH = CHALLONGE_DIR / "oauth_config.json"

# API endpoints
TOKEN_URL = "https://api.challonge.com/oauth/token"


def load_json(path: Path) -> dict:
    """Load JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    """Save JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_config() -> dict:
    """Load OAuth configuration from tools/challonge/oauth_config.json."""
    return load_json(OAUTH_CONFIG_PATH)


def get_token_path(config: dict) -> Path:
    """Get full path to token file."""
    return CHALLONGE_DIR / config.get("token_file", "oauth_token.json")


def load_token(config: dict) -> Optional[dict]:
    """Load saved OAuth token."""
    token_path = get_token_path(config)
    if token_path.exists():
        return load_json(token_path)
    return None


def save_token(config: dict, token_data: dict) -> None:
    """Save OAuth token."""
    token_path = get_token_path(config)
    save_json(token_path, token_data)


def refresh_token(config: dict, token: dict) -> Optional[dict]:
    """Refresh OAuth token if expired."""
    if "refresh_token" not in token:
        return None

    token_data = {
        "grant_type": "refresh_token",
        "refresh_token": token["refresh_token"],
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.post(TOKEN_URL, data=token_data, headers=headers)
    if response.status_code != 200:
        print(f"Token refresh failed: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        return None

    new_token = response.json()
    new_token["obtained_at"] = datetime.now().isoformat()
    save_token(config, new_token)
    return new_token


def get_valid_token(config: Optional[dict] = None) -> Optional[str]:
    """Get a valid access token, refreshing if necessary.

    Args:
        config: OAuth configuration dict. If None, loads from default path.

    Returns:
        Access token string, or None if unavailable.
    """
    if config is None:
        config = load_config()

    token = load_token(config)
    if not token:
        print("No token found. Run create_tournament.py --authorize first.")
        return None

    # Check if token needs refresh (expires_in is in seconds)
    obtained_at = datetime.fromisoformat(
        token.get("obtained_at", datetime.now().isoformat())
    )
    expires_in = token.get("expires_in", 7200)
    expiry = obtained_at + timedelta(seconds=expires_in - 300)  # 5 min buffer

    if datetime.now() > expiry:
        print("Token expired, refreshing...")
        token = refresh_token(config, token)
        if not token:
            print("Token refresh failed. Run create_tournament.py --authorize.")
            return None

    return token["access_token"]
