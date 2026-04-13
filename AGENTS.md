# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Banana-CongresoGT is a static site that lets Guatemalan citizens analyze congressional voting behavior and attendance. It consists of two independent components:

1. **Astro frontend** (`/src`): Builds a fully static site at build time using CSV data loaded into an in-memory SQLite database via `better-sqlite3`.
2. **Python data pipeline** (`/pipeline`, `main.py`): Scrapes the official congress website using Playwright, stores data in PostgreSQL, then transforms and exports it to CSV files in `/data`.

## Commands

### Astro Frontend

```bash
npm install        # Install dependencies
npm run dev        # Development server
npm run build      # Production build (reads /data/*.csv)
npm run preview    # Preview production build
```

### Python Pipeline

Requires a `.env` file with `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.

```bash
# Environment managed by mise (python 3.14, node 25)
# Dependencies managed by uv (see pyproject.toml)

python main.py scrape --action all          # Scrape all data from congress website
python main.py scrape --action load_sessions # Scrape only new sessions (default)
python main.py scrape --session-start 41168  # Start from specific session ID
python main.py scrape --log-level DEBUG      # Set log verbosity (DEBUG/INFO/WARNING/ERROR)
python main.py transform                    # Transform DB data → CSV files in /data
python main.py db                           # Initialize DB from backup
python main.py pipeline                     # Run full pipeline (scrape + transform)
```

Scrape actions: `all`, `load_congressmen`, `load_voting`, `load_attendance`, `update_congressmen`, `load_sessions`.

## Architecture

### Data Flow

```
PostgreSQL DB
     ↑
pipeline/scraper.py  (Playwright → congress website)
     ↓
pipeline/transform_data.py  (pandas/SQLAlchemy → computes stats & exports)
     ↓
/data/*.csv  (source of truth for the frontend)
     ↓
src/lib/db.ts  (loads CSVs into in-memory SQLite at build time)
     ↓
src/lib/queries.ts  (all SQL queries against in-memory DB)
     ↓
src/pages/**/*.astro  (static HTML generation)
```

### Frontend Structure

- **`src/lib/db.ts`**: Bootstraps the in-memory SQLite database. Reads all CSV files from `/data` and inserts them into typed tables via transactions. Runs once on module import during build.
- **`src/lib/queries.ts`**: All data access functions. Returns typed objects with camelCase aliases for snake_case DB columns.
- **`src/lib/mappers.ts`**: Enum constants (`VOTE_TYPE`, `ATTENDANCE_STATUS`, `SESSION_TYPE`, `CONGRESSMAN_STATUS`, `PERIOD`) used in both queries and page logic. Also contains display string helpers.
- **`src/lib/paths.ts`**: URL path helpers for routing.
- **`src/lib/util.ts`**: General utility functions.
- **`src/pages/`**: Astro pages using file-based routing. Dynamic routes (`[id].astro`) call `getStaticPaths()` which queries all IDs and pre-renders one page per entity. Top-level pages include `index.astro`, `rankings.astro`, and `compare.astro`.
- **`src/components/`**: Reusable Astro components including chart wrappers (`ApexCharts`, `Chart.js`) and data display components.

### Data Model (in-memory SQLite)

Core tables: `blocks`, `parties`, `districts`, `congressmen`, `sessions`, `voting`, `votes`, `attendance`

Pre-aggregated stat tables (computed by the Python transform): `congressman_stats`, `party_stats`, `district_stats`, `block_stats`, `congressman_similarity`

Stats tables have a `period` column: `"total"` for all-time, or a year string (`"2024"`, `"2025"`, etc.).

### Python Pipeline Structure

- **`pipeline/scraper.py`**: Playwright scraper with retry logic and DataTables pagination handling.
- **`pipeline/transform_data.py`**: Uses pandas/SQLAlchemy to compute statistics (attendance %, vote alignment, Rice Index for group voting cohesion, congressman similarity scores) and exports to `/data/*.csv`.
- **`pipeline/db.py`**: PostgreSQL connection helpers.
- **`pipeline/db_initializer.py`**: Initializes DB schema from backup.
- **`pipeline/logger.py`**: Shared logger (`Log`) used across the pipeline.

## Language Rules

- **Code**: All code, variable names, function names, comments, and commit messages must be in **English**.
- **UI/Content**: All user-facing text, labels, and page content must be in **Spanish**.
- **Naming**: Use full words, no abbreviations (e.g., `attendance_percentage` not `att_pct`).
