# Banana-CongresoGT Site

## Project Overview
This project aims to provide Guatemalan citizens with a highly visual, extremely fast, and lightweight static site to analyze the voting behavior and attendance of their congressmen. The site generates static pages based on CSV data to minimize JavaScript overhead on the client side.

The repository is divided into two main components:
1. **Astro Web Application (`/` root)**: The frontend that builds static pages by consuming CSV data files into an in-memory SQLite database (`better-sqlite3`) during build time.
2. **Python Crawler (`/crawler`)**: A Playwright-based web scraper that periodically extracts data from the official congress website (`https://www.congreso.gob.gt`), stores it in a PostgreSQL database, and then exports it to CSV files.

## Architecture & Data Pipeline
1. **Crawler (`/crawler/scraper.py`)**: Fetches congressmen, sessions, attendance, votations, and individual votes. Data is cleaned and inserted into PostgreSQL.
2. **Export (`/crawler/export_backup.py`)**: Connects to the PostgreSQL database and exports all tables as CSV files into the `/data` directory. 
3. **Data Source (`/data/*.csv`)**: Contains `attendance.csv`, `congressmen.csv`, `congressmen_aliases.csv`, `districts.csv`, `parties.csv`, `sessions.csv`, `votations.csv`, and `votes.csv`.
4. **Static Generation (`npm run build`)**: Astro reads the CSV files (using `csv-parse` and `better-sqlite3`), generating routes for each congressman, party, district, session, and votation.

## Build and Run Commands

### Astro Application
- **Install dependencies**: `npm install`
- **Development server**: `npm run dev`
- **Production build**: `npm run build`
- **Preview build**: `npm run preview`

### Python Crawler
- **Environment Setup**: Requires a `.env` file with PostgreSQL credentials (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`).
- **Dependencies**: Uses `playwright`, `bs4`, `psycopg2`, `python-dotenv`.
- **Run Scraper**: `python crawler/scraper.py --action all`
- **Export Data**: `python crawler/export_backup.py`

## Code Style & Development Guidelines
- **Language**: All project code, variables, and comments must be written in **English**. However, all user-facing text, content on the static pages, and UI labels must be exclusively in **Spanish**.
- **Frontend (Astro)**:
  - Strongly prefer server-side generation via Astro components (`.astro`).
  - Client-side JavaScript is permitted using lightweight, fast libraries (e.g., ApexCharts) to enhance interactivity and data visualization, though fast load times remain a priority.
  - Prioritize highly graphical data representation (heatmaps, stroke/fill charts, color-coded parties) over walls of text.
  - Follow UX guidelines strictly (`specs.md`): facilitate comparison across politicians and summarize key voting behaviors intuitively.
- **Backend (Python)**:
  - Error handling and logging are critical. `logger.py` is used throughout `scraper.py`.
  - Data integrity is paramount. Names must be normalized and trimmed of excess spacing before matching (`match_congressman` function).
  - Treat Playwright operations securely, implementing retries or waits for pagination elements (e.g. DataTables).

## Key Pages & Routing Structure
- `/congressmen`: Master list with search & filter.
- `/congressman/[id]`: Individual behavior and voting alignment graphs.
- `/party/[id]` & `/district/[id]`: Aggregated data for parties and districts.
- `/sessions` & `/session/[id]`: Session overviews and attendance details.
- `/votations` & `/votation/[id]`: Vote outcomes and breakdowns.
