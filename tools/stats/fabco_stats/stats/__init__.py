"""Statistics calculation modules."""

from .elo import calculate_elo, get_elo_history
from .winrate import build_h2h_matrix, build_tie_rate_matrix, get_rivalries, Rivalry
from .streaks import calculate_streaks, calculate_tie_rates, get_top_streaks, get_top_tie_rates

__all__ = [
    "calculate_elo",
    "get_elo_history",
    "build_h2h_matrix",
    "build_tie_rate_matrix",
    "get_rivalries",
    "Rivalry",
    "calculate_streaks",
    "calculate_tie_rates",
    "get_top_streaks",
    "get_top_tie_rates",
]
