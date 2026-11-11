# Verificación editorial: París y el crecimiento de FAB Colombia

Entrada: `src/content/posts/paris-2026-crecer-jugando.mdx`.

## Récord y alcance

El récord se atribuye al **Calling de París**, no al Mundial, a la suma de inscripciones ni a un total de asistentes únicos al fin de semana.

Se verificó directamente el listado de videos del canal oficial [Flesh and Blood TCG](https://www.youtube.com/@fabtcg/videos?hl=en), cuya metadata identifica al canal `UCQW-Jql3r6YlBxl1JzJmFJw` como oficial y cuyo `ownerUrls` contiene `http://www.youtube.com/@fabtcg`. Su listado contiene el video `TrqSDGykAu0` con este título:

> Top 8 of Calling Paris | The Largest Flesh and Blood Tournament Ever!

Fuente primaria enlazada en el artículo: [video oficial](https://www.youtube.com/watch?v=TrqSDGykAu0). El HTML de la pestaña de videos se obtuvo directamente por HTTPS; el navegador de investigación no pudo cargar la página individual. La metadata utilizada para verificar el título queda resumida arriba; los HTML temporales no se incluyen en el PR.

La [publicación oficial de @fabtcg](https://x.com/fabtcg/status/2119338407646093532) también presenta París como su mayor Calling. Su texto y el enlace al original se contrastaron mediante un [espejo de la publicación](https://xitter.gq/fabtcg/status/2119338407646093532). Esta segunda fuente confirma el alcance específico del récord; el título del video respalda la formulación más amplia atribuida al canal oficial.

## Fecha y lugar

La [página del organizador Fanfinity](https://www.fanfinity.gg/event/flesh-and-blood-world-championship-paris-2026/) indica:

- Encuentro de París: 5–8 de noviembre de 2026.
- Recinto: Paris Expo Porte de Versailles, pabellón 5, París, Francia.
- Calling en Classic Constructed y Sunday Showdown en Silver Age dentro de la programación.

El artículo usa las fechas del encuentro completo y no las presenta como cuatro días de Calling.

## Jugadores y resultados

Los tres `summary.json` de `public/data/` y sus resultados normalizados verifican:

| Evento | Nombres observados | Ganador | Héroe del ganador |
| --- | ---: | --- | --- |
| Calling | 1.418 | Matt Muus | Teklovossen, Esteemed Magnate |
| Mundial | 561 | Nicolas Jamoulle | Fang, Dracai of Blades |
| Showdown | 632 | Davorin Pokorn | Ira, Crimson Haze |

El nombre del campeón del Mundial aparece como `nicolas Jamoulle` en el resultado guardado; el artículo normaliza la inicial. El anuncio de campeón de la cuenta oficial, visible en la misma fuente social, confirma Nicolas Jamoulle. Los ganadores se identifican en las finales de rondas 18, 19 y 13, respectivamente.

Son nombres identificados en capturas, no cifras presentadas como inscripciones oficiales. El cruce de los tres listados produce **1.831 jugadores únicos observados** y **2.611 participaciones**. Hay 1.130 nombres en un solo evento, 622 en dos y 79 en los tres. Las coincidencias por parejas son: Calling/Mundial 312, Calling/Showdown 366, Mundial/Showdown 181; cada cifra por pareja incluye a los 79 de los tres eventos. Así, 2.611 − 312 − 366 − 181 + 79 = 1.831.

Se normalizan Unicode NFKC, mayúsculas y espacios, conservando acentos. En estas fuentes coinciden tanto el cruce normalizado como el cruce exacto: 1.831 nombres, sin variantes ni conflictos de país. No se cuentan marcadores «Player 2». Al no tener identificadores únicos de GEM, no se pueden descartar homónimos; el alcance son jugadores observados en estos tres torneos, no todo el público o los eventos paralelos.

Solo aparecen en cada listado: Calling 819, Mundial 147, Showdown 164. El resto de cada torneo también está en alguno de los otros dos. El detalle se publica en `public/data/paris-2026/players.csv`, y `attendance.json` registra los totales, cruces, método y hashes de las fuentes. Regenerar con `python -B tools/stats/summarize_paris_attendance.py` después de regenerar las estadísticas de los torneos.

El artículo enlaza las limitaciones del reporte del Mundial y menciona que falta ronda 16. No publica el registro global incompleto del campeón. Draft se limita a registros de jugadores y no se atribuye a las estadísticas de héroes.

## Contexto local y enlaces

La perspectiva comunitaria, el papel de Chaos Store y los objetivos de competencia abierta provienen del encargo editorial del usuario. Los caminos de entrada y los enlaces se contrastaron con `/empezar`, `/mesa-inicial`, `/formato/sage`, `/formato/cc` y `/calendar`.

No se incorporaron horarios fijos, precios, promesas de préstamo sin coordinación ni eventos nuevos. Se remite al calendario para fechas y sedes vigentes. El artículo utiliza la colección y el layout existentes del blog, sin nuevos componentes ni cambios en la navegación.
