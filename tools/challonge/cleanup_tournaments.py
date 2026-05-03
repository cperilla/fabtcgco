#!/usr/bin/env python3
"""
Tournament Cleanup Tool for FABCO Colombia

Lists all tournaments from Challonge and deletes those with 0 participants.

Usage:
    python cleanup_tournaments.py --list              # List all tournaments with participant counts
    python cleanup_tournaments.py --list-empty        # List only tournaments with 0 participants
    python cleanup_tournaments.py --delete-empty      # Delete tournaments with 0 participants
    python cleanup_tournaments.py --dry-run           # Show what would be deleted without deleting
"""

import argparse
import json
import os
import sys
from datetime import datetime
import requests

# Configuration paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OAUTH_CONFIG_PATH = os.path.join(SCRIPT_DIR, 'oauth_config.json')

# API endpoints
TOKEN_URL = 'https://api.challonge.com/oauth/token'
API_BASE = 'https://api.challonge.com/v2.1'


def load_json(path):
    """Load JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path, data):
    """Save JSON file."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_oauth_config():
    """Load OAuth configuration."""
    return load_json(OAUTH_CONFIG_PATH)


def get_token_path(config):
    """Get full path to token file."""
    return os.path.join(SCRIPT_DIR, config.get('token_file', 'oauth_token.json'))


def load_token(config):
    """Load saved OAuth token."""
    token_path = get_token_path(config)
    if os.path.exists(token_path):
        return load_json(token_path)
    return None


def refresh_token(config, token):
    """Refresh OAuth token if expired."""
    if 'refresh_token' not in token:
        return None

    token_data = {
        'grant_type': 'refresh_token',
        'refresh_token': token['refresh_token'],
        'client_id': config['client_id'],
        'client_secret': config['client_secret']
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    response = requests.post(TOKEN_URL, data=token_data, headers=headers)
    if response.status_code != 200:
        print(f"Token refresh failed: {response.status_code}")
        return None

    new_token = response.json()
    new_token['obtained_at'] = datetime.now().isoformat()
    save_json(get_token_path(config), new_token)
    return new_token


def get_valid_token(config):
    """Get a valid access token, refreshing if necessary."""
    from datetime import timedelta

    token = load_token(config)
    if not token:
        print("No token found. Run create_tournament.py --authorize first.")
        return None

    obtained_at = datetime.fromisoformat(token.get('obtained_at', datetime.now().isoformat()))
    expires_in = token.get('expires_in', 7200)
    expiry = obtained_at + timedelta(seconds=expires_in - 300)

    if datetime.now() > expiry:
        print("Token expired, refreshing...")
        token = refresh_token(config, token)
        if not token:
            print("Token refresh failed. Run create_tournament.py --authorize.")
            return None

    return token['access_token']


def get_api_headers(access_token):
    """Get headers for API requests."""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Authorization-Type': 'v2',
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/vnd.api+json',
        'Accept': 'application/json',
    }


def list_all_tournaments(config, access_token):
    """List all tournaments in the community with pagination."""
    headers = get_api_headers(access_token)
    community_id = config.get('community_id')

    all_tournaments = []
    page = 1
    per_page = 25

    while True:
        url = f"{API_BASE}/communities/{community_id}/tournaments.json"
        params = {'page': page, 'per_page': per_page}

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Failed to list tournaments: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            break

        data = response.json()
        tournaments = data.get('data', [])

        if not tournaments:
            break

        all_tournaments.extend(tournaments)

        if len(tournaments) < per_page:
            break

        page += 1

    return all_tournaments


def get_tournament_participants(config, access_token, url_slug):
    """Get participant count for a tournament using include parameter."""
    headers = get_api_headers(access_token)
    community_id = config.get('community_id')

    url = f"{API_BASE}/communities/{community_id}/tournaments/{url_slug}.json"
    params = {'include': 'participants'}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        # Participants are in the 'included' array with type 'participant'
        included = data.get('included', [])
        participants = [item for item in included if item.get('type') == 'participant']
        return participants
    return []


def delete_tournament(config, access_token, url_slug, dry_run=False):
    """Delete a tournament."""
    if dry_run:
        print(f"  [DRY RUN] Would delete: {url_slug}")
        return True

    headers = get_api_headers(access_token)
    community_id = config.get('community_id')

    url = f"{API_BASE}/communities/{community_id}/tournaments/{url_slug}.json"

    response = requests.delete(url, headers=headers)

    if response.status_code in (200, 204):
        print(f"  Deleted: {url_slug}")
        return True
    else:
        print(f"  Failed to delete {url_slug}: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Cleanup empty tournaments from Challonge',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument('--list', action='store_true',
                        help='List all tournaments with participant counts')
    parser.add_argument('--list-empty', action='store_true',
                        help='List only tournaments with 0 participants')
    parser.add_argument('--delete-empty', action='store_true',
                        help='Delete tournaments with 0 participants')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be deleted without deleting')
    parser.add_argument('--output-json', metavar='PATH',
                        help='Output remaining tournaments to JSON file')

    args = parser.parse_args()

    if not any([args.list, args.list_empty, args.delete_empty, args.dry_run]):
        parser.print_help()
        return 0

    # Load config and get token
    try:
        config = load_oauth_config()
    except FileNotFoundError:
        print(f"OAuth config not found: {OAUTH_CONFIG_PATH}")
        return 1

    access_token = get_valid_token(config)
    if not access_token:
        return 1

    print("Fetching all tournaments...")
    tournaments = list_all_tournaments(config, access_token)
    print(f"Found {len(tournaments)} tournaments\n")

    # Get participant counts for each tournament
    tournament_data = []
    for t in tournaments:
        attrs = t.get('attributes', {})
        url_slug = attrs.get('url', '')
        name = attrs.get('name', '')
        state = attrs.get('state', '')
        starts_at = attrs.get('starts_at', '')

        participants = get_tournament_participants(config, access_token, url_slug)
        participant_count = len(participants)

        tournament_data.append({
            'url_slug': url_slug,
            'name': name,
            'state': state,
            'starts_at': starts_at,
            'participant_count': participant_count,
            'challonge_url': f"https://challonge.com/{url_slug}"
        })

    # Sort by date (starts_at)
    tournament_data.sort(key=lambda x: x.get('starts_at', '') or '')

    # Filter empty tournaments (only past ones for deletion)
    today = datetime.now().date()

    def is_past(t):
        starts_at = t.get('starts_at', '')
        if not starts_at:
            return False
        try:
            tournament_date = datetime.fromisoformat(starts_at.replace('Z', '+00:00')).date()
            return tournament_date < today
        except (ValueError, TypeError):
            return False

    empty_tournaments = [t for t in tournament_data if t['participant_count'] == 0 and is_past(t)]
    future_empty = [t for t in tournament_data if t['participant_count'] == 0 and not is_past(t)]
    non_empty_tournaments = [t for t in tournament_data if t['participant_count'] > 0]

    # List tournaments
    if args.list or args.list_empty:
        display_list = empty_tournaments if args.list_empty else tournament_data

        print(f"{'URL Slug':<45} {'Participants':<12} {'State':<12} {'Date':<12}")
        print("-" * 85)

        for t in display_list:
            date_str = t['starts_at'][:10] if t['starts_at'] else 'N/A'
            print(f"{t['url_slug']:<45} {t['participant_count']:<12} {t['state']:<12} {date_str:<12}")

        print(f"\nTotal: {len(display_list)} tournaments")
        print(f"Past empty (0 participants, will delete): {len(empty_tournaments)}")
        print(f"Future empty (0 participants, keeping): {len(future_empty)}")
        print(f"With participants: {len(non_empty_tournaments)}")

    # Delete empty tournaments
    if args.delete_empty or args.dry_run:
        print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Deleting {len(empty_tournaments)} empty tournaments...\n")

        deleted = 0
        failed = 0

        for t in empty_tournaments:
            success = delete_tournament(config, access_token, t['url_slug'], dry_run=args.dry_run)
            if success:
                deleted += 1
            else:
                failed += 1

        print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Summary: {deleted} deleted, {failed} failed")

        # Show remaining tournaments (non-empty + future empty)
        remaining = non_empty_tournaments + future_empty
        remaining.sort(key=lambda x: x.get('starts_at', '') or '')

        print(f"\n=== Remaining Tournaments ({len(remaining)}) ===\n")
        print(f"{'URL Slug':<45} {'Participants':<12} {'Date':<12}")
        print("-" * 70)

        for t in remaining:
            date_str = t['starts_at'][:10] if t['starts_at'] else 'N/A'
            print(f"{t['url_slug']:<45} {t['participant_count']:<12} {date_str:<12}")

    # Output remaining tournaments to JSON
    if args.output_json:
        remaining = non_empty_tournaments + future_empty
        remaining.sort(key=lambda x: x.get('starts_at', '') or '')
        output_data = {
            'remaining_tournaments': remaining,
            'deleted_count': len(empty_tournaments),
            'generated_at': datetime.now().isoformat()
        }
        save_json(args.output_json, output_data)
        print(f"\nRemaining tournaments saved to: {args.output_json}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
