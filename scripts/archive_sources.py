#!/usr/bin/env python3
"""Save every source link to the Internet Archive and remember the snapshot.

Reads source URLs from docs/data.json (feed, ledger, projects, pinned updates) and
docs/archive/*.json. For each URL not yet in docs/source-archive.json it first asks
the Wayback Machine for an existing snapshot, and if there is none asks it to save
the page. Results go to docs/source-archive.json:

  {"updated": ISO, "urls": {"<source url>": {"a": "<snapshot url>", "at": "YYYY-MM-DD"} |
                                           {"tries": n, "err": "...", "last": ISO}}}

Standard library only. Prints changed=true|false (also to $GITHUB_OUTPUT).
  python3 scripts/archive_sources.py [--max N]
"""
import datetime as dt, glob, json, os, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "source-archive.json")
CFG = json.load(open(os.path.join(ROOT, "tracker.config.json")))
UA = "%s source archiver (+https://github.com/%s/%s)" % (CFG["name"], CFG.get("owner", ""), CFG["slug"])
MAX = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 15
MAX_TRIES = 5
NOW = dt.datetime.now(dt.timezone.utc)


def get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.geturl(), r.headers, r.read()


def sources():
    files = [os.path.join(ROOT, "docs", "data.json")] + sorted(glob.glob(os.path.join(ROOT, "docs", "archive", "????-??.json")))
    urls = []
    for f in files:
        d = json.load(open(f))
        for p in d.get("feed", []):
            urls += [s.get("u") for s in p.get("src", [])] + [u.get("u") for u in p.get("updates", [])]
        for r in d.get("ledger", []) + d.get("projects", []):
            urls += [s.get("u") for s in r.get("src", [])]
    seen, out = set(), []
    for u in urls:
        if u and u.startswith("https://") and u not in seen:
            seen.add(u); out.append(u)
    return out


def available(u):
    _, _, raw = get("https://archive.org/wayback/available?" + urllib.parse.urlencode({"url": u}), timeout=30)
    snap = json.loads(raw).get("archived_snapshots", {}).get("closest") or {}
    if snap.get("available") and snap.get("url"):
        ts = snap.get("timestamp", "")
        return snap["url"].replace("http://", "https://", 1), "%s-%s-%s" % (ts[:4], ts[4:6], ts[6:8]) if ts else NOW.date().isoformat()
    return None


def save(u):
    final, headers, _ = get("https://web.archive.org/save/" + u, timeout=120)
    loc = headers.get("Content-Location") or ""
    if loc.startswith("/web/"):
        return "https://web.archive.org" + loc, NOW.date().isoformat()
    if "/web/" in final:
        return final.replace("http://", "https://", 1), NOW.date().isoformat()
    return None


def main():
    state = json.load(open(OUT)) if os.path.exists(OUT) else {"urls": {}}
    m = state.setdefault("urls", {})
    todo = [u for u in sources() if not m.get(u, {}).get("a") and m.get(u, {}).get("tries", 0) < MAX_TRIES]
    changed = False
    for u in todo[:MAX]:
        rec = m.get(u, {})
        try:
            hit = available(u) or save(u)
            if not hit:
                time.sleep(8)
                hit = available(u)
            if hit:
                m[u] = {"a": hit[0], "at": hit[1]}
            else:
                raise RuntimeError("no snapshot returned")
        except Exception as e:
            m[u] = {"tries": rec.get("tries", 0) + 1, "err": ("%s: %s" % (type(e).__name__, e))[:160], "last": NOW.isoformat(timespec="seconds")}
        changed = True
        print(("saved " if m[u].get("a") else "failed ") + u)
        time.sleep(6)  # stay well under the Wayback Machine's rate limits
    total = len(sources())
    done = sum(1 for u in sources() if m.get(u, {}).get("a"))
    if changed:
        state["updated"] = NOW.isoformat(timespec="seconds")
        state["total"], state["saved"] = total, done
        json.dump(state, open(OUT, "w"), indent=1, ensure_ascii=False)
    line = "changed=%s" % str(changed).lower()
    print(line, "saved=%d/%d" % (done, total), "left=%d" % max(0, len(todo) - MAX))
    if os.environ.get("GITHUB_OUTPUT"):
        open(os.environ["GITHUB_OUTPUT"], "a").write(line + "\n")


if __name__ == "__main__":
    main()
