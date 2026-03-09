"""Timeline and ranking visualizations."""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

from ..data.models import Tournament


def setup_style():
    """Set up matplotlib style for consistent visualizations."""
    plt.style.use("seaborn-v0_8-darkgrid")
    plt.rcParams["figure.facecolor"] = "#1a1a2e"
    plt.rcParams["axes.facecolor"] = "#16213e"
    plt.rcParams["text.color"] = "white"
    plt.rcParams["axes.labelcolor"] = "white"
    plt.rcParams["xtick.color"] = "white"
    plt.rcParams["ytick.color"] = "white"
    plt.rcParams["axes.edgecolor"] = "#0f3460"
    plt.rcParams["grid.color"] = "#0f3460"


def plot_elo_timeline(
    elo_history: Dict[str, List[Tuple[datetime, float]]],
    output_path: Path,
    top_n: int = 10,
    title: str = "Evolución ELO",
    figsize: tuple = (14, 8),
) -> None:
    """Plot ELO rating evolution over time.

    Args:
        elo_history: Dict mapping player names to list of (date, elo) tuples.
        output_path: Path to save the PNG.
        top_n: Number of top players to show.
        title: Plot title.
        figsize: Figure size.
    """
    setup_style()

    fig, ax = plt.subplots(figsize=figsize)

    # Get top players by final ELO
    final_elos = {p: history[-1][1] for p, history in elo_history.items() if history}
    top_players = sorted(final_elos.keys(), key=lambda p: final_elos[p], reverse=True)[
        :top_n
    ]

    # Color palette
    colors = plt.cm.tab10(np.linspace(0, 1, len(top_players)))

    for idx, player in enumerate(top_players):
        history = elo_history[player]
        dates = [h[0] for h in history]
        elos = [h[1] for h in history]

        ax.plot(
            dates,
            elos,
            "o-",
            label=f"{player} ({elos[-1]:.0f})",
            color=colors[idx],
            linewidth=2,
            markersize=4,
        )

    # Formatting
    ax.set_xlabel("Fecha", fontsize=12)
    ax.set_ylabel("ELO", fontsize=12)
    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)

    # Date formatting
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=45, ha="right")

    # Add baseline
    ax.axhline(y=1500, color="gray", linestyle="--", alpha=0.5, label="Baseline (1500)")

    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()


def plot_elo_ranking(
    elo_ratings: Dict[str, float],
    output_path: Path,
    top_n: int = 15,
    title: str = "Ranking ELO",
    figsize: tuple = (12, 8),
) -> None:
    """Plot bar chart of ELO rankings.

    Args:
        elo_ratings: Dict mapping player names to ELO ratings.
        output_path: Path to save the PNG.
        top_n: Number of top players to show.
        title: Plot title.
        figsize: Figure size.
    """
    setup_style()

    fig, ax = plt.subplots(figsize=figsize)

    # Sort and get top players
    sorted_ratings = sorted(elo_ratings.items(), key=lambda x: x[1], reverse=True)[
        :top_n
    ]
    players = [p for p, _ in sorted_ratings]
    elos = [e for _, e in sorted_ratings]

    # Create horizontal bar chart
    y_pos = np.arange(len(players))
    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(players)))[::-1]

    bars = ax.barh(y_pos, elos, color=colors, edgecolor="#0f3460")

    # Add value labels
    for idx, (player, elo) in enumerate(sorted_ratings):
        ax.text(elo + 5, idx, f"{elo:.0f}", va="center", fontsize=10)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(players)
    ax.invert_yaxis()  # Top player at top
    ax.set_xlabel("ELO", fontsize=12)
    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)

    # Set x limits
    min_elo = min(elos) - 50
    max_elo = max(elos) + 80
    ax.set_xlim(min_elo, max_elo)

    # Add baseline
    ax.axvline(x=1500, color="gray", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()


def plot_tournament_participation(
    tournaments: List[Tournament],
    output_path: Path,
    title: str = "Participación por Torneo",
    figsize: tuple = (14, 6),
) -> None:
    """Plot bar chart of tournament participation.

    Args:
        tournaments: List of tournaments.
        output_path: Path to save the PNG.
        title: Plot title.
        figsize: Figure size.
    """
    setup_style()

    fig, ax = plt.subplots(figsize=figsize)

    # Sort tournaments by date
    sorted_tournaments = sorted(tournaments, key=lambda t: t.date)

    # Extract data
    labels = [t.date.strftime("%m/%d") for t in sorted_tournaments]
    participants = [t.participant_count for t in sorted_tournaments]
    matches = [t.match_count for t in sorted_tournaments]

    x = np.arange(len(labels))
    width = 0.35

    # Create bars
    bars1 = ax.bar(
        x - width / 2,
        participants,
        width,
        label="Participantes",
        color="#e94560",
        edgecolor="#0f3460",
    )
    bars2 = ax.bar(
        x + width / 2,
        matches,
        width,
        label="Partidas",
        color="#0f3460",
        edgecolor="#e94560",
    )

    # Add value labels
    ax.bar_label(bars1, padding=3, fontsize=8)
    ax.bar_label(bars2, padding=3, fontsize=8)

    ax.set_xlabel("Fecha del Torneo", fontsize=12)
    ax.set_ylabel("Cantidad", fontsize=12)
    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()


def plot_top_streaks(
    streaks: List[Tuple[str, int]],
    output_path: Path,
    title: str = "Top Winstreaks",
    figsize: tuple = (10, 6),
) -> None:
    """Plot bar chart of top win streaks.

    Args:
        streaks: List of (player_name, streak_length) tuples.
        output_path: Path to save the PNG.
        title: Plot title.
        figsize: Figure size.
    """
    setup_style()

    fig, ax = plt.subplots(figsize=figsize)

    players = [s[0] for s in streaks]
    streak_values = [s[1] for s in streaks]

    y_pos = np.arange(len(players))
    colors = plt.cm.YlOrRd(np.linspace(0.3, 0.9, len(players)))[::-1]

    bars = ax.barh(y_pos, streak_values, color=colors, edgecolor="#0f3460")

    # Add value labels
    for idx, streak in enumerate(streak_values):
        ax.text(streak + 0.1, idx, str(streak), va="center", fontsize=11, fontweight="bold")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(players)
    ax.invert_yaxis()
    ax.set_xlabel("Victorias Consecutivas", fontsize=12)
    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)

    ax.set_xlim(0, max(streak_values) + 2)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()


def plot_top_ties(
    ties: List[Tuple[str, float, int]],
    output_path: Path,
    title: str = "Top 8 Tasa de Empates",
    figsize: tuple = (10, 6),
) -> None:
    """Plot bar chart of top tie rates.

    Args:
        ties: List of (player_name, tie_rate, match_count) tuples.
        output_path: Path to save the PNG.
        title: Plot title.
        figsize: Figure size.
    """
    setup_style()

    fig, ax = plt.subplots(figsize=figsize)

    players = [f"{t[0]} ({t[2]} partidas)" for t in ties]
    tie_rates = [t[1] * 100 for t in ties]  # Convert to percentage

    y_pos = np.arange(len(players))
    colors = plt.cm.Purples(np.linspace(0.4, 0.9, len(players)))[::-1]

    bars = ax.barh(y_pos, tie_rates, color=colors, edgecolor="#0f3460")

    # Add value labels
    for idx, rate in enumerate(tie_rates):
        ax.text(rate + 0.5, idx, f"{rate:.1f}%", va="center", fontsize=10)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(players)
    ax.invert_yaxis()
    ax.set_xlabel("Tasa de Empates (%)", fontsize=12)
    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)

    ax.set_xlim(0, max(tie_rates) + 10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
