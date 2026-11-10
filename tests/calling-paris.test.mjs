import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { filterPlayers, filterMatchups, paginate } from '../src/utils/tournamentReport.js';

const data = JSON.parse(readFileSync(new URL('../public/data/calling-paris/summary.json', import.meta.url), 'utf8'));
const rounds = JSON.parse(readFileSync(new URL('../public/data/calling-paris/player-rounds.json', import.meta.url), 'utf8'));

test('player search handles accents, translated finishes and exact hero filters', () => {
  assert.equal(filterPlayers(data.players, 'leo baty', '')[0].player, 'Léo Baty');
  assert.deepEqual(filterPlayers(data.players, 'campeon', '').map(p => p.player), ['Matt Muus']);
  assert.equal(filterPlayers(data.players, '', 'N/A').length, 26);
  assert.equal(filterPlayers(data.players, 'Matt Muus', 'Jarl Vetreiði').length, 0);
});

test('pagination covers every player and clamps an empty search', () => {
  const names = [];
  for (let page = 0; page <= paginate(data.players, 0).lastPage; page++) {
    names.push(...paginate(data.players, page).rows.map(p => p.player));
  }
  assert.equal(names.length, 1418);
  assert.equal(new Set(names).size, 1418);
  assert.deepEqual(paginate([], 50), { rows: [], page: 0, lastPage: 0, start: 0, end: 0, total: 0 });
});

test('each player displays the pooled Swiss hero rate, with unknown heroes left blank', () => {
  for (const player of data.players) {
    const hero = data.heroes.find(h => h.hero === player.hero);
    assert.equal(player.hero_swiss_win_pct, player.hero === 'N/A' ? null : hero.swiss_win_pct);
    assert.ok(rounds[player.player].length > 0);
  }
  const champion = data.players.find(p => p.player === data.champion);
  assert.equal(champion.swiss_win_pct, 86.67);
  assert.equal(champion.hero_swiss_win_pct, 44.44);
  assert.equal(rounds[champion.player].length, 18);
});

test('matchup filters retain both directions and enforce the sample threshold', () => {
  const pair = filterMatchups(data.matchups, 'Aurora', 100);
  assert.equal(pair.length, 2);
  assert.equal(pair[0].matches, 135);
  assert.equal(filterMatchups(data.matchups, 'absent hero', 1).length, 0);
  assert.ok(filterMatchups(data.matchups, '', 50).every(m => m.matches >= 50));
});
