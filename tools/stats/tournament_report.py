"""Standalone reports for configured saved tournaments (standard library only)."""
import html
from collections import Counter

TABLE_SCRIPT = r'''
const normalized = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
document.querySelectorAll('input[data-target]').forEach(input => input.addEventListener('input', () => {
  const query = normalized(input.value);
  document.querySelectorAll('#'+input.dataset.target+' tbody tr').forEach(row => row.hidden = !normalized(row.textContent).includes(query));
}));
document.querySelectorAll('table').forEach(table => {
  const headers = Array.from(table.tHead.rows[0].cells);
  headers.forEach((header, column) => {
    const label = header.textContent;
    const button = document.createElement('button');
    button.type = 'button'; button.textContent = label+' ↕'; button.title = 'Ordenar / Sort: '+label;
    button.style.cssText = 'background:transparent;color:inherit;border:0;font:inherit;font-weight:inherit;text-align:left;cursor:pointer';
    header.setAttribute('aria-sort','none'); header.replaceChildren(button);
    button.addEventListener('click', () => {
      const desc = header.getAttribute('aria-sort') === 'ascending';
      headers.forEach(h => { h.setAttribute('aria-sort','none'); h.firstChild.textContent = h.firstChild.textContent.replace(/ [↕↑↓]$/,' ↕'); });
      header.setAttribute('aria-sort', desc ? 'descending' : 'ascending'); button.textContent = label+(desc ? ' ↓' : ' ↑');
      const body = table.tBodies[0], rows = Array.from(body.rows);
      const number = text => { const match = text.trim().match(/^(-?\d+(?:[.,]\d+)?)/); return match ? Number(match[1].replace(',','.')) : null; };
      const numeric = rows.some(r => number(r.cells[column]?.textContent || '') !== null);
      rows.sort((a,b) => {
        const left = a.cells[column]?.textContent || '', right = b.cells[column]?.textContent || '';
        if (!numeric) return (desc ? -1 : 1)*left.localeCompare(right,'es',{sensitivity:'base',numeric:true});
        const l=number(left), r=number(right);
        if(l===null || r===null) return Number(l===null)-Number(r===null);
        return (desc ? -1 : 1)*(l-r);
      });
      rows.forEach(row => body.append(row));
    });
  });
});
'''


def percent(value):
    return '—' if value is None else f'{value:.1f}%'


def hero_sample(hero, period):
    games = hero[f'{period}_matches']
    players = hero[f'{period}_players']
    low, high = hero[f'{period}_ci95_low'], hero[f'{period}_ci95_high']
    ci = 'IC no estimable' if low is None else f'IC 95% {percent(low)}–{percent(high)}'
    if players == 1:
        ci += ' (solo 1 jugador)'
    return f'{percent(hero[f"{period}_win_pct"])} · {ci} · {games} partidas / {players} jugadores'


def write_tournament_report(output, data, audit, results):
    event = data['event']
    players = data['players']
    champion = next(p for p in players if p['player']==data['champion'])
    top8 = sorted([p for p in players if p['top8']],key=lambda p:({'Champion':0,'Runner-up':1,'Top 4':2,'Top 8':3}[p['finish']],p['player']))
    notes = [*event['notes'],
             'Tasa de victoria: V / (V + D + E). Empates y dobles derrotas se conservan. Los rivales sin identificar se excluyen de las tasas y se preservan en los CSV.',
             'Los héroes usan solo rondas suizas del formato '+event['format']+'. Los jugadores conservan todas las rondas y tienen registros separados por formato. Las eliminatorias no afectan las tasas suizas.',
             'Los IC 95% remuestrean jugadores completos 2.000 veces, conservando sus partidas, con semilla reproducible. No se estima IC con menos de dos jugadores, sin datos, sin héroe o sin variación entre réplicas. Muestras con pocos jugadores son inestables.',
             'El día 2 representa a quienes avanzaron. Los intervalos son descriptivos, no garantías sobre fuerza de héroe ni comparaciones causales entre días.',
             'Los nombres son las identidades observadas, no identificadores verificados. El orden por victorias suizas no sustituye la clasificación oficial; GEM prevalece sobre la cobertura.',
             f"Héroes sin registrar: {audit['unknown_hero_players']}. Filas con rival sin identificar: {len(audit['placeholder_rows'])}. Rondas ausentes: {audit['missing_rounds'] or 'ninguna'}."]
    hero_headers = ['Héroe','Jugadores','Participación','Top 8','Victorias suizas / confianza','Día 1 / confianza','Día 2 / confianza','Sin espejos']
    hero_rows = [[h['hero'],h['players'],percent(h['field_pct']),h['top8'],hero_sample(h,'swiss'),hero_sample(h,'day1'),hero_sample(h,'day2') if event['day2_start'] else 'No aplica',percent(h['nonmirror_win_pct'])] for h in data['heroes']]
    player_headers = ['Jugador','Héroe registrado','Resultado','Suizo total V-D-E','Victorias suizas del jugador','Suizo '+event['format']+' V-D-E','Draft V-D-E','Victorias del héroe','Héroe día 1','Héroe día 2','Total V-D-E']
    def player_row(p):
        return [p['player'],p['hero'],p['finish'] or '—',f"{p['swiss_wins']}-{p['swiss_losses']}-{p['swiss_draws']}",percent(p['swiss_win_pct']),f"{p['constructed_wins']}-{p['constructed_losses']}-{p['constructed_draws']}",f"{p['draft_wins']}-{p['draft_losses']}-{p['draft_draws']}",percent(p['hero_swiss_win_pct']),percent(p['hero_day1_win_pct']),percent(p['hero_day2_win_pct']) if event['day2_start'] else 'No aplica',f"{p['all_wins']}-{p['all_losses']}-{p['all_draws']}"]
    player_rows = [player_row(p) for p in players]
    matchup_headers = ['Héroe','Rival','Partidas','V-D-E','Victorias']
    matchup_rows = [[m['hero'],m['opponent_hero'],m['matches'],f"{m['wins']}-{m['losses']}-{m['draws']}",percent(m['win_pct'])] for m in sorted(data['matchups'],key=lambda m:-m['matches'])]
    round_headers = ['Jugador','Ronda','Fase','Formato','Rival','Resultado']
    round_rows = [[r[k] for k in ('player','round','phase','format','opponent','outcome')] for r in results]
    def markdown_table(headers,rows):
        return '| '+' | '.join(headers)+' |\n|'+'|'.join(['---']*len(headers))+'|\n'+'\n'.join('| '+' | '.join(str(v).replace('|','/') for v in row)+' |' for row in rows)
    leaders = sorted([h for h in data['heroes'] if h['players']>=30 and h['nonmirror_win_pct'] is not None],key=lambda h:-h['nonmirror_win_pct'])
    findings = [f"Campeón: {data['champion']} ({champion['hero']}). Finalista: {data['finalist']}.",
                'Más jugados: '+', '.join(f"{h['hero']}: {h['players']} ({percent(h['field_pct'])})" for h in data['heroes'][:3])+'.',
                'Mejores tasas sin espejos con al menos 30 jugadores: '+', '.join(f"{h['hero']}: {percent(h['nonmirror_win_pct'])}" for h in leaders[:4])+'.',
                'Composición del Top 8: '+', '.join(f'{h}: {n}' for h,n in Counter(p['hero'] for p in top8).most_common())+'.']
    intro=f"{data['observed_players']} jugadores observados; {data['match_rows']} filas de resultados. Estadísticas de héroes: {event['format']} suizo."
    md=['# '+event['name'],'',intro,'','## Hallazgos','',*['- '+s for s in findings],'','## Metodología y límites','',*['- '+s for s in notes],'','## Top 8','',markdown_table(player_headers,[player_row(p) for p in top8]),'','## Héroes','',markdown_table(hero_headers,hero_rows),'','## Jugadores','', 'Todos los jugadores y las rondas están en el HTML y los CSV. Primeros 40 en orden descriptivo:','',markdown_table(player_headers,player_rows[:40]),'','## Enfrentamientos','',markdown_table(matchup_headers,matchup_rows[:30]),'','## Reproducir','',f"`python -B tools/stats/analyze_saved_results.py --event {event['slug']} --matches public/data/{event['slug']}/matches.csv --output public/data/{event['slug']}`",'']
    (output/'report.md').write_text('\n'.join(md),encoding='utf-8')
    def html_table(headers,rows,ident):
        return '<label>Filtrar '+html.escape(ident)+' <input type="search" data-target="'+ident+'"></label><div class="scroll"><table id="'+ident+'"><thead><tr>'+''.join('<th>'+html.escape(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table></div>'
    esc=html.escape
    doc='<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(event['name'])+'</title><style>body{font:16px/1.6 system-ui;background:#f6f7f9;color:#192b39;max-width:1400px;margin:30px auto;padding:0 20px}h1,h2{color:#183d55}table{border-collapse:collapse;width:100%;background:white}th,td{text-align:left;padding:10px;border-bottom:1px solid #ccd3db;min-width:130px}th{position:sticky;top:0;background:#183d55;color:white}.scroll{overflow:auto;max-height:680px;margin:20px 0}input{font:inherit;padding:8px;max-width:90%}.warning{padding:16px;border:2px solid #8c2719}a{color:#12648d}li{margin:10px 0}</style><h1>'+esc(event['name'])+'</h1><p>'+esc(intro)+'</p>'
    if data['missing_rounds']:
        doc+='<p class="warning"><strong>Datos incompletos: falta la ronda '+esc(str(data['missing_rounds']))+'.</strong> La copia de ronda 15 no se cuenta dos veces.</p>'
    doc+='<p>'+ ' · '.join('<a href="'+file+'">'+esc(label)+'</a>' for file,label in [('report.md','Análisis'),('players.csv','Jugadores CSV'),('player-results.csv','Rondas CSV'),('heroes.csv','Héroes CSV'),('matchups.csv','Enfrentamientos CSV'),('audit.json','Auditoría')])+'</p><h2>Hallazgos</h2><ul>'+''.join('<li>'+esc(s)+'</li>' for s in findings)+'</ul><h2>Metodología</h2><ul>'+''.join('<li>'+esc(s)+'</li>' for s in notes)+'</ul>'
    for heading,headers,rows,ident in [('Top 8',player_headers,[player_row(p) for p in top8],'top8'),('Héroes',hero_headers,hero_rows,'heroes'),('Jugadores',player_headers,player_rows,'jugadores'),('Resultados por ronda',round_headers,round_rows,'rondas'),('Enfrentamientos',matchup_headers,matchup_rows,'enfrentamientos')]:
        doc+='<h2>'+heading+'</h2>'+html_table(headers,rows,ident)
    doc+='<script>'+TABLE_SCRIPT+'</script></html>'
    (output/'report.html').write_text(doc,encoding='utf-8')
