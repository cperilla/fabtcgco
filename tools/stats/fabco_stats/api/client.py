"""Challonge API v2.1 client for fetching tournament data."""

from typing import List, Optional
import requests


class ChallongePublicClient:
    """Client for Challonge public JSON endpoints.

    Uses the public JSON export available at challonge.com/{url}.json
    which works for any public tournament without authentication.
    """

    PUBLIC_BASE = "https://api.challonge.com/v1/tournaments"

    def __init__(self):
        """Initialize the public client."""
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        })

    def get_tournament_with_matches(self, url_slug: str) -> Optional[dict]:
        """Get tournament with matches and participants via public JSON.

        Args:
            url_slug: Tournament URL slug.

        Returns:
            Tournament data dict with nested matches and participants.
        """
        # Public JSON endpoint includes matches and participants
        url = f"{self.PUBLIC_BASE}/{url_slug}.json?include_matches=1&include_participants=1"
        try:
            response = self._session.get(url)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching {url_slug}: {e}")
        return None


class ChallongeClient:
    """Client for Challonge API v2.1.

    Provides methods to fetch tournaments, matches, and participants
    from a Challonge community.
    """

    API_BASE = "https://api.challonge.com/v2.1"

    def __init__(self, access_token: str, community_id: str = "fabtcgcolombia"):
        """Initialize the client.

        Args:
            access_token: OAuth2 bearer token.
            community_id: Challonge community ID (default: fabtcgcolombia).
        """
        self.access_token = access_token
        self.community_id = community_id
        self._session = requests.Session()
        self._session.headers.update(self._get_headers())

    def _get_headers(self) -> dict:
        """Get headers for API requests."""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Authorization-Type": "v2",
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
        }

    def _make_request(
        self, method: str, endpoint: str, params: Optional[dict] = None, silent: bool = False
    ) -> Optional[dict]:
        """Make an API request.

        Args:
            method: HTTP method (GET, POST, etc.).
            endpoint: API endpoint path.
            params: Query parameters.
            silent: If True, don't print error messages.

        Returns:
            JSON response data, or None on error.
        """
        url = f"{self.API_BASE}{endpoint}"
        response = self._session.request(method, url, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            if not silent:
                print(f"API request failed: {response.status_code}")
                print(f"URL: {url}")
                print(f"Response: {response.text[:500]}")
            return None

    def list_tournaments(self, page: int = 1, per_page: int = 25) -> List[dict]:
        """List all tournaments in the community.

        Args:
            page: Page number (1-indexed).
            per_page: Results per page (max 25).

        Returns:
            List of tournament data dicts.
        """
        endpoint = f"/communities/{self.community_id}/tournaments.json"
        params = {"page": page, "per_page": per_page}
        result = self._make_request("GET", endpoint, params)

        if result and "data" in result:
            return result["data"]
        return []

    def list_all_tournaments(self) -> List[dict]:
        """List all tournaments in the community (handles pagination).

        Returns:
            List of all tournament data dicts.
        """
        all_tournaments = []
        page = 1
        per_page = 25

        while True:
            tournaments = self.list_tournaments(page=page, per_page=per_page)
            if not tournaments:
                break
            all_tournaments.extend(tournaments)
            if len(tournaments) < per_page:
                break
            page += 1

        return all_tournaments

    def get_tournament(self, url_slug: str) -> Optional[dict]:
        """Get tournament details by URL slug.

        Args:
            url_slug: Tournament URL slug (e.g., fabco_cc_20250301).

        Returns:
            Tournament data dict, or None if not found.
        """
        endpoint = f"/communities/{self.community_id}/tournaments/{url_slug}.json"
        result = self._make_request("GET", endpoint)

        if result and "data" in result:
            return result["data"]
        return None

    def get_tournament_full(self, url_slug: str) -> Optional[dict]:
        """Get tournament with matches and participants included.

        Uses the include parameter to fetch all data in one request.

        Args:
            url_slug: Tournament URL slug.

        Returns:
            Full API response with data and included arrays, or None.
        """
        endpoint = f"/communities/{self.community_id}/tournaments/{url_slug}.json"
        params = {"include": "matches,participants"}
        result = self._make_request("GET", endpoint, params=params)
        return result if result else None

    def get_matches(self, url_slug: str) -> List[dict]:
        """Get all matches for a tournament.

        Args:
            url_slug: Tournament URL slug.

        Returns:
            List of match data dicts.
        """
        # Try non-community-scoped endpoint first (works for public tournaments)
        endpoint = f"/tournaments/{url_slug}/matches.json"
        result = self._make_request("GET", endpoint, silent=True)

        if result and "data" in result:
            return result["data"]

        # Fallback to community-scoped endpoint
        endpoint = f"/communities/{self.community_id}/tournaments/{url_slug}/matches.json"
        result = self._make_request("GET", endpoint)

        if result and "data" in result:
            return result["data"]
        return []

    def get_participants(self, url_slug: str) -> List[dict]:
        """Get all participants for a tournament.

        Args:
            url_slug: Tournament URL slug.

        Returns:
            List of participant data dicts.
        """
        # Try non-community-scoped endpoint first (works for public tournaments)
        endpoint = f"/tournaments/{url_slug}/participants.json"
        result = self._make_request("GET", endpoint, silent=True)

        if result and "data" in result:
            return result["data"]

        # Fallback to community-scoped endpoint
        endpoint = f"/communities/{self.community_id}/tournaments/{url_slug}/participants.json"
        result = self._make_request("GET", endpoint)

        if result and "data" in result:
            return result["data"]
        return []
