"""Win streak and tie rate calculations."""

from collections import defaultdict
from typing import Dict, List, Tuple

from ..data.models import Match


def calculate_streaks(matches: List[Match]) -> Dict[str, int]:
    """Calculate longest win streak for each player.

    Args:
        matches: List of matches in chronological order.

    Returns:
        Dict mapping player names to their longest win streak.
    """
    # Sort matches by date
    sorted_matches = sorted(matches, key=lambda m: m.date)

    # Track current and max streaks
    current_streak: Dict[str, int] = defaultdict(int)
    max_streak: Dict[str, int] = defaultdict(int)

    for match in sorted_matches:
        p1, p2 = match.player1, match.player2

        if match.is_tie:
            # Ties reset both streaks
            current_streak[p1] = 0
            current_streak[p2] = 0
        elif match.winner == p1:
            # P1 wins, extend streak; P2 loses, reset
            current_streak[p1] += 1
            current_streak[p2] = 0
            max_streak[p1] = max(max_streak[p1], current_streak[p1])
        else:
            # P2 wins
            current_streak[p2] += 1
            current_streak[p1] = 0
            max_streak[p2] = max(max_streak[p2], current_streak[p2])

    return dict(max_streak)


def get_top_streaks(
    matches: List[Match], limit: int = 8
) -> List[Tuple[str, int]]:
    """Get players with longest win streaks.

    Args:
        matches: List of matches.
        limit: Number of top players to return.

    Returns:
        List of (player_name, streak_length) sorted by streak descending.
    """
    streaks = calculate_streaks(matches)
    sorted_streaks = sorted(streaks.items(), key=lambda x: x[1], reverse=True)
    return sorted_streaks[:limit]


def calculate_tie_rates(matches: List[Match]) -> Dict[str, float]:
    """Calculate tie rate for each player.

    Args:
        matches: List of matches.

    Returns:
        Dict mapping player names to their tie rate (0-1).
    """
    player_matches: Dict[str, int] = defaultdict(int)
    player_ties: Dict[str, int] = defaultdict(int)

    for match in matches:
        p1, p2 = match.player1, match.player2
        player_matches[p1] += 1
        player_matches[p2] += 1

        if match.is_tie:
            player_ties[p1] += 1
            player_ties[p2] += 1

    tie_rates = {}
    for player, total in player_matches.items():
        if total > 0:
            tie_rates[player] = player_ties[player] / total
        else:
            tie_rates[player] = 0.0

    return tie_rates


def get_top_tie_rates(
    matches: List[Match], min_matches: int = 5, limit: int = 8
) -> List[Tuple[str, float, int]]:
    """Get players with highest tie rates.

    Args:
        matches: List of matches.
        min_matches: Minimum matches required.
        limit: Number of top players to return.

    Returns:
        List of (player_name, tie_rate, match_count) sorted by rate descending.
    """
    tie_rates = calculate_tie_rates(matches)

    # Count matches per player
    match_counts: Dict[str, int] = defaultdict(int)
    for match in matches:
        match_counts[match.player1] += 1
        match_counts[match.player2] += 1

    # Filter by minimum matches
    filtered = [
        (player, rate, match_counts[player])
        for player, rate in tie_rates.items()
        if match_counts[player] >= min_matches
    ]

    # Sort by tie rate
    filtered.sort(key=lambda x: x[1], reverse=True)
    return filtered[:limit]


def calculate_dominance(matches: List[Match]) -> Dict[str, float]:
    """Calculate dominance score for each player.

    Dominance is how far a player's win rate deviates from 50%.
    A player with 70% win rate has 0.2 dominance (|0.7 - 0.5|).

    Args:
        matches: List of matches.

    Returns:
        Dict mapping player names to dominance score (0-0.5).
    """
    player_wins: Dict[str, int] = defaultdict(int)
    player_decisive: Dict[str, int] = defaultdict(int)

    for match in matches:
        p1, p2 = match.player1, match.player2

        if not match.is_tie:
            player_decisive[p1] += 1
            player_decisive[p2] += 1
            if match.winner == p1:
                player_wins[p1] += 1
            else:
                player_wins[p2] += 1

    dominance = {}
    for player, decisive in player_decisive.items():
        if decisive > 0:
            win_rate = player_wins[player] / decisive
            dominance[player] = abs(win_rate - 0.5)
        else:
            dominance[player] = 0.0

    return dominance
