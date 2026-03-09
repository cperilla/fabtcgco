"""Tournament data fetcher with caching support."""

import json
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional

from ..api.client import ChallongeClient, ChallongePublicClient
from .models import Match, Tournament
from .nicknames import NicknameNormalizer


class TournamentFetcher:
    """Fetches and caches tournament data from Challonge API."""

    def __init__(
        self,
        client: ChallongeClient,
        cache_dir: Optional[Path] = None,
        normalizer: Optional[NicknameNormalizer] = None,
    ):
        """Initialize the fetcher.

        Args:
            client: ChallongeClient instance.
            cache_dir: Directory for caching API responses.
            normalizer: NicknameNormalizer for player name normalization.
        """
        self.client = client
        self.public_client = ChallongePublicClient()
        self.cache_dir = cache_dir or Path(__file__).parent.parent.parent / "data" / "raw"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.normalizer = normalizer or NicknameNormalizer()

    def _cache_path(self, tournament_url: str) -> Path:
        """Get cache file path for a tournament."""
        return self.cache_dir / f"{tournament_url}.json"

    def _load_cached(self, tournament_url: str) -> Optional[dict]:
        """Load cached tournament data."""
        path = self._cache_path(tournament_url)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def _save_cache(self, tournament_url: str, data: dict) -> None:
        """Save tournament data to cache."""
        path = self._cache_path(tournament_url)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _parse_tournament_date(self, tournament_data: dict) -> Optional[datetime]:
        """Parse tournament date from API response.

        Always returns a naive datetime for consistent comparison.
        """
        attrs = tournament_data.get("attributes", {})
        starts_at = attrs.get("starts_at") or attrs.get("created_at")
        if starts_at:
            try:
                # Handle ISO format with timezone
                if "T" in starts_at:
                    dt = datetime.fromisoformat(starts_at.replace("Z", "+00:00"))
                    # Convert to naive datetime (strip timezone)
                    return dt.replace(tzinfo=None)
                return datetime.strptime(starts_at[:10], "%Y-%m-%d")
            except ValueError:
                pass
        return None

    def _parse_format_from_url(self, url: str) -> str:
        """Extract tournament format from URL slug."""
        # URL format: fabco_location_format_date
        parts = url.lower().split("_")
        if len(parts) >= 3:
            # Try to identify format from known types
            known_formats = ["cc", "sage", "ll", "blitz", "draft", "sealed"]
            for part in parts:
                if part in known_formats:
                    return part.upper()
        return "CC"  # Default to Classic Constructed

    def _parse_match(
        self,
        match_data: dict,
        participants: dict,
        tournament_id: str,
        tournament_name: str,
        tournament_date: datetime,
    ) -> Optional[Match]:
        """Parse a match from API response.

        Args:
            match_data: Match data from API (v2.1 format).
            participants: Dict mapping participant IDs to names.
            tournament_id: Tournament ID.
            tournament_name: Tournament name.
            tournament_date: Tournament date.

        Returns:
            Match object, or None if invalid.
        """
        attrs = match_data.get("attributes", {})

        # v2.1 format uses points_by_participant array
        points_by_participant = attrs.get("points_by_participant", [])
        if len(points_by_participant) >= 2:
            player1_id = str(points_by_participant[0].get("participant_id"))
            player2_id = str(points_by_participant[1].get("participant_id"))

            # Get scores from score_in_sets or points_by_participant
            score_in_sets = attrs.get("score_in_sets", [])
            if score_in_sets and len(score_in_sets) > 0:
                player1_score = score_in_sets[0][0] if len(score_in_sets[0]) > 0 else 0
                player2_score = score_in_sets[0][1] if len(score_in_sets[0]) > 1 else 0
            else:
                # Fallback to scores from points_by_participant
                p1_scores = points_by_participant[0].get("scores", [])
                p2_scores = points_by_participant[1].get("scores", [])
                player1_score = sum(p1_scores) if p1_scores else 0
                player2_score = sum(p2_scores) if p2_scores else 0
        else:
            # Fallback to old format (player1_id, player2_id)
            player1_id = str(attrs.get("player1_id", ""))
            player2_id = str(attrs.get("player2_id", ""))

            # Parse scores from scores_csv
            scores_csv = attrs.get("scores_csv", "") or attrs.get("scores", "")
            player1_score = 0
            player2_score = 0
            if scores_csv:
                try:
                    parts = scores_csv.replace(" ", "").split("-")
                    if len(parts) == 2:
                        player1_score = int(parts[0])
                        player2_score = int(parts[1])
                except ValueError:
                    pass

        if not player1_id or not player2_id:
            return None

        # Get player names from participants
        player1_name = participants.get(player1_id)
        player2_name = participants.get(player2_id)

        if not player1_name or not player2_name:
            return None

        # Normalize names
        player1 = self.normalizer.normalize(player1_name)
        player2 = self.normalizer.normalize(player2_name)

        # Determine winner
        winner_id = attrs.get("winner_id")
        winner = None
        if winner_id:
            winner_name = participants.get(str(winner_id))
            if winner_name:
                winner = self.normalizer.normalize(winner_name)

        return Match(
            tournament_id=tournament_id,
            tournament_name=tournament_name,
            date=tournament_date,
            player1=player1,
            player2=player2,
            winner=winner,
            player1_score=player1_score,
            player2_score=player2_score,
            round_number=attrs.get("round", 0),
        )

    def fetch_tournament(
        self, url_slug: str, use_cache: bool = True
    ) -> Optional[Tournament]:
        """Fetch a single tournament with all matches.

        Args:
            url_slug: Tournament URL slug.
            use_cache: Whether to use cached data if available.

        Returns:
            Tournament object, or None if not found.
        """
        # Try cache first
        if use_cache:
            cached = self._load_cached(url_slug)
            if cached:
                # Detect format and parse accordingly
                if "included" in cached:
                    # v2.1 format with includes
                    return self._parse_tournament_v21_full(cached)
                elif "tournament" in cached and "matches" in cached.get("tournament", {}):
                    # v1 public format
                    return self._parse_tournament_from_public(cached, url_slug)
                else:
                    # v2.1 format without includes (legacy)
                    return self._parse_tournament_from_cache(cached)

        # Use v2.1 API with include parameter (works for community tournaments)
        if self.client:
            full_data = self.client.get_tournament_full(url_slug)
            if full_data and "data" in full_data:
                self._save_cache(url_slug, full_data)
                return self._parse_tournament_v21_full(full_data)

        return None

    def _parse_tournament_v21_full(self, data: dict) -> Optional[Tournament]:
        """Parse a Tournament from v2.1 API response with includes.

        This format has 'data' for the tournament and 'included' array
        containing matches and participants.
        """
        tournament_data = data.get("data", {})
        included = data.get("included", [])

        attrs = tournament_data.get("attributes", {})
        tournament_id = tournament_data.get("id", "")
        tournament_name = attrs.get("name", "")
        tournament_url = attrs.get("url", "")
        tournament_date = self._parse_tournament_date(tournament_data) or datetime.now()

        # Extract participants and matches from included array
        participants = {}
        participant_names = []
        matches_data = []

        for item in included:
            item_type = item.get("type")
            if item_type == "participant":
                p_id = item.get("id")
                p_attrs = item.get("attributes", {})
                p_name = p_attrs.get("name") or p_attrs.get("display_name") or p_attrs.get("username")
                if p_id and p_name:
                    participants[str(p_id)] = p_name
                    participant_names.append(self.normalizer.normalize(p_name))
            elif item_type == "match":
                matches_data.append(item)

        # Parse matches
        matches = []
        for match_item in matches_data:
            match = self._parse_match(
                match_item,
                participants,
                tournament_id,
                tournament_name,
                tournament_date,
            )
            if match:
                matches.append(match)

        return Tournament(
            id=tournament_id,
            name=tournament_name,
            url=tournament_url,
            date=tournament_date,
            format=self._parse_format_from_url(tournament_url),
            location=self._extract_location(tournament_name),
            participants=participant_names,
            matches=matches,
            state=attrs.get("state", "complete"),
        )

    def _parse_tournament_from_public(self, data: dict, url_slug: str) -> Optional[Tournament]:
        """Parse a Tournament from public API (v1 format).

        The v1 format has tournament data with nested matches and participants.
        """
        tournament = data.get("tournament", {})

        tournament_id = str(tournament.get("id", ""))
        tournament_name = tournament.get("name", "")
        tournament_url = tournament.get("url", url_slug)

        # Parse date
        starts_at = tournament.get("started_at") or tournament.get("created_at", "")
        tournament_date = datetime.now()
        if starts_at:
            try:
                if "T" in starts_at:
                    tournament_date = datetime.fromisoformat(starts_at.replace("Z", "+00:00"))
                else:
                    tournament_date = datetime.strptime(starts_at[:10], "%Y-%m-%d")
            except ValueError:
                pass

        # Build participants dict from nested data
        participants = {}
        participant_names = []
        for p in tournament.get("participants", []):
            p_data = p.get("participant", {})
            p_id = p_data.get("id")
            p_name = p_data.get("name") or p_data.get("display_name") or p_data.get("username")
            if p_id and p_name:
                participants[str(p_id)] = p_name
                participant_names.append(self.normalizer.normalize(p_name))

        # Parse matches from nested data
        matches = []
        for m in tournament.get("matches", []):
            m_data = m.get("match", {})
            match = self._parse_match_v1(
                m_data,
                participants,
                tournament_id,
                tournament_name,
                tournament_date,
            )
            if match:
                matches.append(match)

        return Tournament(
            id=tournament_id,
            name=tournament_name,
            url=tournament_url,
            date=tournament_date,
            format=self._parse_format_from_url(tournament_url),
            location=self._extract_location(tournament_name),
            participants=participant_names,
            matches=matches,
            state=tournament.get("state", "complete"),
        )

    def _parse_match_v1(
        self,
        match_data: dict,
        participants: dict,
        tournament_id: str,
        tournament_name: str,
        tournament_date: datetime,
    ) -> Optional[Match]:
        """Parse a match from v1 API response."""
        player1_id = match_data.get("player1_id")
        player2_id = match_data.get("player2_id")

        if not player1_id or not player2_id:
            return None

        player1_name = participants.get(str(player1_id))
        player2_name = participants.get(str(player2_id))

        if not player1_name or not player2_name:
            return None

        player1 = self.normalizer.normalize(player1_name)
        player2 = self.normalizer.normalize(player2_name)

        # Parse scores
        scores_csv = match_data.get("scores_csv", "") or ""
        player1_score = 0
        player2_score = 0

        if scores_csv:
            try:
                parts = scores_csv.split("-")
                if len(parts) == 2:
                    player1_score = int(parts[0])
                    player2_score = int(parts[1])
            except ValueError:
                pass

        # Determine winner
        winner_id = match_data.get("winner_id")
        winner = None
        if winner_id:
            winner_name = participants.get(str(winner_id))
            if winner_name:
                winner = self.normalizer.normalize(winner_name)

        return Match(
            tournament_id=tournament_id,
            tournament_name=tournament_name,
            date=tournament_date,
            player1=player1,
            player2=player2,
            winner=winner,
            player1_score=player1_score,
            player2_score=player2_score,
            round_number=match_data.get("round", 0),
        )

    def _parse_tournament_from_cache(self, cached: dict) -> Optional[Tournament]:
        """Parse a Tournament from cached data."""
        tournament_data = cached.get("tournament", {})
        participants_data = cached.get("participants", [])
        matches_data = cached.get("matches", [])

        attrs = tournament_data.get("attributes", {})
        tournament_id = tournament_data.get("id", "")
        tournament_name = attrs.get("name", "")
        tournament_url = attrs.get("url", "")
        tournament_date = self._parse_tournament_date(tournament_data) or datetime.now()

        # Build participants dict
        participants = {}
        participant_names = []
        for p in participants_data:
            p_id = p.get("id")
            p_name = p.get("attributes", {}).get("name") or p.get("attributes", {}).get(
                "display_name"
            )
            if p_id and p_name:
                participants[str(p_id)] = p_name
                participant_names.append(self.normalizer.normalize(p_name))

        # Parse matches
        matches = []
        for match_data in matches_data:
            match = self._parse_match(
                match_data,
                participants,
                tournament_id,
                tournament_name,
                tournament_date,
            )
            if match:
                matches.append(match)

        return Tournament(
            id=tournament_id,
            name=tournament_name,
            url=tournament_url,
            date=tournament_date,
            format=self._parse_format_from_url(tournament_url),
            location=self._extract_location(tournament_name),
            participants=participant_names,
            matches=matches,
            state=attrs.get("state", "complete"),
        )

    def _extract_location(self, tournament_name: str) -> str:
        """Extract location from tournament name."""
        # Name format: FAB Location Format Day Date : CardName
        parts = tournament_name.split()
        if len(parts) >= 2:
            # Skip "FAB" prefix and try to get location
            return parts[1] if parts[0].upper() == "FAB" else parts[0]
        return "Unknown"

    def fetch_all_tournaments(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        use_cache: bool = True,
    ) -> List[Tournament]:
        """Fetch all tournaments in date range.

        Args:
            start_date: Start date filter (inclusive).
            end_date: End date filter (inclusive).
            use_cache: Whether to use cached data.

        Returns:
            List of Tournament objects.
        """
        # List all tournaments in the community
        tournament_list = self.client.list_all_tournaments()

        tournaments = []
        for t in tournament_list:
            attrs = t.get("attributes", {})
            url_slug = attrs.get("url")
            t_date = self._parse_tournament_date(t)

            if not url_slug:
                continue

            # Filter by date if specified
            if t_date:
                if start_date and t_date.date() < start_date:
                    continue
                if end_date and t_date.date() > end_date:
                    continue

            # Only include completed tournaments
            state = attrs.get("state", "")
            if state not in ("complete", "awaiting_review"):
                continue

            # Fetch full tournament data
            tournament = self.fetch_tournament(url_slug, use_cache=use_cache)
            if tournament:
                tournaments.append(tournament)
                print(f"Fetched: {tournament.name} ({len(tournament.matches)} matches)")

        return tournaments

    def load_all_cached(self) -> List[Tournament]:
        """Load all tournaments from cache without API calls.

        Returns:
            List of Tournament objects from cached data.
        """
        tournaments = []
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached = json.load(f)

                url_slug = cache_file.stem

                # Detect format and parse accordingly
                if "included" in cached:
                    # v2.1 format with includes
                    tournament = self._parse_tournament_v21_full(cached)
                elif "tournament" in cached:
                    tournament_data = cached["tournament"]
                    # v1 public format has matches nested in tournament
                    if "matches" in tournament_data or "participants" in tournament_data:
                        tournament = self._parse_tournament_from_public(cached, url_slug)
                    else:
                        # v2.1 format has separate matches/participants arrays (legacy)
                        tournament = self._parse_tournament_from_cache(cached)
                else:
                    tournament = self._parse_tournament_from_cache(cached)

                if tournament and tournament.matches:
                    tournaments.append(tournament)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading cache {cache_file}: {e}")

        # Sort by date
        tournaments.sort(key=lambda t: t.date)
        return tournaments
