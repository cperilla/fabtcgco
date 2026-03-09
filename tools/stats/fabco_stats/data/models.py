"""Data models for tournament statistics."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Set


@dataclass
class Match:
    """Represents a single match in a tournament."""

    tournament_id: str
    tournament_name: str
    date: datetime
    player1: str
    player2: str
    winner: Optional[str]  # None = tie
    player1_score: int
    player2_score: int
    round_number: int = 0

    @property
    def is_tie(self) -> bool:
        """Check if the match was a tie."""
        return self.winner is None

    @property
    def loser(self) -> Optional[str]:
        """Get the losing player, or None if tie."""
        if self.winner is None:
            return None
        return self.player2 if self.winner == self.player1 else self.player1

    def involves_player(self, player: str) -> bool:
        """Check if a player was in this match."""
        return player in (self.player1, self.player2)

    def get_opponent(self, player: str) -> Optional[str]:
        """Get the opponent of a player in this match."""
        if player == self.player1:
            return self.player2
        elif player == self.player2:
            return self.player1
        return None


@dataclass
class Tournament:
    """Represents a tournament with its matches and participants."""

    id: str
    name: str
    url: str
    date: datetime
    format: str  # CC, Sage, LL, etc.
    location: str
    participants: List[str] = field(default_factory=list)
    matches: List[Match] = field(default_factory=list)
    state: str = "complete"

    @property
    def match_count(self) -> int:
        """Get the number of matches in this tournament."""
        return len(self.matches)

    @property
    def participant_count(self) -> int:
        """Get the number of participants."""
        return len(self.participants)


@dataclass
class PlayerStats:
    """Aggregated statistics for a player."""

    name: str
    matches: int = 0
    wins: int = 0
    losses: int = 0
    ties: int = 0
    elo: float = 1500.0
    opponents: Set[str] = field(default_factory=set)
    tournaments_played: int = 0

    @property
    def win_rate(self) -> float:
        """Calculate win rate (excluding ties)."""
        total = self.wins + self.losses
        if total == 0:
            return 0.0
        return self.wins / total

    @property
    def tie_rate(self) -> float:
        """Calculate tie rate."""
        if self.matches == 0:
            return 0.0
        return self.ties / self.matches

    @property
    def unique_opponents(self) -> int:
        """Get count of unique opponents faced."""
        return len(self.opponents)

    def add_match_result(
        self, opponent: str, won: bool, tied: bool = False
    ) -> None:
        """Record a match result.

        Args:
            opponent: Name of the opponent.
            won: True if this player won.
            tied: True if the match was a tie.
        """
        self.matches += 1
        self.opponents.add(opponent)
        if tied:
            self.ties += 1
        elif won:
            self.wins += 1
        else:
            self.losses += 1
