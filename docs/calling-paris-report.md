# Reporte de Calling: Paris

La página `/reportes/calling-paris/` integra el análisis de 18 páginas de cobertura guardadas. Se accede desde `/competitivo` y `/reportes` y comparte el layout, la navegación y los temas del sitio.

## Datos y criterios

Los archivos publicados están en `public/data/calling-paris/`. `matches.csv` conserva las 5.181 filas extraídas (15 rondas suizas y tres eliminatorias); `audit.json` conserva los nombres y hashes SHA-256 de las 18 páginas de origen. Los recursos descargados de esas páginas no son necesarios para servir ni regenerar el reporte.

Se cuentan 1.418 nombres distintos, 26 sin héroe registrado y seis resultados contra el marcador «Player 2». Los marcadores no se cuentan como personas ni partidas jugadas. Se conservan las victorias registradas, las dobles derrotas y los empates. No se inventan héroes, byes ni desempates oficiales.

Las tasas suizas de jugador y héroe se muestran juntas. La tasa del héroe agrupa las partidas de todos sus jugadores, incluido el jugador de la fila. La tasa sin espejos excluye partidas con héroes desconocidos. Los criterios completos están en la página y en `report.md`.

## Regeneración

Desde los datos normalizados incluidos en el repositorio:

```sh
python -B tools/stats/analyze_saved_results.py \
  --matches public/data/calling-paris/matches.csv \
  --output public/data/calling-paris
```

Si están disponibles las capturas HTML originales en `Scraping/`:

```sh
python -B tools/stats/analyze_saved_results.py --output public/data/calling-paris
```

El script solo utiliza la biblioteca estándar de Python. Genera los CSV, la auditoría, `summary.json`, las rondas por jugador y el reporte independiente. El sitio se construye con los archivos generados; no ejecuta Python ni solicita datos externos en producción.

`summary.json` se solicita cuando se utilizan búsquedas o paginación; las rondas se descargan al seleccionar un jugador. El HTML inicial ya incluye el resumen, el Top 8, todos los héroes, los primeros 25 jugadores y enfrentamientos, y las rondas del campeón. Los CSV dan acceso al conjunto completo sin JavaScript. El reporte independiente está en inglés; la página integrada está en español.

## Validación

```sh
python -B -m unittest discover -s tests -p 'test_saved_tournament_results.py' -v
node --test tests/calling-paris.test.mjs
npm run build
```

Los tests verifican la contabilidad de resultados, los casos de héroe desconocido y rival sin identificar, la clasificación de eliminatorias, las tasas agregadas por héroe, la búsqueda con acentos, los filtros y la paginación.
