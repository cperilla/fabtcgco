#!/usr/bin/env python3
"""
Challonge Tournament Creator for FABCO Colombia
Uses API v2.1 with OAuth2 authentication

Usage:
    python create_tournament.py --authorize          # OAuth setup (prompts for code)
    python create_tournament.py --code <code>        # Exchange auth code for token
    python create_tournament.py --list               # List upcoming events from calendar
    python create_tournament.py --create <date>      # Create tournament for specific date
    python create_tournament.py --create-range <start> <end>  # Create tournaments for date range
    python create_tournament.py --dry-run <date>     # Show what would be created without creating
    python create_tournament.py --update <url> [url...]       # Update existing tournament(s)
    python create_tournament.py --update-dry-run <url> [url...] # Show what would be updated

Options:
    --location <loc>    Filter by location (e.g., "Palmira", "Chaos Store")

Settings applied to new/updated tournaments:
    - quick_advance: true (allows quick match advancement)
    - open_signup: true (makes signup page publicly visible)
    - signup_cap: 32 (maximum participants)
"""

import argparse
import json
import os
import random
import sys
from datetime import datetime, timedelta
from urllib.parse import urlencode
import requests

# Configuration paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OAUTH_CONFIG_PATH = os.path.join(SCRIPT_DIR, 'oauth_config.json')
TEMPLATES_PATH = os.path.join(SCRIPT_DIR, 'templates.json')
CARDS_PATH = os.path.join(SCRIPT_DIR, 'cards.json')
CALENDAR_PATH = os.path.join(SCRIPT_DIR, '..', '..', 'src', 'data', 'Eventos_Comunidad_Q1_2026.json')

# API endpoints
AUTH_URL = 'https://api.challonge.com/oauth/authorize'
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


def load_templates():
    """Load tournament templates."""
    return load_json(TEMPLATES_PATH)


def load_cards():
    """Load card names for tournament naming."""
    return load_json(CARDS_PATH)


def get_random_card_name(cards_data):
    """Get a random card name from the cards list."""
    cards = cards_data.get('cards', [])
    if not cards:
        return "Unknown Card"
    return random.choice(cards)


def load_calendar():
    """Load calendar events."""
    return load_json(CALENDAR_PATH)


def get_token_path(config):
    """Get full path to token file."""
    return os.path.join(SCRIPT_DIR, config.get('token_file', 'oauth_token.json'))


def load_token(config):
    """Load saved OAuth token."""
    token_path = get_token_path(config)
    if os.path.exists(token_path):
        return load_json(token_path)
    return None


def save_token(config, token_data):
    """Save OAuth token."""
    token_path = get_token_path(config)
    save_json(token_path, token_data)


def authorize(config, code=None):
    """Perform OAuth2 authorization flow."""
    # Build authorization URL
    params = {
        'response_type': 'code',
        'client_id': config['client_id'],
        'redirect_uri': config['redirect_uri'],
        'scope': config['scope']
    }
    auth_url = f"{AUTH_URL}?{urlencode(params)}"

    # If code provided directly, skip to token exchange
    if code:
        print(f"Using provided authorization code...")
        auth_code = code
    else:
        # CLI mode: user copies code from redirect URL
        print(f"\nAuthorization URL:\n{auth_url}\n")
        print("1. Open the URL above in your browser")
        print("2. Authorize the application")
        print("3. You'll be redirected to a URL like:")
        print(f"   {config['redirect_uri']}?code=AUTHORIZATION_CODE")
        print("4. Copy the 'code' parameter value and paste it below\n")

        auth_code = input("Enter authorization code: ").strip()
        if not auth_code:
            print("No code entered")
            return False

    # Exchange code for token
    print("Exchanging authorization code for access token...")
    token_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'client_id': config['client_id'],
        'client_secret': config['client_secret'],
        'redirect_uri': config['redirect_uri']
    }

    # Use browser-like headers to avoid Cloudflare bot detection
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    response = requests.post(TOKEN_URL, data=token_data, headers=headers)
    if response.status_code != 200:
        print(f"Token exchange failed: {response.status_code}")
        print(f"\n--- Request Details ---")
        print(f"URL: {TOKEN_URL}")
        print(f"Method: POST")
        print(f"Headers: {dict(response.request.headers)}")
        # Mask secrets in token_data for display
        display_data = {k: (v[:8] + '...' if k in ('client_secret', 'code') and v else v) for k, v in token_data.items()}
        print(f"Data: {display_data}")
        print(f"\n--- Response Details ---")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Body: {response.text[:500] if len(response.text) > 500 else response.text}")
        return False

    token = response.json()
    token['obtained_at'] = datetime.now().isoformat()
    save_token(config, token)

    print("Authorization successful! Token saved.")
    return True


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

    # Use browser-like headers to avoid Cloudflare bot detection
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    response = requests.post(TOKEN_URL, data=token_data, headers=headers)
    if response.status_code != 200:
        print(f"\n--- Refresh Token Request Failed ---")
        print(f"URL: {TOKEN_URL}")
        print(f"Method: POST")
        print(f"Headers: {dict(response.request.headers)}")
        # Mask secrets for display
        display_data = {k: (v[:8] + '...' if k in ('client_secret', 'refresh_token') and v else v) for k, v in token_data.items()}
        print(f"Data: {display_data}")
        print(f"\n--- Response ---")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Body: {response.text[:500] if len(response.text) > 500 else response.text}")
        return None

    new_token = response.json()
    new_token['obtained_at'] = datetime.now().isoformat()
    save_token(config, new_token)
    return new_token


def get_valid_token(config):
    """Get a valid access token, refreshing if necessary."""
    token = load_token(config)
    if not token:
        print("No token found. Run with --authorize first.")
        return None

    # Check if token needs refresh (expires_in is in seconds)
    obtained_at = datetime.fromisoformat(token.get('obtained_at', datetime.now().isoformat()))
    expires_in = token.get('expires_in', 7200)
    expiry = obtained_at + timedelta(seconds=expires_in - 300)  # 5 min buffer

    if datetime.now() > expiry:
        print("Token expired, refreshing...")
        token = refresh_token(config, token)
        if not token:
            print("Token refresh failed. Run with --authorize.")
            return None

    return token['access_token']


def get_api_headers(access_token):
    """Get headers for API requests."""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Authorization-Type': 'v2',
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/vnd.api+json',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
    }


def create_tournament_payload(event, templates, cards_data=None):
    """Create tournament payload from calendar event and templates."""
    event_type = event.get('EventType', 'CC')
    default_template = templates.get('default', {})
    event_template = templates.get('event_types', {}).get(event_type, {})

    # Merge templates (event-specific overrides default)
    merged = {**default_template}
    for key, value in event_template.items():
        if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
            merged[key] = {**merged[key], **value}
        else:
            merged[key] = value

    # Build tournament name with short format (max 60 chars):
    # FAB {Location} {FormatCode} {WeekdayAbbr} {Date} : {CardName}
    date = datetime.strptime(event['Date'], '%Y-%m-%d')
    date_str = date.strftime('%d/%m/%y')  # Short year format

    # Get short location name from event's Location field
    event_location = event.get('Location', 'Chaos Store')
    location_config = templates.get('locations', {}).get(event_location, {})
    location = location_config.get('short_name', event_location)

    # Use event type code (CC, Sage, LL, etc.) for shorter name
    format_code = event_type

    # Abbreviate weekday
    weekday_abbr = {
        'Lunes': 'Lun', 'Martes': 'Mar', 'Miércoles': 'Mié',
        'Jueves': 'Jue', 'Viernes': 'Vie', 'Sábado': 'Sáb', 'Domingo': 'Dom'
    }.get(event.get('Day', ''), event.get('Day', '')[:3])

    # Get random card name
    card_name = get_random_card_name(cards_data) if cards_data else "Unknown Card"

    tournament_name = f"FAB {location} {format_code} {weekday_abbr} {date_str} : {card_name}"

    # Build URL slug (lowercase, underscores only - no hyphens allowed by Challonge)
    # Include location to avoid conflicts for same-date events at different locations
    location_slug = location.lower().replace(' ', '_')
    url_slug = f"fabco_{location_slug}_{event_type.lower()}_{date.strftime('%Y%m%d')}"

    # Parse start time
    time_str = event.get('Time', '5 PM')
    try:
        time_parts = time_str.replace(' ', '').upper()
        if 'PM' in time_parts:
            hour = int(time_parts.replace('PM', ''))
            if hour != 12:
                hour += 12
        else:
            hour = int(time_parts.replace('AM', ''))
            if hour == 12:
                hour = 0
        starts_at = date.replace(hour=hour, minute=0).isoformat()
    except ValueError:
        starts_at = date.replace(hour=17, minute=0).isoformat()  # Default 5 PM

    # Build description with ranking links based on location (HTML format)
    # Skip rankings for event types with no_rankings flag (e.g., Freeplay)
    description = merged.get('description', '')
    rankings = templates.get('rankings', {})
    location_rankings = location_config.get('rankings', ['season', 'year'])  # Default to Chaos Store rankings
    no_rankings = merged.get('no_rankings', False)

    if rankings and location_rankings and not no_rankings:
        ranking_links = '\n\n<p><strong>📊 Rankings:</strong></p>\n<ul>\n'
        for ranking_key in location_rankings:
            if ranking_key in rankings:
                name = rankings[ranking_key]['name']
                url = rankings[ranking_key]['url']
                ranking_links += f'<li><a href="{url}">{name}</a></li>\n'
        ranking_links += '</ul>'
        description = description + ranking_links

    # Build ranking_ids from location config
    ranking_ids = []
    for ranking_key in location_rankings:
        if ranking_key in rankings and 'id' in rankings[ranking_key]:
            ranking_ids.append(rankings[ranking_key]['id'])

    # Build payload in JSON:API format
    attributes = {
        'name': tournament_name,
        'url': url_slug,
        'tournament_type': merged.get('tournament_type', 'swiss'),
        'game_name': merged.get('game_name', 'Flesh and Blood'),
        'description': description,
        'private': merged.get('private', False),
        'quick_advance': merged.get('quick_advance', True),
        'starts_at': starts_at,
        'group_stage_enabled': False,  # Single stage tournament
    }

    # Add ranking_ids if available
    if ranking_ids:
        attributes['ranking_ids'] = ranking_ids

    # Add optional nested options
    for opt_key in ['notifications', 'match_options', 'registration_options',
                    'seeding_options', 'swiss_options']:
        if opt_key in merged:
            attributes[opt_key] = merged[opt_key]

    return {
        'data': {
            'type': 'Tournaments',
            'attributes': attributes
        }
    }


def create_tournament(config, access_token, payload, dry_run=False):
    """Create a tournament via API."""
    if dry_run:
        print("\n[DRY RUN] Would create tournament:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return {'dry_run': True, 'payload': payload}

    headers = get_api_headers(access_token)
    community_id = config.get('community_id')

    # Use resource scoping URL format for community tournaments
    if community_id:
        url = f"{API_BASE}/communities/{community_id}/tournaments.json"
    else:
        url = f"{API_BASE}/tournaments.json"

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        result = response.json()
        print(f"Tournament created successfully!")
        tournament_data = result.get('data', {})
        attrs = tournament_data.get('attributes', {})
        print(f"  Name: {attrs.get('name')}")
        print(f"  URL: https://challonge.com/{attrs.get('url')}")
        return result
    else:
        print(f"Failed to create tournament: {response.status_code}")
        print(f"\n--- Request Details ---")
        print(f"URL: {url}")
        print(f"Method: POST")
        # Mask the bearer token in headers for display
        display_headers = {k: (v[:20] + '...' if k == 'Authorization' else v) for k, v in headers.items()}
        print(f"Headers: {display_headers}")
        print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        print(f"\n--- Response Details ---")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Body: {response.text[:1000] if len(response.text) > 1000 else response.text}")
        return None


def get_tournament(config, access_token, tournament_url):
    """Fetch current tournament data from API."""
    headers = get_api_headers(access_token)
    community_id = config.get('community_id')

    if community_id:
        url = f"{API_BASE}/communities/{community_id}/tournaments/{tournament_url}.json"
    else:
        url = f"{API_BASE}/tournaments/{tournament_url}.json"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get('data', {}).get('attributes', {})
    else:
        print(f"Failed to fetch tournament: {response.status_code}")
        return None


def update_tournament(config, access_token, tournament_url, updates, dry_run=False):
    """Update an existing tournament via API.

    Fetches current tournament data first, merges with updates, then sends
    the complete data to avoid resetting fields.
    """
    headers = get_api_headers(access_token)
    community_id = config.get('community_id')

    if community_id:
        url = f"{API_BASE}/communities/{community_id}/tournaments/{tournament_url}.json"
    else:
        url = f"{API_BASE}/tournaments/{tournament_url}.json"

    # First, fetch current tournament data
    if not dry_run:
        current = get_tournament(config, access_token, tournament_url)
        if not current:
            return None
    else:
        current = {}

    # Merge updates with current data, preserving existing values
    merged = {}

    # Always preserve starts_at if it exists
    if current.get('starts_at'):
        merged['starts_at'] = current['starts_at']

    # Merge registration_options - only include non-null values
    current_reg = current.get('registration_options', {})
    update_reg = updates.get('registration_options', {})
    merged_reg = {}
    for key, value in {**current_reg, **update_reg}.items():
        if value is not None:
            merged_reg[key] = value
    if merged_reg:
        merged['registration_options'] = merged_reg

    # Preserve swiss_options - only include non-null/non-zero values
    current_swiss = current.get('swiss_options', {})
    update_swiss = updates.get('swiss_options', {})
    merged_swiss = {}
    for key, value in {**current_swiss, **update_swiss}.items():
        if value is not None and value != 0 and value != 0.0:
            merged_swiss[key] = value
    if merged_swiss:
        merged['swiss_options'] = merged_swiss

    # Add any other updates (skip None values and nested options already handled)
    skip_keys = {'registration_options', 'swiss_options'}
    for key, value in updates.items():
        if key not in skip_keys and value is not None:
            merged[key] = value

    if dry_run:
        print(f"\n[DRY RUN] Would update tournament {tournament_url}:")
        print(json.dumps(merged, indent=2, ensure_ascii=False))
        return {'dry_run': True, 'updates': merged}

    payload = {
        'data': {
            'type': 'Tournaments',
            'attributes': merged
        }
    }

    response = requests.put(url, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        print(f"Tournament updated successfully!")
        tournament_data = result.get('data', {})
        attrs = tournament_data.get('attributes', {})
        print(f"  Name: {attrs.get('name')}")
        print(f"  URL: https://challonge.com/{attrs.get('url')}")
        print(f"  starts_at: {attrs.get('starts_at')}")
        print(f"  open_signup: {attrs.get('registration_options', {}).get('open_signup')}")
        return result
    else:
        print(f"Failed to update tournament: {response.status_code}")
        print(f"\n--- Request Details ---")
        print(f"URL: {url}")
        print(f"Method: PUT")
        display_headers = {k: (v[:20] + '...' if k == 'Authorization' else v) for k, v in headers.items()}
        print(f"Headers: {display_headers}")
        print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        print(f"\n--- Response Details ---")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Body: {response.text[:1000] if len(response.text) > 1000 else response.text}")
        return None


def list_events(calendar, days_ahead=30):
    """List upcoming events from calendar."""
    today = datetime.now().date()
    end_date = today + timedelta(days=days_ahead)

    upcoming = []
    for event in calendar:
        event_date = datetime.strptime(event['Date'], '%Y-%m-%d').date()
        if today <= event_date <= end_date:
            upcoming.append(event)

    if not upcoming:
        print(f"No events found in the next {days_ahead} days.")
        return []

    print(f"\nUpcoming events (next {days_ahead} days):\n")
    print(f"{'Date':<12} {'Day':<10} {'Type':<6} {'Event':<25} {'Time':<8} {'Location'}")
    print("-" * 85)

    for event in upcoming:
        print(f"{event['Date']:<12} {event['Day']:<10} {event['EventType']:<6} "
              f"{event['Event']:<25} {event['Time']:<8} {event.get('Location', '')}")

    return upcoming


def find_event_by_date(calendar, date_str):
    """Find calendar event by date. Returns first match for backwards compatibility."""
    for event in calendar:
        if event['Date'] == date_str:
            return event
    return None


def find_events_by_date(calendar, date_str):
    """Find all calendar events for a given date."""
    return [event for event in calendar if event['Date'] == date_str]


def main():
    parser = argparse.ArgumentParser(
        description='Create Challonge tournaments from FABCO calendar',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument('--authorize', action='store_true',
                        help='Perform OAuth2 authorization (prompts for code)')
    parser.add_argument('--auth-url', action='store_true',
                        help='Print OAuth authorization URL and exit')
    parser.add_argument('--code', metavar='CODE',
                        help='Exchange authorization code for token')
    parser.add_argument('--list', action='store_true',
                        help='List upcoming events')
    parser.add_argument('--days', type=int, default=30,
                        help='Days ahead to show for --list (default: 30)')
    parser.add_argument('--create', metavar='DATE',
                        help='Create tournament for date (YYYY-MM-DD)')
    parser.add_argument('--create-range', nargs=2, metavar=('START', 'END'),
                        help='Create tournaments for date range')
    parser.add_argument('--dry-run', metavar='DATE',
                        help='Show what would be created for date')
    parser.add_argument('--calendar', metavar='PATH',
                        help='Path to calendar JSON file')
    parser.add_argument('--location', metavar='LOC',
                        help='Filter events by location (e.g., "Palmira", "Chaos Store")')
    parser.add_argument('--update', metavar='URL', nargs='+',
                        help='Update existing tournament(s) by URL slug (e.g., fabco_sage_20260205)')
    parser.add_argument('--update-dry-run', metavar='URL', nargs='+',
                        help='Show what would be updated for tournament(s)')

    args = parser.parse_args()

    # Load configurations
    try:
        config = load_oauth_config()
    except FileNotFoundError:
        print(f"OAuth config not found: {OAUTH_CONFIG_PATH}")
        return 1

    # Override calendar path if specified
    global CALENDAR_PATH
    if args.calendar:
        CALENDAR_PATH = args.calendar

    # Handle auth-url (just print URL)
    if args.auth_url:
        params = {
            'response_type': 'code',
            'client_id': config['client_id'],
            'redirect_uri': config['redirect_uri'],
            'scope': config['scope']
        }
        auth_url = f"{AUTH_URL}?{urlencode(params)}"
        print(f"Authorization URL:\n{auth_url}")
        return 0

    # Handle authorization
    if args.authorize or args.code:
        success = authorize(config, code=args.code)
        return 0 if success else 1

    # Load calendar, templates, and cards
    try:
        calendar = load_calendar()
        templates = load_templates()
        cards_data = load_cards()
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return 1

    # Handle list command
    if args.list:
        list_events(calendar, args.days)
        return 0

    # Handle dry-run
    if args.dry_run:
        events = find_events_by_date(calendar, args.dry_run)
        if args.location:
            events = [e for e in events if e.get('Location') == args.location]
        # Skip FreePlay events (casual sessions, no tournaments)
        events = [e for e in events if e.get('EventType') != 'FreePlay']
        if not events:
            print(f"No event found for date: {args.dry_run}" + (f" at {args.location}" if args.location else ""))
            return 1
        for event in events:
            print(f"\n--- {event.get('Event')} at {event.get('Location')} ---")
            payload = create_tournament_payload(event, templates, cards_data)
            create_tournament(config, None, payload, dry_run=True)
        return 0

    # Handle create commands
    if args.create or args.create_range:
        access_token = get_valid_token(config)
        if not access_token:
            return 1

        dates_to_create = []

        if args.create:
            dates_to_create = [args.create]
        elif args.create_range:
            start = datetime.strptime(args.create_range[0], '%Y-%m-%d')
            end = datetime.strptime(args.create_range[1], '%Y-%m-%d')
            current = start
            while current <= end:
                dates_to_create.append(current.strftime('%Y-%m-%d'))
                current += timedelta(days=1)

        created = 0
        failed = 0

        for date_str in dates_to_create:
            events = find_events_by_date(calendar, date_str)
            if args.location:
                events = [e for e in events if e.get('Location') == args.location]
            # Skip FreePlay events (casual sessions, no tournaments)
            events = [e for e in events if e.get('EventType') != 'FreePlay']
            if not events:
                continue

            for event in events:
                location = event.get('Location', 'Unknown')
                print(f"\nCreating tournament for {date_str} ({event['Event']} at {location})...")
                payload = create_tournament_payload(event, templates, cards_data)
                result = create_tournament(config, access_token, payload)

                if result:
                    created += 1
                else:
                    failed += 1

        print(f"\nSummary: {created} created, {failed} failed")
        return 0 if failed == 0 else 1

    # Handle update commands
    if args.update or args.update_dry_run:
        tournament_urls = args.update or args.update_dry_run
        is_dry_run = args.update_dry_run is not None

        if not is_dry_run:
            access_token = get_valid_token(config)
            if not access_token:
                return 1
        else:
            access_token = None

        # Settings to apply to all tournaments
        # Note: Only send open_signup, not signup_cap, to avoid resetting other settings
        updates = {
            'registration_options': {
                'open_signup': True
            }
        }

        updated = 0
        failed = 0

        for tournament_url in tournament_urls:
            print(f"\nUpdating tournament: {tournament_url}...")
            result = update_tournament(config, access_token, tournament_url, updates, dry_run=is_dry_run)

            if result:
                updated += 1
            else:
                failed += 1

        print(f"\nSummary: {updated} updated, {failed} failed")
        return 0 if failed == 0 else 1

    # No command specified
    parser.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
