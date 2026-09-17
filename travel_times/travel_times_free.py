#!/usr/bin/env python3
# =============================================================================
#  FILL TRAVEL TIMES  -  NO API KEY VERSION
#  Bengaluru non-shifters OD file. Free public services, no signup, no key.
# =============================================================================
#
#  WHAT THIS IS
#  A drop-in alternative to travel_times.py that needs no API key. It swaps
#  TomTom for two free public services:
#
#    geocoding   Nominatim        (OpenStreetMap)  nominatim.openstreetmap.org
#    routing     Valhalla         (FOSSGIS)        valhalla1.openstreetmap.de
#
#  Valhalla is the reason to prefer this over OSRM: it has real `motorcycle`,
#  `bus` and `auto` costing models, so the three columns you actually want map
#  onto genuine travel modes rather than one car profile for everything.
#
#  It reads the PLACES dictionary from travel_times.py rather than keeping its
#  own copy, so the two scripts can never drift apart. Fix a place name once
#  and both pick it up. travel_times.py must sit in the same folder.
#
# -----------------------------------------------------------------------------
#  READ THIS BEFORE YOU USE ANY NUMBER IT PRODUCES
# -----------------------------------------------------------------------------
#  NO TRAFFIC. This is the big one. Nominatim and Valhalla route on OSM speed
#  limits, with no congestion data of any kind. Every time below is a FREE-FLOW
#  time: what the trip would take on empty roads.
#
#  In Bengaluru that is not a small correction. Free-flow times will understate
#  real peak-hour travel substantially, and they understate it UNEVENLY - a
#  congested arterial is hit harder than a quiet side road, so the gap is not a
#  constant you can multiply away. If your analysis turns on why people do not
#  switch modes, congestion is close to the centre of the question and this
#  version cannot see it.
#
#  Concretely, compared with the TomTom version:
#    - there is NO traffic delay column, because there is no traffic model
#    - --depart is GONE. Departure time changes nothing here, so offering the
#      option would imply a precision that does not exist
#    - the same OD pair returns the same time at 09:00 and at 23:00
#
#  Use this to get the geometry and the mode ordering roughly right, to test
#  the pipeline, or where free-flow time is genuinely what you want. For
#  peak-hour figures in a published output, use a traffic-aware service and
#  say which one.
#
#  EVERYTHING ELSE FROM travel_times.py STILL APPLIES:
#    Auto/Cab is a capped-motorcycle proxy. No routing engine has an
#    auto-rickshaw mode. The cap is an ASSUMPTION, not a finding.
#    Bus is in-vehicle road time for a bus-sized vehicle. NOT a BMTC journey
#    time - it excludes waiting, dwell time and transfers, which are often the
#    majority of a real bus trip. A true bus time needs BMTC GTFS data.
#    Every trip end is a locality CENTROID, not a respondent address.
#
#  GEOCODING IS WEAKER TOO. Nominatim is good but not as strong as a
#  commercial geocoder on Bengaluru locality names. The output therefore
#  records what Nominatim actually matched for every place, plus how far that
#  is from the city centre, so you can audit it. Read those columns.
#
# -----------------------------------------------------------------------------
#  FAIR USE  -  these are donated public servers, not a paid tier
# -----------------------------------------------------------------------------
#  Both services are run by volunteers and funded by donations. Their usage
#  policies are conditions of access, not suggestions:
#    - Nominatim: absolute maximum 1 request per second, and a User-Agent that
#      identifies who is calling. Set CONTACT below or the script will stop.
#    - Valhalla/FOSSGIS: fair use, no heavy batch loads.
#  This script rate-limits itself and caches everything, so a re-run costs no
#  requests at all. Do not raise the rate to speed it up.
#    Nominatim policy   https://operations.osmfoundation.org/policies/nominatim/
#    FOSSGIS services   https://www.fossgis.de/arbeitsgruppen/osm-server/
#
# -----------------------------------------------------------------------------
#  HOW TO RUN
# -----------------------------------------------------------------------------
#    1. Put this beside travel_times.py and the xlsx.
#    2. Set CONTACT below to your work email.
#    3. python3 -m pip install requests openpyxl
#    4. python3 travel_times_free.py
#       Preview without making any requests:
#         python3 travel_times_free.py --dry-run
#
#  Takes roughly 8 minutes for this file: 66 geocodes at 1/sec, then 368
#  routes. Re-runs are instant from cache.
#
#  Geocoding (c) OpenStreetMap contributors, ODbL. Routing by Valhalla on
#  FOSSGIS infrastructure, on OpenStreetMap data. Attribute both if you
#  publish anything derived from them.
# =============================================================================

# ----------------------------- SETTINGS --------------------------------------

CONTACT = ""          # <<< YOUR WORK EMAIL. Required by Nominatim's policy so
                      #     they can contact you about a misbehaving script.
                      #     Leave blank and this script stops.

INPUT_FILE = "Non_Shifters_120_Improved_Approx_Travel_Times.xlsx"
OUTPUT_FILE = "Travel_Times_FILLED_free.xlsx"

RICKSHAW_MAX_SPEED_KMPH = 45   # assumption for the Auto/Cab column - calibrate
SHORT_TRIP_KM = 3.0            # below this, flag the row as unreliable

NOMINATIM_DELAY = 1.1          # seconds. Their policy is max 1/sec. Do not lower.
VALHALLA_DELAY = 0.3           # seconds, to stay a polite guest
MAX_RETRIES = 4                # public servers throttle; back off and retry

# -----------------------------------------------------------------------------

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

try:
    import requests
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
except ImportError as e:
    sys.exit(f"Missing library: {e.name}\n"
             f"Install both with:\n    python3 -m pip install requests openpyxl")

try:
    from travel_times import AMBER, BODY, HDRF, NAVY, NOTEF, RED, REVIEW, THIN, \
        WHY, YELL, canonical, norm
except ImportError:
    sys.exit("Could not import travel_times.py.\n"
             "  This script reads the PLACES dictionary from travel_times.py so\n"
             "  the two cannot drift apart. Put them in the SAME FOLDER.")

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
VALHALLA_URL = "https://valhalla1.openstreetmap.de/route"

BLR = (12.9716, 77.5946)   # city centre, for the geocode sanity check
FAR_FROM_BLR_KM = 120.0    # beyond this, flag the geocode as suspicious

# Valhalla costing models. The third entry caps top speed to stand in for an
# auto-rickshaw, exactly as the TomTom version does with vehicleMaxSpeed.
MODES = (("auto", None),
         ("motorcycle", None),
         ("motorcycle", RICKSHAW_MAX_SPEED_KMPH),
         ("bus", None))


def haversine_km(a, b):
    r = 6371.0
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp, dl = p2 - p1, math.radians(b[1] - a[1])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def get_contact():
    c = (CONTACT or os.environ.get("OSM_CONTACT") or "").strip()
    if not c:
        sys.exit("\nNo contact address set.\n"
                 "  Nominatim's usage policy requires a User-Agent that identifies\n"
                 "  the caller, so they can get in touch about a script that\n"
                 "  misbehaves. It is a condition of using the service.\n\n"
                 "  Set CONTACT near the top of this file, or run:\n"
                 "      export OSM_CONTACT=you@ceew.in\n\n"
                 "  Policy: https://operations.osmfoundation.org/policies/nominatim/\n")
    return c


def load_cache(p):
    if p.exists():
        try:
            return json.loads(p.read_text())
        except json.JSONDecodeError:
            print(f"  (cache {p.name} was corrupt, starting fresh)")
    return {}


def request_with_retry(method, url, ua, **kw):
    """Public servers throttle. Back off on 429 and 5xx, fail fast otherwise."""
    delay = 2.0
    last = None
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.request(method, url, headers={"User-Agent": ua},
                                 timeout=45, **kw)
        except requests.RequestException as e:
            last = f"{type(e).__name__}: {e}"
            if attempt == MAX_RETRIES - 1:
                raise RuntimeError(f"network error after {MAX_RETRIES} tries: {last}")
            print(f"      network error, retrying in {delay:.0f}s ({last})")
            time.sleep(delay)
            delay *= 2
            continue

        if r.status_code == 429 or r.status_code >= 500:
            last = f"HTTP {r.status_code}"
            if attempt == MAX_RETRIES - 1:
                raise RuntimeError(f"{last} after {MAX_RETRIES} tries - the server is "
                                   f"throttling or down. Wait and re-run; the cache "
                                   f"keeps what you already have.")
            print(f"      {last}, backing off {delay:.0f}s")
            time.sleep(delay)
            delay *= 2
            continue
        return r
    raise RuntimeError(last or "unreachable")


# ============================== GEOCODING =====================================

def geocode(query, cache, ua):
    """Nominatim. Falls back to a shortened query if the full string misses."""
    if query in cache:
        return cache[query], True

    tries = [query]
    parts = [p.strip() for p in query.split(",")]
    if len(parts) > 2:                       # 'X, Bengaluru, Karnataka' -> 'X, Bengaluru'
        tries.append(", ".join(parts[:-1]))
    if len(parts) > 1:                       # then just the locality plus the city
        tries.append(f"{parts[0]}, Bengaluru")

    for i, q in enumerate(tries):
        r = request_with_retry("GET", NOMINATIM_URL, ua,
                               params={"q": q, "format": "jsonv2", "limit": 1,
                                       "countrycodes": "in",
                                       "addressdetails": 0})
        if r.status_code == 403:
            sys.exit("\nNominatim returned 403 - blocked.\n"
                     "  Almost always a User-Agent problem. Set CONTACT to a real\n"
                     "  address. If it persists you have exceeded the 1/sec limit;\n"
                     "  wait an hour before retrying.\n")
        r.raise_for_status()
        res = r.json() or []
        time.sleep(NOMINATIM_DELAY)
        if res:
            hit = res[0]
            pos = (float(hit["lat"]), float(hit["lon"]))
            v = {"lat": pos[0], "lon": pos[1],
                 "matched": hit.get("display_name", ""),
                 "kind": f"{hit.get('category', '')}/{hit.get('type', '')}".strip("/"),
                 "query_used": q,
                 "fallback": i > 0,
                 "km_from_centre": round(haversine_km(pos, BLR), 1)}
            cache[query] = v
            return v, False

    raise ValueError("no Nominatim result, including shortened queries")


# ============================== ROUTING =======================================

def route(o, d, costing, top_speed, cache, ua):
    ck = f"{o[0]:.5f},{o[1]:.5f}|{d[0]:.5f},{d[1]:.5f}|{costing}|{top_speed}"
    if ck in cache:
        return cache[ck], True

    body = {
        "locations": [{"lat": o[0], "lon": o[1]}, {"lat": d[0], "lon": d[1]}],
        "costing": costing,
        "directions_options": {"units": "kilometers"},
    }
    if top_speed:
        body["costing_options"] = {costing: {"top_speed": int(top_speed)}}

    r = request_with_retry("POST", VALHALLA_URL, ua, json=body)
    if r.status_code >= 400:
        try:
            msg = r.json().get("error", r.text[:160])
        except ValueError:
            msg = r.text[:160]
        raise RuntimeError(f"HTTP {r.status_code}: {msg}")

    trip = (r.json() or {}).get("trip") or {}
    summ = trip.get("summary")
    if not summ:
        raise RuntimeError("no route returned")
    v = {"t": summ["time"], "d": summ["length"] * 1000}   # seconds, metres
    cache[ck] = v
    time.sleep(VALHALLA_DELAY)
    return v, False


# ============================== WORKBOOK ======================================

HEAD = ["PID", "Home area", "work area",
        "2-Wheeler Time (approx)", "Bus Time (approx)", "Auto/Cab Time (approx)",
        "Distance (km)", "Car (min)",
        "Home area used", "Work area used",
        "Home geocoded as", "Work geocoded as", "Status"]
WIDTHS = [8, 26, 26, 15, 13, 16, 12, 10, 30, 30, 44, 44, 32]
NCOL = len(HEAD)

NOTE = [
    "ALL TIMES ARE FREE-FLOW. There is no traffic model anywhere in this file. "
    "Valhalla routes on OSM speed limits, so these are empty-road times and they "
    "understate real Bengaluru peak travel substantially - and unevenly, because a "
    "congested arterial is hit harder than a quiet side road. Do not present any "
    "figure here as a peak-hour or typical-commute time.",
    "There is no traffic delay column because there is nothing to put in it. The same "
    "OD pair returns the same time at 09:00 and at 23:00.",
    "2-Wheeler Time = Valhalla `motorcycle` costing.",
    f"Auto/Cab Time = Valhalla `motorcycle` costing capped at {RICKSHAW_MAX_SPEED_KMPH} "
    "km/h. No routing engine has an auto-rickshaw mode; this is a proxy and the cap is "
    "an ASSUMPTION, not a finding. Calibrate it against real observed trips and state it "
    "in your methodology. Car time is shown separately so you can see how much the mode "
    "choice moves the number. Valhalla also offers `motor_scooter` and `taxi` costing if "
    "you want to test a different proxy.",
    "Bus Time = Valhalla `bus` costing: in-vehicle road time for a bus-sized vehicle. "
    "NOT a BMTC journey time. It EXCLUDES waiting for the bus, stop dwell time and "
    "transfers, which are often the majority of a real bus trip. A true bus time needs "
    "BMTC route and headway (GTFS) data. Do not present this column as a bus journey time.",
    "'Home/Work geocoded as' is what Nominatim actually returned, and is there to be "
    "READ, not ignored. Nominatim is weaker than a commercial geocoder on Bengaluru "
    "locality names. A row whose geocode landed somewhere unexpected is flagged in "
    "Status, but only your eye will catch a match that is plausible and still wrong.",
    "Origins and destinations are locality CENTROIDS, not respondent addresses - that is "
    f"all the source file records. Trips under {SHORT_TRIP_KM} km are flagged unreliable "
    "because the centroid error is then a large share of the trip.",
    "Rows marked NEEDS REVIEW were left blank on purpose rather than guessed. See the "
    "'Needs review' sheet.",
    "Geocoding (c) OpenStreetMap contributors, ODbL. Routing by Valhalla on FOSSGIS "
    "infrastructure, on OpenStreetMap data. Attribute both if you publish anything "
    "derived from this. Verify before publication.",
]


def write_workbook(path, rows, geo, geo_fail, route_fail):
    wb = Workbook()
    ws = wb.active
    ws.title = "Travel Times"
    ws.append(HEAD)
    for c in ws[1]:
        c.fill, c.font = PatternFill("solid", fgColor=NAVY), HDRF
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 34

    for x in rows:
        hg = geo.get(x["home_c"], {})
        wg = geo.get(x["work_c"], {})
        ws.append([x["pid"], x["home"], x["work"],
                   x.get("m2w"), x.get("mbus"), x.get("mauto"),
                   x.get("km"), x.get("mcar"),
                   x["home_c"] or "", x["work_c"] or "",
                   hg.get("matched", ""), wg.get("matched", ""),
                   x["status"]])
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.font, c.border = BODY, THIN
            c.alignment = Alignment(vertical="top", wrap_text=True)
        for i in (3, 4, 5, 6, 7):
            row[i].number_format = "0.0"
        st = str(row[NCOL - 1].value)
        if st == "NEEDS REVIEW":
            row[NCOL - 1].fill = RED
        elif st != "ok":
            row[NCOL - 1].fill = AMBER
    for i, w in enumerate(WIDTHS, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "D2"
    ws.auto_filter.ref = f"A1:{get_column_letter(NCOL)}{ws.max_row}"

    r = ws.max_row + 2
    ws.cell(r, 1, "What these columns mean - read before using any figure").font = \
        Font(name="Arial", size=11, bold=True, color=NAVY)
    r += 1
    ws.cell(r, 1, "Engine: Valhalla (FOSSGIS) on OpenStreetMap data, via Nominatim "
                  "geocoding. No API key, and no traffic data.").font = NOTEF
    r += 1
    for line in NOTE:
        c = ws.cell(r, 1, "•  " + line)
        c.font = NOTEF
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=NCOL)
        ws.row_dimensions[r].height = 14 * (1 + len(line) // 130)
        r += 1

    rv = wb.create_sheet("Needs review")
    rv.append(["PID", "Field", "Value as recorded", "Why it was not resolved",
               "Correct place (fill in)"])
    for c in rv[1]:
        c.fill, c.font = PatternFill("solid", fgColor=NAVY), HDRF
    for x in rows:
        for field, raw in (("Home", x["home"]), ("Work", x["work"])):
            if canonical(raw)[1] == REVIEW:
                rv.append([x["pid"], field, raw,
                           WHY.get(norm(raw), "Could not be matched to a known locality."), ""])
    for row in rv.iter_rows(min_row=2):
        for c in row:
            c.font, c.border = BODY, THIN
            c.alignment = Alignment(wrap_text=True, vertical="top")
        row[4].fill = YELL
    for i, w in enumerate([8, 10, 28, 58, 32], 1):
        rv.column_dimensions[get_column_letter(i)].width = w
    rv.freeze_panes = "A2"
    r = rv.max_row + 2
    c = rv.cell(r, 1, "Fill the yellow column, then edit the PLACES dictionary in "
                      "travel_times.py (replace None with the place name, change REVIEW "
                      "to MED) and run again. resolve_places.py proposes candidates for "
                      "these, though it needs a TomTom key.")
    c.font, c.alignment = NOTEF, Alignment(wrap_text=True)
    rv.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)

    gs = wb.create_sheet("Geocoding")
    gs.append(["Canonical place asked for", "Query Nominatim answered",
               "Fell back to a shorter query", "What Nominatim matched",
               "Kind of place", "Lat", "Lon", "km from city centre", "Check"])
    for c in gs[1]:
        c.fill, c.font = PatternFill("solid", fgColor=NAVY), HDRF
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for p in sorted(geo):
        g = geo[p]
        far = g["km_from_centre"] > FAR_FROM_BLR_KM
        gs.append([p, g["query_used"], "yes" if g["fallback"] else "",
                   g["matched"], g["kind"], g["lat"], g["lon"],
                   g["km_from_centre"],
                   "FAR FROM BENGALURU - check" if far
                   else ("matched on a shortened query - check" if g["fallback"] else "")])
    for row in gs.iter_rows(min_row=2):
        for c in row:
            c.font, c.border = BODY, THIN
            c.alignment = Alignment(wrap_text=True, vertical="top")
        row[5].number_format = row[6].number_format = "0.00000"
        row[7].number_format = "0.0"
        if str(row[8].value).startswith("FAR"):
            for c in row:
                c.fill = RED
        elif row[8].value:
            for c in row:
                c.fill = AMBER
    for i, w in enumerate([34, 34, 14, 52, 16, 11, 11, 12, 30], 1):
        gs.column_dimensions[get_column_letter(i)].width = w
    gs.freeze_panes = "A2"
    r = gs.max_row + 2
    c = gs.cell(r, 1, "Every trip in this workbook starts and ends at one of these "
                      "points. A wrong point here is a wrong travel time everywhere it "
                      "appears, so this sheet is worth a slow read. Nominatim is weaker "
                      "than a commercial geocoder on Bengaluru locality names.")
    c.font, c.alignment = NOTEF, Alignment(wrap_text=True, vertical="top")
    gs.merge_cells(start_row=r, start_column=1, end_row=r, end_column=9)
    gs.row_dimensions[r].height = 30

    if geo_fail or route_fail:
        f = wb.create_sheet("Failures")
        f.append(["Type", "Item", "Error"])
        for c in f[1]:
            c.fill, c.font = PatternFill("solid", fgColor=NAVY), HDRF
        for k, e in geo_fail:
            f.append(["geocode", k, e])
        for k, e in route_fail:
            f.append(["route", k, e])
        for row in f.iter_rows(min_row=2):
            for c in row:
                c.font, c.border = BODY, THIN
                c.alignment = Alignment(wrap_text=True, vertical="top")
        for i, w in enumerate([12, 62, 60], 1):
            f.column_dimensions[get_column_letter(i)].width = w

    wb.save(path)


# ============================== MAIN =========================================

def main():
    ap = argparse.ArgumentParser(
        description="Fill travel times with no API key, using Nominatim and Valhalla. "
                    "Free-flow times only - there is no traffic model.")
    ap.add_argument("--input", default=None, help=f"default: {INPUT_FILE}")
    ap.add_argument("--output", default=None, help=f"default: {OUTPUT_FILE}")
    ap.add_argument("--dry-run", action="store_true", help="No requests; just report.")
    a = ap.parse_args()

    here = Path(__file__).resolve().parent
    inp = Path(a.input) if a.input else here / INPUT_FILE
    outp = Path(a.output) if a.output else here / OUTPUT_FILE
    if not inp.is_absolute():
        inp = (Path.cwd() / inp).resolve()
    if not outp.is_absolute():
        outp = (Path.cwd() / outp).resolve()

    print("=" * 70)
    print(f" INPUT   {inp}")
    print(f" OUTPUT  {outp}")
    print(" ENGINE  Nominatim + Valhalla, no API key, NO TRAFFIC MODEL")
    print("=" * 70)
    if not inp.exists():
        sys.exit(f"\nInput file not found.\n  Looked for: {inp}\n"
                 f"  Put '{INPUT_FILE}' beside this script, or pass --input <path>.\n")
    if outp.resolve() == inp.resolve():
        sys.exit("\nOutput would overwrite your input file. Choose a different --output.\n")

    ws = load_workbook(inp, data_only=True).active
    rows = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not r or not r[0]:
            continue
        rows.append({"pid": str(r[0]).strip(),
                     "home": str(r[1]).replace("\xa0", " ").strip(),
                     "work": str(r[2]).replace("\xa0", " ").strip()})
    if not rows:
        sys.exit("No data rows found. Is row 1 the header and column A the PID?")

    for x in rows:
        x["home_c"], hc = canonical(x["home"])
        x["work_c"], wc = canonical(x["work"])
        x["blocked"] = REVIEW in (hc, wc)
        x["status"] = "NEEDS REVIEW" if x["blocked"] else "ok"

    todo = [x for x in rows if not x["blocked"]]
    places = sorted({x["home_c"] for x in todo} | {x["work_c"] for x in todo})
    pairs = sorted({(x["home_c"], x["work_c"]) for x in todo})

    mins = (len(places) * NOMINATIM_DELAY + len(pairs) * len(MODES) * VALHALLA_DELAY) / 60
    print(f"\n respondents        {len(rows)}")
    print(f" ready to route     {len(todo)}")
    print(f" need your decision {len(rows) - len(todo)}")
    print(f" unique places      {len(places)}   -> Nominatim requests")
    print(f" unique OD pairs    {len(pairs)}   -> {len(pairs)*len(MODES)} Valhalla requests")
    print(f" rough run time     {mins:.0f} min (rate-limited on purpose; cache makes "
          f"re-runs instant)")

    if a.dry_run:
        print("\n --dry-run: no requests made, no output written.")
        blocked = [x for x in rows if x["blocked"]]
        if blocked:
            print("\n rows needing a decision before they can be routed:")
            for x in blocked:
                bad = []
                if canonical(x["home"])[1] == REVIEW:
                    bad.append(f"home={x['home']!r}")
                if canonical(x["work"])[1] == REVIEW:
                    bad.append(f"work={x['work']!r}")
                print(f"   {x['pid']:<7} {', '.join(bad)}")
        print("\n Reminder: this engine has NO traffic data. Free-flow times only.\n")
        return

    contact = get_contact()
    ua = f"ceew-bbus-traveltime/1.0 ({contact})"
    gc_path = outp.parent / "geocode_cache_osm.json"
    rc_path = outp.parent / "route_cache_valhalla.json"
    gcache, rcache = load_cache(gc_path), load_cache(rc_path)

    print(f"\n geocoding via Nominatim (1/sec by policy)...")
    geo, coords, geo_fail = {}, {}, []
    try:
        for i, p in enumerate(places, 1):
            try:
                g, was_cached = geocode(p, gcache, ua)
                geo[p] = g
                coords[p] = (g["lat"], g["lon"])
                flag = ""
                if g["km_from_centre"] > FAR_FROM_BLR_KM:
                    flag = f"  <- {g['km_from_centre']:.0f} km from centre, CHECK"
                elif g["fallback"]:
                    flag = "  <- matched on a shortened query, check"
                print(f"   [{i}/{len(places)}] {p}{'  (cached)' if was_cached else ''}{flag}")
            except Exception as e:
                geo_fail.append((p, str(e)))
                print(f"   [{i}/{len(places)}] FAILED  {p}  ({e})")
    finally:
        gc_path.write_text(json.dumps(gcache, indent=1, sort_keys=True))

    print("\n routing via Valhalla...")
    res, route_fail = {}, []
    try:
        for i, (o, d) in enumerate(pairs, 1):
            if o not in coords or d not in coords:
                route_fail.append((f"{o} -> {d}", "an endpoint failed geocoding"))
                continue
            try:
                got = {}
                for costing, ts in MODES:
                    v, _ = route(coords[o], coords[d], costing, ts, rcache, ua)
                    got[(costing, ts)] = v
                res[(o, d)] = got
                print(f"   [{i}/{len(pairs)}] {o.split(',')[0]} -> {d.split(',')[0]}")
            except Exception as e:
                route_fail.append((f"{o} -> {d}", str(e)))
                print(f"   [{i}/{len(pairs)}] FAILED  ({e})")
    finally:
        rc_path.write_text(json.dumps(rcache, indent=1, sort_keys=True))

    filled = 0
    for x in rows:
        if x["blocked"]:
            continue
        got = res.get((x["home_c"], x["work_c"]))
        if not got:
            x["status"] = "routing failed - see Failures sheet"
            continue
        km = got[("auto", None)]["d"] / 1000
        x["km"] = round(km, 2)
        x["mcar"] = round(got[("auto", None)]["t"] / 60, 1)
        x["m2w"] = round(got[("motorcycle", None)]["t"] / 60, 1)
        x["mauto"] = round(got[("motorcycle", RICKSHAW_MAX_SPEED_KMPH)]["t"] / 60, 1)
        x["mbus"] = round(got[("bus", None)]["t"] / 60, 1)

        notes = []
        if x["home_c"] == x["work_c"]:
            notes.append("same locality - centroid method cannot resolve this trip")
        elif km < SHORT_TRIP_KM:
            notes.append(f"short trip ({km:.1f} km) - centroid unreliable")
        for end, lbl in ((x["home_c"], "home"), (x["work_c"], "work")):
            g = geo.get(end, {})
            if g.get("km_from_centre", 0) > FAR_FROM_BLR_KM:
                notes.append(f"{lbl} geocode {g['km_from_centre']:.0f} km from centre")
            elif g.get("fallback"):
                notes.append(f"{lbl} geocoded on a shortened query")
        if notes:
            x["status"] = "; ".join(notes)
        filled += 1

    write_workbook(outp, rows, geo, geo_fail, route_fail)

    print("\n" + "=" * 70)
    print(f" WROTE  {outp}")
    print("=" * 70)
    print(f"   {filled} of {len(rows)} rows filled")
    print(f"   {sum(x['blocked'] for x in rows)} need your decision  -> 'Needs review' sheet")
    flagged = sum(1 for x in rows if x["status"] not in ("ok", "NEEDS REVIEW"))
    if flagged:
        print(f"   {flagged} filled but flagged -> read the Status column")
    if geo_fail or route_fail:
        print(f"   {len(geo_fail)} geocoding + {len(route_fail)} routing failures "
              f"-> 'Failures' sheet")
    print("\n FREE-FLOW TIMES ONLY. No traffic model, so these understate real")
    print(" Bengaluru peak travel substantially and unevenly. Do not present any")
    print(" figure here as a peak-hour time.")
    print(" Auto/Cab is a capped-motorcycle proxy, not a measured rickshaw time.")
    print(" Bus is in-vehicle road time only - it excludes waiting and transfers.")
    print(" Read the 'Geocoding' sheet: a wrong point there is wrong everywhere.\n")


if __name__ == "__main__":
    main()
