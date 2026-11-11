export const finishNames = { Champion: 'Campeón', 'Runner-up': 'Finalista', 'Top 4': 'Top 4', 'Top 8': 'Top 8' };

const percent = value => value === null || value === undefined ? '—' : `${value.toLocaleString('es-CO', { minimumFractionDigits: 1, maximumFractionDigits: 1 })}%`;

export function formatHeroSample(hero, period = 'swiss') {
  if (!hero) return 'Sin héroe registrado';
  const games = hero[`${period}_matches`];
  const players = hero[`${period}_players`];
  if (!games) return 'Sin partidas\n0 partidas · 0 jugadores';
  const low = hero[`${period}_ci95_low`];
  const high = hero[`${period}_ci95_high`];
  const status = hero[`${period}_ci_status`];
  let confidence = low === null ? 'IC no estimable' : `IC 95%: ${percent(low)}–${percent(high)}`;
  if (status === 'insufficient_players') confidence = 'IC no estimable: solo 1 jugador';
  if (status === 'no_between_player_variation') confidence = 'IC no estimable: sin variación entre jugadores';
  if (status === 'unknown_hero') confidence = 'IC no estimable: héroe desconocido';
  return `${percent(hero[`${period}_win_pct`])}\n${confidence}\n${games} partidas · ${players} ${players === 1 ? 'jugador' : 'jugadores'}` + (players < 5 && status === 'estimated' ? '\nPocos jugadores: intervalo inestable' : '');
}

export function formatPlayerHeroRate(hero, hasDay2 = true) {
  if (!hero || hero.hero === 'N/A') return 'Sin héroe registrado';
  return `${formatHeroSample(hero)}\nDía 1: ${percent(hero.day1_win_pct)} · Día 2: ${hasDay2 ? percent(hero.day2_win_pct) : 'No aplica'}`;
}

export function formatPlayerRecord(player) {
  const total = `${player.swiss_wins}–${player.swiss_losses}–${player.swiss_draws}`;
  if (!(player.draft_wins + player.draft_losses + player.draft_draws)) return total;
  return `${total}\nCC: ${player.constructed_wins}–${player.constructed_losses}–${player.constructed_draws}\nDraft: ${player.draft_wins}–${player.draft_losses}–${player.draft_draws}`;
}

export function sortRows(rows, key, direction = 'asc', type = 'number') {
  const order = direction === 'asc' ? 1 : -1;
  return [...rows].sort((a, b) => {
    const left = a[key], right = b[key];
    const emptyLeft = left === null || left === undefined || left === '';
    const emptyRight = right === null || right === undefined || right === '';
    if (emptyLeft || emptyRight) return Number(emptyLeft) - Number(emptyRight);
    if (type === 'string') return order * String(left).localeCompare(String(right), 'es', { sensitivity: 'base', numeric: true });
    return order * (Number(left) - Number(right));
  });
}

export function normalizeSearch(value) {
  return value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase().trim();
}

export function filterPlayers(players, query, hero) {
  const search = normalizeSearch(query);
  return players.filter(p => (!hero || p.hero === hero) && normalizeSearch(`${p.player} ${p.hero} ${p.finish} ${finishNames[p.finish] || ''}`).includes(search));
}

export function filterMatchups(matchups, query, minMatches) {
  const search = normalizeSearch(query);
  return matchups.filter(m => m.matches >= minMatches && normalizeSearch(`${m.hero} ${m.opponent_hero}`).includes(search)).sort((a, b) => b.matches - a.matches);
}

export function paginate(items, page, size = 25) {
  const lastPage = Math.max(0, Math.ceil(items.length / size) - 1);
  const currentPage = Math.min(Math.max(0, page), lastPage);
  const start = currentPage * size;
  return { rows: items.slice(start, start + size), page: currentPage, lastPage, start: items.length ? start + 1 : 0, end: Math.min(start + size, items.length), total: items.length };
}
