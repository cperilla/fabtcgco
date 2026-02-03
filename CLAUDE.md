# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FABCOTCG is a Spanish-language community website for Flesh and Blood TCG events in Colombia. It features an event calendar, blog, and game mechanics reference pages.

## Tech Stack

- **Framework**: Astro 5.x with server-side rendering
- **Styling**: Tailwind CSS with CSS custom properties for theming
- **Content**: Astro Content Collections with MDX for blog posts
- **Deployment**: Cloudflare Pages via Wrangler
- **Package Manager**: Yarn 4.x

## Commands

```bash
yarn dev          # Start dev server at localhost:4321
yarn build        # Build for production to ./dist/
yarn preview      # Build and preview with Wrangler locally
yarn deploy       # Build and deploy to Cloudflare Pages
yarn cf-typegen   # Generate Cloudflare Workers types
```

## Architecture

### Data Flow for Events

Events are stored as quarterly JSON files in `src/data/` (e.g., `Eventos_Comunidad_Q4_2025.json`). The active quarter is imported in `src/utils/dataLoader.js`. To switch quarters, update the import path in that file.

Event JSON structure:
```json
{
  "Date": "2025-10-02",
  "Day": "Jueves",
  "Event": "Silver Age",
  "Time": "5 PM",
  "Location": "Chaos Store",
  "Ciudad": "Cali",
  "Emoji": "🌀",
  "EventType": "Sage"
}
```

Calendar utilities in `src/utils/calendarUtils.js` transform this data for display (grouping by month, generating calendar grids).

Living Legend (LL) events are scheduled for the last Saturday of each month.

### Blog Content

Blog posts are MDX files in `src/content/posts/`. Schema defined in `src/content.config.ts`:
- `title` (string, required)
- `author` (string, required)
- `description` (string, optional)
- `publishDate` (date, required)

### Theme System

Themes are CSS custom properties in `src/css/base.css`, activated via `data-theme` attribute on HTML. Available themes: default, high-seas, high-seas-light, welcome-to-rathe, hunted.

### Key Components

- `src/components/interfaces.ts` - Event interfaces and calendar utility functions (ICS generation, Google Calendar links)
- `src/layouts/Layout.astro` - Base layout wrapping all pages
- `src/components/Calendar.astro` / `CalendarDay.astro` / `CalendarEvent.astro` - Calendar rendering

## Tools
### Challonge

 - There are two challonge APIs v1 and v2.1, v1 is deprecated.
 - New work should never use v1 api or urls
 - Local keys are located in the keys files at the base of the repo as env variables CHALLONGE CLIENT KEY AND SECRETS and one OATH Code obtained from the oauth login

### Tournament creation tool

Uses the calendar data defined tournaments and creates them according the templates rules 

## Language

All content is in Spanish. Date formatting uses Spanish locale via date-fns.
