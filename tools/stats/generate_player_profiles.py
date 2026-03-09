#!/usr/bin/env python3
"""Generate individual player profile data and visualizations."""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict

from fabco_stats.data import TournamentFetcher, NicknameNormalizer, Match, Tournament
from fabco_stats.stats import calculate_elo, get_elo_history
from fabco_stats.stats.winrate import get_all_player_stats, build_h2h_matrix
from fabco_stats.viz.radar import plot_player_radar

# Paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
OUTPUT_DIR = SCRIPT_DIR / "output"


def get_quarter(date: datetime) -> str:
    """Get quarter string from date (e.g., 'Q1', 'Q2')."""
    quarter = (date.month - 1) // 3 + 1
    return f"Q{quarter}"


def filter_tournaments_by_year(tournaments: List[Tournament], year: int) -> List[Tournament]:
    """Filter tournaments by year."""
    return [t for t in tournaments if t.date.year == year]


def filter_tournaments_by_quarter(tournaments: List[Tournament], year: int, quarter: int) -> List[Tournament]:
    """Filter tournaments by year and quarter."""
    start_month = (quarter - 1) * 3 + 1
    end_month = start_month + 2
    return [
        t for t in tournaments
        if t.date.year == year and start_month <= t.date.month <= end_month
    ]


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


def get_player_matches(matches: List[Match], player: str) -> List[Match]:
    """Get all matches involving a player."""
    return [m for m in matches if m.player1 == player or m.player2 == player]


def calculate_h2h_record(matches: List[Match], player: str) -> Dict[str, Dict]:
    """Calculate head-to-head record against each opponent."""
    h2h = defaultdict(lambda: {"wins": 0, "losses": 0, "ties": 0})

    for m in matches:
        if m.player1 == player:
            opponent = m.player2
            if m.winner == player:
                h2h[opponent]["wins"] += 1
            elif m.winner == opponent:
                h2h[opponent]["losses"] += 1
            else:
                h2h[opponent]["ties"] += 1
        elif m.player2 == player:
            opponent = m.player1
            if m.winner == player:
                h2h[opponent]["wins"] += 1
            elif m.winner == opponent:
                h2h[opponent]["losses"] += 1
            else:
                h2h[opponent]["ties"] += 1

    return dict(h2h)


def get_player_elo_history(elo_history: Dict, player: str) -> List[Dict]:
    """Get ELO history for a specific player."""
    if player not in elo_history:
        return []

    history = []
    for date, elo in elo_history[player]:
        history.append({
            "date": date.isoformat() if hasattr(date, 'isoformat') else str(date),
            "elo": round(elo, 1)
        })
    return history


def calculate_quarterly_rivals(
    h2h: Dict[str, Dict],
    quarterly_h2h: Dict[str, Dict[str, Dict]],
    qualified_players: List[str]
) -> Dict[str, List[Dict]]:
    """
    Calculate rival triplets per quarter.
    Rivals are the players with worst matchup (who beat the player most).
    Only includes qualified players (30%+ participation).
    """
    quarterly_rivals = {}
    qualified_set = set(qualified_players)

    for quarter, q_h2h in quarterly_h2h.items():
        rivals = []
        for opponent, record in q_h2h.items():
            # Only include qualified players as rivals
            if opponent not in qualified_set:
                continue

            total = record["wins"] + record["losses"] + record["ties"]
            if total >= 1:  # At least 1 match
                win_rate = record["wins"] / total if total > 0 else 0
                rivals.append({
                    "opponent": opponent,
                    "wins": record["wins"],
                    "losses": record["losses"],
                    "ties": record["ties"],
                    "win_rate": round(win_rate, 3),
                    "total_matches": total,
                })

        # Sort by win_rate (ascending = worst matchups first), then by total matches
        rivals.sort(key=lambda x: (x["win_rate"], -x["total_matches"]))
        quarterly_rivals[quarter] = rivals[:3]  # Top 3 rivals (hardest to beat)

    return quarterly_rivals


def calculate_quarterly_h2h(matches: List[Match], player: str, year: int, all_tournaments: List[Tournament]) -> Dict[str, Dict[str, Dict]]:
    """Calculate H2H records per quarter."""
    quarterly_h2h = {}

    for q in range(1, 5):
        q_tournaments = filter_tournaments_by_quarter(all_tournaments, year, q)
        if not q_tournaments:
            continue

        q_matches = get_all_matches(q_tournaments)
        q_player_matches = get_player_matches(q_matches, player)

        if not q_player_matches:
            continue

        h2h = defaultdict(lambda: {"wins": 0, "losses": 0, "ties": 0})

        for m in q_player_matches:
            if m.player1 == player:
                opponent = m.player2
                if m.winner == player:
                    h2h[opponent]["wins"] += 1
                elif m.winner == opponent:
                    h2h[opponent]["losses"] += 1
                else:
                    h2h[opponent]["ties"] += 1
            elif m.player2 == player:
                opponent = m.player1
                if m.winner == player:
                    h2h[opponent]["wins"] += 1
                elif m.winner == opponent:
                    h2h[opponent]["losses"] += 1
                else:
                    h2h[opponent]["ties"] += 1

        quarterly_h2h[f"Q{q}"] = dict(h2h)

    return quarterly_h2h


def calculate_best_progress(quarterly_stats: Dict) -> Optional[Dict]:
    """
    Find the best improvement between consecutive quarters.
    Returns the quarter pair with the biggest win_rate improvement.
    """
    quarters = sorted([q for q in quarterly_stats.keys()])

    if len(quarters) < 2:
        return None

    best_progress = None
    best_improvement = -999

    for i in range(len(quarters) - 1):
        q_from = quarters[i]
        q_to = quarters[i + 1]

        wr_from = quarterly_stats[q_from].get("win_rate", 0)
        wr_to = quarterly_stats[q_to].get("win_rate", 0)
        improvement = wr_to - wr_from

        if improvement > best_improvement:
            best_improvement = improvement
            best_progress = {
                "from_quarter": q_from,
                "to_quarter": q_to,
                "from_win_rate": round(wr_from, 3),
                "to_win_rate": round(wr_to, 3),
                "improvement": round(improvement, 3),
                "improvement_pct": round(improvement * 100, 1),
            }

    return best_progress


# Medal definitions with icons (using CSS classes and Unicode symbols)
MEDAL_DEFINITIONS = {
    # Positive medals
    "titan": {
        "name": "Titan",
        "description": "Mas partidas jugadas",
        "icon": "trophy",
        "emoji": "🏆",
        "color": "#ffd700",
        "positive": True,
    },
    "inquebrantable": {
        "name": "Inquebrantable",
        "description": "Mayor tasa de victorias",
        "icon": "crown",
        "emoji": "👑",
        "color": "#ffd700",
        "positive": True,
    },
    "asistencia_perfecta": {
        "name": "Asistencia Perfecta",
        "description": "Mas torneos asistidos",
        "icon": "calendar-check",
        "emoji": "📅",
        "color": "#10b981",
        "positive": True,
    },
    "matador_gigantes": {
        "name": "Matador de Gigantes",
        "description": "Mejor record vs top ELO",
        "icon": "target",
        "emoji": "🎯",
        "color": "#ef4444",
        "positive": True,
    },
    "ascenso_meteorico": {
        "name": "Ascenso Meteorico",
        "description": "Mayor mejora entre trimestres",
        "icon": "rocket",
        "emoji": "🚀",
        "color": "#8b5cf6",
        "positive": True,
    },
    "coleccionista": {
        "name": "Coleccionista",
        "description": "Mas rivales unicos enfrentados",
        "icon": "users",
        "emoji": "👥",
        "color": "#3b82f6",
        "positive": True,
    },
    "constante": {
        "name": "El Constante",
        "description": "Rendimiento mas estable",
        "icon": "balance",
        "emoji": "⚖️",
        "color": "#06b6d4",
        "positive": True,
    },
    # Neutral/Funny medals
    "empatador": {
        "name": "El Empatador",
        "description": "Mayor tasa de empates",
        "icon": "handshake",
        "emoji": "🤝",
        "color": "#f59e0b",
        "positive": False,
    },
    "resiliente": {
        "name": "Resiliente",
        "description": "Sigue jugando a pesar de las derrotas",
        "icon": "heart",
        "emoji": "💪",
        "color": "#ec4899",
        "positive": True,
    },
    "veterano": {
        "name": "Veterano",
        "description": "Jugador experimentado con historia",
        "icon": "shield",
        "emoji": "🛡️",
        "color": "#6366f1",
        "positive": True,
    },
}


def calculate_player_medals(
    player: str,
    profile: Dict,
    all_profiles: List[Dict],
    elo_ratings: Dict,
    all_h2h: Dict[str, Dict],
) -> List[Dict]:
    """
    Calculate medals for a player based on standout statistics.
    Compare against all qualified players to determine medal winners.
    """
    medals = []

    # Get all player data for comparison
    all_matches = [p["matches"] for p in all_profiles if p.get("matches", 0) > 0]
    all_win_rates = [p["win_rate"] for p in all_profiles if p.get("win_rate", 0) > 0]
    all_tournaments = [p["tournaments"] for p in all_profiles if p.get("tournaments", 0) > 0]

    player_data = profile["summary"]
    player_matches = player_data.get("matches", 0)
    player_win_rate = player_data.get("win_rate", 0)
    player_tournaments = player_data.get("tournaments", 0)
    player_tie_rate = player_data.get("tie_rate", 0)
    player_opponents = player_data.get("opponent_count", 0)

    # Titan - Most matches played
    if all_matches and player_matches == max(all_matches):
        medals.append({**MEDAL_DEFINITIONS["titan"], "stat": f"{player_matches} partidas"})

    # Inquebrantable - Highest win rate
    if all_win_rates and player_win_rate == max(all_win_rates):
        medals.append({**MEDAL_DEFINITIONS["inquebrantable"], "stat": f"{round(player_win_rate * 100)}% victorias"})

    # Asistencia Perfecta - Most tournaments attended
    if all_tournaments and player_tournaments == max(all_tournaments):
        medals.append({**MEDAL_DEFINITIONS["asistencia_perfecta"], "stat": f"{player_tournaments} torneos"})

    # Coleccionista - Most unique opponents
    all_opponents = [p.get("opponent_count", 0) for p in all_profiles if isinstance(p, dict)]
    # Get opponent count from profiles
    player_opponents_count = player_data.get("opponent_count", 0)
    if player_opponents_count > 0:
        max_opponents = max([prof["summary"].get("opponent_count", 0) for prof in [profile] + [p for p in all_profiles if "summary" in p]], default=0)
        if player_opponents_count >= max_opponents * 0.95:  # Within 5% of max
            medals.append({**MEDAL_DEFINITIONS["coleccionista"], "stat": f"{player_opponents_count} rivales"})

    # El Empatador - Highest tie rate (must have significant ties)
    if player_tie_rate >= 0.05:  # At least 5% tie rate
        all_tie_rates = [p.get("tie_rate", 0) for p in all_profiles if isinstance(p, dict)]
        if all_tie_rates:
            # Need to calculate from profiles
            tie_rates_full = []
            for prof in [profile]:
                tr = prof["summary"].get("tie_rate", 0)
                if tr > 0:
                    tie_rates_full.append(tr)
            if tie_rates_full and player_tie_rate == max(tie_rates_full, default=0):
                medals.append({**MEDAL_DEFINITIONS["empatador"], "stat": f"{round(player_tie_rate * 100)}% empates"})

    # Ascenso Meteorico - Best quarterly improvement
    best_progress = profile.get("best_progress")
    if best_progress and best_progress.get("improvement", 0) > 0.10:  # More than 10% improvement
        medals.append({
            **MEDAL_DEFINITIONS["ascenso_meteorico"],
            "stat": f"+{best_progress['improvement_pct']}% ({best_progress['from_quarter']}→{best_progress['to_quarter']})"
        })

    # Matador de Gigantes - Beat top players
    top_elo_players = sorted(elo_ratings.items(), key=lambda x: x[1], reverse=True)[:3]
    top_names = [p[0] for p in top_elo_players]

    if player not in top_names:  # Only for non-top players
        giant_slayer_score = 0
        giant_slayer_wins = 0
        h2h = profile.get("h2h", {})
        for top_player in top_names:
            if top_player in h2h:
                record = h2h[top_player]
                if record["wins"] > record["losses"]:
                    giant_slayer_score += 1
                    giant_slayer_wins += record["wins"]

        if giant_slayer_score >= 2:  # Beat at least 2 of top 3
            medals.append({
                **MEDAL_DEFINITIONS["matador_gigantes"],
                "stat": f"{giant_slayer_wins} victorias vs top 3"
            })

    # Resiliente - High match count despite low win rate
    if player_win_rate < 0.45 and player_matches >= sum(all_matches) / len(all_matches) * 0.8:
        medals.append({**MEDAL_DEFINITIONS["resiliente"], "stat": f"{player_matches} partidas, sigue adelante"})

    # Constante - Stable performance across quarters
    quarterly = profile.get("quarterly", {})
    if len(quarterly) >= 3:
        q_win_rates = [q.get("win_rate", 0) for q in quarterly.values() if q.get("matches", 0) >= 3]
        if len(q_win_rates) >= 3:
            variance = sum((wr - sum(q_win_rates)/len(q_win_rates))**2 for wr in q_win_rates) / len(q_win_rates)
            if variance < 0.01:  # Very stable
                medals.append({**MEDAL_DEFINITIONS["constante"], "stat": f"±{round(variance**0.5 * 100, 1)}%"})

    # Veterano - Experienced player (many matches + many opponents)
    if player_matches >= sum(all_matches) / len(all_matches) * 1.2 and player_opponents_count >= 10:
        if not any(m["name"] == "Titan" for m in medals):  # Don't double-award
            medals.append({**MEDAL_DEFINITIONS["veterano"], "stat": f"{player_matches} partidas, {player_opponents_count} rivales"})

    return medals


def generate_player_profile(
    player: str,
    all_tournaments: List[Tournament],
    year: int,
    all_stats: Dict,
    elo_ratings: Dict,
    elo_history: Dict,
    output_dir: Path,
    qualified_players: List[str],
) -> Dict:
    """Generate complete profile data for a player."""

    # Filter tournaments for this year
    year_tournaments = filter_tournaments_by_year(all_tournaments, year)
    year_matches = get_all_matches(year_tournaments)
    player_matches = get_player_matches(year_matches, player)

    # Calculate tournament participation
    tournament_counts = get_player_tournament_counts(year_tournaments)
    player_tournaments = tournament_counts.get(player, 0)

    # Player stats
    stats = all_stats.get(player, {})

    # Head-to-head records
    h2h = calculate_h2h_record(player_matches, player)

    # Sort H2H by total matches
    h2h_sorted = sorted(
        h2h.items(),
        key=lambda x: x[1]["wins"] + x[1]["losses"] + x[1]["ties"],
        reverse=True
    )

    # Calculate quarterly stats
    quarterly_stats = {}
    for q in range(1, 5):
        q_tournaments = filter_tournaments_by_quarter(all_tournaments, year, q)
        if not q_tournaments:
            continue

        q_matches = get_all_matches(q_tournaments)
        q_player_matches = get_player_matches(q_matches, player)

        if not q_player_matches:
            continue

        q_tournament_counts = get_player_tournament_counts(q_tournaments)

        wins = sum(1 for m in q_player_matches if m.winner == player)
        losses = sum(1 for m in q_player_matches if m.winner and m.winner != player)
        ties = sum(1 for m in q_player_matches if m.winner is None)

        quarterly_stats[f"Q{q}"] = {
            "tournaments": q_tournament_counts.get(player, 0),
            "matches": len(q_player_matches),
            "wins": wins,
            "losses": losses,
            "ties": ties,
            "win_rate": round(wins / len(q_player_matches), 3) if q_player_matches else 0,
        }

    # ELO history for this player
    player_elo_history = get_player_elo_history(elo_history, player)

    # Best/Worst matchups (only against qualified players)
    best_matchups = []
    worst_matchups = []
    qualified_set = set(qualified_players)

    for opponent, record in h2h_sorted:
        # Only include qualified players in matchup analysis
        if opponent not in qualified_set:
            continue

        total = record["wins"] + record["losses"] + record["ties"]
        if total >= 2:  # Minimum 2 matches for meaningful matchup
            win_rate = record["wins"] / total if total > 0 else 0
            matchup_data = {
                "opponent": opponent,
                "wins": record["wins"],
                "losses": record["losses"],
                "ties": record["ties"],
                "win_rate": round(win_rate, 3),
            }
            if win_rate >= 0.6:
                best_matchups.append(matchup_data)
            elif win_rate <= 0.4:
                worst_matchups.append(matchup_data)

    # Sort matchups
    best_matchups.sort(key=lambda x: x["win_rate"], reverse=True)
    worst_matchups.sort(key=lambda x: x["win_rate"])

    # Calculate quarterly H2H for rival triplets
    quarterly_h2h = calculate_quarterly_h2h(player_matches, player, year, all_tournaments)
    quarterly_rivals = calculate_quarterly_rivals(h2h, quarterly_h2h, qualified_players)

    # Calculate best progress between quarters
    best_progress = calculate_best_progress(quarterly_stats)

    profile = {
        "player": player,
        "year": year,
        "summary": {
            "elo": round(elo_ratings.get(player, 1500), 1),
            "tournaments": player_tournaments,
            "matches": stats.get("matches", 0),
            "wins": stats.get("wins", 0),
            "losses": stats.get("losses", 0),
            "ties": stats.get("ties", 0),
            "win_rate": round(stats.get("win_rate", 0.5), 3),
            "tie_rate": round(stats.get("tie_rate", 0), 3),
            "opponent_count": stats.get("opponent_count", 0),
        },
        "quarterly": quarterly_stats,
        "quarterly_rivals": quarterly_rivals,
        "best_progress": best_progress,
        "h2h": {opp: rec for opp, rec in h2h_sorted[:15]},  # Top 15 opponents
        "best_matchups": best_matchups[:5],
        "worst_matchups": worst_matchups[:5],
        "elo_history": player_elo_history,
        "radar_values": {
            "win_rate": round(stats.get("win_rate", 0.5), 3),
            "tie_rate": round(stats.get("tie_rate", 0), 3),
            "opponents_normalized": round(stats.get("opponent_count", 0) / max(s.get("opponent_count", 1) for s in all_stats.values()), 3),
            "matches_normalized": round(stats.get("matches", 0) / max(s.get("matches", 1) for s in all_stats.values()), 3),
            "dominance": round(abs(stats.get("win_rate", 0.5) - 0.5) * 2, 3),
        }
    }

    return profile


def main():
    print("Loading tournament data...")

    normalizer = NicknameNormalizer(DATA_DIR / "nicknames.json")
    fetcher = TournamentFetcher(None, RAW_DIR, normalizer)
    all_tournaments = fetcher.load_all_cached()

    print(f"Loaded {len(all_tournaments)} tournaments")

    min_participation_pct = 0.30

    for year in [2025, 2026]:
        print(f"\n{'='*50}")
        print(f"Generating Player Profiles for {year}")
        print(f"{'='*50}")

        year_tournaments = filter_tournaments_by_year(all_tournaments, year)
        if not year_tournaments:
            print(f"No tournaments found for {year}")
            continue

        year_matches = get_all_matches(year_tournaments)
        tournament_counts = get_player_tournament_counts(year_tournaments)
        min_tournaments = max(1, int(len(year_tournaments) * min_participation_pct))

        print(f"Tournaments: {len(year_tournaments)}")
        print(f"Minimum participation: {min_tournaments} tournaments ({min_participation_pct*100:.0f}%)")

        # Calculate stats
        elo_ratings = calculate_elo(year_matches)
        elo_history = get_elo_history(year_matches)
        player_stats = get_all_player_stats(year_matches)

        # Add tournament counts to player stats
        for player in player_stats:
            player_stats[player]["tournaments"] = tournament_counts.get(player, 0)

        # Get qualified players
        qualified = [
            p for p, s in player_stats.items()
            if tournament_counts.get(p, 0) >= min_tournaments
        ]

        print(f"Qualified players: {len(qualified)}")

        # Create output directory
        output_dir = OUTPUT_DIR / str(year) / "players"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate profiles (first pass - basic data)
        profiles_data = {}
        all_profiles_summary = []

        for player in qualified:
            print(f"  Generating profile for {player}...")

            profile = generate_player_profile(
                player,
                all_tournaments,
                year,
                player_stats,
                elo_ratings,
                elo_history,
                output_dir,
                qualified,
            )
            profiles_data[player] = profile

            all_profiles_summary.append({
                "player": player,
                "slug": player.lower().replace(" ", "-"),
                "elo": profile["summary"]["elo"],
                "matches": profile["summary"]["matches"],
                "tournaments": profile["summary"]["tournaments"],
                "win_rate": profile["summary"]["win_rate"],
                "tie_rate": profile["summary"]["tie_rate"],
                "opponent_count": profile["summary"]["opponent_count"],
                "summary": profile["summary"],
            })

        # Second pass - calculate medals (needs comparison across all players)
        print("  Calculating medals...")
        all_h2h = {p: profiles_data[p].get("h2h", {}) for p in qualified}

        for player in qualified:
            profile = profiles_data[player]
            medals = calculate_player_medals(
                player,
                profile,
                all_profiles_summary,
                elo_ratings,
                all_h2h,
            )
            profile["medals"] = medals

            # Save individual player JSON
            player_slug = player.lower().replace(" ", "-")
            with open(output_dir / f"{player_slug}.json", "w") as f:
                json.dump(profile, f, indent=2, ensure_ascii=False, default=str)

            # Generate individual radar chart
            plot_player_radar(
                player,
                player_stats[player],
                player_stats,
                output_dir / f"{player_slug}-radar.png",
            )

        # Prepare final profiles list for index
        all_profiles = []
        for p in all_profiles_summary:
            all_profiles.append({
                "player": p["player"],
                "slug": p["slug"],
                "elo": p["elo"],
                "matches": p["matches"],
                "tournaments": p["tournaments"],
                "win_rate": p["win_rate"],
                "medals": [m["name"] for m in profiles_data[p["player"]].get("medals", [])],
            })

        # Sort by ELO
        all_profiles.sort(key=lambda x: x["elo"], reverse=True)

        # Save players index
        with open(output_dir / "index.json", "w") as f:
            json.dump({
                "year": year,
                "min_tournaments": min_tournaments,
                "players": all_profiles,
            }, f, indent=2, ensure_ascii=False)

        print(f"Generated {len(qualified)} player profiles")

    print("\n" + "=" * 50)
    print("All player profiles generated!")
    print("=" * 50)


if __name__ == "__main__":
    main()
