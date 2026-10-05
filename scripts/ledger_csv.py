#!/usr/bin/env python3
"""Regenerate ledger.csv (newest first) from the ledger in docs/data.json."""
import csv, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(os.path.join(ROOT, "docs", "data.json")))
rows = sorted(data.get("ledger", []), key=lambda r: r["d"], reverse=True)
with open(os.path.join(ROOT, "ledger.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["date", "type", "from", "to", "amount_usd", "note", "sources"])
    for r in rows:
        w.writerow([r["d"], r["t"], r["from"], r["to"], "" if r.get("amt") is None else r["amt"], r.get("note", ""), " ".join(s["u"] for s in r.get("src", []))])
print("ledger.csv: %d rows" % len(rows))
