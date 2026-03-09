#!/usr/bin/env python3
"""
FABCO Tournament Statistics CLI

Command-line tool for fetching, analyzing, and visualizing
Flesh and Blood tournament data from Challonge.

Usage:
    python cli.py fetch --start 2024-11-01 --end 2025-04-15
    python cli.py analyze
    python cli.py viz
    python cli.py report --quarter Q1-2025
    python cli.py all --start DATE --end DATE
"""

import json
from datetime import date, datetime
from pathlib import Path
from typing import List

import click

# Package imports
from fabco_stats.api import ChallongeClient, get_valid_token, load_config
from fabco_stats.data import (
    Match,
    Tournament,
    TournamentFetcher,
    NicknameNormalizer,
    load_nicknames,
)
from fabco_stats.stats import (
    calculate_elo,
    get_elo_history,
    build_h2h_matrix,
    build_tie_rate_matrix,
    get_rivalries,
    calculate_streaks,
    get_top_streaks,
    get_top_tie_rates,
)
from fabco_stats.stats.winrate import get_all_player_stats
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


def ensure_dirs():
    """Ensure required directories exist."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_date(date_str: str) -> date:
    """Parse date string in YYYY-MM-DD format."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()


@click.group()
def cli():
    """FABCO Tournament Statistics CLI."""
    ensure_dirs()


@cli.command()
@click.option("--start", required=True, help="Start date (YYYY-MM-DD)")
@click.option("--end", required=True, help="End date (YYYY-MM-DD)")
@click.option("--no-cache", is_flag=True, help="Force re-fetch even if cached")
def fetch(start: str, end: str, no_cache: bool):
    """Fetch tournament data from Challonge API."""
    start_date = parse_date(start)
    end_date = parse_date(end)

    click.echo(f"Fetching tournaments from {start_date} to {end_date}...")

    # Get API token
    config = load_config()
    token = get_valid_token(config)
    if not token:
        click.echo("Failed to get API token. Run create_tournament.py --authorize first.")
        return

    # Create client and fetcher
    client = ChallongeClient(token, config.get("community_id", "fabtcgcolombia"))
    normalizer = NicknameNormalizer(DATA_DIR / "nicknames.json")
    fetcher = TournamentFetcher(client, RAW_DIR, normalizer)

    # Fetch tournaments
    tournaments = fetcher.fetch_all_tournaments(
        start_date=start_date,
        end_date=end_date,
        use_cache=not no_cache,
    )

    click.echo(f"\nFetched {len(tournaments)} tournaments")

    # Summary
    total_matches = sum(t.match_count for t in tournaments)
    total_participants = len(set(p for t in tournaments for p in t.participants))

    click.echo(f"Total matches: {total_matches}")
    click.echo(f"Unique players: {total_participants}")


@cli.command()
@click.option("--min-matches", default=5, help="Minimum matches for player inclusion")
def analyze(min_matches: int):
    """Run statistics calculations on cached data."""
    click.echo("Loading cached tournament data...")

    # Load from cache
    normalizer = NicknameNormalizer(DATA_DIR / "nicknames.json")
    fetcher = TournamentFetcher(None, RAW_DIR, normalizer)
    tournaments = fetcher.load_all_cached()

    if not tournaments:
        click.echo("No cached data found. Run 'fetch' first.")
        return

    click.echo(f"Loaded {len(tournaments)} tournaments")

    # Collect all matches
    all_matches: List[Match] = []
    for t in tournaments:
        all_matches.extend(t.matches)

    click.echo(f"Total matches: {len(all_matches)}")

    # Calculate statistics
    click.echo("\nCalculating ELO ratings...")
    elo_ratings = calculate_elo(all_matches)
    elo_history = get_elo_history(all_matches)

    click.echo("Building H2H matrix...")
    h2h_matrix = build_h2h_matrix(all_matches, min_matches=1)

    click.echo("Calculating player stats...")
    player_stats = get_all_player_stats(all_matches)

    click.echo("Calculating streaks...")
    streaks = calculate_streaks(all_matches)

    # Filter by minimum matches
    qualified_players = [
        p for p, s in player_stats.items() if s["matches"] >= min_matches
    ]
    click.echo(f"\nPlayers with {min_matches}+ matches: {len(qualified_players)}")

    # Save processed data
    processed_data = {
        "tournaments": len(tournaments),
        "total_matches": len(all_matches),
        "player_count": len(qualified_players),
        "elo_ratings": elo_ratings,
        "player_stats": {
            p: {k: v for k, v in s.items() if k != "opponents"}
            for p, s in player_stats.items()
        },
        "streaks": streaks,
        "date_range": {
            "start": min(t.date for t in tournaments).isoformat(),
            "end": max(t.date for t in tournaments).isoformat(),
        },
    }

    output_file = PROCESSED_DIR / "stats.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, indent=2, ensure_ascii=False, default=str)

    click.echo(f"\nStatistics saved to {output_file}")

    # Print top players
    click.echo("\nTop 10 ELO:")
    sorted_elo = sorted(elo_ratings.items(), key=lambda x: x[1], reverse=True)
    for i, (player, elo) in enumerate(sorted_elo[:10], 1):
        matches = player_stats.get(player, {}).get("matches", 0)
        click.echo(f"  {i}. {player}: {elo:.0f} ({matches} matches)")


@cli.command()
@click.option("--min-matches", default=5, help="Minimum matches for visualizations")
def viz(min_matches: int):
    """Generate all visualizations."""
    click.echo("Loading cached tournament data...")

    # Load from cache
    normalizer = NicknameNormalizer(DATA_DIR / "nicknames.json")
    fetcher = TournamentFetcher(None, RAW_DIR, normalizer)
    tournaments = fetcher.load_all_cached()

    if not tournaments:
        click.echo("No cached data found. Run 'fetch' first.")
        return

    # Collect all matches
    all_matches: List[Match] = []
    for t in tournaments:
        all_matches.extend(t.matches)

    click.echo(f"Loaded {len(all_matches)} matches from {len(tournaments)} tournaments")

    # Calculate all stats
    click.echo("\nCalculating statistics...")
    elo_ratings = calculate_elo(all_matches)
    elo_history = get_elo_history(all_matches)
    player_stats = get_all_player_stats(all_matches)

    # Filter players by minimum matches for matrices
    qualified = [p for p, s in player_stats.items() if s["matches"] >= min_matches]
    qualified_matches = [
        m for m in all_matches
        if m.player1 in qualified and m.player2 in qualified
    ]

    click.echo(f"Players with {min_matches}+ matches: {len(qualified)}")

    # Build matrices
    h2h_matrix = build_h2h_matrix(qualified_matches, min_matches=1)
    tie_matrix = build_tie_rate_matrix(qualified_matches, min_matches=1)

    # Generate visualizations
    click.echo("\nGenerating visualizations...")

    # Win rate matrix
    click.echo("  - Win rate matrix...")
    plot_winrate_matrix(h2h_matrix, OUTPUT_DIR / "matrix_winrate.png")

    # Rivalry matrix
    click.echo("  - Rivalry matrix...")
    plot_rivalry_matrix(h2h_matrix, OUTPUT_DIR / "matriz_rivalidades.png")

    # Tie rate matrix
    click.echo("  - Tie rate matrix...")
    plot_tierate_matrix(tie_matrix, OUTPUT_DIR / "matrix_tierate.png")

    # ELO timeline
    click.echo("  - ELO timeline...")
    plot_elo_timeline(elo_history, OUTPUT_DIR / "timeline-elo.png")

    # ELO ranking
    click.echo("  - ELO ranking...")
    # Filter by minimum matches for ranking
    qualified_elo = {p: e for p, e in elo_ratings.items() if player_stats.get(p, {}).get("matches", 0) >= min_matches}
    plot_elo_ranking(qualified_elo, OUTPUT_DIR / "ranking_elo.png")

    # Tournament participation
    click.echo("  - Tournament participation...")
    plot_tournament_participation(tournaments, OUTPUT_DIR / "evolucion_resultado_torneos.png")

    # Top streaks
    click.echo("  - Top streaks...")
    top_streaks = get_top_streaks(all_matches, limit=8)
    plot_top_streaks(top_streaks, OUTPUT_DIR / "top_winstreaks.png")

    # Top tie rates
    click.echo("  - Top tie rates...")
    top_ties = get_top_tie_rates(all_matches, min_matches=min_matches, limit=8)
    plot_top_ties(top_ties, OUTPUT_DIR / "top_8_empates.png")

    # Radar charts
    click.echo("  - Radar charts...")
    radar_paths = generate_all_radar_pages(
        player_stats,
        OUTPUT_DIR,
        players_per_page=6,
        min_matches=min_matches,
    )
    click.echo(f"    Generated {len(radar_paths)} radar chart pages")

    click.echo(f"\nVisualizations saved to {OUTPUT_DIR}")


@cli.command()
@click.option("--quarter", required=True, help="Quarter label (e.g., Q1-2025)")
def report(quarter: str):
    """Generate MDX blog post template."""
    # Load processed stats
    stats_file = PROCESSED_DIR / "stats.json"
    if not stats_file.exists():
        click.echo("No processed stats found. Run 'analyze' first.")
        return

    with open(stats_file, "r", encoding="utf-8") as f:
        stats = json.load(f)

    # Generate MDX template
    mdx_content = f'''---
title: "Análisis Competitivo de la Comunidad FAB - {quarter}"
description: "Exploración de la escena competitiva de Flesh and Blood en Colombia."
author: Aldturi + lots of IA
publishDate: {datetime.now().strftime("%Y-%m-%d")}
---

**Fechas de análisis:** {stats["date_range"]["start"]} al {stats["date_range"]["end"]}
**Torneos registrados:** {stats["tournaments"]}
**Partidas analizadas:** {stats["total_matches"]}
**Jugadores activos con más de 10 partidas:** {stats["player_count"]}

---

### Winrate y Enfrentamientos

![Winrate Matrix](/stats/{quarter}/matrix_winrate.png)

---

### Rivalidades

![Matriz Rivalidades](/stats/{quarter}/matriz_rivalidades.png)

---

### Tasa de Empates

![Top 8 Empates](/stats/{quarter}/top_8_empates.png)

---

### Top 8 Winstreaks

![Ranking ELO](/stats/{quarter}/ranking_elo.png)

---

### Radar Charts de Estilo de Juego

![Radar 01](/stats/{quarter}/radar-jugadores-01.png)

---

### Análisis ELO

![Evolución Resultado Torneos](/stats/{quarter}/evolucion_resultado_torneos.png)
![Timeline ELO](/stats/{quarter}/timeline-elo.png)
'''

    output_file = OUTPUT_DIR / f"stats{quarter.replace('-', '')}.mdx"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(mdx_content)

    click.echo(f"Report template saved to {output_file}")


@cli.command("all")
@click.option("--start", required=True, help="Start date (YYYY-MM-DD)")
@click.option("--end", required=True, help="End date (YYYY-MM-DD)")
@click.option("--min-matches", default=5, help="Minimum matches for inclusion")
@click.option("--no-cache", is_flag=True, help="Force re-fetch")
@click.pass_context
def run_all(ctx, start: str, end: str, min_matches: int, no_cache: bool):
    """Run full pipeline: fetch + analyze + viz."""
    click.echo("=" * 50)
    click.echo("FABCO Stats Pipeline")
    click.echo("=" * 50)

    # Fetch
    click.echo("\n[1/3] Fetching data...")
    ctx.invoke(fetch, start=start, end=end, no_cache=no_cache)

    # Analyze
    click.echo("\n[2/3] Analyzing data...")
    ctx.invoke(analyze, min_matches=min_matches)

    # Visualize
    click.echo("\n[3/3] Generating visualizations...")
    ctx.invoke(viz, min_matches=min_matches)

    click.echo("\n" + "=" * 50)
    click.echo("Pipeline complete!")
    click.echo("=" * 50)


@cli.command()
def list_cached():
    """List cached tournaments."""
    cache_files = list(RAW_DIR.glob("*.json"))
    if not cache_files:
        click.echo("No cached tournaments found.")
        return

    click.echo(f"Cached tournaments ({len(cache_files)}):\n")
    for f in sorted(cache_files):
        with open(f, "r", encoding="utf-8") as file:
            data = json.load(file)
            tournament = data.get("tournament", {})
            attrs = tournament.get("attributes", {})
            name = attrs.get("name", f.stem)
            date_str = attrs.get("starts_at", "Unknown date")[:10]
            matches = len(data.get("matches", []))
            click.echo(f"  {f.stem}: {name} ({date_str}) - {matches} matches")


if __name__ == "__main__":
    cli()
