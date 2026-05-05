# IMPROVEMENTS.md

Running list of planned improvements and open ideas for **Banana-CongresoGT / Guate No Olvida**.
Items are grouped by category and roughly prioritized within each section.

---

## UX (improvements to the existing experience)

1. **Make the landing page useful.** `src/pages/index.astro` is just six counters. Surface the most recent session, the last 3 most-voted-on subjects, the closest-margin "vote of the week", and the top/bottom of the attendance ranking.
2. **Centralize and rethink vote colors.** A Favor=`#00b2e3`, En Contra=`#00da9f`, Ausente=`#ffd700` are hardcoded in `compare.astro:129`, `diputados/[id].astro:73-77`, `votaciones/[id].astro:38-41`, and several others. Meanwhile `--color-favor`/`--color-contra` (green/red) are defined in `global.css:17-18` but unused. Pick one convention (the green/red pair reads as approve/reject everywhere), expose as CSS vars + entries in `mappers.ts`, then delete the literals.
3. **Fix contrast on the "Ausente" yellow.** `#ffd700` on white fails WCAG. Affects vote pills, attendance dots, and the heatmap.
4. **Dark mode.** Navbar is already dark navy (`Layout.astro:124`); the rest is light. Add a `prefers-color-scheme` toggle.
5. **Replace the exact-date filter on `/sesiones`** with a date-range or month picker. Currently effectively useless.
6. **Pagination / virtualization on `/votaciones` and `/sesiones`.** All cards are rendered up-front and toggled with `display:none`. Will degrade past ~1k items.
7. **Compare page polish**: add a swap button between the two slots, and let the user re-edit a selected name without first clicking the X.
8. **Per-page Open Graph metadata.** `Layout.astro` only sets `<title>`/`<meta description>`. Add `og:title`, `og:description`, `og:image` per congressman / voting page. Currently sharing yields no preview.
9. ~~**Stop truncating the voting `<title>`.** `votaciones/[id].astro:50` does `subject.substring(0, 30) + "..."` — just use the full subject.~~ *(COMPLETED)*
10. **Heatmap & tabs accessibility.** Heatmap dots are click-only with `cursor: help`; add `tabindex` + `aria-label` + keyboard activation. `GroupedActionTabs` `view-tab` buttons need `role="tab"` / `aria-selected` / `aria-controls`.
11. ~~**Compute age at build time.** `diputados/[id].astro:405-419` computes age client-side, causing layout shift. `birth_date` is in the CSV.~~ *(CANCELLED)*
12. **Custom 404 page.**
13. **Sort direction toggle on `/rankings`.** Always descending today; metrics like "% Inasistencia" require mental inversion.
14. **Persist filter state in the URL** on `/diputados`, `/votaciones`, `/sesiones`. Filters disappear on back-navigation.
15. **Skip-to-content link** for keyboard users.

---

## Feature (new content, charts, or capabilities)

1. **Block-vs-block / party-vs-party comparison page.** `/compare` is diputado-only today.
2. **Ideological map (PCA on the similarity matrix).** Project `congressman_similarity` into 2D (colored by bancada). Compute in the Python pipeline, ship a CSV, render with Chart.js scatter. High editorial appeal.
3. **"Most controversial votings" view.** Sort by smallest |in_favor − against| margin. No new tables required.
4. **Topic / decree-number tagging.** `voting.subject` is free text; classify into categories (Presupuesto, Estado de Calamidad, Reforma Electoral, etc.) via keyword rules in the pipeline; expose as a filter on `/votaciones`.
5. **Per-congressman voting timeline.** A small inline strip chart of monthly favor/contra/ausente share, alongside the existing attendance heatmap.
6. **CSV / JSON download buttons** on every detail page. The CSVs already exist; just expose them.
7. **`/metodologia` page.** Explain Rice index, Pearson similarity, "with majority", data source, and update cadence. Critical for credibility.
8. **About / Contacto page** with mission, source-code link, contributors, last-update timestamp.
9. **RSS / Atom feed** for new sessions and votings.
10. **`sitemap.xml` via `@astrojs/sitemap`.** ~5 lines of config in Astro 6.
11. **Per-session Rice-index timeline** (not just per-year). Reveals breakpoints where a bancada split.
12. **Per-voting "rebels" list.** Diputados who voted against their bancada's majority on each voting. Computable from existing data, very compelling editorially.
13. **Global search palette (Cmd-K)** across diputados / votaciones / sesiones.
14. **"Votos clave" highlights** — editor-curated or auto-flagged historic votings.
15. **Block-defection tracker** — surface diputados who switched bancada (requires the scraper to record changes over time).

---

## Housekeeping (technical debt)

### Bugs / wrong things

1. ~~**Stale `Voting` interface** in `src/lib/db.ts:44-65` declares `votes_in_favor_x` / `votes_in_favor_y` / `attendance_present_x` etc. The actual `voting.csv` and the `CREATE TABLE` / `INSERT` (lines 185-199, 325) use the un-suffixed names. Delete the `_x`/`_y` fields.~~ *(COMPLETED)*
2. ~~**`pyproject.toml` dependencies are wrong / missing**:
   - `bs4>=0.0.2` should be `beautifulsoup4` (`bs4` on PyPI is a deprecated stub).
   - `dotenv>=0.9.9` should be `python-dotenv`.
   - `numpy` is used in `transform_data.py` but not declared.
   - `playwright` is used by `scraper.py` but not declared.
   - `pandas>=3.0.1` does not exist; correct to a real 2.x version.~~ *(COMPLETED)*
3. **`README.md` is empty.** First impression is poor for a civic-data project.
4. **Several pages bypass `queries.ts`** with raw `db.prepare(...) as any[]` — see `src/pages/rankings.astro:19-59`. Move into typed query functions.
5. **`MarkedMap.astro` ships ~56 KB of inline SVG** on every `/distritos` listing card and detail page. Extract to a single `/public/distritos.svg` referenced by ID, or rely on the per-district SVGs already in `/public/distritos/{id}.svg`.
6. **`/compare` ships the full vote dataset inline** as JSON via `define:vars` (`compare.astro:122`). At ~160 diputados × 600+ votings this is already large and grows linearly. Move to a fetched static `/data/votes.json` (or per-congressman shards).

### Refactors

7. **Vote color literals scattered everywhere.** Add `VOTE_COLOR` to `mappers.ts` (and CSS vars), replace all `#00b2e3` / `#00da9f` / `#ffd700` literals.
8. **Mega-files to split**:
   - `src/pages/diputados/[id].astro` (~1080 lines)
   - `src/pages/compare.astro` (~917 lines)
   - `src/pages/rankings.astro` (~671 lines)
   - `src/scripts/chart-processing.ts` (~500 lines, many chart types in one file)
9. **Pipeline transform is `.groupby().apply(lambda)`-heavy** (`pipeline/transform_data.py:141-283`). Vectorize for ~10× speedup; runtime is fine today but degrades over the legislatura.
10. **Similarity computation is an O(n²) Python loop** (`transform_data.py:314-344`). A single NumPy matrix product is shorter and faster, with the same output.
11. **`getCongressman` aliases `partyName` from `p.short_name`** (`queries.ts:234`) while `getAllCongressmen` uses `p.name` (line 211). Pick one or document why.

### Tooling / hygiene

12. **No tests anywhere.** Pipeline transforms (Rice index, similarity) and the SQL queries are pure functions — easy to cover with `pytest` + fixture CSVs and a small in-memory SQLite fixture for `queries.ts`.
13. **No CI.** Add a GitHub Actions workflow: `npm run build` + a pipeline lint / dry-run on PR.
14. **Husky is configured but `.husky/_/` is empty.** Either remove or wire actual hooks (lint, typecheck, build).
15. **`tmp/` is committed.** Add to `.gitignore`.
16. **`AGENTS.md` references `IMPROVEMENTS.md` and `specs.md`** that don't exist in the repo. Commit them or drop the references.
17. **No image optimization for congressman photos.** Raw `.jpg` served at full size. Use `astro:assets` / `getImage` for build-time resizing.
18. **`tsconfig.json` is minimal** (~125 bytes). Verify `strict: true` and other recommended flags are set.
19. **No linter / formatter** in `package.json`. Add `eslint` + `prettier` (or `biome`) with a minimal config.
20. **No `robots.txt` / `manifest.json`.** Standard SEO + PWA hygiene.

---

## Suggested first batch

Low-risk, high-leverage, before tackling bigger features:

- Housekeeping #1 (stale `Voting` interface)
- Housekeeping #2 (`pyproject.toml` deps)
- Housekeeping #5 (extract `MarkedMap` inline SVG)
- UX #2 (centralize vote colors)
- UX #11 (compute age at build time)
