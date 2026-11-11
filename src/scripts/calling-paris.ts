import { filterPlayers, filterMatchups, finishNames, normalizeSearch, paginate, formatPlayerHeroRate, formatPlayerRecord, sortRows } from '../utils/tournamentReport.js';

type Summary = typeof import('../../public/data/calling-paris/summary.json').default;
type Round = { round: number; phase: string; format: string; opponent: string; opponent_hero: string; outcome: string; placeholder_opponent: boolean };
const root = document.querySelector<HTMLElement>('[data-paris-report]');

if (root) {
  const dataBase = root.dataset.reportBase || '/data/calling-paris';
  const get = <T extends HTMLElement>(id: string) => root.querySelector<T>(`#${id}`)!;
  const percent = (value: number | null) => value === null ? '—' : `${value.toLocaleString('es-CO', { minimumFractionDigits: 1, maximumFractionDigits: 1 })}%`;
  const heroName = (hero: string) => hero === 'N/A' ? 'Sin héroe registrado' : hero;
  const record = formatPlayerRecord;
  let dataPromise: Promise<Summary> | undefined;
  let roundsPromise: Promise<Record<string, Round[]>> | undefined;
  async function loadJSON<T>(url: string): Promise<T> {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Unable to load ${url}`);
    return response.json();
  }
  function data() {
    return dataPromise ??= loadJSON<Summary>(`${dataBase}/summary.json`).catch(error => { dataPromise = undefined; throw error; });
  }
  function rounds() {
    return roundsPromise ??= loadJSON<Record<string, Round[]>>(`${dataBase}/player-rounds.json`).catch(error => { roundsPromise = undefined; throw error; });
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
      if (player && index === 5) cell.className = 'hero-rate';
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
  let playerSort: { key: string; direction: string; type: string } | undefined;
  let matchupSort: { key: string; direction: string; type: string } | undefined;

  async function renderPlayers() {
    const request = ++playerRequest;
    try {
      const report = await data();
      if (request !== playerRequest) return;
      const filtered = filterPlayers(report.players, get<HTMLInputElement>('player-search').value, get<HTMLSelectElement>('player-hero').value);
      const sorted = playerSort ? sortRows(filtered, playerSort.key, playerSort.direction, playerSort.type) : filtered;
      const page = paginate(sorted, playerPage);
      playerPage = page.page;
      const body = get('player-rows');
      body.replaceChildren();
      const heroes = new Map(report.heroes.map(h => [h.hero, h]));
      for (const p of page.rows) addRow(body, [p.player, heroName(p.hero), finishNames[p.finish] || '—', record(p), percent(p.swiss_win_pct), formatPlayerHeroRate(heroes.get(p.hero), Boolean(report.event.day2_start)), `${p.all_wins}–${p.all_losses}–${p.all_draws}`], p.player);
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
      const sorted = matchupSort ? sortRows(filtered, matchupSort.key, matchupSort.direction, matchupSort.type) : filtered;
      const page = paginate(sorted, matchupPage);
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
      get('detail-summary').textContent = `${heroName(player.hero)} · Suizo: ${record(player)} · Victorias del jugador: ${percent(player.swiss_win_pct)}\nVictorias del héroe: ${formatPlayerHeroRate(report.heroes.find(h => h.hero === player.hero), Boolean(report.event.day2_start))}`;
      const body = get('detail-rows');
      body.replaceChildren();
      for (const r of details[name]) addRow(body, [r.round, (r.phase === 'Swiss' ? 'Suizo' : 'Eliminatoria') + (r.format ? ' · ' + r.format : ''), r.placeholder_opponent ? 'Rival sin identificar' : r.opponent, r.format === 'Booster Draft' ? 'No indicado (Draft)' : heroName(r.opponent_hero), ({ W:'Victoria', L:'Derrota', D:'Empate' }[r.outcome] || r.outcome) + (r.placeholder_opponent ? ' (excluida de la tasa)' : '')]);
      const detailTable = body.closest('table')!;
      const selectedHeader = detailTable.querySelector<HTMLTableCellElement>('th[aria-sort="ascending"],th[aria-sort="descending"]');
      if (selectedHeader) sortDOMTable(detailTable, selectedHeader.cellIndex, selectedHeader.getAttribute('aria-sort') === 'ascending' ? 'asc' : 'desc');
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

  function sortDOMTable(table: HTMLTableElement, column: number, direction: string) {
    const body = table.tBodies[0];
    const rows = Array.from(body.rows);
    const numeric = table.tHead!.rows[0].cells[column].dataset.sortType === 'number';
    const parsed = rows.map(row => {
      const text = row.cells[column]?.textContent?.trim() || '';
      const number = text.replace(/\./g, '').replace(',', '.').match(/^-?\d+(?:\.\d+)?/);
      return { row, value: numeric ? (number ? Number(number[0]) : null) : text };
    });
    for (const { row } of sortRows(parsed, 'value', direction, numeric ? 'number' : 'string')) body.append(row);
  }

  const playerColumns = [['player', 'string'], ['hero', 'string'], ['finish', 'string'], ['swiss_wins', 'number'], ['swiss_win_pct', 'number'], ['hero_swiss_win_pct', 'number'], ['all_wins', 'number']];
  const matchupColumns = [['hero', 'string'], ['opponent_hero', 'string'], ['matches', 'number'], ['wins', 'number'], ['win_pct', 'number']];
  root.querySelectorAll<HTMLTableElement>('table').forEach(table => {
    const body = table.tBodies[0];
    const cells = Array.from(table.tHead!.rows[0].cells);
    const isPlayers = body.id === 'player-rows';
    const isMatchups = body.id === 'matchup-rows';
    cells.forEach((header, column) => {
      const heading = header.textContent || '';
      const field = isPlayers ? playerColumns[column] : isMatchups ? matchupColumns[column] : undefined;
      const numeric = field ? field[1] === 'number' : body.id === 'hero-rows' ? column > 0 : body.id === 'detail-rows' ? column === 0 : column >= 3;
      header.dataset.sortType = numeric ? 'number' : 'string';
      header.setAttribute('aria-sort', 'none');
      const button = document.createElement('button');
      button.type = 'button';
      button.dataset.sortColumn = String(column);
      button.textContent = heading + ' ↕';
      button.title = `Ordenar por ${heading}`;
      header.replaceChildren(button);
      button.addEventListener('click', () => {
        const direction = header.getAttribute('aria-sort') === 'ascending' ? 'desc' : 'asc';
        cells.forEach(cell => { cell.setAttribute('aria-sort', 'none'); const control = cell.querySelector('button'); if (control) control.textContent = control.textContent!.replace(/ [↕↑↓]$/, ' ↕'); });
        header.setAttribute('aria-sort', direction === 'asc' ? 'ascending' : 'descending');
        button.textContent = heading + (direction === 'asc' ? ' ↑' : ' ↓');
        if (isPlayers && field) { playerSort = { key: field[0], type: field[1], direction }; playerPage = 0; void renderPlayers(); }
        else if (isMatchups && field) { matchupSort = { key: field[0], type: field[1], direction }; matchupPage = 0; void renderMatchups(); }
        else sortDOMTable(table, column, direction);
      });
    });
  });
}
