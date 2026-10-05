# Source checklist

Tested 2026-10-05. Every source below was loaded during testing; the table says how. Each hourly check opens the primary pages (not just keyword searches), triages the Wire, and records in `reports/YYYY-MM-DD.md` which sources it read and which failed. The first check of the morning reads all of them.

## How to fetch (learned 2026-10-05)

- **WebFetch was blocked for every source tested** (the session's egress proxy refused government and news hosts). **Firecrawl `firecrawl_scrape` worked for almost all of them.** Use markdown, `onlyMainContent: true`, `maxAge: 0` for pages that change hourly.
- **Firecrawl's rate limit is roughly 10 to 15 requests per minute, shared across everything on the account, and failed 429 calls still count.** Space calls to about 3 per minute; read the Wire first so you only open what matters.
- JSON APIs come back from Firecrawl wrapped in a json code fence inside the markdown: strip the fence before parsing. Responses over about 70K characters are saved to a file; read them with `jq` or Python.
- On agency press pages, read every release since the last check, not only titles that match keywords.
- The Wire (GitHub Action) fetches feeds directly from GitHub's runners, which are not behind this proxy. Its own health per source is in `docs/wire-status.json`; a source that fails there for a day goes in the report and, if it stays broken, in the blind spots below.

## Primary pages and APIs (routine reads these)

| Source | Recipe (exact URL loaded) | Result on 2026-10-05 |
|---|---|---|
| FTC press releases | `https://www.ftc.gov/news-events/news/press-releases` Firecrawl the listing; 20 items per page, each '### [title](url)' followed by a date line. Newest: Oct 2, 2026. | Firecrawl ok, current; WebFetch blocked |
| DOJ all news | `https://www.justice.gov/news` Prefer the RSS feed https://www.justice.gov/news/rss?m=1 through Firecrawl (rss+xml, items dated Oct 5, 2026). The HTML listing also works (newest Oct 5, 2026). RSS: `https://www.justice.gov/news/rss?m=1` | Firecrawl ok, current; WebFetch blocked |
| DOJ Antitrust Division press releases | `https://www.justice.gov/atr/press-releases` Firecrawl the listing, which shows title, summary and date. Newest: Sep 23, 2026 (low volume, about 43 releases in 2026). RSS: `https://www.justice.gov/news/rss?type=press_release&groupname=56&field_component=376&search_api_language=en&show_public_archived=0&require_all=0` | Firecrawl ok, current; WebFetch blocked |
| FCC headlines | `https://www.fcc.gov/news-events/headlines` Firecrawl the page and take the first 25 entries (date, doc type, title link). Newest: Oct 2, 2026. Add ?year_released=2026&items_per_page=25 to filter. | Firecrawl ok, current; WebFetch blocked |
| FERC news releases & headlines | `https://www.ferc.gov/news-events/news` Firecrawl it. It redirects to /news-events/news/news-releases-headlines and lists 10 items with dates. Newest: Oct 1, 2026. | Firecrawl ok, current; WebFetch blocked |
| FERC eLibrary | `https://elibrary.ferc.gov/eLibrary/search` Not usable by GET. The page loads, but it is an Angular search form with no results in the HTML. For docket activity, use FERC news, PJM Inside Lines, RTO Insider, or the Federal Register API (agencies[]=federal-energy-regulatory-commission). | Firecrawl ok, not current or not usable; WebFetch blocked |
| SEC EDGAR full-text search (efts) | `https://efts.sec.gov/LATEST/search-index?q=%22data%20center%22&forms=8-K&dateRange=custom&startdt=2026-09-28&enddt=2026-10-05` Firecrawl the search-index URL with a date window: &dateRange=custom&startdt=YYYY-MM-DD&enddt=YYYY-MM-DD. The response is JSON with hits.hits[]._source fields display_names, file_date, form, adsh, items, file_description. Build the filing link as https://www.sec.gov/Archives/edgar/data/{cik}/{adsh without dashes}/{_id after ':'}. | Firecrawl ok, current; WebFetch blocked |
| SEC EDGAR company 8-K atom feed | `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000789019&type=8-K&output=atom` Firecrawl the atom URL per CIK. Markdown conversion flattens the XML into run-on text, so regex for 'Filed: YYYY-MM-DD' and the Archives index URLs. Adding &count=10 should shrink it (not tested). RSS: `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000789019&type=8-K&output=atom` | Firecrawl ok, current; WebFetch blocked |
| Senate LDA API (lda.gov) | `https://lda.gov/api/v1/filings/?filing_year=2026&filing_period=second_quarter&client_name=Meta%20Platforms&format=json` Firecrawl the API URL. The JSON has count, next and results[] with fields filing_period, filing_type, dt_posted, client.name, registrant.name, income, expenses. Use filing_period values first_quarter\|second_quarter\|third_quarter\|fourth_quarter (also mid_year/year_end for older years). | Firecrawl ok, current; WebFetch blocked |
| FEC API (OpenFEC) | `https://api.open.fec.gov/v1/committees/?q=leading%20the%20future&api_key=DEMO_KEY` Firecrawl the API URL with api_key=DEMO_KEY. It returns JSON. LEADING THE FUTURE is committee_id C00916114, a Super PAC (NV), last_file_date 2026-07-15. Next calls: /v1/schedules/schedule_a/?committee_id=C00916114 and /v1/committee/C00916114/totals/. | Firecrawl ok, current; WebFetch blocked |
| USAspending API | `https://api.usaspending.gov/api/v2/search/spending_by_award/` Not usable for keyword search. spending_by_award returns HTTP 405 'GET not allowed' (POST only), and neither WebFetch nor Firecrawl scrape can POST. GET-only alternatives: /api/v2/awards/{generated_internal_id}/ for a known award. Otherwise rely on agency press releases. | Firecrawl ok, not current or not usable; WebFetch blocked |
| CourtListener search feed (opinions) | `https://www.courtlistener.com/feed/search/?q=%22data+center%22&type=o` Firecrawl the feed URL (atom+xml). It returns 20 newest opinions with case name, date, court, link and snippet. Newest: Sep 18, 2026 (Ohio Supreme Court, data-center ordinance). RSS: `https://www.courtlistener.com/feed/search/?q=%22data+center%22&type=o` | Firecrawl ok, current; WebFetch blocked |
| CourtListener search (HTML) | `https://www.courtlistener.com/?q=%22data+center%22` Avoid it and use the feed instead. The HTML results are relevance-sorted and old-first (1,012 results). Adding &order_by=dateFiled+desc should fix the ordering (not tested). | Firecrawl ok, not current or not usable; WebFetch blocked |
| Federal Register API | `https://www.federalregister.gov/api/v1/documents.json?conditions[term]=%22data+center%22&order=newest` Firecrawl the API URL. The JSON results[] have title, type, document_number, html_url, publication_date, agencies, excerpts. Newest: 2026-10-01. | Firecrawl ok, current; WebFetch blocked |
| Virginia SCC news releases | `https://www.scc.virginia.gov/about-the-scc/newsreleases/news-categories/general/` Poor. The category page renders with no list (JS-loaded). /component-library/news-releases/ shows only the 1-2 featured items: Oct 1, 2026 and Sep 22, 2026 (Dominion-NextEra hearings). Use WebSearch site:scc.virginia.gov/about-the-scc/newsreleases/release for discovery instead. | Firecrawl ok, not current or not usable; WebFetch blocked |
| Georgia PSC | `https://psc.ga.gov/` Firecrawl the homepage. Its 'Recent News' block (newest 8/25/2026 media advisory) and calendar list upcoming hearings, e.g. Docket 57171 on 10-15-2026. Data center fact sheet: https://psc.ga.gov/site/downloads/datacenterfactsheet_202609.pdf. | Firecrawl ok, current; WebFetch blocked |
| Texas PUC news releases | `https://www.puc.texas.gov/agency/resources/pubs/news/` Firecrawl the page. The 2026 list links to PDFs on ftp.puc.texas.gov. Newest: Sep 23, 2026. Includes Jun 18, 2026 'PUCT Approves New ERCOT Process to Manage Electricity Requests from Data Centers'. | Firecrawl ok, current; WebFetch blocked |
| ERCOT news releases | `https://www.ercot.com/news/releases` Firecrawl it; the result is a small date/title table. Newest: 09/21/2026. Large-load item: 06/18/2026 Batch Zero approval. | Firecrawl ok, current; WebFetch blocked |
| Arizona Corporation Commission news | `https://azcc.gov/news` Firecrawl it. The list has about 10 dated items. Newest: Oct 2, 2026; a Sep 29, 2026 item covers an AI-in-utility-ops workshop. | Firecrawl ok, current; WebFetch blocked |
| Indiana IURC newsroom | `https://www.in.gov/iurc/news-and-notices/newsroom/` Firecrawl it; the '2026 News Releases' list has dates and PDF links. Newest: Aug 19, 2026. | Firecrawl ok, current; WebFetch blocked |
| Ohio PUCO news | `https://puco.ohio.gov/media-room/media-releases` Firecrawl it. It redirects to the PUCO homepage, whose 'News' block shows the 3 newest items (newest Oct 2, 2026, Duke Energy Ohio rate hearings). Full list: https://puco.ohio.gov/wps/portal/gov/puco/home/news-and-events/all-news/ (not tested). | Firecrawl ok, current; WebFetch blocked |
| Louisiana PSC | `https://lpsc.louisiana.gov/` Firecrawl the homepage (not /PressReleases). The 'News and Information' block has bulletins, e.g. Sep 25, 2026 Bulletin #1385, plus Docket R-37905 (private networks for new large loads) and X-37921 (large load guidelines). | Firecrawl ok, current; WebFetch blocked |
| Pennsylvania PUC press releases | `https://www.puc.pa.gov/about-the-puc/press-releases` Poor. The listing is a search form and renders no items. Discover releases with WebSearch site:puc.pa.gov/press-release/2026, then Firecrawl individual URLs, which follow the pattern https://www.puc.pa.gov/press-release/2026/{slug}-{MMDDYYYY}. | Firecrawl ok, not current or not usable; WebFetch blocked |
| Wisconsin PSC press releases | `https://psc.wi.gov/Pages/NewsEvents/PressReleases.aspx` Firecrawl it; the result is a date/title table with PDF links. Newest: 08/25/2026. Includes data center tariff items (04/24/2026 We Energies, 05/07/2026 Alliant). | Firecrawl ok, current; WebFetch blocked |
| PJM Inside Lines (news) | `https://insidelines.pjm.com/category/news/` Prefer the RSS feed https://insidelines.pjm.com/feed/ through Firecrawl: rss+xml with full text, newest Oct 2, 2026, covering large-load forecast, ride-through rules and the backstop procurement. The HTML category page also works (newest Sep 30, 2026). RSS: `https://insidelines.pjm.com/feed/` | Firecrawl ok, current; WebFetch blocked |
| Texas AG news releases | `https://www.texasattorneygeneral.gov/news/releases` Firecrawl it; 10 items with title, summary and date. Newest: Oct 5, 2026. Includes Sep 24, 2026 'Landmark Investigation into Hundreds of Data Center Developments' (water use). | Firecrawl ok, current; WebFetch blocked |
| California AG press releases | `https://oag.ca.gov/media/news` Firecrawl it; 30 items with title and date. Newest: Oct 2, 2026. Paginate with ?page=1. | Firecrawl ok, current; WebFetch blocked |
| New York AG press releases | `https://ag.ny.gov/press-releases` Firecrawl it; 25 items with date and title. Newest: Oct 5, 2026. For a smaller page use the month view, https://ag.ny.gov/press-releases-for-month/202610. | Firecrawl ok, current; WebFetch blocked |
| OpenSecrets federal lobbying industries | `https://www.opensecrets.org/federal-lobbying/industries` Firecrawl it. It redirects to /federal-lobbying/top-industries and shows a top-20 table for 2026. Data runs Jan 1 to Jun 30, 2026, downloaded Jul 23, 2026. | Firecrawl ok, current; WebFetch blocked |
| Data Center Watch | `https://www.datacenterwatch.org/` Use the Substack feed https://datacenterwatch.substack.com/feed through Firecrawl (newest post Oct 5, 2026). It holds full text and is large (about 200K chars, overflowing to a file), so extract only <item> titles and dates with jq or grep. RSS: `https://datacenterwatch.substack.com/feed` | Firecrawl ok, not current or not usable; WebFetch blocked |
| Good Jobs First Subsidy Tracker | `https://subsidytracker.goodjobsfirst.org/` The homepage loads but is mostly a giant parent-company dropdown (avoid it). Use https://subsidytracker.goodjobsfirst.org/megadeals and /parent-totals (linked from the homepage, not scraped). Search query-string params were not verified. | Firecrawl ok, current; WebFetch blocked |
| Reuters | `https://www.reuters.com/business/energy/` Firecrawl works for both the section page (items timestamped minutes ago) and article pages. The full text of a Cenovus Oct 5, 2026 article came through. | Firecrawl ok, current; WebFetch blocked |
| Bloomberg | `https://www.bloomberg.com/technology` Section pages give headlines and dates only (current to Oct 5, 2026). Use them for headline confirmation, not body text. | Firecrawl ok, current, paywalled; WebFetch blocked |
| Wall Street Journal | `https://www.wsj.com/tech` The section page gives headlines and decks (current Oct 5, 2026); use it for headline-level confirmation only. | Firecrawl ok, current, paywalled; WebFetch blocked |
| The Information | `https://www.theinformation.com/` The homepage gives headlines plus 1-line briefing summaries (current Oct 5, 2026), e.g. 'Amazon Pledges To Give Up NDAs... Data-Center Buildout' (Oct 2). Use them as leads to confirm elsewhere. | Firecrawl ok, current, paywalled; WebFetch blocked |
| E&E News | `https://www.eenews.net/` Skip it. The homepage is stale (newest item 08/28/2026) because E&E has been folded into POLITICO Pro (subscriber content). | Firecrawl ok, not current or not usable, paywalled; WebFetch blocked |
| RTO Insider | `https://www.rtoinsider.com/` Firecrawl the homepage: headlines plus a 1-2 sentence deck per story, current Oct 4, 2026 (e.g. 'CAISO, PG&E Spar Over Large Loads Definition'). The decks are often enough to confirm a fact. | Firecrawl ok, current, paywalled; WebFetch blocked |
| Law360 | `https://www.law360.com/` The homepage gives headlines plus a short lede (current Oct 5, 2026). Use it as a lead source only. | Firecrawl ok, current, paywalled; WebFetch blocked |

## Every-check search set (after the Wire and primary pages)

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

Add "today" on later checks. Search the feed AND archive for the subject before posting: late catches are the usual gap.

## Watch list
quarterly LDA lobbying deadlines (Jan 20, Apr 20, Jul 20, Oct 20); FEC quarterly and pre-election reports; PJM capacity auctions; state utility commission large-load tariff dockets; DOJ v. Google remedies and appeals; FTC v. Meta; FTC v. Amazon; pending AI/chip merger reviews

Fixed dates known on 2026-10-05: Oct 20 LDA third-quarter lobbying reports due (`filing_period=third_quarter` is empty until then); Oct 20 Loudoun County formal vote on the data center application pause; FEC pre-general reports late October.

## Staleness calendar

| Item | Cadence | Where it lands |
|---|---|---|
| Senate LDA lobbying (in-house and outside firms) | quarterly (Jan 20, Apr 20, Jul 20, Oct 20) | Lobbying ledger rows, money diagram |
| FEC reports for tech-funded super PACs (Leading the Future C00916114, Public First Action) | quarterly and pre/post-election | Political ledger rows |
| PJM capacity auction results | yearly (next date set by PJM) | Energy & water posts, Rate decision rows |
| OpenSecrets industry totals (2026 data ran Jan to Jun when tested) | about 1 month after each LDA deadline | context only, never the ledger |
| Data center project status (`projects` in data.json) | check each project's latest source monthly | project cards, state map |

If a figure is older than its cadence, say so in the report.

## Wire feeds (`wire-sources.json`, polled by `.github/workflows/wire.yml`)

Lanes: agency, court, filing, news, search. `on: false` sources are kept for the record with the reason.

| id | Source | On | Test on 2026-10-05 |
|---|---|---|---|
| ftc-press | FTC press releases | yes | feed ok; 10 items, newest Fri, 02 Oct 2026 08:00:00 -0400. RSS 200 application/rss+xml. Item count from Firecrawl query-mode answer (not raw parse). |
| ftc-competition | FTC competition releases | yes | feed ok; 30 items, newest Fri, 02 Oct 2026 08:00:00 -0400. RSS, raw-parsed. 2nd: 28 Sep 2026 Corteva antitrust case. |
| ftc-consumer | FTC consumer protection releases | yes | feed ok; 30 items, newest Fri, 02 Oct 2026 08:00:00 -0400. RSS, raw-parsed. |
| doj-news | DOJ news | yes | feed ok; 25 items, newest Mon, 05 Oct 2026 12:00:00 +0000. RSS 'Justice News' (all DOJ components incl. OPA, USAO). pubDate always 12:00 UTC (date-only precision). |
| doj-opa | DOJ Office of Public Affairs | no: 404 on 2026-10-05; doj-news is the same Justice News feed | not a feed; 0 items, newest None. HTTP 404 'Page not found' HTML. Legacy OPA feed is gone; replacement is the 'Justice News' feed already listed as doj-news (tested OK, 25 items, newest 05 Oct 2026) - drop doj-opa as a duplicate. Replaced with the tested URL now in the config. |
| doj-atr | DOJ Antitrust Division | yes | not a feed; 0 items, newest None. Original: HTTP 404 HTML. Fixed URL found on https://www.justice.gov/atr/news-feeds (Antitrust Division component=376): RSS 200, 25 items, newest Mon 05 Oct 2026 (a stray USAO item); newest ATR item Wed 23 Sep 2026 'Justice Department Issues Statements on ... P Replaced with the tested URL now in the config. |
| sec-press | SEC press releases | yes | feed ok; 25 items, newest Mon, 05 Oct 2026 08:47:36 -0400. RSS 200 application/rss+xml. Count/titles from Firecrawl query-mode answer (not raw parse). |
| sec-litigation | SEC litigation releases | yes | not a feed; 0 items, newest None. Original redirects to /litigation/litreleases/rss -> 404. Fixed URL: RSS 200, 25 items, newest Fri 02 Oct 2026 18:03 'David Reichman et al.' (LR-26664). Replaced with the tested URL now in the config. |
| fcc-headlines | FCC news releases | yes | not a feed; 0 items, newest None. Redirects to fcc.gov/page-not-found (HTML). FCC now publishes feeds via EDOCS API (listed on https://www.fcc.gov/news-events/rss-feeds-and-email-updates-fcc). Fixed URL: RSS 200, 6 items, NO per-item pubDate (channel lastBuildDate = now); newest 'FCC Votes to  Replaced with the tested URL now in the config. |
| fcc-edocs | FCC daily releases | no: old URL redirects to page not found; same feed as fcc-headlines after fix | not a feed; 0 items, newest None. Redirects to fcc.gov/page-not-found. Same replacement as fcc-headlines (EDOCS API). Untested sibling: https://api2.fcc.gov/api/exp/v1.0.0/edocspublic/rss (all document types). Replaced with the tested URL now in the config. |
| ferc-news | FERC news | no: 404 on 2026-10-05; FERC publishes no news RSS. Routine reads the news page; Wire uses fr-ferc | not a feed; 0 items, newest None. HTTP 404. No FERC news RSS found: news page https://www.ferc.gov/news-events/news/news-releases-headlines (HTML, 200, latest 'FERC Announces 2027 Commission Meeting Schedule', 'Summaries September 2026 Commission Meeting') has no feed link; web search only sur |
| ferc-news2 | FERC news releases | no: 404 on 2026-10-05; see ferc-news | not a feed; 0 items, newest None. HTTP 404. See ferc-news. |
| doe-news | DOE newsroom | yes | feed ok; 10 items, newest Thu, 01 Oct 2026 14:59:11 -0400. Redirects to https://www.energy.gov/rss/energygov/2193718 ('Energy News'). 2nd: 29 Sep 2026 SPR release. ~2-3 items/week. |
| cppa-news | California Privacy Protection Agency (CalPrivacy) | yes | not a feed; 0 items, newest None. Original HTTP 404 (Apache). CPPA (now 'CalPrivacy') moved news to WordPress site privacy.ca.gov. Fixed URL: RSS 200, 10 items, newest Mon 28 Sep 2026 'California Expands Privacy Protections by Strengthening Deletion Rights'; 03 Sep 'Enforcement Advisory Target Replaced with the tested URL now in the config. |
| nlrb-news | NLRB news | yes | feed ok; 10 items, newest Fri, 11 Sep 2026 12:46:33 +0000. Valid RSS but newest item is 24 days old (outside 14-day window). Low-volume source; feed itself is working. |
| gao-reports | GAO reports | yes | feed ok; 25 items, newest Mon, 05 Oct 2026 07:26:32 -0400. RSS, raw-parsed. Also 05 Oct 'Concrete Masonry Promotion Program: Commerce Could Enhance Its Oversight Controls'. |
| fr-datacenter | Federal Register: data center | yes | feed ok; 20 items, newest 2026-09-30. JSON API OK (application/json). count=754 total. Many hits are incidental SRO/Privacy Act notices mentioning 'data center'; ordering is newest but results are noisy. |
| fr-ai | Federal Register: artificial intelligence | yes | feed ok; 20 items, newest 2026-10-05. JSON API OK, count=1316. IMPORTANT: 2026-10-02 Presidential Document 'Inaugurating the Era of Super Intelligence' (2026-20321) directs agencies to use 'Super Intelligence'/'SI' instead of 'Artificial Intelligence'/'AI' - add "super intelligence" to this query  |
| fr-largeload | Federal Register: FERC documents | yes | feed ok; 1 items, newest 2025-04-07. JSON API works but count=1 (single 2025 doc). Query effectively dead; consider broader terms (e.g. "large loads", colocation, "behind-the-meter") - not tested. |
| edgar-8k-datacenter | SEC EDGAR full-text: 8-K data center | yes | feed ok; 100 items, newest 2026-09-22. Original returns JSON (200) but without startdt/enddt it is NOT date-filtered and is relevance-sorted (top hit 2002-06-28; total >=10000). Fixed URL (adds startdt/enddt; dates must be generated dynamically) returns JSON total=96, all 2026-09-21..2026-10-05, ne Replaced with the tested URL now in the config. |
| courtlistener-dc | CourtListener: data center opinions | yes | feed ok; 20 items, newest 2026-09-18. Atom 200. Newest opinion 17 days old - normal cadence for court opinions. |
| courtlistener-antitrust | CourtListener: tech antitrust opinions | yes | feed ok; 20 items, newest 2026-09-30. Atom 200. Noisy (matches incidental citations, e.g. Google Earth). |
| verge-policy | The Verge policy | yes | feed ok; 10 items, newest 2026-10-05T10:05:42-04:00. Atom 200. |
| verge | The Verge | yes | feed ok; 10 items, newest 2026-10-05T10:42:34-04:00. Atom 200. |
| ars-policy | Ars Technica policy | yes | feed ok; 20 items, newest Fri, 02 Oct 2026 20:30:27 +0000. RSS 200 text/xml. |
| techcrunch | TechCrunch | yes | feed ok; 20 items, newest Mon, 05 Oct 2026 14:58:42 +0000. RSS 200. |
| dcd | DatacenterDynamics | yes | feed ok; 20 items, newest Mon, 05 Oct 2026 14:52:09 +0000. RSS 200. 2nd: 'Applied Digital adds 75MW of capacity at Ellendale data center campus in North Dakota'. |
| dck | Data Center Knowledge | yes | feed ok; 50 items, newest Mon, 05 Oct 2026 13:00:00 GMT. RSS 200 text/xml. |
| utilitydive | Utility Dive | yes | feed ok; 10 items, newest Mon, 05 Oct 2026 05:00:00 -0400. RSS 200. Top 3 items are sponsored (/spons/); newest editorial item Fri 02 Oct 2026 'Cities, states sue EPA over power plant emissions rollback'. Filter /spons/ links. |
| canary | Canary Media | yes | feed ok; 100 items, newest Mon, 05 Oct 2026 03:30:00 -0400. RSS 2.0 body but served with Content-Type text/html; strict parsers may need to ignore content-type. |
| icn | Inside Climate News | yes | feed ok; 10 items, newest Mon, 05 Oct 2026 09:00:00 +0000. RSS 200. |
| propublica | ProPublica | yes | feed ok; 20 items, newest Mon, 05 Oct 2026 10:00:00 +0000.  |
| markup | The Markup | yes | feed ok; 20 items, newest Wed, 16 Sep 2026 08:00:00 -0400. Working feed but newest item is ~19 days old (low publishing cadence); slightly outside 14-day window. |
| 404media | 404 Media | yes | feed ok; 15 items, newest Mon, 05 Oct 2026 14:13:58 GMT.  |
| wired | Wired | yes | feed ok; 50 items, newest Mon, 05 Oct 2026 11:00:00 +0000. Firehose feed; heavy on Gear/coupons content. Policy/data-center items present (e.g. 'Amazon Says It’s No Longer Using NDAs for Data Centers'). |
| npr-tech | NPR Technology | yes | feed ok; 10 items, newest Sun, 04 Oct 2026 14:36:48 -0400.  |
| nyt-tech | New York Times Technology | no: untestable on 2026-10-05: Firecrawl refuses nytimes.com, WebFetch blocked; Google News site: fallback returned general news | not a feed; None items, newest None. Could not verify original URL with either tool (WebFetch unable to fetch; Firecrawl refuses nytimes). Not shown to be broken. Fallback Google News site: feed loaded OK (100 items, newest Mon, 05 Oct 2026 14:37:32 GMT 'Geography Is Back With a Vengeance') but i Replaced with the tested URL now in the config. |
| wapo-tech | Google News: washingtonpost.com/technology | yes | feed ok; 0 items, newest None. Original returns valid RSS channel with ZERO items (lastBuildDate current) - effectively dead. Alt https://www.washingtonpost.com/arcio/rss/category/technology/ also 0 items. Google News fallback: 6 items, newest Sat, 03 Oct 2026 06:37:12 GMT 'A police search  Replaced with the tested URL now in the config. |
| cnbc-tech | CNBC Technology | yes | feed ok; 30 items, newest Mon, 05 Oct 2026 14:26:11 GMT.  |
| politico-tech | Politico Technology | yes | feed ok; 30 items, newest Mon, 05 Oct 2026 06:56:00 EDT.  |
| axios | Axios | yes | feed ok; 100 items, newest Mon, 05 Oct 2026 14:25:45 +0000. General all-topics feed (~975KB). |
| techpolicypress | Tech Policy Press | yes | not a feed; 0 items, newest None. /rss/ returns a Next.js HTML page. Correct feed (found via feeder.co listing) https://www.techpolicy.press/rss/feed.xml loaded OK: RSS, very large (~1.7MB, ~4000 items - full archive), newest Mon, 05 Oct 2026 13:40:38 GMT 'Circuit Court Ruling on Border Search Replaced with the tested URL now in the config. |
| courthousenews | Courthouse News | yes | feed ok; 10 items, newest Mon, 05 Oct 2026 14:10:13 +0000. General all-topics feed, only 10 items with full content. |
| opensecrets | OpenSecrets News | yes | feed ok; 11 items, newest Wed, 30 Sep 2026 13:07:12 +0000.  |
| guardian-tech | The Guardian Technology | yes | not a feed; 0 items, newest None. Original is HTTP 404. https://www.theguardian.com/technology/rss loaded OK (redirected to https://www.theguardian.com/us/technology/rss): 36 items, newest Mon, 05 Oct 2026 14:00:27 GMT 'OpenAI must explain action taken to stop AI hacking Australians’ private d Replaced with the tested URL now in the config. |
| bbc-tech | BBC Technology | yes | feed ok; 21 items, newest Mon, 05 Oct 2026 10:03:38 GMT. Includes some Tech Life/Tech Now programme entries. |
| ap-tech | AP Technology | no: AP has no working RSS (HTML redirect, technology.rss 404); Google News site:apnews.com fallback is mostly general news | not a feed; 0 items, newest None. Original redirects to HTML section page apnews.com/technology (no RSS). apnews.com/technology.rss (linked from page) is 404. AP has no working native feed. Google News fallback loaded OK: 100 items, newest Mon, 05 Oct 2026 14:04:00 GMT 'Privacy concerns put sm Replaced with the tested URL now in the config. |
| reuters-tech | Google News: reuters.com/technology | yes | not a feed; 0 items, newest None. Original is HTTP 404. Google News 'site:reuters.com/technology' fallback loaded OK: only 4 items, newest Mon, 05 Oct 2026 11:56:09 GMT 'Italy PM Meloni seeks EU trademark for her voice amid AI deepfake risks - Reuters'. Broader 'site:reuters.com technology' gi Replaced with the tested URL now in the config. |
| hn-dc | Heatmap News | yes | not a feed; 0 items, newest None. Original is HTTP 404 (HTML). Feed URL linked from site head: https://heatmap.news/feeds/feed.rss loaded OK: 30 items, newest Mon, 05 Oct 2026 12:00:16 +0000 'The Supreme Court Kicks Off with a Big Climate Case'. Replaced with the tested URL now in the config. |
| restofworld | Rest of World | yes | feed ok; 12 items, newest Mon, 05 Oct 2026 10:00:43 +0000. Content truncated to excerpts. |
| eff | EFF Deeplinks | yes | feed ok; 50 items, newest Fri, 02 Oct 2026 18:59:23 +0000.  |
| gn-dc-zoning | Google News: dc-zoning | yes | feed ok; 49 items, newest Mon, 05 Oct 2026 14:02:37 GMT.  |
| gn-dc-utility | Google News: dc-utility | yes | feed ok; 43 items, newest Mon, 05 Oct 2026 14:40:18 GMT.  |
| gn-dc-incent | Google News: dc-incent | yes | feed ok; 35 items, newest Mon, 05 Oct 2026 14:02:37 GMT. Some off-topic hits (e.g. NYC pied-a-terre tax, VPN article). |
| gn-dc-water | Google News: dc-water | yes | feed ok; 61 items, newest Mon, 05 Oct 2026 14:02:07 GMT.  |
| gn-ai-deals | Google News: ai-deals | yes | feed ok; 53 items, newest Mon, 05 Oct 2026 14:48:45 GMT.  |
| gn-antitrust | Google News: antitrust | yes | feed ok; 44 items, newest Mon, 05 Oct 2026 14:46:18 GMT.  |
| gn-money | Google News: money | yes | feed ok; 30 items, newest Mon, 05 Oct 2026 13:25:48 GMT. Noisy: several Zcash/crypto and Venezuela-lobbying hits. |
| gn-contracts | Google News: contracts | yes | feed ok; 36 items, newest Mon, 05 Oct 2026 14:45:30 GMT. Noisy: 'ICE' matches Intercontinental Exchange (NYSE owner) and stock-tip sites. |
| gn-labor | Google News: labor | yes | feed ok; 0 items, newest None. Original returns valid RSS with ZERO items (top-level OR of parenthesized groups appears to break the query). Restructured query loaded OK: 60 items, newest Mon, 05 Oct 2026 14:17:26 GMT 'Your Boss Can Use AI To Watch You. California Just Drew Some New Lines - Replaced with the tested URL now in the config. |
| gn-privacy | Google News: privacy | yes | feed ok; 9 items, newest Mon, 05 Oct 2026 14:00:00 GMT. Works but low volume; some noise (Ceuta 'settlement', Lina Khan interview). |
| gn-corruption | Google News: corruption | no: query returned 3 irrelevant items on 2026-10-05; needs a rewritten, tested query | feed ok; 3 items, newest Mon, 05 Oct 2026 12:50:00 GMT. Technically working but all 3 items are irrelevant junk from one local paper (Pet of the Week, Five indicted on theft charges, AP photos). Query needs rework; no replacement tested. |
| pjm-insidelines | PJM Inside Lines | yes | Firecrawl ok (primary-source test): current, newest Oct 2 / Oct 5 |
| datacenterwatch | Data Center Watch | yes | Firecrawl ok (primary-source test): current, newest Oct 2 / Oct 5 |

## Known blind spots (keep this list honest; `docs/blindspots.json` mirrors it on the About page)

- **WebFetch blocked everywhere** in the routine's sandbox: everything depends on Firecrawl, whose shared rate limit slows each check.
- **New York Times**: Firecrawl refuses nytimes.com and WebFetch is blocked; NYT stories are seen only when other outlets cite them.
- **AP and Reuters have no working RSS.** AP is missed by the Wire; Reuters is read through a Google News search (few items). Reuters articles do load through Firecrawl.
- **Paywalled (headlines only):** Bloomberg, Wall Street Journal, The Information, RTO Insider, Law360. Used as leads; facts are confirmed elsewhere.
- **E&E News** is paywalled and was stale (newest Aug 28) after moving into POLITICO Pro.
- **USAspending** search needs POST requests, which neither tool can send: federal contract awards are found through agency releases and news, so contract coverage lags.
- **FERC** has no news RSS and eLibrary is a script-only search form: FERC orders reach the Wire through the Federal Register and PJM, the routine reads FERC's news page.
- **State utility commissions:** Virginia SCC and Pennsylvania PUC news lists load by script (only featured items visible); Georgia PSC's newsroom stopped in 2019 (use the homepage); none of the tested commissions offer RSS. Local data center votes reach us through news searches, often a day or more late.
- **County and city meetings** (rezonings, NDAs, abatements) have no central feed at all; coverage depends on local news and Data Center Watch.
- **Court dockets:** CourtListener's feed covers opinions, not new filings; PACER is not read. New lawsuits are seen when agencies or outlets report them.
- **Washington Post technology RSS is empty**; read through a Google News search instead.
- **Google News searches** return redirect links and some off-topic items (for example "ICE" matching Intercontinental Exchange). They are Wire leads only.
- **Lag:** the Wire runs every 5 to 15 minutes (GitHub decides), the verified Feed hourly. Lobbying and FEC money appears only when filings are due, weeks after the spending.

