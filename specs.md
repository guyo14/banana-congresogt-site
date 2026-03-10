# Banana Site Specifications

## Core Goal
Facilitate citizens to analyze the information from `site/data` (which updates ~2 times per week) to understand, compare, and remember how congressmen have behaved and voted, enabling informed decisions during elections. The site must be extremely fast, lightweight, and user-friendly, using Astro for purely static generation.

## Technical Approach
* **Framework**: Astro (Static Site Generation).
* **Data Source**: CSV files from `site/data`. Loaded and processed at build time (e.g., using `better-sqlite3` in-memory during build) to generate static HTML.
* **Focus**: Highly graphical, fast load times, and zero/minimal JavaScript overhead for users.

## Page Requirements

### 1. General Congressmen Listing Page (`/congressmen`)
* **List**: Display all congressmen.
* **Search & Filter**: Find congressmen by name, party, and district.

### 2. Congressman Profile Page (`/congressman/[id]`)
* **Scope**: Generated individually for each congressman.
* **Graphs & Visuals**:
  * Attendance to sessions (general/all-time).
  * Attendance to sessions (breakdown per year).
  * Attendance to the last 5 sessions.
  * Votes for specific, important "key votations" to summarize ideological alignment.

### 3. Party Profile Page (`/party/[id]`)
* **Scope**: Generated individually for each party.
* **Content**: Similar structure to the congressman page.
* **Data**: Aggregated data and averages of all congressmen that belong to that specific party.

### 4. District Profile Page (`/district/[id]`)
* **Scope**: Generated individually for each district.
* **Content**: Similar structure to the party page.
* **Data**: Aggregated data and averages of all congressmen that represent that specific district.

### 5. General Sessions Page (`/sessions`)
* **List**: General overview of all legislative sessions.
* **Content**: List of all sessions with basic information, allowing users to navigate to a specific session.

### 6. Specific Session Page (`/session/[id]`)
* **Scope**: Generated individually for each legislative session.
* **Content**:
  * Important information/metadata about the session.
  * General assistance/attendance rate for that session.
  * Which votations took place during that session, with links to the corresponding votation pages.

### 7. General Votations Page (`/votations`)
* **List**: General overview of all key or recent votations.
* **Search & Filter**: Find specific votations by topic, date, or session.

### 8. Votation Page (`/votation/[id]`)
* **Scope**: Generated individually for every votation.
* **Content**:
  * Graphs illustrating the outcome of the votation (e.g., pie charts of In Favor vs. Against).
  * Detailed breakdown of how individuals and parties voted.

## UX/UI & Design Guidelines
* **Highly Graphical**: Heavily utilize charts, graphs, and visual indicators (colors for parties, attendance heatmaps, stroke/fill charts for votes) to make dense data easy to digest.
* **Compare & Remember**: The design should help users intuitively compare different politicians and remember key voting behaviors without reading walls of text. Provide clear visual summaries.
