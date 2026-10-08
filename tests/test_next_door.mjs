// Tests for Next Door's formulas and data (node --test tests/test_next_door.mjs). No network.
import { test } from "node:test";
import assert from "node:assert/strict";
import {
  ASSUMPTIONS, SOURCES, STATES, CHECKED_ON, annualKwh, households, power, water, townWater, jobs, taxBreak,
  estimate, hasRange, round, formatValue, readParams, toParams, isComplete, MAX_MW,
} from "../docs/next-door/estimates.js";
import { parsePlaces, shortName, findPlace, placesUrl, loadPlaces } from "../docs/next-door/census.js";

const close = (a, b, tol = 1e-6) => assert.ok(Math.abs(a - b) <= tol * Math.max(1, Math.abs(b)), `${a} != ${b}`);

test("every assumption is checked, sourced and located in its source", () => {
  assert.match(CHECKED_ON, /^\d{4}-\d{2}-\d{2}$/);
  for (const [id, a] of Object.entries(ASSUMPTIONS)) {
    assert.equal(a.checked, true, `${id} is not checked`);
    assert.ok(SOURCES[a.sourceId], `${id} has unknown source ${a.sourceId}`);
    assert.ok(a.where && a.where.length > 5, `${id} doesn't say where in the source`);
    assert.ok(a.label && a.unit && a.note, `${id} is missing text`);
    assert.ok(a.low <= a.value && a.value <= a.high, `${id} value outside its range`);
  }
});

test("every source links to https", () => {
  for (const [id, s] of Object.entries(SOURCES)) {
    assert.match(s.url, /^https:\/\//, id);
    assert.ok(s.title && s.publisher && s.year > 2000, id);
  }
});

test("state table matches JLARC (34 exemptions) and Tax Foundation", () => {
  assert.equal(Object.keys(STATES).length, 51);
  assert.equal(Object.values(STATES).filter((s) => s.exemption === true).length, 34);
  for (const c of ["AK", "DE", "MT", "NH", "OR"]) assert.equal(STATES[c].rate, 0, c);
  assert.equal(STATES.DC.exemption, null);
  assert.equal(STATES.VA.rate, 0.053);
  assert.equal(STATES.VA.exemption, true);
  for (const c of ["CA", "KS", "NJ", "NM"]) assert.equal(STATES[c].exemption, false, c);
  for (const s of Object.values(STATES)) assert.match(s.fips, /^\d{2}$/);
  assert.equal(new Set(Object.values(STATES).map((s) => s.fips)).size, 51);
});

test("electricity: homes' worth", () => {
  assert.equal(annualKwh(100), 100 * 1000 * 8760 * 0.5);
  const p = power(100);
  close(p.value, 438_000_000 / 10791);
  close(p.low, 438_000_000 / 14774);
  close(p.high, 438_000_000 / 6178);
  assert.ok(p.low < p.value && p.value < p.high);
  close(households(25_300), 10_000);
});

test("water: gallons a day via PUE and WUE", () => {
  const w = water(100);
  const itKwh = (100 * 1000 * 24 * 0.5) / 1.4;
  close(w.value, (itKwh * 0.36) / 3.785412);
  close(w.low, (itKwh * 0.32) / 3.785412);
  close(w.high, (itKwh * 0.48) / 3.785412);
  close(w.value, 81_516.3, 1e-5);
  assert.equal(townWater(20_000), 1_640_000);
});

test("jobs: Virginia ratio, no range", () => {
  const j = jobs(100);
  close(j.value, (100 * 8000) / 5050);
  assert.equal(hasRange(j), false);
  close(ASSUMPTIONS.jobsPerMw.value, ASSUMPTIONS.vaJobs.value / ASSUMPTIONS.vaMw.value);
});

test("tax: only with an exemption, a sales tax and an investment", () => {
  const t = taxBreak("VA", 300e6, 20_000);
  close(t.total, 300e6 * 0.682 * 0.053);
  close(t.perResident.value, (300e6 * 0.682 * 0.053) / 20_000);
  assert.equal(taxBreak("VA", 0, 20_000), null);
  assert.equal(taxBreak("VA", undefined, 20_000), null);
  assert.equal(taxBreak("CA", 300e6, 20_000), null); // no exemption
  assert.equal(taxBreak("OR", 300e6, 20_000), null); // no sales tax
  assert.equal(taxBreak("DC", 300e6, 20_000), null); // not covered
  assert.equal(taxBreak("ZZ", 300e6, 20_000), null);
});

test("estimate clamps size and bundles everything", () => {
  const e = estimate({ state: "VA", mw: 300, population: 20_000, investment: 500e6 });
  close(e.power.value, power(300).value);
  close(e.water.value, water(300).value);
  assert.equal(e.construction, 1500);
  assert.ok(e.tax.total > 0);
  close(estimate({ state: "VA", mw: 99_999, population: 1 }).power.value, power(MAX_MW).value);
});

test("rounding and formatting", () => {
  assert.equal(round(40_589.4), 41_000);
  assert.equal(round(81_516.3), 82_000);
  assert.equal(round(158.4), 160);
  assert.equal(round(47.6), 48);
  assert.equal(round(1_234_567), 1_200_000);
  assert.equal(formatValue(40_589.4), "41,000");
  assert.equal(formatValue(1_234_567), "1.2 million");
  assert.equal(formatValue(542.19, "usd"), "$540");
  assert.equal(formatValue(18_073_000, "usd"), "$18 million");
  assert.equal(formatValue(NaN), "0");
});

test("shareable URL round-trips", () => {
  const p = { town: "Culpeper", state: "VA", mw: 300, population: 20_620, investment: 500e6 };
  const back = readParams("?" + toParams(p));
  assert.deepEqual(back, p);
  assert.ok(isComplete(back));
  assert.equal(new URLSearchParams(toParams({ ...p, investment: 0 })).has("inv"), false);
  const bad = readParams("?town=X&state=zz&mw=-4&pop=abc");
  assert.equal(bad.state, "");
  assert.equal(bad.mw, undefined);
  assert.equal(bad.population, undefined);
  assert.equal(isComplete(bad), false);
  assert.equal(readParams("?state=va").state, "VA");
  assert.equal(readParams("?mw=50000").mw, MAX_MW);
});

test("Census places: parse, name and match", async () => {
  const rows = [
    ["NAME", "B01003_001E", "state", "place"],
    ["Culpeper town, Virginia", "20620", "51", "20752"],
    ["Richmond city, Virginia", "227171", "51", "67000"],
    ["Bad place, Virginia", "null", "51", "1"],
  ];
  const places = parsePlaces(rows);
  assert.deepEqual(places.map((p) => p.name), ["Culpeper", "Richmond"]);
  assert.equal(shortName("Ventura (San Buenaventura) city, California"), "Ventura (San Buenaventura)");
  assert.equal(shortName("Bethesda CDP, Maryland"), "Bethesda");
  assert.equal(findPlace(places, " culpeper ").population, 20620);
  assert.equal(findPlace(places, "Culpeper town").population, 20620);
  assert.equal(findPlace(places, "Nowhere"), null);
  assert.deepEqual(parsePlaces(null), []);
  assert.match(placesUrl("51", ""), /acs\/acs5\?get=NAME,B01003_001E&for=place:\*&in=state:51$/);
  assert.match(placesUrl("51", "k y"), /&key=k%20y$/);

  const ok = await loadPlaces("99", { fetchFn: async () => ({ ok: true, json: async () => rows }) });
  assert.equal(ok.length, 2);
  await assert.rejects(loadPlaces("98", { fetchFn: async () => ({ ok: false, status: 302 }) }));
  await assert.rejects(loadPlaces("97", { fetchFn: async () => { throw new TypeError("Failed to fetch"); } }));
});
