"""Matrix visualizations for win rates and rivalries."""

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


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
    plt.rcParams["figure.dpi"] = 100


def plot_winrate_matrix(
    h2h: pd.DataFrame,
    output_path: Path,
    title: str = "Matriz de Winrate",
    figsize: tuple = (14, 12),
) -> None:
    """Plot head-to-head win rate heatmap.

    Args:
        h2h: DataFrame with players as rows/cols, values are win rates.
        output_path: Path to save the PNG.
        title: Plot title.
        figsize: Figure size (width, height).
    """
    setup_style()

    fig, ax = plt.subplots(figsize=figsize)

    # Create custom colormap (red -> white -> green)
    cmap = sns.diverging_palette(10, 130, as_cmap=True)

    # Plot heatmap
    mask = np.isnan(h2h.values)
    sns.heatmap(
        h2h,
        mask=mask,
        cmap=cmap,
        center=0.5,
        vmin=0,
        vmax=1,
        annot=True,
        fmt=".0%",
        linewidths=0.5,
        linecolor="#0f3460",
        cbar_kws={"label": "Win Rate", "shrink": 0.8},
        ax=ax,
    )

    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)
    ax.set_xlabel("Oponente", fontsize=12)
    ax.set_ylabel("Jugador", fontsize=12)

    # Rotate x labels
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()


def plot_rivalry_matrix(
    h2h: pd.DataFrame,
    output_path: Path,
    title: str = "Matriz de Rivalidades",
    figsize: tuple = (14, 12),
) -> None:
    """Plot rivalry matrix showing balanced vs dominated matchups.

    Colors:
    - Green: Balanced rivalry (40-60%)
    - Red/Blue: Dominated matchup (one player dominates)

    Args:
        h2h: DataFrame with players as rows/cols, values are win rates.
        output_path: Path to save the PNG.
        title: Plot title.
        figsize: Figure size (width, height).
    """
    setup_style()

    fig, ax = plt.subplots(figsize=figsize)

    # Create rivalry classification
    # Convert win rates to rivalry scores:
    # - Near 0.5 = balanced (green)
    # - Near 0 or 1 = dominated (red)
    rivalry_score = np.abs(h2h.values - 0.5)

    # Custom colormap (green for balanced, red for dominated)
    cmap = sns.diverging_palette(130, 10, as_cmap=True, center="light")

    mask = np.isnan(h2h.values)

    # Create annotation showing dominance
    def format_rivalry(val):
        if np.isnan(val):
            return ""
        if val > 0.6:
            return f"{val:.0%}"
        elif val < 0.4:
            return f"{val:.0%}"
        else:
            return f"{val:.0%}"

    annot = h2h.map(format_rivalry)

    sns.heatmap(
        rivalry_score,
        mask=mask,
        cmap=cmap,
        center=0.25,
        vmin=0,
        vmax=0.5,
        annot=annot,
        fmt="",
        linewidths=0.5,
        linecolor="#0f3460",
        cbar_kws={"label": "Desbalance", "shrink": 0.8},
        ax=ax,
        xticklabels=h2h.columns,
        yticklabels=h2h.index,
    )

    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)
    ax.set_xlabel("Oponente", fontsize=12)
    ax.set_ylabel("Jugador", fontsize=12)

    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)

    # Add legend text
    fig.text(
        0.5,
        0.02,
        "Verde = Rivalidad equilibrada (40-60%) | Rojo = Dominancia clara",
        ha="center",
        fontsize=10,
        style="italic",
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()


def plot_tierate_matrix(
    tierate: pd.DataFrame,
    output_path: Path,
    title: str = "Matriz de Tasa de Empates",
    figsize: tuple = (14, 12),
) -> None:
    """Plot tie rate matrix between players.

    Args:
        tierate: DataFrame with players as rows/cols, values are tie rates.
        output_path: Path to save the PNG.
        title: Plot title.
        figsize: Figure size (width, height).
    """
    setup_style()

    fig, ax = plt.subplots(figsize=figsize)

    # Use purple colormap for tie rates
    cmap = sns.color_palette("Purples", as_cmap=True)

    mask = np.isnan(tierate.values)
    sns.heatmap(
        tierate,
        mask=mask,
        cmap=cmap,
        vmin=0,
        vmax=1,
        annot=True,
        fmt=".0%",
        linewidths=0.5,
        linecolor="#0f3460",
        cbar_kws={"label": "Tie Rate", "shrink": 0.8},
        ax=ax,
    )

    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)
    ax.set_xlabel("Oponente", fontsize=12)
    ax.set_ylabel("Jugador", fontsize=12)

    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()


def plot_combined_winrate_tierate(
    winrate: pd.DataFrame,
    tierate: pd.DataFrame,
    output_path: Path,
    title: str = "Winrate + Tie Rate",
    figsize: tuple = (16, 14),
) -> None:
    """Plot combined winrate and tie rate visualization.

    Shows winrate as cell color and adds tie rate as text annotation.

    Args:
        winrate: Win rate DataFrame.
        tierate: Tie rate DataFrame.
        output_path: Path to save the PNG.
        title: Plot title.
        figsize: Figure size (width, height).
    """
    setup_style()

    fig, ax = plt.subplots(figsize=figsize)

    # Win rate colormap
    cmap = sns.diverging_palette(10, 130, as_cmap=True)

    mask = np.isnan(winrate.values)

    # Create combined annotations
    def format_combined(wr, tr):
        if np.isnan(wr):
            return ""
        if np.isnan(tr) or tr == 0:
            return f"{wr:.0%}"
        return f"W:{wr:.0%}\nT:{tr:.0%}"

    annot = np.vectorize(format_combined)(winrate.values, tierate.values)

    sns.heatmap(
        winrate,
        mask=mask,
        cmap=cmap,
        center=0.5,
        vmin=0,
        vmax=1,
        annot=annot,
        fmt="",
        linewidths=0.5,
        linecolor="#0f3460",
        cbar_kws={"label": "Win Rate", "shrink": 0.8},
        ax=ax,
        annot_kws={"size": 8},
    )

    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)
    ax.set_xlabel("Oponente", fontsize=12)
    ax.set_ylabel("Jugador", fontsize=12)

    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
