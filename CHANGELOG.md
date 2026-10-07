# Changelog

Content updates are committed as "Update YYYY-MM-DD HH:MM" and summarized in `reports/`. Wire commits are "Wire <time>". Design and feature changes are listed here, newest first.

## 2026-10-07 (paused)
- Verified updates paused (out of Firecrawl credits). A `paused` field in `docs/data.json` shows a "Tracewire is paused" banner on every page, switches the header to "Verified updates paused · last checked …", and makes the scheduled check stop at step 0. The Wire and the source archiver keep running. Delete the field to resume.

## 2026-10-05 (players: even grid)
- Players (beta): circles replaced with same-size tiles. Each tile shows the number of verified moves, with shading that darkens as the number rises, and the disclosed amount below; rows and columns now line up evenly. Legend shows the shading scale.
- The "beta" label stays visible on the selected Players tab (it takes the tab's text color).

## 2026-10-05 (players: moves view)
- Players (beta) now sorts each company's verified record into five kinds of moves (Deals, Build, Influence, Scrutiny, Workers) instead of a month-by-month count of mentions. Each cell shows the number of verified posts and the dollar amount disclosed in the confirmed ledger; a summary row shows the totals for the selected sector and where most moves fall. The chart fits the screen at every width (no sideways scrolling). Every number still opens the items behind it with their sources.
- Fixed the money format: whole amounts lost a zero ($70B showed as $7B, $50B as $5B) on the Ledger, entity pages and diagrams.

## 2026-10-05 (players, beta)
- Entities > Players (beta): the largest companies and groups, grouped by sector (AI labs, chips, cloud and platforms, data center builders, apps and gig work, government tech, political money), with a dot per month sized by how many posts and ledger rows Tracewire recorded and a running-total line. Every dot opens the items behind it with their sources and saved copies. Includes a table view. Sectors are set with a `sec` field in `docs/entities.json`.

## 2026-10-05 (repository renamed)
- Removed the animated circuit traces from the header; the header keeps its grid and the dot-grid logo.
- Repository renamed to `chrisqtruong/tracewire`; the site moved to https://chrisqtruong.github.io/tracewire/ . Updated the config (slug, site and repo links, giscus repository), README, license credit, launch steps and routine prompt. The old address chrisqtruong.github.io/rackwatch no longer serves the site.

## 2026-10-05 (new name and header)
- Renamed from Rackwatch to **Tracewire**: on a circuit board a trace is the path that carries the signal; here it also means following the money and the deals, and the Wire is the live headline lane. The name is set in `tracker.config.json`. Repository and site URLs still say `rackwatch` until the GitHub repository is renamed.
- New logo: a halftone dot grid (after Bankrolled's halftone dot) with two lit circuit traces; matching favicon.
- Header: circuit traces drawn on the header's 24 px grid, with pads, vias, a dot field and a slow signal pulse (off when the device asks for reduced motion). Light-mode grid made more visible.

## 2026-10-05 (record keeping)
- Saved copies: a new hourly GitHub Action saves every source link to the Internet Archive (`scripts/archive_sources.py`, `docs/source-archive.json`); posts and ledger rows show a "saved copy" link next to each source once it exists.
- Corrections: corrected posts carry a "Corrected" label, and the About page lists every correction with its date and what changed. The validator checks the correction note format.
- Status page (new tab, also linked from the update times in the header): last verification check, last Wire update, Wire sources working and failing, switched-off sources and why, recent checks (new `checks` log in data.json, written by each scheduled run), and saved-copy coverage.

## 2026-10-05 (shorter pages)
- Every long list is now paged with Prev/Next and a "1–8 of 41" count, and the page number is kept in the link: Feed (8 posts), Wire (30), Entities (24), entity timelines (12) and ledger rows (10), Ledger (20 rows, 6 projects), Archive (8).
- Wire sidebar on the Feed is a fixed-height panel that stays in view and scrolls on its own (desktop). On phones it is replaced by the one-line Wire strip.
- Ledger: search box (companies, agencies, notes, dates, sources) and a type filter; data center projects can be searched and filtered by status.
- Entities: search, sort (most activity, A to Z, most recent), and per-kind counts. Entity pages no longer repeat every post in full under the timeline; they link to the Feed filtered to that entity.
- Posts added since your last visit carry a "New since your last visit" label (stored only in your browser).
- Spacing tightened to one scale (8, 12, 16, 24, 32 px).

## 2026-10-05 (after first live Wire run)
- Wire: switched off FTC, SEC litigation, CalPrivacy and OpenSecrets feeds (HTTP 403 from GitHub runners) and added Google News searches for FTC and CalPrivacy; PJM Inside Lines switched off (serves a bot-check page to GitHub runners); lenient fallback reader for malformed feeds; clearer error when a feed returns an HTML page; tighter filters for general outlets (core topic, or tech subject plus impact term, on the title). Tests cover the filters with real headlines.
- About: blind spot for agencies that block the headline collector.

## 2026-10-05
- Created from the Tracker Kit with `tracker.config.json` (tech, AI and data-center power).
- New design: dark slate default with a light option, Hanken Grotesk and JetBrains Mono, one cyan accent, status colors for confirmed / reported / disputed.
- Wire: GitHub Action polling public feeds and APIs every 5 minutes into `docs/wire.json`; shown as a live lane beside the verified Feed.
- Entities: `docs/entities.json`, entity pages with timeline, deals, money in and out, linked posts; Feed filters by entity, category, status and state.
- Ledger tabs for mergers and deals, lobbying and political money, enforcement and fines, contracts and incentives, and a data center project tracker.
- Maps & diagrams: state tile map of data center projects, deal network, money-toward-government bars, each with a text version.
- Archive with monthly files and search across the Feed and archive.
- giscus comments per post (needs repo and category IDs; see LAUNCH-STEPS.md).
- Seeded with verified posts, a first ledger, entities and data center projects.
