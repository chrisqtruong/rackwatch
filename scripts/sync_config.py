#!/usr/bin/env python3
"""Copy the public part of tracker.config.json into docs/config.json (read by the page).
The tracker's name lives in exactly one place: "name" in tracker.config.json."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
c = json.load(open(os.path.join(ROOT, "tracker.config.json")))
keys = ["name", "slug", "tagline", "categories", "ledger_types", "archive_days", "tz", "site_url", "repo_url",
        "sister", "giscus", "wire_interval", "routine_interval"]
out = {k: c[k] for k in keys if k in c}
p = os.path.join(ROOT, "docs", "config.json")
new = json.dumps(out, indent=1, ensure_ascii=False) + "\n"
if not os.path.exists(p) or open(p).read() != new:
    open(p, "w").write(new)
    print("docs/config.json updated")
