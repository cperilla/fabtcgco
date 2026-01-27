# FAB Colombia - Comunidad Flesh and Blood

Sitio web de la comunidad de Flesh and Blood TCG en Colombia. Incluye calendario de eventos, blog, rankings y guías de mecánicas del juego.

## Tech Stack

- **Framework**: [Astro 5.x](https://astro.build/) con SSR
- **Styling**: Tailwind CSS + CSS custom properties
- **Content**: Astro Content Collections con MDX para blog
- **Deployment**: Cloudflare Pages via Wrangler
- **Package Manager**: Yarn 4.x

## Estructura del Proyecto

```
/
├── public/
│   ├── images/              # Imágenes estáticas (logos, screenshots)
│   └── css/fontawesome/     # Font Awesome icons
├── src/
│   ├── components/          # Componentes Astro
│   │   ├── Header.astro     # Navegación principal
│   │   ├── Footer.astro     # Footer con theme switcher
│   │   ├── EventTicket.astro # Tarjeta de evento (calendario)
│   │   └── interfaces.ts    # Tipos e interfaces + utilidades ICS/Google Calendar
│   ├── content/
│   │   └── posts/           # Blog posts en MDX
│   ├── css/
│   │   ├── base.css         # Estilos globales y temas
│   │   └── cards.css        # Estilos de tarjetas (legacy)
│   ├── data/
│   │   ├── Eventos_Comunidad_Q1_2026.json  # Eventos del trimestre actual
│   │   └── rankings.json    # Rankings de la comunidad
│   ├── layouts/
│   │   └── Layout.astro     # Layout base
│   ├── pages/
│   │   ├── index.astro      # Home
│   │   ├── calendar.astro   # Calendario de eventos
│   │   ├── blog.astro       # Índice del blog
│   │   ├── blog/[slug].astro # Posts individuales
│   │   ├── rankings.astro   # Rankings de la comunidad
│   │   ├── mechanics.astro  # Mecánicas de juego
│   │   ├── equipment_mechanics.astro # Mecánicas de equipos
│   │   └── codigo-de-conducta.astro  # Código de conducta
│   └── utils/
│       ├── dataLoader.js    # Carga datos de eventos (cambiar trimestre aquí)
│       └── calendarUtils.js # Utilidades de calendario
└── package.json
```

## Comandos

| Comando | Descripción |
|---------|-------------|
| `yarn dev` | Servidor de desarrollo en `localhost:4321` |
| `yarn build` | Build de producción en `./dist/` |
| `yarn preview` | Build + preview local con Wrangler |
| `yarn deploy` | Build + deploy a Cloudflare Pages |

## Gestión de Datos

### Eventos del Calendario

Los eventos se guardan en archivos JSON por trimestre en `src/data/`. Estructura:

```json
{
  "Date": "2026-01-15",
  "Day": "Miércoles",
  "Event": "Classic Constructed",
  "Time": "6 PM",
  "Location": "Chaos Store",
  "Ciudad": "Cali",
  "Emoji": "⚔️",
  "EventType": "CC"
}
```

**Para cambiar de trimestre**: Editar el import en `src/utils/dataLoader.js`.

### Rankings

Editar `src/data/rankings.json`:

```json
{
  "name": "Nombre del Ranking",
  "dateStart": "2026-01-01",
  "dateEnd": "2026-03-31",
  "link": "https://challonge.com/..."
}
```

Los rankings activos/pasados se calculan automáticamente en el cliente.

### Blog Posts

Crear archivos MDX en `src/content/posts/`:

```mdx
---
title: "Título del Post"
author: "Autor"
description: "Descripción corta"
publishDate: 2026-01-27
---

Contenido en Markdown...
```

## Temas

El sitio usa colores oficiales de FAB:
- `#91160d` - Tamarillo (rojo)
- `#765d2f` - Old Copper (bronce)
- `#fcf0ef` - Linen (crema)

Temas adicionales disponibles via `data-theme` en HTML:
- `highseas` - High Seas
- `highseas-light` - High Seas Light
- `wtr` - Welcome to Rathe
- `hunted` - The Hunted

## Links Útiles

- [Astro Documentation](https://docs.astro.build)
- [FAB Official Rules](https://fabtcg.com/resources/rules/)
- [Challonge Community](https://challonge.com/communities/fabco)
