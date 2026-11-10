"""Analyze saved FAB coverage results, without network access or third-party packages.

Run: python tools/stats/analyze_saved_results.py
"""
import argparse
import csv
import hashlib
import html
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


def clean(value):
    return ' '.join(html.unescape(re.sub(r'<[^>]*>', ' ', value)).split())


def required(pattern, value):
    found = re.search(pattern, value, re.S)
    if not found:
        raise ValueError(f'Missing expected HTML field: {pattern}')
    return found.group(1)


def parse_page(path):
    source = path.read_text(encoding='utf-8')
    round_number = int(required(r'Calling: Paris - Round (\d+) Results', source))
    matches = []
    for index, row in enumerate(re.findall(r'<tr class="match-row">(.*?)</tr>', source, re.S), 1):
        record = dict(round=round_number, table_order=index,
                      phase='Swiss' if round_number <= 15 else 'Elimination', source=path.name)
        record['result'] = clean(required(r'<span class="winner-pill">(.*?)</span>', row))
        if record['result'] not in ('Player 1 Win', 'Player 2 Win', 'Draw', 'Double Loss'):
            raise ValueError(f'Unrecognized result: {record}')
        for side in (1, 2):
            cell = required(fr'<td class="player-{side}-cell">(.*?)</td>', row)
            record[f'player{side}'] = clean(required(r'<strong>(.*?)</strong>', cell))
            record[f'hero{side}'] = clean(required(r'<div class="player-text">.*?<span>(.*?)</span>', cell))
            flag = re.search(r'class="flag ([^"]+)"', cell)
            record[f'country{side}'] = flag.group(1) if flag else ''
        record['placeholder_opponent'] = any(record[f'player{s}'] in ('Player 1', 'Player 2', 'BYE', 'Bye') for s in (1, 2))
        record['known_heroes'] = all(record[f'hero{s}'] != 'N/A' for s in (1, 2))
        record['mirror'] = record['known_heroes'] and record['hero1'] == record['hero2']
        matches.append(record)
    if len(matches) != source.count('class="match-row"') or not matches:
        raise ValueError(f'Incomplete row extraction: {path}')
    return matches


def outcome(result, side):
    if result == 'Draw':
        return 'D'
    if result == 'Double Loss':
        return 'L'
    return 'W' if result == f'Player {side} Win' else 'L'


def rate(wins, losses, draws=0):
    total = wins + losses + draws
    return round(100 * wins / total, 2) if total else None


def wilson(wins, total):
    if not total:
        return (None, None)
    z = 1.95996398454
    p = wins / total
    center = (p + z*z/(2*total)) / (1 + z*z/total)
    half = z * math.sqrt(p*(1-p)/total + z*z/(4*total*total)) / (1+z*z/total)
    return round(100*(center-half), 2), round(100*(center+half), 2)


def write_csv(path, rows):
    if rows:
        with path.open('w', newline='', encoding='utf-8-sig') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


def pct(value):
    return '—' if value is None else f'{value:.1f}%'


def table(headers, rows):
    return '| ' + ' | '.join(headers) + ' |\n|' + '|'.join(['---']*len(headers)) + '|\n' + '\n'.join('| ' + ' | '.join(map(str, row)) + ' |' for row in rows)


def analyze(source_dir, output_dir, normalized=None):
    paths = []
    if normalized:
        with normalized.open(encoding='utf-8-sig') as stream:
            matches = list(csv.DictReader(stream))
        for match in matches:
            for key in ('round', 'table_order'):
                match[key] = int(match[key])
            for key in ('placeholder_opponent', 'known_heroes', 'mirror'):
                if match[key] not in ('True', 'False'):
                    raise ValueError(f'Invalid boolean in {normalized}: {key}')
                match[key] = match[key] == 'True'
        sources = json.loads(normalized.with_name('audit.json').read_text())['sources']
    else:
        paths = sorted(source_dir.glob('*.html'), key=lambda p: int(re.search(r'Results(\d+)', p.name).group(1)))
        matches = [m for p in paths for m in parse_page(p)]
        sources = [dict(file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths]
    if {m['round'] for m in matches} != set(range(1, 19)):
        raise ValueError('Expected the 18 Calling: Paris rounds; refusing partial analysis')
    players = {}
    results = []
    seen = set()
    for m in matches:
        for side in (1, 2):
            name = m[f'player{side}']
            if name in ('Player 1', 'Player 2', 'BYE', 'Bye'):
                continue
            if (m['round'], name) in seen:
                raise ValueError(f'Duplicate player in a round: {name}, {m["round"]}')
            seen.add((m['round'], name))
            player = players.setdefault(name, dict(player=name, hero=m[f'hero{side}'], country=m[f'country{side}']))
            if player['hero'] != m[f'hero{side}']:
                raise ValueError(f'Hero changed for {name}')
            results.append(dict(player=name, hero=player['hero'], round=m['round'], phase=m['phase'],
                                opponent=m[f'player{3-side}'], opponent_hero=m[f'hero{3-side}'],
                                outcome=outcome(m['result'], side), source_result=m['result'],
                                placeholder_opponent=m['placeholder_opponent'], source=m['source']))
    by_player = defaultdict(list)
    for r in results:
        by_player[r['player']].append(r)
    top8 = {m[f'player{s}'] for m in matches if m['round'] == 16 for s in (1, 2)}
    day2 = {r['player'] for r in results if r['round'] == 10}
    final = next(m for m in matches if m['round'] == 18)
    champion = final['player1'] if final['result'] == 'Player 1 Win' else final['player2']
    finalist = final['player2'] if champion == final['player1'] else final['player1']
    for name, p in players.items():
        rs = by_player[name]
        swiss = [r for r in rs if r['phase'] == 'Swiss']
        played = [r for r in swiss if not r['placeholder_opponent']]
        counts = Counter(r['outcome'] for r in played)
        all_counts = Counter(r['outcome'] for r in rs if not r['placeholder_opponent'])
        p.update(swiss_wins=counts['W'], swiss_losses=counts['L'], swiss_draws=counts['D'],
                 swiss_matches=len(played), swiss_win_pct=rate(counts['W'], counts['L'], counts['D']),
                 swiss_recorded_wins=sum(r['outcome']=='W' for r in swiss),
                 placeholder_wins=sum(r['placeholder_opponent'] and r['outcome']=='W' for r in swiss),
                 all_wins=all_counts['W'], all_losses=all_counts['L'], all_draws=all_counts['D'],
                 all_win_pct=rate(all_counts['W'],all_counts['L'],all_counts['D']),
                 first_round=min(r['round'] for r in rs), last_round=max(r['round'] for r in rs),
                 day2=name in day2, top8=name in top8,
                 finish='Champion' if name == champion else 'Runner-up' if name == finalist else 'Top 4' if any(r['round']==17 for r in rs) else 'Top 8' if name in top8 else '')
    leaderboard = sorted(players.values(), key=lambda p: (-p['swiss_recorded_wins'],p['swiss_losses'],p['swiss_draws'],p['player'].casefold()))
    heroes = []
    known_contested = [m for m in matches if m['phase']=='Swiss' and m['known_heroes'] and not m['placeholder_opponent']]
    for hero in sorted({p['hero'] for p in players.values()}):
        ps = [p for p in players.values() if p['hero']==hero]
        rs = [r for r in results if r['hero']==hero and r['phase']=='Swiss' and not r['placeholder_opponent']]
        counts = Counter(r['outcome'] for r in rs)
        nonmirror = Counter()
        for m in known_contested:
            if not m['mirror']:
                for side in (1,2):
                    if m[f'hero{side}']==hero:
                        nonmirror[outcome(m['result'],side)]+=1
        lo,hi = wilson(nonmirror['W'],sum(nonmirror.values()))
        heroes.append(dict(hero=hero, players=len(ps), field_pct=round(100*len(ps)/len(players),2),
                           day2=sum(p['day2'] for p in ps), day2_conversion_pct=round(100*sum(p['day2'] for p in ps)/len(ps),2),
                           top8=sum(p['top8'] for p in ps), top8_conversion_pct=round(100*sum(p['top8'] for p in ps)/len(ps),2),
                           swiss_wins=counts['W'],swiss_losses=counts['L'],swiss_draws=counts['D'],
                           swiss_win_pct=rate(counts['W'],counts['L'],counts['D']),
                           nonmirror_wins=nonmirror['W'],nonmirror_losses=nonmirror['L'],nonmirror_draws=nonmirror['D'],
                           nonmirror_win_pct=rate(nonmirror['W'],nonmirror['L'],nonmirror['D']),
                           nonmirror_ci95_low=lo,nonmirror_ci95_high=hi))
    heroes.sort(key=lambda h:-h['players'])
    hero_rates = {h['hero']: h['swiss_win_pct'] for h in heroes if h['hero'] != 'N/A'}
    for player in leaderboard:
        player['hero_swiss_win_pct'] = hero_rates.get(player['hero'])
    matchup_counts = defaultdict(Counter)
    for m in known_contested:
        if not m['mirror']:
            for side in (1,2):
                matchup_counts[(m[f'hero{side}'],m[f'hero{3-side}'])][outcome(m['result'],side)]+=1
    matchups = [dict(hero=h,opponent_hero=o,matches=sum(c.values()),wins=c['W'],losses=c['L'],draws=c['D'],win_pct=rate(c['W'],c['L'],c['D'])) for (h,o),c in sorted(matchup_counts.items())]
    rounds = []
    for rnd in range(1,19):
        ms = [m for m in matches if m['round']==rnd]
        counts=Counter(m['result'] for m in ms)
        rounds.append(dict(round=rnd,phase=ms[0]['phase'],rows=len(ms),named_players=sum(r['round']==rnd for r in results),
                           draws=counts['Draw'],double_losses=counts['Double Loss'],unknown_hero_rows=sum(not m['known_heroes'] for m in ms),
                           placeholders=sum(m['placeholder_opponent'] for m in ms)))
    unknowns = [p for p in leaderboard if p['hero']=='N/A']
    audit = dict(observed_named_players=len(players),known_hero_players=len(players)-len(unknowns),unknown_hero_players=len(unknowns),
                 match_rows=len(matches),swiss_rows=sum(m['phase']=='Swiss' for m in matches),
                 elimination_rows=sum(m['phase']=='Elimination' for m in matches),
                 placeholder_rows=[m for m in matches if m['placeholder_opponent']],
                 unknown_players=unknowns, first_seen_after_round1=[p['player'] for p in leaderboard if p['first_round']>1],
                 sources=sources)
    output_dir.mkdir(parents=True,exist_ok=True)
    for filename, rows in [('matches',matches),('players',leaderboard),('player-results',results),('heroes',heroes),('matchups',matchups),('rounds',rounds)]:
        write_csv(output_dir/f'{filename}.csv',rows)
    (output_dir/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
    site_data = dict(heroes=heroes, players=leaderboard, matchups=matchups, rounds=rounds,
                     champion=champion, finalist=finalist,
                     observed_players=len(players), known_hero_players=len(players)-len(unknowns),
                     unknown_hero_players=len(unknowns), match_rows=len(matches))
    (output_dir/'summary.json').write_text(json.dumps(site_data,ensure_ascii=False,separators=(',',':'))+'\n')
    details = defaultdict(list)
    for result in results:
        details[result['player']].append({key:result[key] for key in ('round','phase','opponent','opponent_hero','outcome','placeholder_opponent')})
    (output_dir/'player-rounds.json').write_text(json.dumps(details,ensure_ascii=False,separators=(',',':'))+'\n')
    write_report(output_dir,heroes,leaderboard,matchups,rounds,audit,champion,finalist,matches)
    print(json.dumps({k:v for k,v in audit.items() if k not in ('unknown_players','sources','placeholder_rows')},ensure_ascii=False,indent=2))


def write_report(out,heroes,players,matchups,rounds,audit,champion,finalist,matches):
    known = audit['known_hero_players']
    top8 = sorted([p for p in players if p['top8']], key=lambda p:({'Champion':0,'Runner-up':1,'Top 4':2,'Top 8':3}[p['finish']],p['player']))
    major = sorted([h for h in heroes if h['players']>=30 and h['nonmirror_win_pct'] is not None],key=lambda h:-h['nonmirror_win_pct'])
    hero_rows = [[h['hero'],h['players'],pct(h['field_pct']),h['day2'],pct(h['day2_conversion_pct']),h['top8'],f"{h['swiss_wins']}-{h['swiss_losses']}-{h['swiss_draws']}",pct(h['swiss_win_pct']),pct(h['nonmirror_win_pct'])] for h in heroes]
    headers=['Hero','Players','Field share','Day 2','Day 2 conversion','Top 8','Swiss W-L-D','Swiss win rate','Non-mirror win rate']
    def player_row(p):
        return [p['player'],p['hero'],p['finish'],f"{p['swiss_wins']}-{p['swiss_losses']}-{p['swiss_draws']}",pct(p['swiss_win_pct']),pct(p['hero_swiss_win_pct']),f"{p['all_wins']}-{p['all_losses']}-{p['all_draws']}"]
    player_rows = [player_row(p) for p in players]
    pheaders=['Player','Hero','Finish','Swiss W-L-D','Player Swiss win rate','Hero Swiss win rate','All rounds W-L-D']
    lines=['# Calling: Paris — saved tournament results analysis','',
           f"{audit['observed_named_players']:,} observed named players; {known:,} with a known hero; {audit['unknown_hero_players']} named players with source hero `N/A`. {audit['match_rows']:,} result rows: {audit['swiss_rows']:,} Swiss (rounds 1–15) and 7 elimination (rounds 16–18).",'',
           f'**Champion: {champion} (Teklovossen). Runner-up: {finalist} (Jarl).**','',
           '## Reading the results','',
           '- Participation counts distinct exact player names seen anywhere in the saved pages. This is an observed field, not a registration list. No conflicting heroes or duplicate player names within a round were found; exact names are not verified unique player IDs.',
           '- Day 2 means an appearance in round 10. The 128 observed round-10 players provide an observed Day 2 cohort; qualification rules are not inferred.',
           '- Swiss win rate = W / (W + L + D). Draws count as games without a win; a double loss is one loss for each player. Mirrors are included in the basic Swiss rate.',
           '- In player tables, Hero Swiss win rate is the pooled Swiss rate of every observed player using that hero, including the current player. It uses the same denominator and exclusions as the player rate; unknown heroes show no hero rate.',
           '- Non-mirror win rate additionally excludes mirror matches and every match with an unknown hero. It uses Swiss rounds only, avoiding extra weight from the elimination bracket. CSV includes approximate 95% Wilson intervals; repeated games from the same player are correlated, so these intervals are descriptive, not a player-adjusted model.',
           '- Six rows (rounds 2, 4, 6, 7, 13 and 14) record wins against the literal placeholder “Player 2” / `N/A`. These are not counted as real opponents or played matches. They remain in raw matches and in each player’s recorded Swiss wins, with a separate placeholder-wins count in players.csv. The source does not label them as byes; other unlisted byes cannot be recovered.',
           '- The 26 named `N/A` players appear only in round 1, each with a loss. Their reason for missing hero data is not supplied. Their results are preserved in basic player/hero totals; non-mirror and matchup metrics exclude those rows. This can inflate basic rates for their opponents.',
           '- Participation shares include the 26 unknowns in the denominator. To compare only known heroes, divide a hero’s player count by '+str(known)+'.',
           '- Player tables are sorted by recorded Swiss wins, then losses, draws and name. This is not official standings: tie-breakers, byes absent from coverage, and final Swiss ranks are unavailable. Elimination finish is taken directly from rounds 16–18.',
           '- The source warns that coverage results are provisional relative to GEM. All figures describe these saved snapshots, not a fresh live scrape. No event date is inferred from file timestamps.','',
           '## Main findings','',
           f"- Most played: {heroes[0]['hero']} ({heroes[0]['players']}, {pct(heroes[0]['field_pct'])}), followed by {heroes[1]['hero']} ({heroes[1]['players']}) and {heroes[2]['hero']} ({heroes[2]['players']}).",
           '- Best non-mirror Swiss rates among heroes with at least 30 observed players: '+ '; '.join(f"{h['hero']} {pct(h['nonmirror_win_pct'])} ({h['nonmirror_wins']}-{h['nonmirror_losses']}-{h['nonmirror_draws']})" for h in major[:5])+'.',
           '- Top 8 hero composition: '+', '.join(f'{hero}: {count}' for hero,count in Counter(p['hero'] for p in top8).most_common())+'.',
           '- Jarl converted 3 of 132 players to Top 8 (2.3%); Aurora converted 2 of 120 (1.7%). Fang and Levia had the two largest cohorts but neither reached Top 8.',
           '- Dorinthea also had the highest observed Day 2 conversion among cohorts of at least 30 players: 8 of 37 (21.6%), against a field baseline of 128 / 1,418 (9.0%). None reached Top 8.',
           '- Teklovossen won the event but posted a 44.3% non-mirror Swiss rate across 18 players. Matt Muus was its only observed Day 2 player. The champion’s result therefore differs sharply from the hero’s aggregate performance.',
           '- Among well-represented matchups, Aurora went 81–54 against Fang (60.0%) but 23–57–2 against Jarl (28.1%). Fang went 61–32 against Ira (65.6%). Pairing mix can change a hero’s aggregate result substantially.',
           '- These are tournament outcomes, not causal measures of hero strength: player skill, pairings and survivor selection affect the rates. Small cohorts and sparse matchups are particularly uncertain.','',
           '## Elimination results','',table(pheaders,[player_row(p) for p in top8]),'',
           '## Hero participation and performance','',table(headers,hero_rows),'',
           '## Most-supported non-mirror matchups','',
           'Swiss only; each pairing is shown once. Opposite-direction rates need not sum to 100% because draws and double losses exist.','',
           table(['Hero','Opponent','Matches','W-L-D','Win rate'],[[m['hero'],m['opponent_hero'],m['matches'],f"{m['wins']}-{m['losses']}-{m['draws']}",pct(m['win_pct'])] for m in sorted([m for m in matchups if m['hero']<m['opponent_hero']],key=lambda m:-m['matches'])[:20]]),'',
           '## Player results','', 'All players and round-by-round opponents are in [players.csv](players.csv) and [player-results.csv](player-results.csv). Open [report.html](report.html) for searchable player and matchup tables. The first 40 players in the descriptive Swiss ordering are below.','',table(pheaders,player_rows[:40]),'',
           '## Round coverage','',table(['Round','Phase','Rows','Named players','Draws','Double losses','Unknown hero rows','Placeholder rows'],[[r[k] for k in r] for r in rounds]),'',
           '## Reproduce and audit','',
           'Run `python -B tools/stats/analyze_saved_results.py --matches public/data/calling-paris/matches.csv --output public/data/calling-paris` from the repository root to rebuild from the included normalized data. If the original pages are available in Scraping/, omit --matches to extract them again. The script uses only the Python standard library. `audit.json` lists source filenames and SHA-256 hashes, unknown players, placeholder rows and late first appearances. `matches.csv` preserves source results and filenames; `player-results.csv` expands each named player’s individual result.','']
    markdown='\n'.join(lines)
    (out/'report.md').write_text(markdown,encoding='utf-8')
    def html_table(hs,rs,ident):
        return '<input class="search" data-target="'+ident+'" placeholder="Search players, heroes, or opponents…" aria-label="Filter '+ident+'"><div class="scroll"><table id="'+ident+'"><thead><tr>'+''.join('<th>'+html.escape(h)+'</th>' for h in hs)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in row)+'</tr>' for row in rs)+'</tbody></table></div>'
    bars = ''.join(f'<div class="barrow"><span>{html.escape(h["hero"])}</span><div class="bar" style="width:{h["players"]/heroes[0]["players"]*100:.2f}%">{h["players"]}</div></div>' for h in heroes[:15])
    definitions=markdown.split('## Reading the results\n\n',1)[1].split('\n\n## Main findings',1)[0]
    paragraphs=''.join('<p>'+html.escape(line[2:])+'</p>' for line in definitions.splitlines() if line.startswith('- '))
    document='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Calling: Paris results analysis</title><style>body{font:16px/1.5 system-ui;margin:32px auto;max-width:1440px;padding:0 20px;color:#192b39;background:#f6f7f9}h1,h2{color:#183d55}.scroll{overflow:auto;max-height:680px}table{border-collapse:collapse;width:100%;background:white}th,td{padding:9px 12px;text-align:left;border-bottom:1px solid #dde3e8;white-space:nowrap}th{position:sticky;top:0;background:#183d55;color:white}input{font:inherit;padding:12px;margin:12px 0;width:min(90%,500px)}.barrow{display:grid;grid-template-columns:300px 1fr;align-items:center;margin:6px 0}.bar{background:#287ba5;color:white;padding:3px 8px;box-sizing:border-box;min-width:30px}a{color:#12648d}summary{cursor:pointer;font-weight:bold}@media(max-width:650px){.barrow{grid-template-columns:180px 1fr;font-size:12px}body{margin:16px auto}}</style><h1>Calling: Paris — results analysis</h1>'''
    document+=f'<p>{audit["observed_named_players"]:,} observed named players · {known:,} players with known heroes · {len(matches):,} result rows</p><p><b>Champion: {html.escape(champion)} — Teklovossen. Runner-up: {html.escape(finalist)} — Jarl.</b></p>'
    document+='<p><a href="report.md">Full analysis</a> · <a href="players.csv">Player CSV</a> · <a href="player-results.csv">Player round results</a> · <a href="heroes.csv">Hero CSV</a> · <a href="matchups.csv">Matchup CSV</a> · <a href="audit.json">Audit</a></p><details><summary>Definitions and data limitations</summary>'+paragraphs+'</details><h2>Participation: 15 most played heroes</h2>'+bars
    findings=markdown.split('## Main findings\n\n',1)[1].split('\n\n## Elimination results',1)[0]
    document+='<h2>Findings</h2><ul>'+''.join('<li>'+html.escape(line[2:])+'</li>' for line in findings.splitlines() if line.startswith('- '))+'</ul>'
    document+='<h2>Top 8 player results</h2>'+html_table(pheaders,[player_row(p) for p in top8],'top8')
    document+='<h2>Heroes</h2>'+html_table(headers,hero_rows,'heroes')
    document+='<h2>All player results</h2><p>Descriptive Swiss ordering, not official standings. W-L-D excludes all six placeholder opponents. See the player CSV for recorded wins including placeholders.</p>'+html_table(pheaders,player_rows,'players')
    with (out/'player-results.csv').open(encoding='utf-8-sig') as stream:
        individual_results=list(csv.DictReader(stream))
    document+='<h2>Player round-by-round results</h2>'+html_table(['Player','Hero','Round','Phase','Opponent','Opponent hero','Result','Placeholder opponent'],[[r[k] for k in ('player','hero','round','phase','opponent','opponent_hero','outcome','placeholder_opponent')] for r in individual_results],'round-results')
    document+='<h2>Swiss matchups</h2>'+html_table(['Hero','Opponent','Matches','W-L-D','Win rate'],[[m['hero'],m['opponent_hero'],m['matches'],f"{m['wins']}-{m['losses']}-{m['draws']}",pct(m['win_pct'])] for m in sorted(matchups,key=lambda m:-m['matches'])],'matchups')
    document+='''<script>document.querySelectorAll('.search').forEach(input=>input.addEventListener('input',()=>{const query=input.value.toLocaleLowerCase();document.querySelectorAll('#'+input.dataset.target+' tbody tr').forEach(row=>row.hidden=!row.textContent.toLocaleLowerCase().includes(query))}));</script></html>'''
    (out/'report.html').write_text(document,encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=Path('Scraping'))
    parser.add_argument('--output',type=Path,default=Path('output/calling-paris'))
    parser.add_argument('--matches',type=Path,help='Rebuild from normalized matches.csv and its sibling audit.json')
    args=parser.parse_args()
    analyze(args.source,args.output,args.matches)
