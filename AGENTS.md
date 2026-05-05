# AGENTS.md

This file provides guidance to coding agents (Claude Code, Codex, etc.) when working with code in this repository.

## Project Overview

**Banana-CongresoGT** (branded as **Guate No Olvida**) is a static site that lets Guatemalan citizens analyze the behavior of the **X Legislatura (2024–2027)** of the Guatemalan Congress: voting records, attendance, ideological similarity between congressmen, and group cohesion. The site is updated roughly twice per week from the official congress website.

The repository contains two independent components:

1. **Astro frontend** (`/src`): Builds a fully static site at build time using CSV data loaded into an in-memory SQLite database via `better-sqlite3`. Zero/minimal client-side JS.
2. **Python data pipeline** (`/pipeline`, `main.py`): Scrapes the official congress website with Playwright, persists in PostgreSQL, then transforms and exports the data to CSV files in `/data` (the source of truth for the frontend).

Design priority: extremely fast, lightweight, highly graphical pages that help users **compare and remember** how representatives voted.

## Tech Stack

- **Frontend**: Astro 6, TypeScript, `better-sqlite3` (build-time in-memory DB), `csv-parse`, Chart.js. Spanish UI.
- **Backend pipeline**: Python ≥ 3.13, Playwright (chromium, headless), BeautifulSoup, pandas, NumPy, SQLAlchemy, psycopg2 (PostgreSQL).
- **Tooling**: `mise` (python 3.14, node 25), `uv` (Python deps), `npm` (Node deps), `husky` (git hooks).
- **Persistence**: PostgreSQL for raw scraped data; an in-memory SQLite reconstructed from CSVs at build time for the site.

## Commands

### Astro Frontend

```bash
npm install        # Install dependencies
npm run dev        # Development server (loads /data/*.csv into in-memory SQLite on startup)
npm run build      # Production build → /dist
npm run preview    # Preview production build
```

### Python Pipeline

Requires a `.env` file in the project root with `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` (see `.env.example`). Environment is managed by `mise`; Python deps by `uv` (see `pyproject.toml`, `uv.lock`).

```bash
python main.py scrape --action all              # Scrape everything (congressmen, voting, attendance, sessions)
python main.py scrape --action load_sessions    # (default) Scrape only new sessions
python main.py scrape --action load_congressmen # Scrape congressmen catalog
python main.py scrape --action load_voting      # Scrape voting records
python main.py scrape --action load_attendance  # Scrape attendance records
python main.py scrape --action update_congressmen # Update profile data (block, district)
python main.py scrape --session-start 41168     # Start scraping at a specific session ID
python main.py scrape --log-level DEBUG         # DEBUG/INFO/WARNING/ERROR (default INFO)

python main.py transform                        # Read PostgreSQL → compute stats → write /data/*.csv
python main.py db                               # Initialize PostgreSQL schema + initial_data from /database/*.sql
python main.py pipeline                         # Full pipeline: scrape new sessions + transform
```

The pipeline is incremental: `run_pipeline()` looks up the last session in PostgreSQL and resumes from `last + 1`. Errors are appended to `.report.txt` (gitignored).

## Architecture

### Data Flow

```
congress.gob.gt
     ↓  pipeline/scraper.py  (Playwright + BeautifulSoup, DataTables pagination, retry logic)
PostgreSQL (raw scraped data)
     ↓  pipeline/transform_data.py  (pandas/SQLAlchemy → aggregations, Rice Index, similarity matrix)
/data/*.csv  (committed, source of truth for the frontend)
     ↓  src/lib/db.ts  (loads all CSVs into in-memory SQLite at module import)
     ↓  src/lib/queries.ts  (typed query functions; snake_case → camelCase aliasing)
src/pages/**/*.astro  (static HTML; dynamic routes pre-render via getStaticPaths)
```

Note: the frontend never talks to PostgreSQL. The CSVs in `/data` are the only contract between pipeline and site. CSVs are committed to git so the site can be rebuilt without the pipeline.

### Frontend Structure

- **`src/lib/db.ts`**: Bootstraps the in-memory SQLite database. Defines the schema, reads every CSV in `/data`, and bulk-inserts via prepared statements wrapped in transactions. Runs once on module import.
- **`src/lib/queries.ts`**: All data-access functions. Returns typed objects with `camelCase` aliases for `snake_case` columns. Includes count/list/detail queries, stats by period (total / per-year), session/voting breakdowns, and similarity lookups.
- **`src/lib/mappers.ts`**: Enum constants (`VOTE_TYPE`, `ATTENDANCE_STATUS`, `SESSION_TYPE`, `CONGRESSMAN_STATUS`, `MAJORITY`, `WITH_MAJORITY`, `PERIOD`) plus their Spanish display strings and helper functions (`getVoteString`, `getSessionTypeString`, `getCongressmanStatusString`).
- **`src/lib/paths.ts`**: URL builders for routing. Top-level paths: `/diputados`, `/distritos`, `/bancadas`, `/partidos`, `/sesiones`, `/votaciones`, `/rankings`, `/compare`. Asset helpers: `getCongressmanPhotoPath`, `getDistrictImagePath`, `getBlockImagePath`, `getPartyImagePath`.
- **`src/lib/util.ts`**: Generic utilities (e.g., `formatDate` using `es-GT` locale).
- **`src/layouts/Layout.astro`**: Single global layout. Sticky navbar (responsive with mobile hamburger), `lang="es"`, page title pattern `"{title} | Guate No Olvida"`.
- **`src/pages/`**: File-based routing.
  - Top-level pages: `index.astro`, `rankings.astro`, `compare.astro`.
  - Dynamic routes (each in its own folder): `bancadas/[id]`, `diputados/[id]`, `distritos/[id]`, `partidos/[id]`, `sesiones/[id]`, `votaciones/[id]`. Each `[id].astro` defines `getStaticPaths()` from the corresponding `getAll*Id()` query and pre-renders one page per entity.
- **`src/components/`**: Reusable Astro components — Chart.js wrappers (`BarChart`, `LineChart`, `DoughnutChart`, `RiceIndexChart`, `AttendanceCharts`, `VotesCharts`) and data display (`CongressmanCard`, `OrgCard`, `MembersGrid`, `VotationCard`, `CongressmanActionCard`, `GroupedActionTabs`, `ExpandableGroup`, `OrgDetailLayout`, `PageHero`, `MarkedMap`).
- **`src/scripts/chart-processing.ts`**: Client-side chart bootstrapping. Reads serialized chart data from `data-*` attributes on `.banana-chart-container` nodes and instantiates Chart.js charts. This is the main piece of client-side JS.
- **`src/styles/`**: `global.css`, `charts.css`. Accent color via CSS var `--accent-color`.
- **`public/`**: Static assets served as-is.
  - `public/diputados/{id}.jpg` — congressman photos.
  - `public/distritos/{id}.svg` — district maps/icons.
  - `public/bancadas/{id}.svg` — block logos.
  - `public/partidos/{id}.svg` — party logos.
  - `favicon.svg`.

### Data Model (in-memory SQLite, reconstructed each build)

**Core entity tables**: `blocks`, `parties`, `districts`, `congressmen`, `sessions`, `voting`, `votes`, `attendance`.

**Pre-aggregated stat tables** (computed by `pipeline/transform_data.py`): `congressman_stats`, `party_stats`, `district_stats`, `block_stats`, `congressman_similarity`.

Stats tables share a `period` column:
- `"total"` — all-time aggregate.
- A year string (`"2024"`, `"2025"`, `"2026"`, `"2027"`) — year-scoped aggregate.

`congressman_similarity` is **double-stored** (a row for `(c1, c2)` and another for `(c2, c1)`) so lookups by either side hit a single row.

### Status / Enum Conventions

Numeric enums are used end-to-end (Postgres → Python `IntEnum` → CSV → SQLite → TypeScript constants):

- `CONGRESSMAN_STATUS`: `ACTIVE=0`, `INACTIVE=1`
- `SESSION_TYPE`: `ORDINARY=0`, `EXTRAORDINARY=1`, `SOLEMN=2`
- `ATTENDANCE_STATUS`: `PRESENT=0`, `ABSENT=1`, `LICENSE=2`
- `VOTE_TYPE`: `IN_FAVOR=0`, `AGAINST=1`, `ABSENT=2`
- `MAJORITY`: `IN_FAVOR=0`, `AGAINST=1`, `TIE=2`
- `WITH_MAJORITY`: `YES=0`, `NO=1`, `NA=2`

Independent congressmen (no block) use `block_id = -1` after transformation (Postgres NULL is replaced with -1 in `transform_data.py`); UI displays "Independiente" / "Independientes" / "Ind." via `COALESCE(b.short_name, ...)`.

### Python Pipeline Structure

- **`main.py`**: CLI entry point with `argparse` subcommands (`scrape`, `transform`, `db`, `pipeline`).
- **`pipeline/scraper.py`**: Playwright scraper for `congreso.gob.gt`. Hard-coded `BLOCK_MAP` and `DISTRICT_MAP` translate normalized profile-page strings to DB IDs. Uses normalized name matching (lowercase, accent-stripped, space-stripped) against a congressman key/alias dictionary. Handles DataTables pagination by selecting `length="-1"`.
- **`pipeline/transform_data.py`**: The analytical core. Reads all PostgreSQL tables, casts ENUMs to int, merges sessions to attach a `period` (year) to every vote/attendance row, then computes:
  - **Voting aggregates** per voting (counts of in-favor/against/absent, attendance breakdown, majority outcome).
  - **`with_majority`** label per individual vote (yes/no/na).
  - **Sequential numbering**: chronological `voting_number` across all voting and per-session `session_voting_number`.
  - **Per-congressman stats** by period and total.
  - **Group stats (party / district / block) with the Rice Index**: per-voting cohesion `|in_favor − against| / (in_favor + against)`, averaged across votings.
  - **Congressman similarity**: for every pair of congressmen, restrict to votings where both were present (non-absent), compute Pearson correlation on `{IN_FAVOR=+1, AGAINST=-1}` vectors plus `agreement_percentage` and `common_votes`. Skipped when fewer than 2 common votes; pairs are stored both directions.
- **`pipeline/db.py`**: Raw psycopg2 helpers — connection, schema bootstrap, idempotent `INSERT ... ON CONFLICT DO UPDATE` for every entity, `get_last_session()` for incremental scraping, `get_congressmen_dict()` (merges `congressmen.key` and `congressmen_aliases.alias` for name matching).
- **`pipeline/db_initializer.py`**: Thin wrapper running `db.init_db()` + `db.insert_initial_data()` against `/database/schema.sql` and `/database/initial_data.sql`.
- **`pipeline/pipeline.py`**: Glues incremental scrape + transform.
- **`pipeline/logger.py`**: Custom `Log` class with levels `DEBUG/INFO/WARNING/ERROR`. ERRORs are appended to `.report.txt`.
- **`pipeline/samples/`**: Reference HTML / data samples used while developing scrapers.

### Postgres Schema

Defined in `/database/schema.sql`. Uses ENUM types (`congressman_status`, `session_type`, `attendance_status`, `vote_type`) and FK cascades for `voting → sessions`, `votes → voting/congressmen`, `attendance → sessions/congressmen`. There is a `congressmen_aliases` table for matching scraped names to canonical congressman IDs.

Note: the Postgres schema is the *raw* model. Columns like `voting.voting_number`, `votes.with_majority`, `voting.majority`, and the `period` derivation are produced by `transform_data.py` and only exist in the CSVs and the in-memory SQLite (the SQLite schema in `src/lib/db.ts` is the authoritative shape for the frontend).

## Conventions

### Language Rules

- **Code**: All code, identifiers, function names, comments, and commit messages must be in **English**.
- **UI / content**: All user-facing text, page titles, labels, and copy must be in **Spanish** (e.g., "Diputados", "Bancadas", "A Favor", "Independiente").
- **Naming**: Use full words, no abbreviations (e.g., `attendance_percentage`, not `att_pct`).

### Database Aliasing

Postgres / SQLite columns are `snake_case`. TypeScript layer aliases them to `camelCase` inside SQL (`AS firstName`) so that consumers in `.astro` files only see `camelCase`.

### Routing & Asset Conventions

- All routes are Spanish: `/diputados`, `/distritos`, `/bancadas`, `/partidos`, `/sesiones`, `/votaciones`, `/rankings`, `/compare`.
- Always go through `src/lib/paths.ts` helpers when generating links or asset URLs — do not hard-code paths.

### Styling

- The brand color is exposed as the `--accent-color` CSS variable; reuse it instead of hard-coding hex values.
- `.glass-panel` is the standard container surface; reuse it for cards and grouped sections.
- Charts must use the shared wrappers in `src/components/` rather than instantiating Chart.js directly in pages.

## Files & Directories You Should Not Touch Without Reason

- `/data/*.csv` — regenerated by the pipeline. Manual edits will be overwritten on the next `transform`.
- `/database/initial_data.sql` — seed data for fresh PostgreSQL setups.
- `/dist`, `/.astro`, `/node_modules`, `/.venv`, `/tmp` — build / vendor / scratch output (gitignored).
- `.env`, `uv.lock`, `package-lock.json` — environment & lockfiles.

## Reference Documents

- `specs.md` — original product specification (page-by-page requirements).
- `IMPROVEMENTS.md` — running list of planned improvements / open ideas.
- `README.md` — currently empty.
