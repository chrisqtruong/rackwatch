// Live population lookup: Census ACS 5-year estimates, all places in one state.
// The Census API now asks for a key. Get a free one at https://api.census.gov/data/key_signup.html
// and paste it below. Without a key (or if the request fails) the page asks people to type the population.
export const CENSUS_KEY = "";
export const ACS_YEAR = 2024; // 2020–2024 5-year estimates

export function placesUrl(fips, key = CENSUS_KEY) {
  const u = `https://api.census.gov/data/${ACS_YEAR}/acs/acs5?get=NAME,B01003_001E&for=place:*&in=state:${fips}`;
  return key ? `${u}&key=${encodeURIComponent(key)}` : u;
}

const SUFFIX = / (city|town|village|borough|CDP|municipality|city and borough|urban county|consolidated government|metro government|unified government|zona urbana|comunidad)(\s*\(.*\))?$/i;

/** "Culpeper town, Virginia" → "Culpeper". */
export const shortName = (name) => name.split(",")[0].replace(SUFFIX, "").trim();

/** Census rows ([["NAME","B01003_001E","state","place"], ...]) → [{name, full, population}], sorted by name. */
export function parsePlaces(rows) {
  if (!Array.isArray(rows) || rows.length < 2) return [];
  const [head, ...data] = rows;
  const iName = head.indexOf("NAME"), iPop = head.indexOf("B01003_001E");
  if (iName < 0 || iPop < 0) return [];
  return data
    .map((r) => ({ full: String(r[iName]), name: shortName(String(r[iName])), population: Number(r[iPop]) }))
    .filter((p) => p.name && Number.isFinite(p.population) && p.population > 0)
    .sort((a, b) => a.name.localeCompare(b.name));
}

/** Best match for what someone typed: exact name first, then the full Census name. */
export function findPlace(places, typed) {
  const t = typed.trim().toLowerCase();
  if (!t) return null;
  const exact = places.filter((p) => p.name.toLowerCase() === t);
  if (exact.length) return exact.sort((a, b) => b.population - a.population)[0];
  return places.find((p) => p.full.split(",")[0].toLowerCase() === t) || null;
}

const cache = new Map();

/** Fetch places for a state FIPS code. Rejects on network errors, a missing key or a bad response. */
export async function loadPlaces(fips, { fetchFn = fetch, key = CENSUS_KEY, timeoutMs = 8000 } = {}) {
  if (cache.has(fips)) return cache.get(fips);
  const ctl = typeof AbortController === "function" ? new AbortController() : null;
  const timer = ctl && setTimeout(() => ctl.abort(), timeoutMs);
  try {
    const res = await fetchFn(placesUrl(fips, key), ctl ? { signal: ctl.signal } : {});
    if (!res.ok) throw new Error(`Census returned ${res.status}`);
    const places = parsePlaces(await res.json());
    if (!places.length) throw new Error("Census returned no places");
    cache.set(fips, places);
    return places;
  } finally {
    if (timer) clearTimeout(timer);
  }
}
