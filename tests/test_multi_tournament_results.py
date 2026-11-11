"""Cross-format accounting and source coverage for the added Paris tournaments."""
import csv
import json
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / 'public/data'


def rows(event, filename):
    with (DATA/event/f'{filename}.csv').open(encoding='utf-8-sig') as stream:
        return list(csv.DictReader(stream))


class MultiTournamentTests(unittest.TestCase):
    def test_worlds_draft_only_contributes_to_players(self):
        event = 'world-championship-paris-2026'
        results = rows(event,'player-results')
        heroes = rows(event,'heroes')
        players = rows(event,'players')
        swiss = [r for r in results if r['phase']=='Swiss' and r['placeholder_opponent']=='False']
        constructed = [r for r in swiss if r['format']=='Classic Constructed']
        draft = [r for r in swiss if r['format']=='Booster Draft']
        self.assertTrue(draft)
        self.assertEqual({int(r['round']) for r in draft},set(range(6,12)))
        self.assertEqual(sum(int(h['swiss_matches']) for h in heroes),len(constructed))
        self.assertEqual(sum(int(p['swiss_matches']) for p in players),len(constructed)+len(draft))
        self.assertEqual(sum(int(p['draft_wins']) for p in players),sum(r['outcome']=='W' for r in draft))
        for hero in heroes:
            for period, rounds in [('day1',set(range(1,6))),('day2',set(range(12,17)))]:
                matches = [r for r in constructed if r['hero']==hero['hero'] and int(r['round']) in rounds]
                self.assertEqual(int(hero[f'{period}_matches']),len(matches))
                self.assertEqual(int(hero[f'{period}_wins']),sum(r['outcome']=='W' for r in matches))

    def test_worlds_duplicate_is_excluded_and_missing_round_is_visible(self):
        event = 'world-championship-paris-2026'
        audit = json.loads((DATA/event/'audit.json').read_text())
        self.assertEqual(audit['missing_rounds'],[16])
        self.assertEqual(audit['duplicate_round_sources'][0]['round'],15)
        matches = rows(event,'matches')
        self.assertEqual(len(matches),2703)
        self.assertNotIn('16',{m['round'] for m in matches})
        self.assertEqual(len({(m['round'],m['table_order']) for m in matches}),len(matches))
        self.assertNotIn('Flesh and Blood TCG-WorldsParisResults16.html',{m['source'] for m in matches})
        summary = json.loads((DATA/event/'summary.json').read_text())
        self.assertEqual(summary['champion'],'nicolas Jamoulle')
        self.assertTrue(any('ausente' in note for note in summary['event']['notes']))

    def test_showdown_is_single_day_and_has_no_invented_second_day(self):
        event = 'showdown-paris-2026'
        summary = json.loads((DATA/event/'summary.json').read_text())
        self.assertEqual(summary['observed_players'],632)
        self.assertEqual(summary['champion'],'Davorin Pokorn')
        self.assertIsNone(summary['event']['day2_start'])
        self.assertEqual(summary['missing_rounds'],[])
        for hero in summary['heroes']:
            self.assertEqual(hero['swiss_matches'],hero['day1_matches'])
            self.assertIsNone(hero['day2_win_pct'])
            self.assertEqual(hero['day2_players'],0)


if __name__ == '__main__':
    unittest.main()
