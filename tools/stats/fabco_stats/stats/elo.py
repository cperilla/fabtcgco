"""ELO rating calculation for tournament matches."""

from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple

from ..data.models import Match


def expected_score(rating_a: float, rating_b: float) -> float:
    """Calculate expected score for player A against player B.

    Args:
        rating_a: ELO rating of player A.
        rating_b: ELO rating of player B.

    Returns:
        Expected score between 0 and 1.
    """
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def calculate_elo(
    matches: List[Match],
    k: int = 32,
    initial: int = 1500,
) -> Dict[str, float]:
    """Calculate ELO ratings from match history.

    Args:
        matches: List of matches in chronological order.
        k: K-factor for rating changes.
        initial: Initial rating for new players.

    Returns:
        Dict mapping player names to final ELO ratings.
    """
    ratings: Dict[str, float] = defaultdict(lambda: initial)

    # Sort matches by date
    sorted_matches = sorted(matches, key=lambda m: m.date)

    for match in sorted_matches:
        player1 = match.player1
        player2 = match.player2

        # Get current ratings
        r1 = ratings[player1]
        r2 = ratings[player2]

        # Calculate expected scores
        e1 = expected_score(r1, r2)
        e2 = expected_score(r2, r1)

        # Determine actual scores
        if match.is_tie:
            s1 = 0.5
            s2 = 0.5
        elif match.winner == player1:
            s1 = 1.0
            s2 = 0.0
        else:
            s1 = 0.0
            s2 = 1.0

        # Update ratings
        ratings[player1] = r1 + k * (s1 - e1)
        ratings[player2] = r2 + k * (s2 - e2)

    return dict(ratings)


def get_elo_history(
    matches: List[Match],
    k: int = 32,
    initial: int = 1500,
) -> Dict[str, List[Tuple[datetime, float]]]:
    """Calculate ELO history over time for each player.

    Args:
        matches: List of matches in chronological order.
        k: K-factor for rating changes.
        initial: Initial rating for new players.

    Returns:
        Dict mapping player names to list of (date, rating) tuples.
    """
    ratings: Dict[str, float] = defaultdict(lambda: initial)
    history: Dict[str, List[Tuple[datetime, float]]] = defaultdict(list)

    # Sort matches by date
    sorted_matches = sorted(matches, key=lambda m: m.date)

    for match in sorted_matches:
        player1 = match.player1
        player2 = match.player2

        # Initialize history if first match
        if not history[player1]:
            history[player1].append((match.date, ratings[player1]))
        if not history[player2]:
            history[player2].append((match.date, ratings[player2]))

        # Get current ratings
        r1 = ratings[player1]
        r2 = ratings[player2]

        # Calculate expected scores
        e1 = expected_score(r1, r2)
        e2 = expected_score(r2, r1)

        # Determine actual scores
        if match.is_tie:
            s1 = 0.5
            s2 = 0.5
        elif match.winner == player1:
            s1 = 1.0
            s2 = 0.0
        else:
            s1 = 0.0
            s2 = 1.0

        # Update ratings
        ratings[player1] = r1 + k * (s1 - e1)
        ratings[player2] = r2 + k * (s2 - e2)

        # Record history
        history[player1].append((match.date, ratings[player1]))
        history[player2].append((match.date, ratings[player2]))

    return dict(history)


def get_elo_ranking(
    elo_ratings: Dict[str, float],
    min_matches: int = 0,
    match_counts: Dict[str, int] = None,
) -> List[Tuple[str, float]]:
    """Get ranked list of players by ELO.

    Args:
        elo_ratings: Dict mapping player names to ELO ratings.
        min_matches: Minimum matches required to be included.
        match_counts: Dict mapping player names to match counts.

    Returns:
        List of (player_name, elo) tuples sorted by ELO descending.
    """
    if min_matches > 0 and match_counts:
        filtered = {
            player: elo
            for player, elo in elo_ratings.items()
            if match_counts.get(player, 0) >= min_matches
        }
    else:
        filtered = elo_ratings

    return sorted(filtered.items(), key=lambda x: x[1], reverse=True)
