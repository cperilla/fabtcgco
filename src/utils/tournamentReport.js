export const finishNames = { Champion: 'Campeón', 'Runner-up': 'Finalista', 'Top 4': 'Top 4', 'Top 8': 'Top 8' };

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
