# FAB Colombia - Comunidad Flesh and Blood

Sitio web de la comunidad colombiana de Flesh and Blood TCG. Publica calendario de eventos, articulos, rankings, reportes competitivos, guias de formatos y herramientas de apoyo para torneos.

## Arquitectura Actual

El sitio es una aplicacion Astro estatica desplegada en Cloudflare Pages.

- **Framework**: Astro 7.
- **Output**: build estatico en `dist/`.
- **Deployment**: Cloudflare Pages, configurado por `wrangler.toml` con `pages_build_output_dir = "./dist"`.
- **Runtime**: no usa adapter de Cloudflare ni Workers runtime para servir paginas.
- **Estilos**: Tailwind CSS 4 mediante `@tailwindcss/vite`, mas CSS global en `src/css/base.css`.
- **Contenido editorial**: Astro Content Collections desde `src/content/posts`.
- **Datos estructurados**: JSON en `src/data` y artefactos de estadisticas en `public/r2/stats`.
- **Package manager**: Yarn 4.

La decision de build estatico es intencional: el repositorio no tiene endpoints server-side ni uso de cookies, sesiones o `Astro.locals`. Las rutas dinamicas se prerenderizan durante el build.

## Despliegue

Cloudflare Pages ejecuta el comando de build y publica `dist/`.

Configuracion relevante:

- `wrangler.toml`: nombre del proyecto, fecha de compatibilidad y directorio de salida.
- `package.json`: `yarn build` / `npm run build` ejecuta `astro build`.
- `.node-version`: fija la version de Node usada por Cloudflare.

No agregues configuracion de Workers como `main`, `assets`, `rules` o bindings generados por `@astrojs/cloudflare` mientras el sitio siga siendo estatico en Pages. Esas claves pertenecen a despliegues Workers y Cloudflare Pages las rechaza en este proyecto.

## Estructura Del Repositorio

```text
/
├── astro.config.mjs        # Astro, MDX y Tailwind 4 via Vite
├── wrangler.toml           # Configuracion de Cloudflare Pages
├── package.json            # Scripts y dependencias JS
├── src/
│   ├── components/         # Componentes Astro reutilizables
│   ├── content.config.ts   # Content Collections
│   ├── content/posts/      # Posts Markdown/MDX del blog
│   ├── css/                # Estilos globales y temas
│   ├── data/               # Eventos, rankings y datos del sitio
│   ├── layouts/            # Layout base
│   ├── pages/              # Rutas Astro
│   └── utils/              # Carga de datos y utilidades de calendario
├── public/
│   ├── images/             # Assets publicos
│   └── r2/stats/           # Artefactos publicados de estadisticas
├── tools/
│   ├── challonge/          # Automatizacion de torneos Challonge
│   └── stats/              # Pipeline Python de estadisticas
└── static/                 # HTML legado usado como referencia/archivo
```

## Rutas Principales

- `/`: pagina de inicio.
- `/calendar`: calendario de eventos.
- `/blog`: indice del blog.
- `/blog/[slug]`: posts prerenderizados desde Content Collections.
- `/rankings`: rankings activos e historicos desde `src/data/rankings.json`.
- `/competitivo`: reportes y datos competitivos.
- `/reportes`, `/reportes/2025`, `/reportes/2026`: reportes anuales.
- `/jugador/[year]/[slug]`: perfiles de jugadores generados desde `public/r2/stats`.
- `/formatos`, `/formato/cc`, `/formato/living-legend`, `/formato/sage`: guias de formatos.
- `/mechanics`, `/equipment_mechanics`: guias de mecanicas.
- `/codigo-de-conducta`: codigo de conducta.
- `/oauth/callback`: pagina estatica para copiar codigos OAuth de Challonge.

## Comandos

| Comando | Uso |
| --- | --- |
| `yarn install --immutable` | Instala dependencias respetando `yarn.lock`. |
| `yarn dev` | Servidor local Astro en `localhost:4321`. |
| `yarn build` | Genera el sitio estatico en `dist/`. |
| `yarn preview` | Build y preview local con Wrangler Pages. |
| `yarn deploy` | Build y deploy manual con Wrangler Pages. |
| `yarn astro ...` | Acceso directo al CLI de Astro. |

Usa Yarn para cambios de dependencias. El archivo `package-lock.json` existe por historia del repo, pero el lock operativo del proyecto es `yarn.lock`.

## Contenido Del Blog

Los posts viven en `src/content/posts` y se cargan con `glob()` en `src/content.config.ts`.

Frontmatter esperado:

```md
---
title: "Titulo del post"
author: "Autor"
description: "Descripcion corta"
publishDate: 2026-01-27
---

Contenido en Markdown o MDX.
```

El slug publico sale del `id` generado por Astro para el archivo. Por ejemplo, `src/content/posts/mi-guia.mdx` genera `/blog/mi-guia/`.

## Datos Del Sitio

### Calendario

Los eventos se guardan por trimestre en `src/data/Eventos_Comunidad_*.json`.

El trimestre activo se selecciona en `src/utils/dataLoader.js`:

```js
import eventsData from '../data/Eventos_Comunidad_Q2_2026.json';
```

Para cambiar el calendario visible, agrega o actualiza el JSON trimestral y cambia ese import.

Campos comunes de evento:

```json
{
  "Date": "2026-04-11",
  "Day": "Sabado",
  "Event": "Classic Constructed",
  "Time": "6 PM",
  "Location": "Chaos Store",
  "Ciudad": "Cali",
  "Emoji": "⚔️",
  "EventType": "CC"
}
```

### Rankings

Los rankings se editan en `src/data/rankings.json`.

```json
{
  "name": "Nombre del ranking",
  "dateStart": "2026-01-01",
  "dateEnd": "2026-12-31",
  "link": "https://challonge.com/..."
}
```

### Estadisticas Competitivas

Los reportes publicados viven bajo `public/r2/stats/<year>/`:

- `stats.json`: resumen anual.
- `players/index.json`: indice de jugadores.
- `players/<slug>.json`: datos de perfil.
- `players/<slug>-radar.png`: visual de radar.
- matrices, rankings ELO, timelines y graficas anuales.

Las paginas `/reportes/[year]` y `/jugador/[year]/[slug]` leen estos archivos como assets publicos durante el build.

## Herramientas Auxiliares

### Challonge

`tools/challonge/create_tournament.py` crea o actualiza torneos desde el calendario.

Ejemplos:

```bash
python tools/challonge/create_tournament.py --authorize
python tools/challonge/create_tournament.py --list
python tools/challonge/create_tournament.py --dry-run 2026-04-11
python tools/challonge/create_tournament.py --create 2026-04-11
python tools/challonge/create_tournament.py --create-range 2026-04-01 2026-04-30
```

`tools/challonge/cleanup_tournaments.py` lista o elimina torneos vacios:

```bash
python tools/challonge/cleanup_tournaments.py --list-empty
python tools/challonge/cleanup_tournaments.py --dry-run
```

Los archivos OAuth locales (`oauth_config.json`, `oauth_token.json`) estan ignorados por Git.

### Estadisticas

El pipeline Python de estadisticas esta en `tools/stats`.

Instalacion recomendada:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r tools/stats/requirements.txt
```

Comandos principales:

```bash
python tools/stats/cli.py fetch --start 2026-01-01 --end 2026-06-30
python tools/stats/cli.py analyze
python tools/stats/cli.py viz
python tools/stats/cli.py all --start 2026-01-01 --end 2026-06-30
python tools/stats/generate_yearly_reports.py
python tools/stats/generate_player_profiles.py
```

El cache raw de Challonge vive en `tools/stats/data/raw`. Los artefactos listos para publicar se copian a `public/r2/stats`.

## Flujo De Trabajo Recomendado

1. Crea una rama desde `master`.
2. Instala dependencias con `yarn install --immutable`.
3. Ejecuta `yarn dev` para desarrollo local.
4. Antes de abrir PR, ejecuta `yarn build`.
5. Si cambias dependencias, usa Yarn y commitea `package.json`, `yarn.lock` y cualquier cambio necesario en `.yarn/`.
6. Si cambias datos publicados, verifica las rutas afectadas en `dist/` o con `yarn dev`.

## Recomendaciones De Mantenimiento

- Mantener el sitio estatico mientras no existan rutas server-side reales. Si se agregan endpoints, sesiones, Actions o Server Islands, revaluar si debe migrarse a Cloudflare Workers.
- Mantener `wrangler.toml` enfocado en Pages; no mezclar configuracion Workers en el mismo archivo.
- Documentar cada nuevo dataset en esta README cuando se agregue una nueva seccion visible del sitio.
- Evitar commitear caches Python, salidas temporales o tokens OAuth.
- Actualizar `src/utils/dataLoader.js` al cambiar de trimestre y retirar eventos obsoletos cuando ya no deban mostrarse.

## Links Utiles

- [Astro Documentation](https://docs.astro.build)
- [Astro Tailwind guide](https://docs.astro.build/en/guides/styling/#tailwind)
- [Cloudflare Pages](https://developers.cloudflare.com/pages/)
- [FAB Official Rules](https://fabtcg.com/resources/rules/)
- [Challonge FABCO](https://challonge.com/communities/fabco)
