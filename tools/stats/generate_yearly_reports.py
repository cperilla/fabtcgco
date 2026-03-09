#!/usr/bin/env python3
"""Generate yearly statistics reports."""

import json
from datetime import datetime
from pathlib import Path
from typing import List

from fabco_stats.data import TournamentFetcher, NicknameNormalizer, Match, Tournament
from fabco_stats.stats import calculate_elo, get_elo_history
from fabco_stats.stats.winrate import (
    build_h2h_matrix,
    build_tie_rate_matrix,
    get_all_player_stats,
)
from fabco_stats.stats.streaks import get_top_streaks, get_top_tie_rates
from fabco_stats.viz import (
    plot_winrate_matrix,
    plot_rivalry_matrix,
    plot_tierate_matrix,
    plot_elo_timeline,
    plot_elo_ranking,
    plot_tournament_participation,
)
from fabco_stats.viz.timeline import plot_top_streaks, plot_top_ties
from fabco_stats.viz.radar import generate_all_radar_pages

# Paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = SCRIPT_DIR / "output"


def filter_tournaments_by_year(tournaments: List[Tournament], year: int) -> List[Tournament]:
    """Filter tournaments by year."""
    return [t for t in tournaments if t.date.year == year]


def get_all_matches(tournaments: List[Tournament]) -> List[Match]:
    """Get all matches from tournaments."""
    matches = []
    for t in tournaments:
        matches.extend(t.matches)
    return matches


def get_player_tournament_counts(tournaments: List[Tournament]) -> dict:
    """Count how many tournaments each player participated in."""
    counts = {}
    for t in tournaments:
        for player in t.participants:
            counts[player] = counts.get(player, 0) + 1
    return counts


def generate_report(tournaments: List[Tournament], year: int, min_participation_pct: float = 0.10):
    """Generate a full report for a given year.

    Args:
        tournaments: List of tournaments.
        year: Year for the report.
        min_participation_pct: Minimum participation percentage (0.10 = 10%).
    """
    output_dir = OUTPUT_DIR / str(year)
    output_dir.mkdir(parents=True, exist_ok=True)

    all_matches = get_all_matches(tournaments)

    print(f"\n{'='*50}")
    print(f"Generating {year} Report")
    print(f"{'='*50}")
    print(f"Tournaments: {len(tournaments)}")
    print(f"Matches: {len(all_matches)}")

    if not all_matches:
        print("No matches found for this year!")
        return

    # Calculate tournament participation
    tournament_counts = get_player_tournament_counts(tournaments)
    min_tournaments = max(1, int(len(tournaments) * min_participation_pct))
    print(f"Minimum participation: {min_tournaments} tournaments ({min_participation_pct*100:.0f}% of {len(tournaments)})")

    # Calculate all stats
    print("\nCalculating statistics...")
    elo_ratings = calculate_elo(all_matches)
    elo_history = get_elo_history(all_matches)
    player_stats = get_all_player_stats(all_matches)

    # Add tournament counts to player stats
    for player in player_stats:
        player_stats[player]["tournaments"] = tournament_counts.get(player, 0)

    # Filter players by minimum tournament participation
    qualified = [
        p for p, s in player_stats.items()
        if tournament_counts.get(p, 0) >= min_tournaments
    ]
    qualified_matches = [
        m for m in all_matches
        if m.player1 in qualified and m.player2 in qualified
    ]

    print(f"Players with {min_tournaments}+ tournaments: {len(qualified)}")

    # Build matrices
    h2h_matrix = build_h2h_matrix(qualified_matches, min_matches=1)
    tie_matrix = build_tie_rate_matrix(qualified_matches, min_matches=1)

    # Generate visualizations
    print("\nGenerating visualizations...")

    # Win rate matrix
    print("  - Win rate matrix...")
    plot_winrate_matrix(h2h_matrix, output_dir / "matrix_winrate.png")

    # Rivalry matrix
    print("  - Rivalry matrix...")
    plot_rivalry_matrix(h2h_matrix, output_dir / "matriz_rivalidades.png")

    # Tie rate matrix
    print("  - Tie rate matrix...")
    plot_tierate_matrix(tie_matrix, output_dir / "matrix_tierate.png")

    # ELO timeline
    print("  - ELO timeline...")
    plot_elo_timeline(elo_history, output_dir / "timeline-elo.png")

    # ELO ranking
    print("  - ELO ranking...")
    qualified_elo = {
        p: e for p, e in elo_ratings.items()
        if tournament_counts.get(p, 0) >= min_tournaments
    }
    plot_elo_ranking(qualified_elo, output_dir / "ranking_elo.png")

    # Tournament participation
    print("  - Tournament participation...")
    plot_tournament_participation(tournaments, output_dir / "evolucion_resultado_torneos.png")

    # Top streaks
    print("  - Top streaks...")
    top_streaks = get_top_streaks(all_matches, limit=8)
    plot_top_streaks(top_streaks, output_dir / "top_winstreaks.png")

    # Top tie rates - filter by qualified players
    print("  - Top tie rates...")
    qualified_matches_for_ties = [
        m for m in all_matches
        if m.player1 in qualified or m.player2 in qualified
    ]
    top_ties = get_top_tie_rates(qualified_matches_for_ties, min_matches=3, limit=8)
    # Filter to only qualified players
    top_ties = [(p, r, c) for p, r, c in top_ties if p in qualified][:8]
    plot_top_ties(top_ties, output_dir / "top_8_empates.png")

    # Radar charts - only qualified players
    print("  - Radar charts...")
    qualified_stats = {p: s for p, s in player_stats.items() if p in qualified}
    radar_paths = generate_all_radar_pages(
        qualified_stats,
        output_dir,
        players_per_page=6,
        min_matches=1,  # Already filtered by tournaments
    )
    print(f"    Generated {len(radar_paths)} radar chart pages")

    # Build top ELO list with only qualified players
    qualified_elo_list = [
        (p, e) for p, e in elo_ratings.items()
        if p in qualified
    ]
    qualified_elo_list.sort(key=lambda x: x[1], reverse=True)

    # Get total unique players
    all_players = set()
    for t in tournaments:
        all_players.update(t.participants)

    # Save stats JSON
    stats_data = {
        "year": year,
        "tournaments": len(tournaments),
        "total_matches": len(all_matches),
        "total_players": len(all_players),
        "qualified_players": len(qualified),
        "min_tournaments": min_tournaments,
        "date_range": {
            "start": min(t.date for t in tournaments).isoformat(),
            "end": max(t.date for t in tournaments).isoformat(),
        },
        "elo_ratings": {p: e for p, e in elo_ratings.items() if p in qualified},
        "top_elo": qualified_elo_list[:10],
        "player_stats": {
            p: {
                "matches": s["matches"],
                "wins": s["wins"],
                "losses": s["losses"],
                "ties": s["ties"],
                "win_rate": s["win_rate"],
                "tournaments": s.get("tournaments", 0),
            }
            for p, s in player_stats.items() if p in qualified
        },
    }
    with open(output_dir / "stats.json", "w") as f:
        json.dump(stats_data, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nOutput saved to: {output_dir}")

    # Print summary
    print(f"\n{year} Summary:")
    print(f"  Tournaments: {len(tournaments)}")
    print(f"  Matches: {len(all_matches)}")
    print(f"  Qualified Players: {len(qualified)} (min {min_tournaments} tournaments)")
    print("\n  Top 10 ELO:")
    for i, (player, elo) in enumerate(qualified_elo_list[:10], 1):
        matches = player_stats.get(player, {}).get("matches", 0)
        tourneys = tournament_counts.get(player, 0)
        print(f"    {i}. {player}: {elo:.0f} ({matches} matches, {tourneys} tournaments)")


def main():
    print("Loading tournament data...")

    normalizer = NicknameNormalizer(DATA_DIR / "nicknames.json")
    fetcher = TournamentFetcher(None, RAW_DIR, normalizer)
    all_tournaments = fetcher.load_all_cached()

    print(f"Loaded {len(all_tournaments)} tournaments")

    # Generate reports for 2025 and 2026
    # Minimum 10% tournament participation required
    for year in [2025, 2026]:
        year_tournaments = filter_tournaments_by_year(all_tournaments, year)
        if year_tournaments:
            generate_report(year_tournaments, year, min_participation_pct=0.30)
        else:
            print(f"\nNo tournaments found for {year}")

    print("\n" + "=" * 50)
    print("All reports generated!")
    print("=" * 50)


if __name__ == "__main__":
    main()
