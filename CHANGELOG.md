# Changelog

Content updates are committed as "Update YYYY-MM-DD HH:MM" and summarized in `reports/`. Wire commits are "Wire <time>". Design and feature changes are listed here, newest first.

## 2026-10-05 (after first live Wire run)
- Wire: switched off FTC, SEC litigation, CalPrivacy and OpenSecrets feeds (HTTP 403 from GitHub runners) and added Google News searches for FTC and CalPrivacy; lenient fallback reader for malformed feeds (PJM); clearer error when a feed returns an HTML page; tighter filters for general outlets (core topic, or tech subject plus impact term, on the title). Tests cover the filters with real headlines.
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
