"""Checks that preserve real tournament accounting across the exported tables."""
import csv
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'public/data/calling-paris'
SPEC = importlib.util.spec_from_file_location('saved_results', ROOT / 'tools/stats/analyze_saved_results.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def records(name):
    with (DATA / f'{name}.csv').open(encoding='utf-8-sig') as stream:
        return list(csv.DictReader(stream))


class SavedResultsTests(unittest.TestCase):
    def test_daily_rates_reconcile_with_round_results(self):
        results = records('player-results')
        for hero in records('heroes'):
            for day, first, last in [('day1', 1, 9), ('day2', 10, 15)]:
                daily = [r for r in results if r['hero'] == hero['hero'] and first <= int(r['round']) <= last and r['placeholder_opponent'] == 'False']
                wins = sum(r['outcome'] == 'W' for r in daily)
                self.assertEqual(int(hero[f'{day}_matches']), len(daily))
                self.assertEqual(int(hero[f'{day}_players']), len({r['player'] for r in daily}))
                self.assertEqual(int(hero[f'{day}_wins']), wins)
                expected = MODULE.rate(wins, len(daily)-wins)
                self.assertEqual(hero[f'{day}_win_pct'], '' if expected is None else str(expected))
            for outcome in ('wins', 'losses', 'draws', 'matches'):
                self.assertEqual(int(hero[f'swiss_{outcome}']), int(hero[f'day1_{outcome}']) + int(hero[f'day2_{outcome}']))
        tek = next(h for h in records('heroes') if h['hero'].startswith('Teklovossen'))
        self.assertEqual(tek['day2_players'], '1')
        self.assertEqual(tek['day2_matches'], '6')
        self.assertEqual(tek['day2_win_pct'], '83.33')
        self.assertEqual(tek['day2_ci95_low'], '')
        self.assertEqual(tek['day2_ci_status'], 'insufficient_players')

    def test_bootstrap_preserves_player_clusters_and_handles_insufficient_data(self):
        concentrated = [{'player': p, 'outcome': outcome} for p, outcome in [('a', 'W'), ('b', 'L')] for _ in range(20)]
        dispersed = [{'player': str(p), 'outcome': 'W' if p < 10 else 'L'} for p in range(20) for _ in range(2)]
        low, high, count, status = MODULE.player_bootstrap(concentrated, 'test', 500)
        lo2, hi2, count2, _ = MODULE.player_bootstrap(dispersed, 'test', 500)
        self.assertEqual((count, count2), (2, 20))
        self.assertGreater(high-low, hi2-lo2, 'same game count, fewer player clusters means greater uncertainty here')
        self.assertEqual(MODULE.player_bootstrap(concentrated, 'test', 500), (low, high, count, status))
        self.assertEqual(MODULE.player_bootstrap(concentrated[:20], 'test')[:2], (None, None))
        self.assertEqual(MODULE.player_bootstrap([], 'test')[3], 'no_games')
        self.assertEqual(MODULE.player_bootstrap([{'player':'a','outcome':'W'},{'player':'b','outcome':'W'}], 'test')[3], 'no_between_player_variation')

    def test_special_outcomes(self):
        self.assertEqual([MODULE.outcome('Double Loss', side) for side in (1, 2)], ['L', 'L'])
        self.assertEqual([MODULE.outcome('Draw', side) for side in (1, 2)], ['D', 'D'])
        self.assertEqual(MODULE.rate(1, 1, 1), 33.33)
        self.assertIsNone(MODULE.rate(0, 0))

    def test_row_and_result_accounting(self):
        matches = records('matches')
        players = records('players')
        results = records('player-results')
        self.assertEqual(len(matches), 5181)
        self.assertEqual(len(players), 1418)
        placeholder_rows = sum(m['placeholder_opponent'] == 'True' for m in matches)
        self.assertEqual(placeholder_rows, 6)
        self.assertEqual(len(results), 2 * len(matches) - placeholder_rows)
        self.assertEqual(len({(r['player'], r['round']) for r in results}), len(results))
        contested = [r for r in results if r['placeholder_opponent'] == 'False']
        double_losses = sum(m['result'] == 'Double Loss' for m in matches)
        self.assertEqual(sum(r['outcome'] == 'L' for r in contested) - sum(r['outcome'] == 'W' for r in contested), 2 * double_losses)
        self.assertEqual(sum(int(p['all_wins']) for p in players), sum(r['outcome'] == 'W' for r in contested))
        self.assertEqual(sum(int(h['players']) for h in records('heroes')), len(players))

    def test_placeholder_and_missing_heroes_are_not_invented(self):
        players = {p['player']: p for p in records('players')}
        self.assertNotIn('Player 2', players)
        self.assertEqual(players['Ben Weinfeld']['placeholder_wins'], '1')
        audit = json.loads((DATA/'audit.json').read_text())
        self.assertEqual(len(audit['unknown_players']), 26)
        self.assertTrue(all(p['last_round'] == 1 and p['swiss_losses'] == 1 for p in audit['unknown_players']))
        self.assertTrue(all(m['hero'] != 'N/A' and m['opponent_hero'] != 'N/A' and m['hero'] != m['opponent_hero'] for m in records('matchups')))

    def test_elimination_and_matchup_reciprocity(self):
        players = records('players')
        self.assertEqual(sum(p['top8'] == 'True' for p in players), 8)
        self.assertEqual(sum(p['day2'] == 'True' for p in players), 128)
        self.assertEqual([p['player'] for p in players if p['finish'] == 'Champion'], ['Matt Muus'])
        matchups = {(m['hero'], m['opponent_hero']): m for m in records('matchups')}
        for (hero, opponent), m in matchups.items():
            reverse = matchups[(opponent, hero)]
            self.assertEqual(m['matches'], reverse['matches'])
            self.assertEqual(m['draws'], reverse['draws'])
            self.assertGreaterEqual(int(reverse['losses']), int(m['wins']))


if __name__ == '__main__':
    unittest.main()
