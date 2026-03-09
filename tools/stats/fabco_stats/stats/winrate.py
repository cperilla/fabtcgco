"""Win rate calculations and head-to-head analysis."""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pandas as pd

from ..data.models import Match


@dataclass
class Rivalry:
    """Represents a head-to-head rivalry between two players."""

    player1: str
    player2: str
    player1_wins: int
    player2_wins: int
    ties: int
    total_matches: int

    @property
    def player1_winrate(self) -> float:
        """Win rate of player1 against player2 (excluding ties)."""
        decisive = self.player1_wins + self.player2_wins
        if decisive == 0:
            return 0.5
        return self.player1_wins / decisive

    @property
    def player2_winrate(self) -> float:
        """Win rate of player2 against player1 (excluding ties)."""
        return 1 - self.player1_winrate

    @property
    def is_balanced(self) -> bool:
        """Check if rivalry is balanced (40-60% range)."""
        return 0.4 <= self.player1_winrate <= 0.6

    @property
    def dominant_player(self) -> Optional[str]:
        """Get the dominant player if rivalry is unbalanced."""
        if self.player1_winrate > 0.6:
            return self.player1
        elif self.player1_winrate < 0.4:
            return self.player2
        return None


def build_h2h_matrix(
    matches: List[Match],
    min_matches: int = 1,
) -> pd.DataFrame:
    """Build head-to-head win rate matrix.

    Args:
        matches: List of matches to analyze.
        min_matches: Minimum matches between players to include.

    Returns:
        DataFrame with players as rows and columns, values are win rates.
        Value at [A, B] is A's win rate against B.
    """
    # Track wins and total matches for each pair
    h2h_wins: Dict[Tuple[str, str], int] = defaultdict(int)
    h2h_total: Dict[Tuple[str, str], int] = defaultdict(int)

    for match in matches:
        p1, p2 = match.player1, match.player2

        # Track total matches (both directions)
        h2h_total[(p1, p2)] += 1
        h2h_total[(p2, p1)] += 1

        # Track wins (only the winner)
        if match.winner:
            if match.winner == p1:
                h2h_wins[(p1, p2)] += 1
            else:
                h2h_wins[(p2, p1)] += 1

    # Get all players
    players = sorted(set(p for pair in h2h_total.keys() for p in pair))

    # Build matrix
    data = []
    for p1 in players:
        row = []
        for p2 in players:
            if p1 == p2:
                row.append(float("nan"))  # No self matchup
            elif h2h_total[(p1, p2)] >= min_matches:
                wins = h2h_wins[(p1, p2)]
                # Win rate excluding ties
                decisive = h2h_wins[(p1, p2)] + h2h_wins[(p2, p1)]
                if decisive > 0:
                    row.append(wins / decisive)
                else:
                    row.append(0.5)  # All ties
            else:
                row.append(float("nan"))  # Not enough matches
        data.append(row)

    return pd.DataFrame(data, index=players, columns=players)


def build_match_count_matrix(matches: List[Match]) -> pd.DataFrame:
    """Build matrix of match counts between players.

    Args:
        matches: List of matches to analyze.

    Returns:
        DataFrame with players as rows and columns, values are match counts.
    """
    counts: Dict[Tuple[str, str], int] = defaultdict(int)

    for match in matches:
        p1, p2 = match.player1, match.player2
        counts[(p1, p2)] += 1
        counts[(p2, p1)] += 1

    players = sorted(set(p for pair in counts.keys() for p in pair))

    data = []
    for p1 in players:
        row = []
        for p2 in players:
            if p1 == p2:
                row.append(0)
            else:
                row.append(counts[(p1, p2)])
        data.append(row)

    return pd.DataFrame(data, index=players, columns=players)


def build_tie_rate_matrix(matches: List[Match], min_matches: int = 1) -> pd.DataFrame:
    """Build matrix of tie rates between players.

    Args:
        matches: List of matches to analyze.
        min_matches: Minimum matches required.

    Returns:
        DataFrame with tie rates for each player pair.
    """
    ties: Dict[Tuple[str, str], int] = defaultdict(int)
    totals: Dict[Tuple[str, str], int] = defaultdict(int)

    for match in matches:
        p1, p2 = match.player1, match.player2
        totals[(p1, p2)] += 1
        totals[(p2, p1)] += 1
        if match.is_tie:
            ties[(p1, p2)] += 1
            ties[(p2, p1)] += 1

    players = sorted(set(p for pair in totals.keys() for p in pair))

    data = []
    for p1 in players:
        row = []
        for p2 in players:
            if p1 == p2:
                row.append(float("nan"))
            elif totals[(p1, p2)] >= min_matches:
                row.append(ties[(p1, p2)] / totals[(p1, p2)])
            else:
                row.append(float("nan"))
        data.append(row)

    return pd.DataFrame(data, index=players, columns=players)


def get_rivalries(
    matches: List[Match],
    min_matches: int = 3,
) -> List[Rivalry]:
    """Get list of rivalries between players.

    Args:
        matches: List of matches to analyze.
        min_matches: Minimum matches for a rivalry.

    Returns:
        List of Rivalry objects sorted by total matches descending.
    """
    # Track stats for each pair (use sorted tuple for consistency)
    pair_stats: Dict[Tuple[str, str], Dict] = defaultdict(
        lambda: {"p1_wins": 0, "p2_wins": 0, "ties": 0, "total": 0}
    )

    for match in matches:
        p1, p2 = sorted([match.player1, match.player2])
        pair = (p1, p2)
        pair_stats[pair]["total"] += 1

        if match.is_tie:
            pair_stats[pair]["ties"] += 1
        elif match.winner == p1:
            pair_stats[pair]["p1_wins"] += 1
        else:
            pair_stats[pair]["p2_wins"] += 1

    # Build rivalry list
    rivalries = []
    for (p1, p2), stats in pair_stats.items():
        if stats["total"] >= min_matches:
            rivalries.append(
                Rivalry(
                    player1=p1,
                    player2=p2,
                    player1_wins=stats["p1_wins"],
                    player2_wins=stats["p2_wins"],
                    ties=stats["ties"],
                    total_matches=stats["total"],
                )
            )

    # Sort by total matches
    rivalries.sort(key=lambda r: r.total_matches, reverse=True)
    return rivalries


def get_player_winrate(matches: List[Match], player: str) -> float:
    """Calculate overall win rate for a player.

    Args:
        matches: List of matches.
        player: Player name.

    Returns:
        Win rate between 0 and 1 (excluding ties).
    """
    wins = 0
    decisive = 0

    for match in matches:
        if match.involves_player(player):
            if not match.is_tie:
                decisive += 1
                if match.winner == player:
                    wins += 1

    if decisive == 0:
        return 0.5
    return wins / decisive


def get_all_player_stats(matches: List[Match]) -> Dict[str, Dict]:
    """Calculate statistics for all players.

    Args:
        matches: List of matches.

    Returns:
        Dict mapping player names to stat dicts with keys:
        - matches, wins, losses, ties, win_rate, tie_rate, opponents
    """
    stats: Dict[str, Dict] = defaultdict(
        lambda: {
            "matches": 0,
            "wins": 0,
            "losses": 0,
            "ties": 0,
            "opponents": set(),
        }
    )

    for match in matches:
        p1, p2 = match.player1, match.player2

        stats[p1]["matches"] += 1
        stats[p2]["matches"] += 1
        stats[p1]["opponents"].add(p2)
        stats[p2]["opponents"].add(p1)

        if match.is_tie:
            stats[p1]["ties"] += 1
            stats[p2]["ties"] += 1
        elif match.winner == p1:
            stats[p1]["wins"] += 1
            stats[p2]["losses"] += 1
        else:
            stats[p2]["wins"] += 1
            stats[p1]["losses"] += 1

    # Calculate rates
    for player, s in stats.items():
        decisive = s["wins"] + s["losses"]
        s["win_rate"] = s["wins"] / decisive if decisive > 0 else 0.5
        s["tie_rate"] = s["ties"] / s["matches"] if s["matches"] > 0 else 0.0
        s["opponent_count"] = len(s["opponents"])

    return dict(stats)
