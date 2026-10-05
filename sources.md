# Source checklist

Each hourly check opens these primary pages (not just keyword searches) and records in `reports/YYYY-MM-DD.md` which it read and which failed. The first morning check reads all of them.

## Primary pages
- [SEC EDGAR current 8-K filings](https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K)
- [FTC press releases](https://www.ftc.gov/news-events/news/press-releases)
- [DOJ press releases](https://www.justice.gov/news)
- [DOJ Antitrust Division](https://www.justice.gov/atr/press-releases)
- [FCC headlines](https://www.fcc.gov/news-events/headlines)
- [FERC news](https://www.ferc.gov/news-events/news)
- [Federal Register](https://www.federalregister.gov/)
- [Senate LDA](https://lda.gov/)
- [FEC](https://www.fec.gov/data/)
- [USAspending](https://www.usaspending.gov/)
- [CourtListener](https://www.courtlistener.com/)

## Every-check search set
- data center rezoning vote OR lawsuit OR moratorium
- data center utility commission large load tariff OR rate case
- data center tax abatement OR incentive OR nondisclosure agreement
- data center water use OR gas plant
- AI acquisition OR acqui-hire billion
- antitrust lawsuit OR settlement Google OR Meta OR Amazon OR Apple OR Microsoft OR Nvidia
- AI super PAC OR lobbying disclosure tech
- Pentagon OR ICE contract AI OR Palantir OR surveillance
- layoffs AI cited
- data broker OR privacy settlement attorney general OR FTC
- gig workers ruling OR content moderators lawsuit
- bribery OR indicted OR ethics complaint data center OR tech contract

Add "today" on later checks. Search the feed and archive for the subject before posting: late catches are the usual gap.

## Watch list
quarterly LDA lobbying deadlines (Jan 20, Apr 20, Jul 20, Oct 20); FEC quarterly and pre-election reports; PJM capacity auctions; state utility commission large-load tariff dockets; DOJ v. Google remedies and appeals; FTC v. Meta; FTC v. Amazon; pending AI/chip merger reviews

## How to fetch
- If WebFetch is blocked or fails for a page, retry with Firecrawl `firecrawl_scrape` (markdown, onlyMainContent, `maxAge: 0` for hourly pages) before skipping it. Note any skip in the report.
- On agency press pages, read every release since the last check, not only titles that match the keywords.

## Staleness calendar
| Item | Cadence | Where it lands |
|---|---|---|
| (fill in: each official figure, how often it is published, which `numbers`/`charts` entry it feeds) | | |

If a figure is older than its cadence, say so in the report.

## Evidence tiers (if used)
See `METHOD.md`. Record the tier in the entry text for conflict, rights and disaster topics.

## Known blind spots (keep this list honest; the About tab mirrors it)
- List every source that blocks automated reading, is paywalled, or is too large, and the workaround used. Update it whenever a run records a failure.
