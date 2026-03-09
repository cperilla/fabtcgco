"""Radar chart visualizations for player profiles."""

import math
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np


def setup_style():
    """Set up matplotlib style for consistent visualizations."""
    plt.style.use("seaborn-v0_8-darkgrid")
    plt.rcParams["figure.facecolor"] = "#1a1a2e"
    plt.rcParams["axes.facecolor"] = "#16213e"
    plt.rcParams["text.color"] = "white"
    plt.rcParams["axes.labelcolor"] = "white"
    plt.rcParams["xtick.color"] = "white"
    plt.rcParams["ytick.color"] = "white"


def plot_player_radar(
    player: str,
    stats: Dict,
    all_stats: Dict[str, Dict],
    output_path: Path,
    figsize: tuple = (12, 12),
) -> None:
    """Plot radar chart for a single player.

    Axes:
    - Win rate (%)
    - Tie rate (%)
    - Unique opponents (normalized)
    - Matches played (normalized)
    - Dominance (distance from 50%)

    Args:
        player: Player name.
        stats: Player's stats dict with keys: win_rate, tie_rate, opponent_count, matches
        all_stats: Stats for all players (for normalization).
        output_path: Path to save the PNG.
        figsize: Figure size.
    """
    setup_style()

    # Calculate normalized values
    max_opponents = max(s.get("opponent_count", 1) for s in all_stats.values())
    max_matches = max(s.get("matches", 1) for s in all_stats.values())

    values = [
        stats.get("win_rate", 0.5),  # 0-1
        stats.get("tie_rate", 0),  # 0-1
        stats.get("opponent_count", 0) / max_opponents if max_opponents > 0 else 0,
        stats.get("matches", 0) / max_matches if max_matches > 0 else 0,
        abs(stats.get("win_rate", 0.5) - 0.5) * 2,  # Dominance: 0-1
    ]

    categories = [
        "Win Rate",
        "Tie Rate",
        "Rivales",
        "Partidas",
        "Dominancia",
    ]

    # Create radar chart
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    values_plot = values + [values[0]]  # Complete the circle
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))
    ax.set_facecolor("#16213e")

    # Plot and fill
    ax.plot(angles, values_plot, "o-", linewidth=3, color="#e94560", markersize=10)
    ax.fill(angles, values_plot, alpha=0.25, color="#e94560")

    # Set labels with larger font
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=18, fontweight="bold")
    ax.set_ylim(0, 1)

    # Add percentage labels with larger font
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["25%", "50%", "75%", "100%"], size=14, color="gray")

    ax.set_title(player, fontsize=24, fontweight="bold", pad=30)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()


def plot_player_radar_batch(
    players: List[str],
    all_stats: Dict[str, Dict],
    output_path: Path,
    cols: int = 3,
    figsize_per_player: tuple = (4, 4),
) -> None:
    """Plot radar charts for multiple players in a grid.

    Args:
        players: List of player names.
        all_stats: Stats for all players.
        output_path: Path to save the PNG.
        cols: Number of columns in the grid.
        figsize_per_player: Figure size per player subplot.
    """
    setup_style()

    # Calculate grid dimensions
    rows = math.ceil(len(players) / cols)
    fig_width = cols * figsize_per_player[0]
    fig_height = rows * figsize_per_player[1]

    fig, axes = plt.subplots(
        rows,
        cols,
        figsize=(fig_width, fig_height),
        subplot_kw=dict(polar=True),
    )

    # Flatten axes array
    if rows == 1 and cols == 1:
        axes = np.array([axes])
    axes = axes.flatten()

    # Hide extra subplots
    for ax in axes[len(players) :]:
        ax.set_visible(False)

    # Normalization factors
    max_opponents = max(s.get("opponent_count", 1) for s in all_stats.values())
    max_matches = max(s.get("matches", 1) for s in all_stats.values())

    categories = [
        "Win Rate",
        "Tie Rate",
        "Rivales",
        "Partidas",
        "Dominancia",
    ]
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles_plot = angles + angles[:1]

    # Color palette
    colors = plt.cm.Set2(np.linspace(0, 1, len(players)))

    for idx, player in enumerate(players):
        ax = axes[idx]
        ax.set_facecolor("#16213e")

        stats = all_stats.get(player, {})
        values = [
            stats.get("win_rate", 0.5),
            stats.get("tie_rate", 0),
            stats.get("opponent_count", 0) / max_opponents if max_opponents > 0 else 0,
            stats.get("matches", 0) / max_matches if max_matches > 0 else 0,
            abs(stats.get("win_rate", 0.5) - 0.5) * 2,
        ]
        values_plot = values + [values[0]]

        ax.plot(angles_plot, values_plot, "o-", linewidth=2, color=colors[idx])
        ax.fill(angles_plot, values_plot, alpha=0.25, color=colors[idx])

        ax.set_xticks(angles)
        ax.set_xticklabels(categories, size=8)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.5, 1.0])
        ax.set_yticklabels(["50%", "100%"], size=7, color="gray")

        ax.set_title(player, fontsize=11, fontweight="bold", pad=10)

    fig.suptitle(
        "Perfiles de Jugadores",
        fontsize=16,
        fontweight="bold",
        y=1.02,
    )

    plt.tight_layout()
    plt.savefig(
        output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor()
    )
    plt.close()


def generate_all_radar_pages(
    all_stats: Dict[str, Dict],
    output_dir: Path,
    players_per_page: int = 6,
    min_matches: int = 5,
) -> List[Path]:
    """Generate paginated radar chart images for all players.

    Args:
        all_stats: Stats for all players.
        output_dir: Directory to save images.
        players_per_page: Number of players per page.
        min_matches: Minimum matches to include a player.

    Returns:
        List of output file paths.
    """
    # Filter and sort players
    qualified_players = [
        p for p, s in all_stats.items() if s.get("matches", 0) >= min_matches
    ]
    qualified_players.sort(key=lambda p: all_stats[p].get("win_rate", 0), reverse=True)

    output_paths = []
    for i in range(0, len(qualified_players), players_per_page):
        page_num = (i // players_per_page) + 1
        page_players = qualified_players[i : i + players_per_page]

        output_path = output_dir / f"radar-jugadores-{page_num:02d}.png"
        plot_player_radar_batch(page_players, all_stats, output_path)
        output_paths.append(output_path)

    return output_paths
