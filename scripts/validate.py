#!/usr/bin/env python3
"""Validate Tracewire data files. Exit 1 on any error. Run before every commit."""
import csv, glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda *p: os.path.join(ROOT, *p)
cfg = json.load(open(D("tracker.config.json")))
errs, warns = [], []
err = errs.append
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID = re.compile(r"^[a-z0-9-]{3,80}$")
STATES = set("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split())

data = json.load(open(D("docs", "data.json")))
ents = json.load(open(D("docs", "entities.json")))["entities"]
E = {}
for e in ents:
    if not ID.match(e.get("id", "")): err("entity bad id: %r" % e.get("id"))
    if e["id"] in E: err("entity duplicate id: " + e["id"])
    if e.get("k") not in ("company", "agency", "official", "utility", "place", "court", "group"): err("entity %s bad kind %r" % (e["id"], e.get("k")))
    if not e.get("n"): err("entity %s has no name" % e["id"])
    E[e["id"]] = e

def src_ok(where, src, need_title=True):
    if not src: err(where + ": no sources")
    for s in src or []:
        if not re.match(r"^https://", s.get("u", "")): err(where + ": source URL must be https: %r" % s.get("u"))
        if not s.get("o"): err(where + ": source without outlet")
        if need_title and not s.get("t"): warns.append(where + ": source without title")

def ents_ok(where, ids):
    for i in ids or []:
        if i not in E: err("%s: unknown entity %r (add it to docs/entities.json)" % (where, i))

posts = [(p, "data.json") for p in data.get("feed", [])]
idx = json.load(open(D("docs", "archive", "index.json")))
months = {m["m"]: m["n"] for m in idx.get("months", [])}
for f in sorted(glob.glob(D("docs", "archive", "????-??.json"))):
    m = os.path.basename(f)[:7]
    a = json.load(open(f))
    if a.get("month") != m: err(f + ": month field mismatch")
    if months.get(m) != len(a.get("feed", [])): err("archive/index.json count for %s is %s, file has %d" % (m, months.get(m), len(a.get("feed", []))))
    for p in a.get("feed", []):
        if p.get("d", "")[:7] != m: err("%s: post %s dated %s is in the wrong month file" % (f, p.get("id"), p.get("d")))
        posts.append((p, "archive/" + m))
if idx.get("total") != sum(months.values()): err("archive/index.json total mismatch")
for m in months:
    if not os.path.exists(D("docs", "archive", m + ".json")): err("archive/index.json lists missing month " + m)

seen = set()
for p, where in posts:
    w = "%s post %s" % (where, p.get("id"))
    for k in ("d", "id", "c", "s", "h", "b", "src"):
        if k not in p: err(w + ": missing " + k)
    if p.get("id") in seen: err(w + ": duplicate id")
    seen.add(p.get("id"))
    if not ID.match(p.get("id", "")): err(w + ": bad id format")
    if not DATE.match(p.get("d", "")): err(w + ": bad date")
    if p.get("c") not in cfg["categories"]: err(w + ": unknown category %r" % p.get("c"))
    if p.get("s") not in ("confirmed", "reported", "disputed"): err(w + ": bad status")
    src_ok(w, p.get("src"))
    if p.get("s") == "confirmed" and len(p.get("src", [])) < 2: warns.append(w + ": confirmed with one source")
    ents_ok(w, p.get("e"))
    for s in p.get("st", []):
        if s not in STATES: err(w + ": bad state " + s)
    for q in re.findall(r"[\"“]([^\"”]+)[\"”]", p.get("b", "") + " " + p.get("h", "")):
        if len(q.split()) >= 15: err(w + ": quotation of 15+ words")
    if p.get("pin") and not p.get("pinUntil"): err(w + ": pin without pinUntil")
    for u in p.get("updates", []):
        if not (DATE.match(u.get("d", "")) and u.get("t") and u.get("u", "").startswith("https://")): err(w + ": bad update entry")
    if p.get("img"):
        for k in ("u", "alt", "credit", "lic", "page"):
            if not p["img"].get(k): err(w + ": image missing " + k)
pins = [p for p in data.get("feed", []) if p.get("pin")]
if len(pins) > 2: err("more than two pinned posts")

lids = set()
for r in data.get("ledger", []):
    w = "ledger %s" % r.get("id")
    if not ID.match(r.get("id", "")): err(w + ": bad id")
    if r.get("id") in lids: err(w + ": duplicate id")
    lids.add(r.get("id"))
    if not DATE.match(r.get("d", "")): err(w + ": bad date")
    if r.get("t") not in cfg["ledger_types"]: err(w + ": unknown type %r" % r.get("t"))
    if r.get("amt") is not None and not isinstance(r["amt"], (int, float)): err(w + ": amt must be a number or null")
    for k in ("fe", "te"):
        if r.get(k): ents_ok(w, [r[k]])
    ents_ok(w, r.get("e"))
    src_ok(w, r.get("src"), need_title=False)

for pr in data.get("projects", []):
    w = "project %s" % pr.get("id")
    for k in ("id", "n", "st", "place", "status", "power", "water", "incent", "opp", "d", "src"):
        if k not in pr: err(w + ": missing " + k)
    if pr.get("st") not in STATES: err(w + ": bad state")
    ents_ok(w, pr.get("e"))
    src_ok(w, pr.get("src"), need_title=False)

for c in data.get("checks", []):
    if not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", c.get("t", "")): err("checks: bad time %r" % c.get("t"))
    for k in ("triaged", "opened", "added", "corrected", "ledger", "rejected"):
        if c.get(k) is not None and not isinstance(c[k], int): err("checks %s: %s must be a whole number or null" % (c.get("t"), k))
if len(data.get("checks", [])) > 200: err("checks: keep at most 200 entries (drop the oldest)")
for p_, where in posts:
    for m in re.finditer(r"\(Corrected ([^:)]*)", p_.get("b", "")):
        if not DATE.match(m.group(1)): err("%s post %s: correction note must read (Corrected YYYY-MM-DD: what changed.)" % (where, p_.get("id")))
if os.path.exists(D("docs", "source-archive.json")):
    sa = json.load(open(D("docs", "source-archive.json")))
    for u, v in sa.get("urls", {}).items():
        if v.get("a") and not v["a"].startswith("https://web.archive.org/"): err("source-archive: bad snapshot for " + u)

# ledger.csv must mirror the ledger
rows = list(csv.reader(open(D("ledger.csv"), newline="")))
if rows[0] != ["date", "type", "from", "to", "amount_usd", "note", "sources"]: err("ledger.csv header changed")
if len(rows) - 1 != len(data.get("ledger", [])): err("ledger.csv has %d rows, data.json ledger has %d (run scripts/ledger_csv.py)" % (len(rows) - 1, len(data.get("ledger", []))))

for f in ("wire.json",):
    if os.path.exists(D("docs", f)):
        w = json.load(open(D("docs", f)))
        if len(w.get("items", [])) > 200: err("wire.json holds more than 200 items")

for x in warns: print("warn:", x)
for x in errs: print("ERROR:", x)
print("%d posts (%d in feed), %d ledger rows, %d entities, %d projects: %s" % (
    len(posts), len(data.get("feed", [])), len(data.get("ledger", [])), len(E), len(data.get("projects", [])), "FAILED" if errs else "ok"))
sys.exit(1 if errs else 0)
