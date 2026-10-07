# Tracewire

The tech, AI and data-center deals and decisions that affect ordinary people, with a source for every fact.

### → [Read Tracewire: chrisqtruong.github.io/tracewire](https://chrisqtruong.github.io/tracewire/)

> [!WARNING]
> **Tracewire is paused.** The verified checks are switched off because we've run out of Firecrawl credits. Everything published so far stays up and the Wire keeps collecting unverified headlines, but no new posts are being checked or added until the checks are switched back on.

Tracewire keeps a permanent, sourced public record of how big tech and infrastructure deals affect communities: where data centers go and what they draw from local power and water, who buys whom, who pays to influence the rules, which public contracts go to which companies, and what courts and regulators decide. It is written and checked by a scheduled AI run, against primary sources, under the rules in `METHOD.md`.

The name "Tracewire" (formerly Rackwatch) lives in one place, `"name"` in `tracker.config.json`; run `python3 scripts/sync_config.py` after changing it (the page reads `docs/config.json`). Also update the first line of `ROUTINE-PROMPT.md`.

## How it stays current

| Lane | What | How often |
|---|---|---|
| **Wire** (`docs/wire.json`) | Unverified headlines from 52 tested public feeds: FTC, DOJ, SEC, FCC, FERC, Federal Register, SEC EDGAR full-text search, CourtListener, news outlets and news searches. Newest 200, de-duplicated, each with source and time. | GitHub Action `.github/workflows/wire.yml`, scheduled every 5 minutes (GitHub runs it every 5 to 15). Commits only when something changed. |
| **Feed** (`docs/data.json`) | Posts verified at their sources, labeled confirmed / reported / disputed, tagged with entities and states. | Claude scheduled task from `ROUTINE-PROMPT.md`, hourly (paused for now; see above). Major news first, then pinned per `PINNING.md`. |
| **Ledger** | Confirmed deals, fines, settlements, contracts, incentives, lobbying and political money. Also `ledger.csv`. | Same run. |
| **Saved copies** (`docs/source-archive.json`) | Every source link saved to the Internet Archive so the record survives broken links. | GitHub Action `.github/workflows/archive-sources.yml`, hourly at :17 and after each data change, 15 links per run. |

The page shows "Wire updated X min ago" and "Verified feed updated X min ago" separately; both link to the **Status** page, which lists recent verification checks (the `checks` log in `data.json`), Wire source health and how many source links have a saved copy.

## What's here

| Path | What it is |
|---|---|
| `docs/index.html` | The whole site (no build step, no libraries): Feed, Wire, Entities, Ledger, Maps & diagrams, Archive, About |
| `docs/data.json` | Feed (last 90 days), ledger, data center projects, `lastCheck` |
| `docs/entities.json` | Companies, agencies, officials, utilities, places, courts and groups that posts and ledger rows are tagged with |
| `docs/wire.json`, `docs/wire-status.json` | Wire headlines and per-source health (written only by the Action) |
| `docs/archive/` | Posts older than 90 days, one file per month, plus `index.json`. Never deleted. |
| `docs/source-archive.json` | Internet Archive copy of every source link (written only by `.github/workflows/archive-sources.yml`, hourly) |
| `docs/blindspots.json` | The About page's "Known blind spots" list |
| `docs/config.json` | Public part of `tracker.config.json` (name, categories, giscus IDs) |
| `wire-sources.json` | The Wire's feed list, keyword filters and polling intervals |
| `scripts/wire.py` | The Wire poller (Python standard library only) |
| `scripts/validate.py` | Data checks: ids, categories, entity tags, sources, archive counts, quote length. Runs in CI. |
| `scripts/ledger_csv.py`, `scripts/sync_config.py` | Regenerate `ledger.csv` and `docs/config.json` |
| `ledger.csv` | The confirmed ledger as a spreadsheet |
| `reports/YYYY-MM-DD.md` | What each check read, added, corrected or could not fetch |
| `sources.md` | Tested fetch recipes for every source, and which ones failed |
| `METHOD.md`, `PINNING.md`, `IMAGES.md` | The rules the scheduled run follows |
| `ROUTINE-PROMPT.md` | The scheduled-task prompt |
| `LAUNCH-STEPS.md` | What to click to put it live |

## Standards

Every item is labeled **confirmed**, **reported** or **disputed** (see `METHOD.md`). Only confirmed items enter the ledger. People are accused until convicted; lawsuits are allegations; Tracewire never calls anything corruption in its own voice and instead says what was filed, charged, alleged or reported, and by whom. When sources disagree on a number, the number is left out. Summaries are in our own words, quotes under 15 words, and every link was actually opened. Corrections are made in place under permanent ids; nothing is deleted; items found late carry their true date.

## Pausing and resuming

The pause is one field: `"paused"` in `docs/data.json`, holding the sentence shown to readers. While it is there, the site shows a "Tracewire is paused" banner on every page, the header reads "Verified updates paused", and the scheduled check stops at its first step without changing anything. To resume, delete the field (and the warning at the top of this README) and commit. The Wire and the source archiver are free GitHub Actions and keep running either way.

## Local preview

```bash
cd docs && python3 -m http.server 8000   # then open http://localhost:8000
python3 scripts/validate.py && python3 tests/test_wire.py
python3 scripts/wire.py --test           # poll every Wire source once and print a health table
```

## License

Content and data: CC BY 4.0. Code: MIT. Comments by [giscus](https://github.com/giscus/giscus) (MIT).

Built with the Tracker Kit method from [Bankrolled](https://github.com/chrisqtruong/bankrolled/tree/main/tracker-kit).
