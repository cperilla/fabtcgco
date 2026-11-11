# Reportes de los torneos de París

Los tres reportes comparten `TournamentReport.astro`, la búsqueda de jugadores, sus resultados por ronda, los intervalos de confianza y las tablas ordenables:

- `/reportes/calling-paris/`: Classic Constructed; día 1 rondas 1–9, día 2 suizo 10–15, eliminatorias 16–18.
- `/reportes/showdown-paris-2026/`: Silver Age; diez rondas suizas en un solo día y eliminatorias 11–13. No se inventa un día 2.
- `/reportes/world-championship-paris-2026/`: evento mixto; suizo 1–16 y eliminatorias 17–19. Las rondas 6–11 son Booster Draft según la clave de formatos guardada. **Draft solo cuenta para jugadores**, nunca para tasas de héroes, sus intervalos ni enfrentamientos.

La configuración está en `tools/stats/tournaments.json`. Cada evento publica CSV, JSON, un reporte HTML independiente y un análisis Markdown en `public/data/<evento>/`. Solo se versionan datos normalizados y hashes de fuentes; las capturas HTML y sus recursos descargados permanecen fuera del PR.

## Límite de los datos de Worlds

`Flesh and Blood TCG-WorldsParisResults16.html` tiene el encabezado y las mismas partidas de la ronda 15. El extractor compara encabezados y filas, descarta esa copia exacta y anota el problema en `audit.json`. Falta la ronda 16; no se extrapolan partidas, registros ni tasas. La recuperación desde el endpoint oficial devolvió HTTP 403. La página y sus descargas muestran que el día 2 y los registros totales están incompletos.

El corte diario de Worlds entre rondas 8 y 9 se infiere de la reducción de participantes y los bloques de Draft; la clave guardada confirma formatos, pero no identifica días. Esa inferencia figura en el reporte. Las tasas de héroes del día 1 solo usan CC 1–5; las de día 2 solo usan CC 12–15 disponible. Los jugadores sí conservan Draft 6–11, con desgloses CC/Draft en la tabla y el CSV. La columna de héroe del detalle de Draft se muestra como «No indicado (Draft)» para no atribuir al Draft el héroe de CC que repite la cobertura.

## Confianza y muestras

Cada héroe tiene tasas globales y diarias, intervalos bootstrap percentiles del 95%, partidas y jugadores contribuyentes. Se remuestrean jugadores completos 2.000 veces, con semilla reproducible y todas sus partidas juntas. No se estima intervalo con menos de dos jugadores, sin datos, con héroe desconocido o sin variación entre réplicas. Las muestras pequeñas se señalan como inestables. Los intervalos Wilson sin espejos existentes en el CSV se mantienen como una aproximación distinta por partida.

La columna «Victorias sin rival identificado» fue retirada de la interfaz. Los casos continúan en los datos y se excluyen de las tasas de partidas jugadas.

## Ordenamiento

Todos los encabezados de tabla activan orden ascendente/descendente, con botones accesibles y `aria-sort`. Nombres de héroes y jugadores usan comparación de texto en español; tasas y cantidades usan valores numéricos. En celdas compuestas se usa el valor principal: tasa para una celda con intervalo, victorias para V–D–E. Valores no disponibles quedan al final en ambos sentidos.

Las tablas paginadas ordenan el conjunto filtrado completo **antes** de paginar, y mantienen el orden al cambiar filtros o página. Los HTML independientes también incluyen búsqueda y ordenamiento sin dependencias externas.

## Regenerar

Desde las capturas, para un evento nuevo:

```sh
python -B tools/stats/analyze_saved_results.py --event showdown-paris-2026 --output public/data/showdown-paris-2026
python -B tools/stats/analyze_saved_results.py --event world-championship-paris-2026 --output public/data/world-championship-paris-2026
```

Desde datos normalizados incluidos en el PR (también sirve para `calling-paris`):

```sh
python -B tools/stats/analyze_saved_results.py --event showdown-paris-2026 --matches public/data/showdown-paris-2026/matches.csv --output public/data/showdown-paris-2026
```

Validación:

```sh
python -B -m unittest discover -s tests -p 'test_*tournament_results.py' -v
node tests/calling-paris.test.mjs
npm run build
```
