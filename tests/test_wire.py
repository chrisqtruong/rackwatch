#!/usr/bin/env python3
"""Offline tests for scripts/wire.py parsing, filtering and de-duplication (no network)."""
import importlib.util, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("wire", os.path.join(ROOT, "scripts", "wire.py"))
w = importlib.util.module_from_spec(spec)
sys.argv = ["wire.py"]
spec.loader.exec_module(w)

RSS = b"""<?xml version="1.0"?><rss version="2.0"><channel><title>x</title>
<item><title>FTC Sues Data Broker &amp; Partner</title><link>https://www.ftc.gov/a?utm_source=rss</link><pubDate>Mon, 05 Oct 2026 14:00:00 GMT</pubDate><description>&lt;p&gt;privacy&lt;/p&gt;</description></item>
<item><title>County approves data center - Local Paper</title><link>https://news.google.com/rss/articles/abc</link><pubDate>Mon, 05 Oct 2026 13:00:00 GMT</pubDate><source url="https://paper.example">Local Paper</source></item>
</channel></rss>"""
ATOM = b"""<?xml version="1.0" encoding="utf-8"?><feed xmlns="http://www.w3.org/2005/Atom"><title>t</title>
<entry><title type="html">8-K - MICROSOFT CORP</title><link rel="alternate" href="https://www.sec.gov/x"/><updated>2026-10-05T09:00:00-04:00</updated><summary>Item 1.01</summary></entry></feed>"""
FR = json.dumps({"results": [{"title": "Large Load Interconnection", "html_url": "https://www.federalregister.gov/d/1", "publication_date": "2026-10-02", "type": "Proposed Rule", "agencies": [{"name": "FERC"}]}]}).encode()

def test():
    r = w.parse_feed(RSS)
    assert len(r) == 2 and r[0]["t"] == "FTC Sues Data Broker & Partner", r
    assert r[0]["x"] == "privacy" and r[0]["at"].hour == 14
    assert r[1]["via_o"] == "Local Paper"
    a = w.parse_feed(ATOM)
    assert a[0]["u"] == "https://www.sec.gov/x" and a[0]["at"].hour == 13
    f = w.parse_fr(FR)
    assert f[0]["t"] == "Large Load Interconnection" and "FERC" in f[0]["x"]
    assert w.norm_url("https://WWW.ftc.gov/a/?utm_source=rss") == "https://www.ftc.gov/a"
    assert w.norm_title("County approves data center - Local Paper") == w.norm_title("County approves data center")
    assert w.FILTERS["tech"].search("FTC Sues Data Broker")
    assert not w.FILTERS["dc"].search("Utility files wildfire plan")
    assert w.FILTERS["dc"].search("Utility signs large-load deal with hyperscaler")
    cfg = json.load(open(os.path.join(ROOT, "wire-sources.json")))
    ids = [s["id"] for s in cfg["sources"]]
    assert len(ids) == len(set(ids)), "duplicate source ids"
    for s in cfg["sources"]:
        assert s["kind"] in w.PARSERS and s["url"].startswith("https://"), s["id"]
        assert not s.get("filter") or s["filter"] in w.FILTERS, s["id"]
    print("wire tests ok (%d sources configured, %d on)" % (len(ids), sum(s.get("on", True) for s in cfg["sources"])))

test()
