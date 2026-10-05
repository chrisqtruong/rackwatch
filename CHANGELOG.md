# Changelog

Content updates are committed as "Update YYYY-MM-DD HH:MM" and summarized in `reports/`. Wire commits are "Wire <time>". Design and feature changes are listed here, newest first.

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
