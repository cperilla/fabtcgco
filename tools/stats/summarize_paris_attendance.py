"""Count observed unique names and overlaps across the three Paris event rosters."""
import csv
import hashlib
import json
import unicodedata
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path


def summarize(data_dir):
    slugs = ['calling-paris', 'world-championship-paris-2026', 'showdown-paris-2026']
    identities = defaultdict(list)
    rosters = {}
    sources = []
    for slug in slugs:
        path = data_dir / slug / 'summary.json'
        report = json.loads(path.read_text())
        roster = set()
        for player in report['players']:
            name = player['player']
            if name in ('Player 1', 'Player 2', 'Bye', 'BYE'):
                continue
            key = ' '.join(unicodedata.normalize('NFKC', name).casefold().split())
            if key in roster:
                raise ValueError(f'Duplicate identity within {slug}: {name}')
            roster.add(key)
            identities[key].append(dict(event=slug, name=name, country=player['country']))
        rosters[slug] = roster
        sources.append(dict(slug=slug, name=report['event']['name'], players=len(roster),
                            source=f'{slug}/summary.json', sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    for key, appearances in identities.items():
        countries = {p['country'] for p in appearances if p['country']}
        if len(countries) > 1:
            raise ValueError(f'Conflicting countries for {key}; manual identity review required')
    distribution = Counter(len(appearances) for appearances in identities.values())
    for source in sources:
        exclusive = sum(len(identities[key]) == 1 for key in rosters[source['slug']])
        source.update(exclusive_players=exclusive, shared_players=source['players']-exclusive)
    result = dict(unique_players=len(identities), tournament_entries=sum(len(roster) for roster in rosters.values()),
                  players_in_one_event=distribution[1], players_in_two_events=distribution[2], players_in_three_events=distribution[3],
                  events=sources,
                  pairwise_overlaps=[dict(events=[a,b], players=len(rosters[a]&rosters[b])) for a,b in combinations(slugs,2)],
                  name_variants=[dict(names=sorted({p['name'] for p in appearances})) for appearances in identities.values() if len({p['name'] for p in appearances})>1],
                  method='Unicode NFKC, case-folding and whitespace normalization of player names; accents preserved; conflicting countries require manual review.',
                  scope='Observed named players in the three saved event rosters. No unique player IDs; homonyms cannot be ruled out. Excludes spectators and other side events, not a census of the whole convention.')
    assert result['tournament_entries'] == sum(n*count for n,count in distribution.items())
    output = data_dir / 'paris-2026'
    output.mkdir(exist_ok=True)
    (output/'attendance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    with (output/'players.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        writer = csv.writer(stream,lineterminator='\n')
        writer.writerow(['player','country','event_count',*slugs])
        for key, appearances in sorted(identities.items()):
            writer.writerow([appearances[0]['name'],appearances[0]['country'],len(appearances),*[key in rosters[slug] for slug in slugs]])
    print(json.dumps({k:v for k,v in result.items() if k not in ('events','method','scope')},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    summarize(Path(__file__).resolve().parents[2]/'public/data')
