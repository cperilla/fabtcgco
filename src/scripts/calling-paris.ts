import { filterPlayers, filterMatchups, finishNames, normalizeSearch, paginate } from '../utils/tournamentReport.js';

type Summary = typeof import('../../public/data/calling-paris/summary.json').default;
type Round = { round: number; phase: string; opponent: string; opponent_hero: string; outcome: string; placeholder_opponent: boolean };
const root = document.querySelector<HTMLElement>('[data-paris-report]');

if (root) {
  const get = <T extends HTMLElement>(id: string) => root.querySelector<T>(`#${id}`)!;
  const percent = (value: number | null) => value === null ? '—' : `${value.toLocaleString('es-CO', { minimumFractionDigits: 1, maximumFractionDigits: 1 })}%`;
  const heroName = (hero: string) => hero === 'N/A' ? 'Sin héroe registrado' : hero;
  const record = (p: Summary['players'][number]) => `${p.swiss_wins}–${p.swiss_losses}–${p.swiss_draws}`;
  let dataPromise: Promise<Summary> | undefined;
  let roundsPromise: Promise<Record<string, Round[]>> | undefined;
  async function loadJSON<T>(url: string): Promise<T> {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Unable to load ${url}`);
    return response.json();
  }
  function data() {
    return dataPromise ??= loadJSON<Summary>('/data/calling-paris/summary.json').catch(error => { dataPromise = undefined; throw error; });
  }
  function rounds() {
    return roundsPromise ??= loadJSON<Record<string, Round[]>>('/data/calling-paris/player-rounds.json').catch(error => { roundsPromise = undefined; throw error; });
  }
  function showError() {
    const message = get('report-error');
    message.textContent = 'No se pudieron cargar los datos interactivos. Intenta buscar de nuevo o usa los archivos de la sección Descargas.';
    message.hidden = false;
  }
  function clearError() { get('report-error').hidden = true; }
  function addRow(body: HTMLElement, values: (string | number)[], player?: string) {
    const row = document.createElement('tr');
    for (const [index, value] of values.entries()) {
      const cell = document.createElement('td');
      if (index === 0 && player) {
        const button = document.createElement('button');
        button.type = 'button';
        button.dataset.player = player;
        button.textContent = String(value);
        cell.append(button);
      } else cell.textContent = String(value);
      row.append(cell);
    }
    body.append(row);
  }
  let playerPage = 0;
  let matchupPage = 0;
  let playerRequest = 0;
  let matchupRequest = 0;
  let detailRequest = 0;

  async function renderPlayers() {
    const request = ++playerRequest;
    try {
      const report = await data();
      if (request !== playerRequest) return;
      const filtered = filterPlayers(report.players, get<HTMLInputElement>('player-search').value, get<HTMLSelectElement>('player-hero').value);
      const page = paginate(filtered, playerPage);
      playerPage = page.page;
      const body = get('player-rows');
      body.replaceChildren();
      for (const p of page.rows) addRow(body, [p.player, heroName(p.hero), finishNames[p.finish] || '—', record(p), percent(p.swiss_win_pct), percent(p.hero_swiss_win_pct), p.placeholder_wins, `${p.all_wins}–${p.all_losses}–${p.all_draws}`], p.player);
      if (!page.total) addRow(body, ['No hay jugadores que coincidan con la búsqueda.']);
      get('player-count').textContent = `Mostrando ${page.start}–${page.end} de ${page.total} jugadores.`;
      get<HTMLButtonElement>('players-prev').disabled = playerPage === 0;
      get<HTMLButtonElement>('players-next').disabled = playerPage === page.lastPage;
      clearError();
    } catch { showError(); }
  }
  async function renderMatchups() {
    const request = ++matchupRequest;
    try {
      const report = await data();
      if (request !== matchupRequest) return;
      const filtered = filterMatchups(report.matchups, get<HTMLInputElement>('matchup-search').value, Number(get<HTMLSelectElement>('matchup-min').value));
      const page = paginate(filtered, matchupPage);
      matchupPage = page.page;
      const body = get('matchup-rows');
      body.replaceChildren();
      for (const m of page.rows) addRow(body, [m.hero, m.opponent_hero, m.matches, `${m.wins}–${m.losses}–${m.draws}`, percent(m.win_pct)]);
      if (!page.total) addRow(body, ['No hay enfrentamientos que coincidan con los filtros.']);
      get('matchup-count').textContent = `Mostrando ${page.start}–${page.end} de ${page.total} enfrentamientos.`;
      get<HTMLButtonElement>('matchups-prev').disabled = matchupPage === 0;
      get<HTMLButtonElement>('matchups-next').disabled = matchupPage === page.lastPage;
      clearError();
    } catch { showError(); }
  }
  async function selectPlayer(name: string) {
    const request = ++detailRequest;
    try {
      const [report, details] = await Promise.all([data(), rounds()]);
      if (request !== detailRequest) return;
      const player = report.players.find(p => p.player === name);
      if (!player || !details[name]) throw new Error('Unknown player');
      get('detail-name').textContent = `Rondas de ${name}`;
      get('detail-summary').textContent = `${heroName(player.hero)} · Suizo: ${record(player)} · Victorias del jugador: ${percent(player.swiss_win_pct)} · Victorias del héroe: ${percent(player.hero_swiss_win_pct)} · Victorias sin rival identificado: ${player.placeholder_wins}`;
      const body = get('detail-rows');
      body.replaceChildren();
      for (const r of details[name]) addRow(body, [r.round, r.phase === 'Swiss' ? 'Suizo' : 'Eliminatoria', r.placeholder_opponent ? 'Rival sin identificar' : r.opponent, heroName(r.opponent_hero), ({ W:'Victoria', L:'Derrota', D:'Empate' }[r.outcome] || r.outcome) + (r.placeholder_opponent ? ' (excluida de la tasa)' : '')]);
      clearError();
      get('detail-name').focus();
    } catch { showError(); }
  }

  get<HTMLInputElement>('hero-search').addEventListener('input', event => {
    const query = normalizeSearch((event.target as HTMLInputElement).value);
    get('hero-rows').querySelectorAll('tr').forEach(row => { row.hidden = !normalizeSearch(row.textContent || '').includes(query); });
  });
  get('player-search').addEventListener('input', () => { playerPage = 0; void renderPlayers(); });
  get('player-hero').addEventListener('change', () => { playerPage = 0; void renderPlayers(); });
  get('players-prev').addEventListener('click', () => { playerPage--; void renderPlayers(); });
  get('players-next').addEventListener('click', () => { playerPage++; void renderPlayers(); });
  get('matchup-search').addEventListener('input', () => { matchupPage = 0; void renderMatchups(); });
  get('matchup-min').addEventListener('change', () => { matchupPage = 0; void renderMatchups(); });
  get('matchups-prev').addEventListener('click', () => { matchupPage--; void renderMatchups(); });
  get('matchups-next').addEventListener('click', () => { matchupPage++; void renderMatchups(); });
  root.addEventListener('click', event => {
    const button = (event.target as HTMLElement).closest<HTMLButtonElement>('button[data-player]');
    if (button?.dataset.player) void selectPlayer(button.dataset.player);
  });
}
