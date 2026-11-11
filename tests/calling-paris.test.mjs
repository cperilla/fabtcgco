import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { filterPlayers, filterMatchups, paginate, formatHeroSample, formatPlayerHeroRate, sortRows, formatPlayerRecord } from '../src/utils/tournamentReport.js';

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

test('daily hero rates show confidence, games and contributing players without inventing single-player certainty', () => {
  const fang = data.heroes.find(h => h.hero.startsWith('Fang,'));
  assert.match(formatHeroSample(fang, 'day1'), /53,3%/);
  assert.match(formatHeroSample(fang, 'day1'), /IC 95%/);
  assert.match(formatHeroSample(fang, 'day1'), /1153 partidas · 159 jugadores/);
  const tek = data.heroes.find(h => h.hero.startsWith('Teklovossen'));
  assert.match(formatHeroSample(tek, 'day2'), /83,3%/);
  assert.match(formatHeroSample(tek, 'day2'), /solo 1 jugador/);
  assert.match(formatPlayerHeroRate(tek), /Día 1: 42,2% · Día 2: 83,3%/);
  const noDay2 = data.heroes.find(h => h.hero.startsWith('Marlynn'));
  assert.match(formatHeroSample(noDay2, 'day2'), /Sin partidas/);
});

test('numeric sorting precedes pagination and keeps unavailable values last in both directions', () => {
  const rows = Array.from({length:60},(_,index)=>({value:index,hero:`Hero ${60-index}`}));
  rows.push({value:null,hero:'Unknown'});
  assert.equal(paginate(sortRows(rows,'value','desc'),0).rows[0].value,59);
  assert.equal(paginate(sortRows(rows,'value','desc'),1).rows[0].value,34);
  assert.equal(sortRows(rows,'value','asc').at(-1).value,null);
  assert.equal(sortRows(rows,'value','desc').at(-1).value,null);
  assert.equal(sortRows(rows,'hero','asc','string')[0].hero,'Hero 1');
  assert.equal(rows[0].value,0,'sorting does not mutate the source order');
});

test('mixed-format player records retain Draft, while hero-only records do not acquire it', () => {
  assert.equal(formatPlayerRecord({swiss_wins:7,swiss_losses:3,swiss_draws:0,constructed_wins:4,constructed_losses:1,constructed_draws:0,draft_wins:3,draft_losses:2,draft_draws:0}), '7–3–0\nCC: 4–1–0\nDraft: 3–2–0');
});
