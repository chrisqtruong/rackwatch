#!/usr/bin/env python3
"""Rackwatch Wire: poll free RSS/Atom feeds and APIs, keep the newest unverified headlines.

  python3 scripts/wire.py            # poll sources that are due, update docs/wire.json
  python3 scripts/wire.py --all      # poll every source regardless of its interval
  python3 scripts/wire.py --test     # poll every source, print a per-source report, write nothing

Standard library only. Writes docs/wire.json and docs/wire-status.json only when the
headline list changed, and prints changed=true|false (also to $GITHUB_OUTPUT).
"""
import concurrent.futures as cf, datetime as dt, email.utils, hashlib, html, json, os, re, ssl, sys, time
import urllib.parse, urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(ROOT, "tracker.config.json")))
SRC = json.load(open(os.path.join(ROOT, "wire-sources.json")))
WIRE = os.path.join(ROOT, "docs", "wire.json")
STATUS = os.path.join(ROOT, "docs", "wire-status.json")
KEEP = int(SRC.get("keep", 200))
MAX_AGE_DAYS = int(SRC.get("max_age_days", 7))
RUN_EVERY = int(SRC.get("run_every_min", 10))
UA = "%s wire bot (+https://github.com/%s/%s)%s" % (
    CFG["name"], CFG.get("owner", ""), CFG["slug"], (" " + CFG["contact"]) if CFG.get("contact") else "")
FILTERS = {k: re.compile(v, re.I) for k, v in SRC["filters"].items()}
NOW = dt.datetime.now(dt.timezone.utc)


def ctx():
    c = ssl.create_default_context()
    for f in (os.environ.get("SSL_CERT_FILE"), "/root/.ccr/ca-bundle.crt"):
        if f and os.path.exists(f):
            c.load_verify_locations(f)
    return c


SSL = ctx()


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/atom+xml, application/xml, application/json, text/xml, */*"})
    with urllib.request.urlopen(req, timeout=25, context=SSL) as r:
        return r.read()


def when(s):
    if not s:
        return None
    s = s.strip()
    try:
        d = email.utils.parsedate_to_datetime(s)
    except Exception:
        try:
            d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return d.astimezone(dt.timezone.utc)


def text(x):
    return html.unescape(re.sub(r"<[^>]+>", " ", x or "")).strip()


def local(tag):
    return tag.rsplit("}", 1)[-1]


def parse_feed(raw):
    raw = raw.lstrip(b"\xef\xbb\xbf \t\r\n")
    if raw[:200].lower().find(b"<html") >= 0 or raw[:15].lower().startswith(b"<!doctype html"):
        raise ValueError("got an HTML page, not a feed (blocked or moved)")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return parse_loose(raw)
    out = []
    for el in root.iter():
        if local(el.tag) not in ("item", "entry"):
            continue
        f = {}
        for ch in el:
            n = local(ch.tag)
            if n == "title":
                f["t"] = text(ch.text)
            elif n == "link":
                href = ch.get("href")
                if href and ch.get("rel", "alternate") == "alternate":
                    f.setdefault("u", href)
                elif ch.text and ch.text.strip():
                    f.setdefault("u", ch.text.strip())
            elif n in ("pubDate", "published", "updated", "date", "issued") and "at" not in f:
                f["at"] = when(ch.text)
            elif n == "source" and ch.text:
                f["via_o"] = text(ch.text)
            elif n in ("description", "summary") and ch.text:
                f["x"] = text(ch.text)[:300]
            elif n == "guid" and ch.text and "u" not in f and ch.text.startswith("http"):
                f["u"] = ch.text.strip()
        if f.get("t") and f.get("u"):
            out.append(f)
    return out


def parse_loose(raw):
    """Fallback for feeds that are not well-formed XML (stray &, bad entities): read <item>/<entry> blocks by pattern."""
    t = raw.decode("utf-8", "replace")
    out = []
    for blk in re.findall(r"<(?:item|entry)\b.*?</(?:item|entry)>", t, re.S):
        g = lambda tag: (re.search(r"<%s\b[^>]*>(.*?)</%s>" % (tag, tag), blk, re.S) or [None, ""])[1]
        title = text(re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", g("title"), flags=re.S))
        link = g("link").strip() or (re.search(r'<link\b[^>]*href="([^"]+)"', blk) or [None, ""])[1]
        link = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", link).strip()
        at = when(g("pubDate") or g("published") or g("updated") or g("dc:date"))
        if title and link.startswith("http"):
            out.append({"t": title, "u": html.unescape(link), "at": at, "x": text(re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", g("description"), flags=re.S))[:300]})
    if not out:
        raise ValueError("not a readable feed")
    return out


def parse_fr(raw):
    out = []
    for d in json.loads(raw).get("results", []):
        out.append({"t": d.get("title", ""), "u": d.get("html_url", ""), "at": when(d.get("publication_date")),
                    "x": "%s: %s" % (d.get("type", ""), ", ".join(a.get("name", "") for a in d.get("agencies", []) if a.get("name")))})
    return out


def parse_efts(raw):
    out = []
    for h in json.loads(raw).get("hits", {}).get("hits", []):
        s = h.get("_source", {})
        cik = (s.get("ciks") or [""])[0].lstrip("0")
        adsh = s.get("adsh", "")
        name = (s.get("display_names") or ["?"])[0]
        if not (cik and adsh):
            continue
        u = "https://www.sec.gov/Archives/edgar/data/%s/%s/%s" % (cik, adsh.replace("-", ""), h.get("_id", "").split(":")[-1])
        out.append({"t": "%s files %s mentioning the search term" % (re.sub(r"\s*\(CIK.*", "", name), s.get("form", s.get("file_type", "filing"))),
                    "u": u, "at": when(s.get("file_date"))})
    return out


PARSERS = {"rss": parse_feed, "atom": parse_feed, "federalregister": parse_fr, "edgar_fts": parse_efts}


def norm_url(u):
    p = urllib.parse.urlsplit(u.strip())
    q = "&".join(x for x in p.query.split("&") if x and not x.startswith(("utm_", "ref=", "cmpid", "ocid")))
    return urllib.parse.urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/"), q, ""))


def norm_title(t):
    t = re.sub(r"\s+[-|–]\s+[^-|–]{2,40}$", "", t)  # drop " - Outlet" suffix (Google News)
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def due(s, force):
    if force:
        return True
    every = int(s.get("every", RUN_EVERY))
    return every <= RUN_EVERY or (int(time.time() // 60) % every) < RUN_EVERY


def keep(flt, hay):
    """filter: None (keep all) | "name" | ["a", "b"] (all must match) | {"any": [...], "all": [...]} (any one, or all of these)."""
    if not flt:
        return True
    if isinstance(flt, str):
        return bool(FILTERS[flt].search(hay))
    if isinstance(flt, list):
        return all(FILTERS[n].search(hay) for n in flt)
    return any(FILTERS[n].search(hay) for n in flt.get("any", [])) or (
        bool(flt.get("all")) and all(FILTERS[n].search(hay) for n in flt["all"]))


def poll(s):
    t0 = time.time()
    try:
        url = s["url"].replace("{start}", (NOW - dt.timedelta(days=MAX_AGE_DAYS)).strftime("%Y-%m-%d")).replace("{end}", NOW.strftime("%Y-%m-%d"))
        raw = get(url)
        items = PARSERS[s["kind"]](raw)
    except Exception as e:
        return s, None, "%s: %s" % (type(e).__name__, str(e)[:160]), time.time() - t0
    kept = []
    for f in items:
        hay = f["t"] if s.get("match") == "title" else f["t"] + " " + f.get("x", "")
        if not keep(s.get("filter"), hay):
            continue
        if s.get("exclude") and re.search(s["exclude"], f["u"]):
            continue
        kept.append(f)
    return s, (items, kept), None, time.time() - t0


def main():
    args = set(sys.argv[1:])
    test, force = "--test" in args, "--all" in args or "--test" in args
    wire = json.load(open(WIRE)) if os.path.exists(WIRE) else {"items": []}
    status = json.load(open(STATUS)) if os.path.exists(STATUS) else {"sources": {}}
    old = wire.get("items", [])
    seen_u = {norm_url(i["u"]) for i in old}
    seen_t = {norm_title(i["t"]) for i in old}
    srcs = [s for s in SRC["sources"] if s.get("on", True) and due(s, force)]
    new = []
    report = []
    with cf.ThreadPoolExecutor(12) as ex:
        for s, res, err, secs in ex.map(poll, srcs):
            st = status["sources"].setdefault(s["id"], {})
            st["name"] = s["name"]
            st["checked"] = NOW.isoformat(timespec="seconds")
            if err:
                st["ok"] = False
                st["err"] = err
                report.append((s["id"], "FAIL", 0, 0, secs, err))
                continue
            items, kept = res
            st.update(ok=True, err=None, last_ok=st["checked"], n=len(items))
            report.append((s["id"], "ok", len(items), len(kept), secs, ""))
            for f in kept:
                at = f.get("at")
                if at and (NOW - at).days > MAX_AGE_DAYS:
                    continue
                if at and at > NOW + dt.timedelta(hours=1):
                    at = NOW
                nu, nt = norm_url(f["u"]), norm_title(f["t"])
                if nu in seen_u or nt in seen_t or not nt:
                    continue
                seen_u.add(nu); seen_t.add(nt)
                new.append({"id": hashlib.sha1(nu.encode()).hexdigest()[:12], "t": f["t"][:240], "u": f["u"],
                            "o": f.get("via_o") or s["org"], "via": s["name"] if f.get("via_o") else None,
                            "lane": s.get("lane", "news"),
                            "at": (at or NOW).isoformat(timespec="seconds"), "seen": NOW.isoformat(timespec="seconds"),
                            "status": "unverified headline"})
    if test:
        w = max(len(r[0]) for r in report) if report else 10
        for r in sorted(report):
            print("%-*s %-4s items=%-4d kept=%-4d %5.1fs %s" % (w, r[0], r[1], r[2], r[3], r[4], r[5]))
        print("sources=%d ok=%d failed=%d new_headlines=%d" % (len(report), sum(r[1] == "ok" for r in report), sum(r[1] != "ok" for r in report), len(new)))
        return
    changed = bool(new)
    for n in new:
        n.pop("via", None) if n.get("via") is None else None
    items = sorted(new + old, key=lambda i: i["at"], reverse=True)[:KEEP]
    if changed:
        wire = {"name": CFG["name"], "updated": NOW.isoformat(timespec="seconds"),
                "note": "Unverified headlines collected automatically from public feeds. Not checked by %s. Verified items appear in the Feed." % CFG["name"],
                "items": items}
        status["updated"] = NOW.isoformat(timespec="seconds")
        json.dump(wire, open(WIRE, "w"), indent=0, ensure_ascii=False)
        json.dump(status, open(STATUS, "w"), indent=1, ensure_ascii=False)
    line = "changed=%s" % str(changed).lower()
    print(line, "new=%d" % len(new), "polled=%d" % len(srcs))
    if os.environ.get("GITHUB_OUTPUT"):
        open(os.environ["GITHUB_OUTPUT"], "a").write(line + "\n")


if __name__ == "__main__":
    main()
