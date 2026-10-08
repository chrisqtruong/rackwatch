// Next Door: every assumption, source and formula behind the estimates.
// Rule (METHOD.md): nothing is published unless it was checked against a source we opened.
// Each assumption records where in the source the figure appears and when it was checked.
// tests/test_next_door.mjs fails if any assumption is unchecked or has no source.

export const CHECKED_ON = "2026-10-07";

export const SOURCES = {
  lbnl: {
    title: "2024 United States Data Center Energy Usage Report",
    publisher: "Lawrence Berkeley National Laboratory",
    url: "https://eta-publications.lbl.gov/sites/default/files/2024-12/lbnl-2024-united-states-data-center-energy-usage-report_1.pdf",
    year: 2024,
  },
  eia: {
    title: "How much electricity does an American home use?",
    publisher: "U.S. Energy Information Administration",
    url: "https://www.eia.gov/tools/faqs/faq.php?id=97&t=3",
    year: 2022,
  },
  epa: {
    title: "WaterSense: Statistics and Facts",
    publisher: "U.S. Environmental Protection Agency",
    url: "https://www.epa.gov/watersense/statistics-and-facts",
    year: 2015,
  },
  census: {
    title: "QuickFacts: United States, persons per household",
    publisher: "U.S. Census Bureau",
    url: "https://www.census.gov/quickfacts/fact/table/US/HSD310224",
    year: 2024,
  },
  acs: {
    title: "American Community Survey 5-year estimates, total population (B01003)",
    publisher: "U.S. Census Bureau",
    url: "https://www.census.gov/data/developers/data-sets/acs-5year.html",
    year: 2024,
  },
  usgs: {
    title: "How big would a million-gallon swimming pool be?",
    publisher: "U.S. Geological Survey",
    url: "https://www.usgs.gov/water-science-school/science/a-million-gallons-water-how-much-it",
    year: 2019,
  },
  nist: {
    title: "NIST Guide to the SI, Appendix B.9: conversion factors",
    publisher: "National Institute of Standards and Technology",
    url: "https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors/nist-guide-si-appendix-b9",
    year: 2019,
  },
  jlarc: {
    title: "Data Centers in Virginia (Report 598)",
    publisher: "Joint Legislative Audit and Review Commission of Virginia",
    url: "https://jlarc.virginia.gov/pdfs/reports/Rpt598.pdf",
    year: 2024,
  },
  taxfdn: {
    title: "State and Local Sales Tax Rates, 2026",
    publisher: "Tax Foundation",
    url: "https://taxfoundation.org/data/all/state/sales-tax-rates/",
    year: 2026,
  },
};

// value is the figure used; low and high are a range only when the source publishes one.
// derived: the figure is calculated from other checked figures, shown in `note`.
export const ASSUMPTIONS = {
  loadFactor: {
    label: "Share of rated power drawn on average",
    value: 0.5, low: 0.5, high: 0.5, unit: "share",
    sourceId: "lbnl", where: "Executive summary (national capacity utilization assumption)",
    note: "LBNL's own assumption for turning yearly energy use into power demand. One facility may run higher or lower.",
    checked: true,
  },
  pue: {
    label: "Total facility power for each unit of computer power (PUE)",
    value: 1.4, low: 1.4, high: 1.4, unit: "ratio",
    sourceId: "lbnl", where: "Section 4, Figure 4.6 (2023 national average)",
    note: "Used to separate the computers' share of power, because cooling water is measured against it.",
    checked: true,
  },
  wue: {
    label: "On-site cooling water per kWh of computer power (WUE)",
    value: 0.36, low: 0.32, high: 0.48, unit: "liters / kWh",
    sourceId: "lbnl", where: "Section 4: 2023 average just over 0.36; 0.32 modeled for hyperscale; up to 0.48 projected for 2028",
    note: "National averages. A single facility's cooling design can put it well outside this range. Excludes water used by power plants.",
    checked: true,
  },
  litersPerGallon: {
    label: "Liters in one U.S. gallon",
    value: 3.785412, low: 3.785412, high: 3.785412, unit: "liters",
    sourceId: "nist", where: "Table B.9, gallon [U.S.] to liter",
    note: "Unit conversion.",
    checked: true,
  },
  householdKwh: {
    label: "Electricity bought by an average U.S. home",
    value: 10791, low: 6178, high: 14774, unit: "kWh / year",
    sourceId: "eia", where: "2022 national average; range is lowest state (Hawaii) to highest (Louisiana)",
    note: "Range spans state averages.",
    checked: true,
  },
  waterPerPerson: {
    label: "Water each American uses at home",
    value: 82, low: 82, high: 82, unit: "gallons / day",
    sourceId: "epa", where: "Statistics and Facts (EPA cites USGS water use estimates for 2015)",
    note: "Used to compare the facility's cooling water with residents' home use.",
    checked: true,
  },
  personsPerHousehold: {
    label: "People per household, U.S.",
    value: 2.53, low: 2.53, high: 2.53, unit: "people",
    sourceId: "census", where: "Persons per household, 2020–2024",
    note: "Used to estimate how many households your town has.",
    checked: true,
  },
  poolGallons: {
    label: "Water in USGS's million-gallon pool (267 ft long, 50 ft wide, 10 ft deep)",
    value: 1_000_000, low: 1_000_000, high: 1_000_000, unit: "gallons",
    sourceId: "usgs", where: "Pool dimensions for one million gallons",
    note: "A yardstick for scale only.",
    checked: true,
  },
  vaJobs: {
    label: "Full-time workers at Virginia data centers, FY2023",
    value: 8000, low: 8000, high: 8000, unit: "jobs",
    sourceId: "jlarc", where: "Chapter 2: direct employees and full-time contract workers, \"over 8,000\"",
    note: "About half are contract workers such as electricians and security staff. JLARC says \"over\" 8,000, so this is a floor.",
    checked: true,
  },
  vaMw: {
    label: "Power used by Virginia data centers",
    value: 5050, low: 5050, high: 5050, unit: "MW",
    sourceId: "jlarc", where: "Chapter 1: about 5,050 MW, from 2024 utility peak load forecasts",
    note: "Measured as peak load, not rated capacity.",
    checked: true,
  },
  jobsPerMw: {
    label: "Permanent jobs per megawatt",
    value: 8000 / 5050, low: 8000 / 5050, high: 8000 / 5050, unit: "jobs / MW",
    sourceId: "jlarc", where: "Derived: 8,000 workers ÷ 5,050 MW",
    note: "Our calculation from the two JLARC figures above, for Virginia, the largest U.S. market. JLARC does not publish a per-megawatt figure.",
    derived: true,
    checked: true,
  },
  constructionPeak: {
    label: "Workers on site at the height of building one facility",
    value: 1500, low: 1500, high: 1500, unit: "workers",
    sourceId: "jlarc", where: "Chapter 2: figure given to JLARC by data center representatives; a building takes 12 to 18 months",
    note: "Per facility, not scaled by size. A campus can take five or more years to build out.",
    checked: true,
  },
  exemptShare: {
    label: "Share of initial spending on tax-exempt equipment and software",
    value: 0.682, low: 0.682, high: 0.682, unit: "share",
    sourceId: "jlarc", where: "Appendix D, Table D-1 (Virginia Economic Development Partnership data, 2021–2023)",
    note: "Virginia data centers that used the exemption. Equipment is usually replaced about every five years, which is exempt again and not counted here.",
    checked: true,
  },
};

// Statewide sales tax rate (Tax Foundation, rates as of January 1, 2026) and whether the state had a
// data center sales tax exemption in 2024 (JLARC Report 598, Appendix E, Figure E-1).
// exemption: true / false; null where JLARC's map does not cover the jurisdiction (D.C.).
export const STATES = {
  AL: { name: "Alabama", fips: "01", rate: 0.04, exemption: true },
  AK: { name: "Alaska", fips: "02", rate: 0, exemption: false },
  AZ: { name: "Arizona", fips: "04", rate: 0.056, exemption: true },
  AR: { name: "Arkansas", fips: "05", rate: 0.065, exemption: true },
  CA: { name: "California", fips: "06", rate: 0.0725, exemption: false },
  CO: { name: "Colorado", fips: "08", rate: 0.029, exemption: false },
  CT: { name: "Connecticut", fips: "09", rate: 0.0635, exemption: true },
  DE: { name: "Delaware", fips: "10", rate: 0, exemption: false },
  DC: { name: "District of Columbia", fips: "11", rate: 0.06, exemption: null },
  FL: { name: "Florida", fips: "12", rate: 0.06, exemption: true },
  GA: { name: "Georgia", fips: "13", rate: 0.04, exemption: true },
  HI: { name: "Hawaii", fips: "15", rate: 0.04, exemption: false },
  ID: { name: "Idaho", fips: "16", rate: 0.06, exemption: true },
  IL: { name: "Illinois", fips: "17", rate: 0.0625, exemption: true },
  IN: { name: "Indiana", fips: "18", rate: 0.07, exemption: true },
  IA: { name: "Iowa", fips: "19", rate: 0.06, exemption: true },
  KS: { name: "Kansas", fips: "20", rate: 0.065, exemption: false },
  KY: { name: "Kentucky", fips: "21", rate: 0.06, exemption: true },
  LA: { name: "Louisiana", fips: "22", rate: 0.05, exemption: true },
  ME: { name: "Maine", fips: "23", rate: 0.055, exemption: false },
  MD: { name: "Maryland", fips: "24", rate: 0.06, exemption: true },
  MA: { name: "Massachusetts", fips: "25", rate: 0.0625, exemption: false },
  MI: { name: "Michigan", fips: "26", rate: 0.06, exemption: true },
  MN: { name: "Minnesota", fips: "27", rate: 0.06875, exemption: true },
  MS: { name: "Mississippi", fips: "28", rate: 0.07, exemption: true },
  MO: { name: "Missouri", fips: "29", rate: 0.04225, exemption: true },
  MT: { name: "Montana", fips: "30", rate: 0, exemption: false },
  NE: { name: "Nebraska", fips: "31", rate: 0.055, exemption: true },
  NV: { name: "Nevada", fips: "32", rate: 0.0685, exemption: true },
  NH: { name: "New Hampshire", fips: "33", rate: 0, exemption: false },
  NJ: { name: "New Jersey", fips: "34", rate: 0.06625, exemption: false },
  NM: { name: "New Mexico", fips: "35", rate: 0.04875, exemption: false },
  NY: { name: "New York", fips: "36", rate: 0.04, exemption: true },
  NC: { name: "North Carolina", fips: "37", rate: 0.0475, exemption: true },
  ND: { name: "North Dakota", fips: "38", rate: 0.05, exemption: true },
  OH: { name: "Ohio", fips: "39", rate: 0.0575, exemption: true },
  OK: { name: "Oklahoma", fips: "40", rate: 0.045, exemption: true },
  OR: { name: "Oregon", fips: "41", rate: 0, exemption: false },
  PA: { name: "Pennsylvania", fips: "42", rate: 0.06, exemption: true },
  RI: { name: "Rhode Island", fips: "44", rate: 0.07, exemption: false },
  SC: { name: "South Carolina", fips: "45", rate: 0.06, exemption: true },
  SD: { name: "South Dakota", fips: "46", rate: 0.042, exemption: false },
  TN: { name: "Tennessee", fips: "47", rate: 0.07, exemption: true },
  TX: { name: "Texas", fips: "48", rate: 0.0625, exemption: true },
  UT: { name: "Utah", fips: "49", rate: 0.061, exemption: true },
  VT: { name: "Vermont", fips: "50", rate: 0.06, exemption: false },
  VA: { name: "Virginia", fips: "51", rate: 0.053, exemption: true },
  WA: { name: "Washington", fips: "53", rate: 0.065, exemption: true },
  WV: { name: "West Virginia", fips: "54", rate: 0.06, exemption: true },
  WI: { name: "Wisconsin", fips: "55", rate: 0.05, exemption: true },
  WY: { name: "Wyoming", fips: "56", rate: 0.04, exemption: true },
};

// JLARC's example of a typical modern 250,000-square-foot facility in Virginia (Chapter 2).
export const VA_EXAMPLE = { costLow: 250e6, costHigh: 325e6, savingsLow: 9e6, savingsHigh: 15.5e6 };

// Figures we looked for and left out because no source we opened supports them.
export const LEFT_OUT = [
  "Construction workers per megawatt: JLARC gives a per-facility figure only, which we show instead.",
  "Equipment spending per megawatt: no source we opened publishes one. Enter the announced investment instead.",
  "Water in an Olympic pool: published depths differ, so the volume does. We use USGS's million-gallon pool.",
  "Local sales taxes: rates vary by town, so the tax figure uses the statewide rate only.",
];

const A = ASSUMPTIONS;
export const MAX_MW = 10000;

const range = (value, a, b) => ({ value, low: Math.min(a, b), high: Math.max(a, b) });

/** Average yearly electricity, kWh, for a facility of `mw` rated megawatts. */
export const annualKwh = (mw, lf = A.loadFactor.value) => mw * 1000 * 8760 * lf;

/** Households in a town of `population`. */
export const households = (population) => population / A.personsPerHousehold.value;

/** Homes' worth of electricity: yearly use ÷ one home's yearly use. */
export function power(mw) {
  const kwh = annualKwh(mw);
  return range(kwh / A.householdKwh.value, kwh / A.householdKwh.high, kwh / A.householdKwh.low);
}

/** On-site cooling water, gallons a day: daily kWh ÷ PUE (computer share) × WUE, in gallons. */
export function water(mw) {
  const itKwhPerDay = (mw * 1000 * 24 * A.loadFactor.value) / A.pue.value;
  const gal = (wue) => (itKwhPerDay * wue) / A.litersPerGallon.value;
  return range(gal(A.wue.value), gal(A.wue.low), gal(A.wue.high));
}

/** Gallons a day used at home by the town's residents. */
export const townWater = (population) => population * A.waterPerPerson.value;

/** Permanent jobs: megawatts × Virginia's jobs per megawatt. */
export function jobs(mw) {
  const n = mw * A.jobsPerMw.value;
  return range(n, n, n);
}

/**
 * Sales tax not collected on initial equipment, per resident.
 * investment is in dollars. Returns null when it can't be estimated (no investment entered,
 * no exemption, exemption unknown, or no statewide sales tax).
 */
export function taxBreak(state, investment, population) {
  const st = STATES[state];
  if (!st || st.exemption !== true || !(st.rate > 0) || !(investment > 0) || !(population > 0)) return null;
  const total = investment * A.exemptShare.value * st.rate;
  return { total, perResident: range(total / population, total / population, total / population) };
}

/** All four estimates for one set of inputs. */
export function estimate({ state, mw, population, investment }) {
  const m = Math.min(Math.max(mw, 0), MAX_MW);
  return {
    households: households(population),
    power: power(m),
    water: water(m),
    townWater: townWater(population),
    jobs: jobs(m),
    construction: A.constructionPeak.value,
    tax: taxBreak(state, investment, population),
  };
}

export const hasRange = (r) => r.high - r.low > Math.abs(r.value) * 1e-9;

/** Round for reading: two significant figures from 100 up, whole numbers below. */
export function round(n) {
  if (!Number.isFinite(n)) return 0;
  if (Math.abs(n) < 100) return Math.round(n);
  const p = 10 ** (Math.floor(Math.log10(Math.abs(n))) - 1);
  return Math.round(n / p) * p;
}

/** "41,000", "1.2 million", "$540", "$18 million". */
export function formatValue(n, kind = "count") {
  const r = round(n);
  const s = Math.abs(r) >= 1e6 ? `${(r / 1e6).toLocaleString("en-US", { maximumFractionDigits: 1 })} million` : r.toLocaleString("en-US");
  return kind === "usd" ? "$" + s : s;
}

/** Read inputs from a query string. Investment is stored in millions of dollars (inv). */
export function readParams(search) {
  const q = new URLSearchParams(search);
  const num = (k) => { const n = Number(q.get(k)); return Number.isFinite(n) && n > 0 ? n : undefined; };
  const state = (q.get("state") || "").toUpperCase();
  return {
    town: (q.get("town") || "").trim().slice(0, 80),
    state: STATES[state] ? state : "",
    mw: num("mw") ? Math.min(num("mw"), MAX_MW) : undefined,
    population: num("pop") ? Math.round(num("pop")) : undefined,
    investment: num("inv") ? num("inv") * 1e6 : undefined,
  };
}

export function toParams({ town, state, mw, population, investment }) {
  const q = new URLSearchParams({ town, state, mw: String(mw), pop: String(population) });
  if (investment > 0) q.set("inv", String(investment / 1e6));
  return q.toString();
}

export const isComplete = (p) => Boolean(p.town && p.state && p.mw && p.population);
