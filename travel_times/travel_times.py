#!/usr/bin/env python3
# =============================================================================
#  FILL TRAVEL TIMES  -  Bengaluru non-shifters OD file
#  Single self-contained script. Nothing else to download.
# =============================================================================
#
#  INPUT FILE   Non_Shifters_120_Improved_Approx_Travel_Times.xlsx
#               Put it in the SAME FOLDER as this script.
#               Expected columns, in this order:
#                   A  PID
#                   B  Home area
#                   C  work area
#                   D  2-Wheeler Time (approx)      <- filled by this script
#                   E  Bus Time (approx)            <- filled by this script
#                   F  Auto/Cab Time (approx)       <- filled by this script
#
#  OUTPUT FILE  Travel_Times_FILLED.xlsx
#               Written into the same folder. Your input file is NEVER modified.
#               Sheet 1 "Travel Times"  - your original columns, now filled,
#                                         plus distance, car time, traffic delay,
#                                         the canonical place names used, status
#               Sheet 2 "Needs review"  - rows whose area name could not be
#                                         resolved, with the reason
#               Sheet 3 "Place map"     - every raw spelling -> canonical place
#
#  ALSO WRITTEN  geocode_cache.json, route_cache.json
#                Caches so re-runs cost no API quota. Safe to delete.
#
# -----------------------------------------------------------------------------
#  HOW TO RUN
# -----------------------------------------------------------------------------
#    1. Get a free TomTom key (email signup, NO credit card):
#         https://developer.tomtom.com/
#    2. Paste it into API_KEY below.
#    3. Install the two libraries once:
#         python3 -m pip install requests openpyxl
#    4. Run it. No arguments needed - the VS Code Run button works:
#         python3 travel_times.py
#       Preview without spending any API calls:
#         python3 travel_times.py --dry-run
#       Model a specific departure time instead of traffic right now:
#         python3 travel_times.py --depart 2026-09-21T09:00:00+05:30
#
#  Quota: about 66 geocoding + 276 routing calls for this file.
#  TomTom free tier is 20,000 of each per month, so roughly 1.5%.
#
# -----------------------------------------------------------------------------
#  WHAT THE THREE FILLED COLUMNS ACTUALLY MEAN  -  read this
# -----------------------------------------------------------------------------
#  2-Wheeler   TomTom `motorcycle` mode, traffic-aware. Reasonable.
#
#  Auto/Cab    TomTom `motorcycle` mode capped at RICKSHAW_MAX_SPEED_KMPH.
#              NO routing API anywhere has an auto-rickshaw travel mode. Autos
#              are road-bound like cars but filter through congestion like a
#              two-wheeler, and are speed-limited below car free-flow speeds -
#              hence a capped motorcycle proxy. The cap is an ASSUMPTION, not a
#              finding. Calibrate it against real observed trips and state it
#              in your methodology. Car time is given separately so you can see
#              how much the choice moves the number.
#
#  Bus         In-vehicle road time for a bus-sized vehicle. This is NOT a BMTC
#              journey time. It EXCLUDES waiting for the bus, stop dwell time
#              and transfers, which are often the majority of a real bus trip.
#              A true bus travel time needs BMTC route and headway (GTFS) data.
#              Do not present this column as a bus journey time.
#
#  Every origin and destination is a locality CENTROID, not a respondent's
#  address, because that is all the source file records. For trips under about
#  3 km the centroid error is a large share of the trip - those rows are
#  flagged "short trip - centroid unreliable".
#
#  Routing, traffic and geocoding data (c) TomTom.
# =============================================================================

# ----------------------------- SETTINGS --------------------------------------

API_KEY = ""          # <<< PASTE YOUR TOMTOM KEY BETWEEN THE QUOTES
                      #     (or leave blank and set the TOMTOM_API_KEY env var)

INPUT_FILE = "/Users/princek.patel/Downloads/Non_Shifters_120_Improved_Approx_Travel_Times.xlsx"
OUTPUT_FILE = "/Users/princek.patel/Downloads/Travel_Times_FILLED.xlsx"

RICKSHAW_MAX_SPEED_KMPH = 45   # assumption for the Auto/Cab column - calibrate
SHORT_TRIP_KM = 3.0            # below this, flag the row as unreliable

# -----------------------------------------------------------------------------

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

try:
    import requests
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
except ImportError as e:
    sys.exit(f"Missing library: {e.name}\n"
             f"Install both with:\n    python3 -m pip install requests openpyxl")

HERE = Path(__file__).resolve().parent
GEOCODE_URL = "https://api.tomtom.com/search/2/geocode/{q}.json"
ROUTE_URL = "https://api.tomtom.com/routing/1/calculateRoute/{locs}/json"
UA = "ceew-bengaluru-traveltime/1.0"

HIGH, MED, REVIEW = "high", "medium", "review"

# =============================================================================
#  PLACE MAP
#  The source file spells 126 distinct strings for 66 real places (129 before
#  trailing whitespace is trimmed). This maps each spelling to a canonical,
#  geocodable name.
#    high   - unambiguous spelling/case variant
#    medium - defensible reading, worth a glance (includes employer/landmark
#             names resolved to their locality)
#    review - not resolvable from the string alone; NOT routed, flagged for you
#  To fix a "review" entry: replace its None with the correct place name and
#  change REVIEW to MED, then re-run.
# =============================================================================

PLACES = {
    # --- BTM Layout (stage kept where stated) ---
    "btm":                          ("BTM Layout, Bengaluru, Karnataka", HIGH),
    "btm layout":                   ("BTM Layout, Bengaluru, Karnataka", HIGH),
    "btm 1st stage":                ("BTM Layout 1st Stage, Bengaluru, Karnataka", HIGH),
    "btm stage 1":                  ("BTM Layout 1st Stage, Bengaluru, Karnataka", HIGH),
    "btm - 2nd stage":              ("BTM Layout 2nd Stage, Bengaluru, Karnataka", HIGH),
    "btm 2nd stage":                ("BTM Layout 2nd Stage, Bengaluru, Karnataka", HIGH),
    "btm stage -2":                 ("BTM Layout 2nd Stage, Bengaluru, Karnataka", HIGH),
    "btm stage 2":                  ("BTM Layout 2nd Stage, Bengaluru, Karnataka", HIGH),

    # --- Bommanahalli vs Bommasandra: two different places, easily confused ---
    "bomanahali":                   ("Bommanahalli, Bengaluru, Karnataka", HIGH),
    "bomanahalii":                  ("Bommanahalli, Bengaluru, Karnataka", HIGH),
    "bomanahalli":                  ("Bommanahalli, Bengaluru, Karnataka", HIGH),
    "bommanahalli":                 ("Bommanahalli, Bengaluru, Karnataka", HIGH),
    "bomasandra":                   ("Bommasandra, Bengaluru, Karnataka", HIGH),
    "bommasandra":                  ("Bommasandra, Bengaluru, Karnataka", HIGH),
    "bommasandra onam temple":      ("Bommasandra, Bengaluru, Karnataka", MED),
    "biocon bommasandra":           ("Biocon Limited, Bommasandra, Bengaluru, Karnataka", MED),

    # --- Electronic City corridor ---
    "electronic city":              ("Electronic City, Bengaluru, Karnataka", HIGH),
    "electronic city phase-1":      ("Electronic City Phase 1, Bengaluru, Karnataka", HIGH),
    "electronic city phase 1":      ("Electronic City Phase 1, Bengaluru, Karnataka", HIGH),
    "electronic city phase 2":      ("Electronic City Phase 2, Bengaluru, Karnataka", HIGH),
    "e city phase 2":               ("Electronic City Phase 2, Bengaluru, Karnataka", HIGH),
    "electronic city (infosys)":    ("Infosys Electronic City, Bengaluru, Karnataka", MED),
    "electronic city, nbil":        ("Electronic City, Bengaluru, Karnataka", MED),
    "velankani tech park":          ("Velankani Tech Park, Electronic City, Bengaluru, Karnataka", MED),
    "hebbagodi":                    ("Hebbagodi, Bengaluru, Karnataka", HIGH),
    "hebbaguddi":                   ("Hebbagodi, Bengaluru, Karnataka", HIGH),
    "kammasandra":                  ("Kammasandra, Bengaluru, Karnataka", HIGH),
    "chandapura":                   ("Chandapura, Bengaluru, Karnataka", HIGH),
    "chandrapura":                  ("Chandapura, Bengaluru, Karnataka", MED),
    "doddaganamangala road":        ("Doddanagamangala Road, Bengaluru, Karnataka", MED),
    "doddanamangala rd":            ("Doddanagamangala Road, Bengaluru, Karnataka", MED),
    "singasandra":                  ("Singasandra, Bengaluru, Karnataka", HIGH),
    "singasandra near metro":       ("Singasandra, Bengaluru, Karnataka", MED),
    "anekal":                       ("Anekal, Karnataka", HIGH),
    "aanekal":                      ("Anekal, Karnataka", HIGH),

    # --- South Bengaluru core ---
    "jayanagar":                    ("Jayanagar, Bengaluru, Karnataka", HIGH),
    "jaynagar 9th block":           ("Jayanagar 9th Block, Bengaluru, Karnataka", HIGH),
    "banashankari":                 ("Banashankari, Bengaluru, Karnataka", HIGH),
    "banishankari":                 ("Banashankari, Bengaluru, Karnataka", HIGH),
    "basavangudi":                  ("Basavanagudi, Bengaluru, Karnataka", HIGH),
    "jp nagar":                     ("JP Nagar, Bengaluru, Karnataka", HIGH),
    "madiwala":                     ("Madiwala, Bengaluru, Karnataka", HIGH),
    "ragigudda":                    ("Ragigudda, Jayanagar, Bengaluru, Karnataka", HIGH),
    "ragiguda":                     ("Ragigudda, Jayanagar, Bengaluru, Karnataka", HIGH),
    "jayadeva":                     ("Jayadeva Hospital, Bengaluru, Karnataka", MED),
    "silk board":                   ("Silk Board Junction, Bengaluru, Karnataka", HIGH),
    "silkboard":                    ("Silk Board Junction, Bengaluru, Karnataka", HIGH),
    "silk board metro station":     ("Silk Board Metro Station, Bengaluru, Karnataka", HIGH),
    "wilison garden":               ("Wilson Garden, Bengaluru, Karnataka", HIGH),
    "tilak nagar":                  ("Tilak Nagar, Bengaluru, Karnataka", HIGH),
    "iti layout":                   ("ITI Layout, Bengaluru, Karnataka", MED),
    "begur main road":              ("Begur Main Road, Bengaluru, Karnataka", HIGH),
    "bannerghattta, ulimavu":       ("Hulimavu, Bannerghatta Road, Bengaluru, Karnataka", MED),
    "bannergata":                   ("Bannerghatta Road, Bengaluru, Karnataka", MED),
    "kudlu":                        ("Kudlu, Bengaluru, Karnataka", HIGH),
    "kudlu gate":                   ("Kudlu Gate, Bengaluru, Karnataka", HIGH),
    "tavarakere healthcare centre": ("Tavarekere, Bengaluru, Karnataka", MED),
    "tirupalaya":                   ("Thirupalya, Bengaluru, Karnataka", MED),

    # --- Koramangala / HSR / inner east ---
    "koramangala":                  ("Koramangala, Bengaluru, Karnataka", HIGH),
    "kormangala":                   ("Koramangala, Bengaluru, Karnataka", HIGH),
    "kormangla":                    ("Koramangala, Bengaluru, Karnataka", HIGH),
    "kpmg, koramangala":            ("Koramangala, Bengaluru, Karnataka", MED),
    "venkatapura":                  ("Venkatapura, Koramangala, Bengaluru, Karnataka", MED),
    "hsr":                          ("HSR Layout, Bengaluru, Karnataka", HIGH),
    "hsr layout":                   ("HSR Layout, Bengaluru, Karnataka", HIGH),
    "hsr layout, opp max showroom": ("HSR Layout, Bengaluru, Karnataka", MED),
    "domlur":                       ("Domlur, Bengaluru, Karnataka", HIGH),
    "aecs layout":                  ("AECS Layout, Bengaluru, Karnataka", MED),

    # --- Outer east ---
    "whitefield":                   ("Whitefield, Bengaluru, Karnataka", HIGH),
    "whitefiled":                   ("Whitefield, Bengaluru, Karnataka", HIGH),
    "marathahalli":                 ("Marathahalli, Bengaluru, Karnataka", HIGH),
    "marathahali":                  ("Marathahalli, Bengaluru, Karnataka", HIGH),
    "bellandur":                    ("Bellandur, Bengaluru, Karnataka", HIGH),
    "belendur":                     ("Bellandur, Bengaluru, Karnataka", HIGH),
    "balagere":                     ("Balagere, Bengaluru, Karnataka", HIGH),
    "sarjapur":                     ("Sarjapur, Bengaluru, Karnataka", HIGH),
    "sarjapur road":                ("Sarjapur Road, Bengaluru, Karnataka", HIGH),
    "vipro, sarjapur":              ("Wipro Sarjapur Road, Bengaluru, Karnataka", MED),
    "mahadevpura":                  ("Mahadevapura, Bengaluru, Karnataka", HIGH),
    "old madras road":              ("Old Madras Road, Bengaluru, Karnataka", HIGH),

    # --- North / west / central ---
    "malleshwaram":                 ("Malleshwaram, Bengaluru, Karnataka", HIGH),
    "mahalakshmi layout":           ("Mahalakshmi Layout, Bengaluru, Karnataka", HIGH),
    "rajajinagar":                  ("Rajajinagar, Bengaluru, Karnataka", HIGH),
    "vijaynagar":                   ("Vijayanagar, Bengaluru, Karnataka", HIGH),
    "vijyanagar":                   ("Vijayanagar, Bengaluru, Karnataka", HIGH),
    "nagarbhavi":                   ("Nagarbhavi, Bengaluru, Karnataka", HIGH),
    "yeshwanthpur":                 ("Yeshwanthpur, Bengaluru, Karnataka", HIGH),
    "yeshwanthpura":                ("Yeshwanthpur, Bengaluru, Karnataka", HIGH),
    "yehlanka":                     ("Yelahanka, Bengaluru, Karnataka", HIGH),
    "majestic":                     ("Majestic, Bengaluru, Karnataka", HIGH),
    "mejestic":                     ("Majestic, Bengaluru, Karnataka", HIGH),
    "mg road":                      ("MG Road, Bengaluru, Karnataka", HIGH),
    "vidhansoudha":                 ("Vidhana Soudha, Bengaluru, Karnataka", HIGH),
    "manyata tech park":            ("Manyata Tech Park, Bengaluru, Karnataka", MED),

    # --- Palya cluster: several distinct small localities ---
    "s g palya":                    ("SG Palya, Bengaluru, Karnataka", HIGH),
    "s g playa":                    ("SG Palya, Bengaluru, Karnataka", HIGH),
    "s g palya, near jayadeva":     ("SG Palya, Bengaluru, Karnataka", MED),
    "g b palya":                    ("GB Palya, Bengaluru, Karnataka", MED),
    "cg palya":                     ("CG Palya, Bengaluru, Karnataka", MED),
    "gurupalya":                    ("Gurupalya, Bengaluru, Karnataka", MED),

    # --- Outside the Bengaluru urban area (long commutes - sanity-check these) ---
    "bidadi":                       ("Bidadi, Ramanagara, Karnataka", HIGH),
    "tumkur":                       ("Tumakuru, Karnataka", HIGH),

    # --- NOT RESOLVABLE: fix these and re-run ---
    "infosys":                      (None, REVIEW),
    "besant technologies":          (None, REVIEW),
    "punjab sind bank":             (None, REVIEW),
    "electricity board":            (None, REVIEW),
    "ect":                          (None, REVIEW),
    "konamapagarha":                (None, REVIEW),
    "kottapalya":                   (None, REVIEW),
    "tilakpura":                    (None, REVIEW),
    "chalagata, jayanagar":         (None, REVIEW),
    "belekhalli":                   (None, REVIEW),
    "bilekhadi":                    (None, REVIEW),
    "billekhadi":                   (None, REVIEW),
}

WHY = {
    "infosys": "Multiple Infosys campuses in Bengaluru - which one?",
    "besant technologies": "Training institute with several Bengaluru branches.",
    "punjab sind bank": "A bank branch, not a locality. Many branches.",
    "electricity board": "A BESCOM office, not a locality. Which office?",
    "ect": "Probably 'Electronic City' but the abbreviation is not certain.",
    "konamapagarha": "No matching Bengaluru locality found.",
    "kottapalya": "No confident match to a Bengaluru locality.",
    "tilakpura": "Ambiguous. May be Tilak Nagar, may be somewhere else.",
    "chalagata, jayanagar": "Sub-locality of Jayanagar not identifiable from this spelling.",
    "belekhalli": "Likely Bilekahalli (Bannerghatta Road) - spelling too far off to assume.",
    "bilekhadi": "Likely Bilekahalli (Bannerghatta Road) - spelling too far off to assume.",
    "billekhadi": "Likely Bilekahalli (Bannerghatta Road) - spelling too far off to assume.",
}


def norm(raw):
    s = str(raw).replace("\xa0", " ").strip().lower()
    s = re.sub(r"\s*,\s*", ", ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip(" ,")


_NORM_PLACES = {norm(k): v for k, v in PLACES.items()}
assert len(_NORM_PLACES) == len(PLACES), "two PLACES keys collapse to the same key"


def canonical(raw):
    return _NORM_PLACES.get(norm(raw), (None, REVIEW))


# ============================== API ==========================================

def get_key():
    k = (API_KEY or os.environ.get("TOMTOM_API_KEY") or "").strip()
    if not k:
        sys.exit("\nNo TomTom API key.\n"
                 "  Paste it into API_KEY near the top of this file, or run:\n"
                 "      export TOMTOM_API_KEY=your_key_here\n"
                 "  Free key, no credit card: https://developer.tomtom.com/\n")
    return k


def load_cache(p):
    if p.exists():
        try:
            return json.loads(p.read_text())
        except json.JSONDecodeError:
            print(f"  (cache {p.name} was corrupt, starting fresh)")
    return {}


def geocode(query, cache, key):
    if query in cache:
        return tuple(cache[query])
    r = requests.get(GEOCODE_URL.format(q=requests.utils.quote(query)),
                     params={"key": key, "limit": 1, "countrySet": "IN"},
                     headers={"User-Agent": UA}, timeout=30)
    if r.status_code in (401, 403):
        sys.exit(f"\nTomTom rejected the key ({r.status_code}). Check API_KEY, "
                 f"or your monthly quota.\n")
    r.raise_for_status()
    res = r.json().get("results") or []
    if not res:
        raise ValueError("no geocoding result")
    pos = res[0]["position"]
    cache[query] = [pos["lat"], pos["lon"]]
    return pos["lat"], pos["lon"]


def route(o, d, mode, key, depart, maxspeed, cache):
    ck = f"{o[0]:.5f},{o[1]:.5f}|{d[0]:.5f},{d[1]:.5f}|{mode}|{depart}|{maxspeed}"
    if ck in cache:
        return cache[ck], True
    params = {"key": key, "travelMode": mode, "routeType": "fastest", "traffic": "true"}
    if depart:
        params["departAt"] = depart
    if maxspeed:
        params["vehicleMaxSpeed"] = int(maxspeed)
    r = requests.get(ROUTE_URL.format(locs=f"{o[0]},{o[1]}:{d[0]},{d[1]}"),
                     params=params, headers={"User-Agent": UA}, timeout=30)
    if r.status_code in (401, 403):
        sys.exit(f"\nTomTom rejected the key ({r.status_code}). Check API_KEY, "
                 f"or your monthly quota.\n")
    if r.status_code >= 400:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:160]}")
    routes = r.json().get("routes") or []
    if not routes:
        raise RuntimeError("no route returned")
    s = routes[0]["summary"]
    v = {"t": s["travelTimeInSeconds"], "d": s["lengthInMeters"],
         "delay": s.get("trafficDelayInSeconds", 0)}
    cache[ck] = v
    return v, False


# ============================== WORKBOOK ======================================

NAVY, HDRF = "1F3864", Font(name="Arial", bold=True, color="FFFFFF", size=10)
BODY = Font(name="Arial", size=10)
NOTEF = Font(name="Arial", size=9, italic=True, color="595959")
AMBER = PatternFill("solid", fgColor="FFF2CC")
RED = PatternFill("solid", fgColor="FCE4E4")
YELL = PatternFill("solid", fgColor="FFFF00")
THIN = Border(*[Side(style="thin", color="D9D9D9")] * 4)

MODE_NOTE = [
    "2-Wheeler Time = TomTom `motorcycle` mode, traffic-aware.",
    f"Auto/Cab Time = TomTom `motorcycle` mode capped at {RICKSHAW_MAX_SPEED_KMPH} km/h. "
    "No routing API has an auto-rickshaw mode; this is a proxy and the cap is an "
    "ASSUMPTION, not a finding. Calibrate against real observed trips and state it in "
    "your methodology. Car time is shown separately so you can see how much the mode "
    "choice moves the number.",
    "Bus Time = in-vehicle road time for a bus-sized vehicle. NOT a BMTC journey time. "
    "It EXCLUDES waiting for the bus, stop dwell time and transfers, which are often the "
    "majority of a real bus trip. A true bus time needs BMTC route and headway (GTFS) data. "
    "Do not present this column as a bus journey time.",
    "Origins and destinations are locality CENTROIDS, not respondent addresses - that is "
    f"all the source file records. Trips under {SHORT_TRIP_KM} km are flagged unreliable "
    "because the centroid error is then a large share of the trip.",
    "Rows marked NEEDS REVIEW were left blank on purpose rather than guessed. See the "
    "'Needs review' sheet.",
    "Routing, traffic and geocoding data (c) TomTom. Verify before publication.",
]


def write_workbook(path, rows, depart, geo_fail, route_fail):
    wb = Workbook()
    ws = wb.active
    ws.title = "Travel Times"
    hdr = ["PID", "Home area", "work area",
           "2-Wheeler Time (approx)", "Bus Time (approx)", "Auto/Cab Time (approx)",
           "Distance (km)", "Car (min)", "Traffic delay (min)",
           "Home area used", "Work area used", "Status"]
    ws.append(hdr)
    for c in ws[1]:
        c.fill, c.font = PatternFill("solid", fgColor=NAVY), HDRF
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 34

    for x in rows:
        ws.append([x["pid"], x["home"], x["work"],
                   x.get("m2w"), x.get("mbus"), x.get("mauto"),
                   x.get("km"), x.get("mcar"), x.get("delay"),
                   x["home_c"] or "", x["work_c"] or "", x["status"]])
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.font, c.border = BODY, THIN
        for i in (3, 4, 5, 6, 7, 8):
            row[i].number_format = "0.0"
        st = str(row[11].value)
        if st == "NEEDS REVIEW":
            row[11].fill = RED
        elif st != "ok":
            row[11].fill = AMBER
    for i, w in enumerate([8, 28, 28, 15, 13, 16, 12, 10, 14, 34, 34, 30], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "D2"
    ws.auto_filter.ref = f"A1:L{ws.max_row}"

    r = ws.max_row + 2
    ws.cell(r, 1, "What these columns mean - read before using any figure").font = \
        Font(name="Arial", size=11, bold=True, color=NAVY)
    r += 1
    ws.cell(r, 1, f"Departure time modelled: {depart or 'live traffic at run time'}").font = NOTEF
    r += 1
    for line in MODE_NOTE:
        c = ws.cell(r, 1, "•  " + line)
        c.font = NOTEF
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=12)
        ws.row_dimensions[r].height = 14 * (1 + len(line) // 120)
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
                      "travel_times.py (replace None with the place name, change REVIEW to "
                      "MED) and run the script again.")
    c.font, c.alignment = NOTEF, Alignment(wrap_text=True)
    rv.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)

    pm = wb.create_sheet("Place map")
    pm.append(["Value as recorded", "Canonical place used", "Confidence", "Times in file"])
    for c in pm[1]:
        c.fill, c.font = PatternFill("solid", fgColor=NAVY), HDRF
    seen = {}
    for x in rows:
        for raw in (x["home"], x["work"]):
            seen[raw] = seen.get(raw, 0) + 1
    for raw in sorted(seen, key=str.lower):
        cn, cf = canonical(raw)
        pm.append([raw, cn or "-- unresolved --", cf, seen[raw]])
    for row in pm.iter_rows(min_row=2):
        for c in row:
            c.font, c.border = BODY, THIN
        if row[2].value == REVIEW:
            for c in row:
                c.fill = RED
        elif row[2].value == MED:
            for c in row:
                c.fill = AMBER
    for i, w in enumerate([32, 52, 12, 14], 1):
        pm.column_dimensions[get_column_letter(i)].width = w
    pm.freeze_panes = "A2"

    if geo_fail or route_fail:
        f = wb.create_sheet("Failures")
        f.append(["Type", "Item", "Error"])
        for c in f[1]:
            c.fill, c.font = PatternFill("solid", fgColor=NAVY), HDRF
        for k, e in geo_fail:
            f.append(["geocode", k, e])
        for k, e in route_fail:
            f.append(["route", k, e])
        for i, w in enumerate([12, 62, 46], 1):
            f.column_dimensions[get_column_letter(i)].width = w

    wb.save(path)


# ============================== MAIN =========================================

def main():
    ap = argparse.ArgumentParser(
        description="Fill travel times in the non-shifters OD file using TomTom.")
    ap.add_argument("--input", default=None, help=f"default: {INPUT_FILE} beside this script")
    ap.add_argument("--output", default=None, help=f"default: {OUTPUT_FILE} beside this script")
    ap.add_argument("--depart", default=None,
                    help="ISO 8601, e.g. 2026-09-21T09:00:00+05:30. Omit for live traffic now.")
    ap.add_argument("--dry-run", action="store_true", help="No API calls; just report.")
    ap.add_argument("--sleep", type=float, default=0.2)
    a = ap.parse_args()

    inp = Path(a.input) if a.input else HERE / INPUT_FILE
    outp = Path(a.output) if a.output else HERE / OUTPUT_FILE
    if not inp.is_absolute():
        inp = (Path.cwd() / inp).resolve()
    if not outp.is_absolute():
        outp = (Path.cwd() / outp).resolve()

    print("=" * 66)
    print(f" INPUT   {inp}")
    print(f" OUTPUT  {outp}")
    print("=" * 66)
    if not inp.exists():
        sys.exit(f"\nInput file not found.\n  Looked for: {inp}\n"
                 f"  Put '{INPUT_FILE}' in the same folder as this script, "
                 f"or pass --input <path>.\n")
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
    modes = (("car", None), ("motorcycle", None), ("motorcycle", RICKSHAW_MAX_SPEED_KMPH),
             ("bus", None))

    print(f"\n respondents        {len(rows)}")
    print(f" ready to route     {len(todo)}")
    print(f" need your decision {len(rows) - len(todo)}")
    print(f" unique places      {len(places)}   -> geocoding calls")
    print(f" unique OD pairs    {len(pairs)}   -> {len(pairs)*len(modes)} routing calls")

    if a.dry_run:
        print("\n --dry-run: no API calls made, no output written.")
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
        return

    key = get_key()
    gc_path, rc_path = outp.parent / "geocode_cache.json", outp.parent / "route_cache.json"
    gcache, rcache = load_cache(gc_path), load_cache(rc_path)

    print("\n geocoding...")
    coords, geo_fail = {}, []
    for i, p in enumerate(places, 1):
        try:
            coords[p] = geocode(p, gcache, key)
            print(f"   [{i}/{len(places)}] {p}")
        except Exception as e:
            geo_fail.append((p, str(e)))
            print(f"   [{i}/{len(places)}] FAILED  {p}  ({e})")
        time.sleep(a.sleep)
    gc_path.write_text(json.dumps(gcache, indent=1, sort_keys=True))

    print("\n routing...")
    res, route_fail = {}, []
    for i, (o, d) in enumerate(pairs, 1):
        if o not in coords or d not in coords:
            route_fail.append((f"{o} -> {d}", "an endpoint failed geocoding"))
            continue
        try:
            got = {}
            for mode, ms in modes:
                v, cached = route(coords[o], coords[d], mode, key, a.depart, ms, rcache)
                got[(mode, ms)] = v
                if not cached:
                    time.sleep(a.sleep)
            res[(o, d)] = got
            print(f"   [{i}/{len(pairs)}] {o.split(',')[0]} -> {d.split(',')[0]}")
        except Exception as e:
            route_fail.append((f"{o} -> {d}", str(e)))
            print(f"   [{i}/{len(pairs)}] FAILED  ({e})")
    rc_path.write_text(json.dumps(rcache, indent=1, sort_keys=True))

    filled = 0
    for x in rows:
        if x["blocked"]:
            continue
        got = res.get((x["home_c"], x["work_c"]))
        if not got:
            x["status"] = "routing failed - see Failures sheet"
            continue
        km = got[("car", None)]["d"] / 1000
        x["km"] = round(km, 2)
        x["mcar"] = round(got[("car", None)]["t"] / 60, 1)
        x["m2w"] = round(got[("motorcycle", None)]["t"] / 60, 1)
        x["mauto"] = round(got[("motorcycle", RICKSHAW_MAX_SPEED_KMPH)]["t"] / 60, 1)
        x["mbus"] = round(got[("bus", None)]["t"] / 60, 1)
        x["delay"] = round(got[("car", None)]["delay"] / 60, 1)
        if x["home_c"] == x["work_c"]:
            x["status"] = "same locality - centroid method cannot resolve this trip"
        elif km < SHORT_TRIP_KM:
            x["status"] = f"short trip ({km:.1f} km) - centroid unreliable"
        filled += 1

    write_workbook(outp, rows, a.depart, geo_fail, route_fail)

    print("\n" + "=" * 66)
    print(f" WROTE  {outp}")
    print("=" * 66)
    print(f"   {filled} of {len(rows)} rows filled")
    print(f"   {sum(x['blocked'] for x in rows)} need your decision  -> 'Needs review' sheet")
    flagged = sum(1 for x in rows if x["status"] not in ("ok", "NEEDS REVIEW"))
    if flagged:
        print(f"   {flagged} filled but flagged (short or same-locality trip)")
    if geo_fail or route_fail:
        print(f"   {len(geo_fail)} geocoding + {len(route_fail)} routing failures "
              f"-> 'Failures' sheet")
    print("\n Auto/Cab is a capped-motorcycle proxy, not a measured rickshaw time.")
    print(" Bus is in-vehicle road time only - it excludes waiting and transfers.\n")


if __name__ == "__main__":
    main()
