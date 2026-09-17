#!/usr/bin/env python3
# =============================================================================
#  RESOLVE PLACE NAMES  -  companion to travel_times.py
#  Turns the "Needs review" rows into an evidence table you can decide from.
# =============================================================================
#
#  WHY THIS EXISTS
#  travel_times.py deliberately refuses to guess an area name it cannot match,
#  and leaves those rows blank. To clear them you have to decide what each
#  unresolved string actually means. This script does the legwork: for every
#  unresolved string it asks TomTom's own search API what real places match,
#  and shows you the candidates with a score and a plausibility check, so the
#  decision rests on retrieved evidence rather than on anybody's hunch.
#
#  IT DOES NOT DECIDE ANYTHING. It proposes; you choose. Nothing is written
#  back into travel_times.py.
#
#  HOW TO RUN
#    1. Put this file in the SAME FOLDER as travel_times.py and the xlsx.
#    2. Same TomTom key as the main script:
#         export TOMTOM_API_KEY=your_key_here
#    3. python3 resolve_places.py
#       See the queries without spending any quota:
#         python3 resolve_places.py --dry-run
#
#  OUTPUT  Place_Candidates.xlsx
#            Sheet "Candidates"  - every unresolved string, every candidate
#                                  match, its score, where it is, how far it
#                                  sits from the other end of that person's
#                                  commute, and a ready-to-paste PLACES line
#            Sheet "Still open"  - strings where no candidate is defensible
#          It also prints the paste-ready lines to the terminal.
#
#  READING THE OUTPUT
#  Score          TomTom's own match confidence. Higher is better, but a high
#                 score on the WRONG place is common with garbled spellings -
#                 read the matched address, do not trust the score alone.
#  Type           Geography = a locality/area (usually what you want).
#                 POI = a single named building or business.
#                 Street / Point Address = narrower than a locality.
#  Dist to other  Straight-line km from this candidate to the other end of the
#                 commute recorded for that respondent. A candidate 80 km from
#                 a daily commute's other end is almost certainly wrong. This
#                 is the single most useful column on the sheet.
#
#  The HINTS block below holds extra spellings worth testing. Those are
#  UNVERIFIED readings based on spelling similarity alone - they are guesses
#  about what to ASK, not answers. Only TomTom's reply is evidence, and even
#  that needs your eye before it enters a CEEW output.
#
#  Geocoding and search data (c) TomTom.
# =============================================================================

# ----------------------------- SETTINGS --------------------------------------

API_KEY = ""          # <<< same key as travel_times.py, or use TOMTOM_API_KEY

INPUT_FILE = "Non_Shifters_120_Improved_Approx_Travel_Times.xlsx"
OUTPUT_FILE = "Place_Candidates.xlsx"

BENGALURU = (12.9716, 77.5946)   # search bias centre
BIAS_RADIUS_M = 70_000           # keep matches near Bengaluru
RESULTS_PER_QUERY = 5
FAR_KM = 60.0                    # flag a candidate this far from the other end

# -----------------------------------------------------------------------------

import argparse
import difflib
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
    from travel_times import BODY, HDRF, MED, NAVY, NOTEF, REVIEW, THIN, WHY, \
        AMBER, RED, YELL, canonical, norm
except ImportError:
    sys.exit("Could not import travel_times.py.\n"
             "  Put this script in the SAME FOLDER as travel_times.py.")

SEARCH_URL = "https://api.tomtom.com/search/2/search/{q}.json"
UA = "ceew-bengaluru-traveltime/1.0"

# =============================================================================
#  HINTS  -  extra spellings to TEST, not answers
#  Keyed by the normalised raw string. Each entry is a list of alternative
#  queries to put to TomTom alongside the raw string itself. A hint earns its
#  place only if it is a plausible mis-spelling of a real Bengaluru place; the
#  search result decides whether it is right, and you decide whether to accept
#  it. Add your own readings here - you know the survey areas.
#
#  A hint must be a SPELLING alternative, never a fall-back to the parent area.
#  Hinting 'Jayanagar' for 'chalagata, jayanagar' would match strongly and look
#  resolved, while silently moving the trip end to the Jayanagar centroid and
#  discarding the sub-locality. Coarsening the geography is a methodological
#  choice to make deliberately and record, not something a lookup should slip
#  past you - so those hints are left out on purpose.
# =============================================================================

HINTS = {
    "bilekhadi":            ["Bilekahalli, Bengaluru, Karnataka",
                             "Bilekahalli, Bannerghatta Road, Bengaluru"],
    "billekhadi":           ["Bilekahalli, Bengaluru, Karnataka",
                             "Bilekahalli, Bannerghatta Road, Bengaluru"],
    "belekhalli":           ["Bilekahalli, Bengaluru, Karnataka",
                             "Bilekahalli, Bannerghatta Road, Bengaluru"],
    "konamapagarha":        ["Konappana Agrahara, Electronic City, Bengaluru",
                             "Konanakunte, Bengaluru, Karnataka"],
    "ect":                  ["Electronic City, Bengaluru, Karnataka"],
    "tilakpura":            ["Tilak Nagar, Bengaluru, Karnataka",
                             "Thilaknagar, Bengaluru, Karnataka"],
    "kottapalya":           ["Kottigepalya, Bengaluru, Karnataka",
                             "Kodipalya, Bengaluru, Karnataka",
                             "Kottanur, Bengaluru, Karnataka"],
    "chalagata, jayanagar": ["Challaghatta, Bengaluru, Karnataka",
                             "Chalavadipalya, Bengaluru, Karnataka"],
    "infosys":              ["Infosys Electronic City, Bengaluru, Karnataka",
                             "Infosys Limited, Bengaluru, Karnataka"],
    "besant technologies":  ["Besant Technologies BTM Layout, Bengaluru",
                             "Besant Technologies Marathahalli, Bengaluru",
                             "Besant Technologies Jayanagar, Bengaluru",
                             "Besant Technologies Rajajinagar, Bengaluru"],
    "punjab sind bank":     ["Punjab and Sind Bank, Bengaluru, Karnataka",
                             "Punjab and Sind Bank, Tumakuru, Karnataka"],
    "electricity board":    ["BESCOM, Electronic City, Bengaluru, Karnataka",
                             "BESCOM Corporate Office, Bengaluru, Karnataka"],
}

# Strings that no amount of searching can settle, because the survey recorded
# an employer or an institution with many Bengaluru sites rather than a place.
# These need the respondent's own answer, not a better query.
NEEDS_RESPONDENT = {
    "infosys": "Infosys runs several Bengaluru campuses. Search returns all of "
               "them and cannot say which one this respondent travels to.",
    "besant technologies": "A training institute with multiple Bengaluru "
                           "branches. Search cannot say which branch.",
    "punjab sind bank": "A bank branch, not a locality, and there are many. "
                        "Search cannot say which branch.",
    "electricity board": "A BESCOM office, not a locality. Search cannot say "
                         "which office.",
}


SAME_RATIO = 0.92   # above this, the match just repeats the recorded spelling


def repeats_input(raw, addr):
    """True when the match reads the same as the string we searched for.

    Two very different things produce this, and string comparison cannot tell
    them apart:

      1. Fuzzy search handed a garbled string back. Search always returns
         something, and for nonsense that something is often a Geography
         result named after the input, scoring well and looking resolved.
      2. The recorded spelling was correct all along and simply absent from
         the PLACES dictionary.

    Either way the row is not settled by the search, so it is flagged for a
    look rather than accepted. A genuine correction reads differently from
    the input ('bilekhadi' -> 'Bilekahalli', ratio ~0.7) and is unaffected.
    """
    if not addr:
        return False
    r, a = norm(raw), norm(addr)
    if a.startswith(r):           # catches multi-component inputs
        return True
    head = norm(addr.split(",")[0])
    return max(difflib.SequenceMatcher(None, r, head).ratio(),
               difflib.SequenceMatcher(None, norm(r.split(",")[0]), head).ratio()
               ) >= SAME_RATIO


def haversine_km(a, b):
    r = 6371.0
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp, dl = p2 - p1, math.radians(b[1] - a[1])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def get_key():
    k = (API_KEY or os.environ.get("TOMTOM_API_KEY") or "").strip()
    if not k:
        sys.exit("\nNo TomTom API key.\n"
                 "  Paste it into API_KEY near the top of this file, or run:\n"
                 "      export TOMTOM_API_KEY=your_key_here\n")
    return k


def load_cache(p):
    if p.exists():
        try:
            return json.loads(p.read_text())
        except json.JSONDecodeError:
            print(f"  (cache {p.name} was corrupt, starting fresh)")
    return {}


def search(query, key, cache, limit):
    ck = f"{query}|{limit}"
    if ck in cache:
        return cache[ck], True
    r = requests.get(SEARCH_URL.format(q=requests.utils.quote(query)),
                     params={"key": key, "limit": limit, "countrySet": "IN",
                             "lat": BENGALURU[0], "lon": BENGALURU[1],
                             "radius": BIAS_RADIUS_M},
                     headers={"User-Agent": UA}, timeout=30)
    if r.status_code in (401, 403):
        sys.exit(f"\nTomTom rejected the key ({r.status_code}). Check the key, "
                 f"or your monthly quota.\n")
    r.raise_for_status()
    out = []
    for res in r.json().get("results") or []:
        addr = res.get("address", {})
        out.append({
            "name": (res.get("poi") or {}).get("name") or
                    addr.get("freeformAddress") or "(unnamed)",
            "addr": addr.get("freeformAddress", ""),
            "type": res.get("type", ""),
            "etype": res.get("entityType", ""),
            "score": round(res.get("score", 0), 2),
            "lat": res["position"]["lat"],
            "lon": res["position"]["lon"],
        })
    cache[ck] = out
    return out, False


def geocode_one(query, key, cache):
    """Locate a canonical place so we can measure plausibility against it."""
    hits, cached = search(query, key, cache, 1)
    if not hits:
        return None, cached
    return (hits[0]["lat"], hits[0]["lon"]), cached


# ============================== WORKBOOK ======================================

HEAD = ["Value as recorded", "PIDs", "Field", "Other end of commute",
        "Query put to TomTom", "Query from", "Candidate match", "Full address",
        "Type", "Score", "Dist to other end (km)", "Verdict",
        "Ready-to-paste PLACES line"]
WIDTHS = [24, 14, 8, 26, 34, 11, 30, 46, 14, 8, 14, 30, 62]
NCOL = len(HEAD)


def write_workbook(path, table, open_rows, made, cached):
    wb = Workbook()
    ws = wb.active
    ws.title = "Candidates"
    ws.append(HEAD)
    for c in ws[1]:
        c.fill, c.font = PatternFill("solid", fgColor=NAVY), HDRF
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 34

    for t in table:
        ws.append([t["raw"], t["pids"], t["field"], t["other"], t["query"],
                   t["qfrom"], t["name"], t["addr"], t["type"], t["score"],
                   t["dist"], t["verdict"], t["paste"]])
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.font, c.border = BODY, THIN
            c.alignment = Alignment(vertical="top", wrap_text=True)
        row[9].number_format = "0.00"
        row[10].number_format = "0.0"
        v = str(row[11].value)
        if v.startswith("strong"):
            for c in row:
                c.fill = PatternFill("solid", fgColor="E2EFDA")
        elif v.startswith("implausible") or v.startswith("needs") or v.startswith("confirm"):
            for c in row:
                c.fill = RED
        elif v.startswith("weak") or v.startswith("unverifiable"):
            for c in row:
                c.fill = AMBER
    for i, w in enumerate(WIDTHS, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = f"A1:{get_column_letter(NCOL)}{ws.max_row}"

    r = ws.max_row + 2
    ws.cell(r, 1, "How to read this sheet").font = \
        Font(name="Arial", size=11, bold=True, color=NAVY)
    r += 1
    notes = [
        f"{made} search calls made, {cached} served from cache. "
        f"Every figure here is TomTom's answer to the query in column E, not a finding.",
        "Score is TomTom's match confidence. A high score on the WRONG place is common "
        "with garbled spellings - read the matched address, never the score alone.",
        "Type: Geography = a locality or area, usually what you want. POI = one named "
        "building or business. Street / Point Address = narrower than a locality.",
        "'Query from' says where the query came from. 'raw' = the spelling as recorded. "
        "'hint' = an alternative spelling tested on the hunch that it is what was meant. "
        "A hint is a guess about what to ASK; only TomTom's reply is evidence.",
        "'Dist to other end' is straight-line km to the other end of that respondent's "
        f"recorded commute. Anything over {FAR_KM:.0f} km is flagged implausible - a daily "
        "commute that long is possible but rare, so check it against the questionnaire.",
        "Verdict is arithmetic on the columns to its left, not a judgement. 'strong' needs "
        "all four: a Geography match, a score of 4 or better, a distance that could be "
        "commuted, and a name that actually differs from the recorded spelling.",
        "'confirm' means the match reads the same as the string searched for. Either fuzzy "
        "search handed a garbled string back (search always returns something, and that "
        "something is not a resolution however high it scores), or the spelling was right "
        "all along and merely missing from PLACES. Open it on a map to see which - this "
        "flag cannot tell them apart, so it accepts neither.",
        "'unverifiable' means the other end of that commute is unresolved too, so no "
        "distance check was possible. The match may be right - nothing here corroborates it.",
        "Accepting a candidate: paste column L into the PLACES dictionary in "
        "travel_times.py, change REVIEW to MED for that entry, and re-run the main script.",
        "Open every match you accept in a map before it enters a CEEW output. "
        "Geocoding and search data (c) TomTom.",
    ]
    for line in notes:
        c = ws.cell(r, 1, "•  " + line)
        c.font = NOTEF
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=NCOL)
        ws.row_dimensions[r].height = 14 * (1 + len(line) // 110)
        r += 1

    so = wb.create_sheet("Still open")
    so.append(["Value as recorded", "PIDs", "Field", "Other end of commute",
               "Why searching cannot settle it", "What would settle it",
               "Correct place (fill in)"])
    for c in so[1]:
        c.fill, c.font = PatternFill("solid", fgColor=NAVY), HDRF
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for o in open_rows:
        so.append([o["raw"], o["pids"], o["field"], o["other"],
                   o["why"], o["fix"], ""])
    for row in so.iter_rows(min_row=2):
        for c in row:
            c.font, c.border = BODY, THIN
            c.alignment = Alignment(wrap_text=True, vertical="top")
        row[6].fill = YELL
    for i, w in enumerate([24, 14, 8, 26, 54, 54, 30], 1):
        so.column_dimensions[get_column_letter(i)].width = w
    so.freeze_panes = "A2"
    r = so.max_row + 2
    c = so.cell(r, 1, "These record an employer or institution with many Bengaluru sites, "
                      "not a locality. No better query fixes that - it needs the "
                      "respondent's own answer, or the site address from the field team. "
                      "Leaving the row blank is a defensible result; guessing is not.")
    c.font, c.alignment = NOTEF, Alignment(wrap_text=True, vertical="top")
    so.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)
    so.row_dimensions[r].height = 42

    wb.save(path)


# ============================== MAIN =========================================

def main():
    ap = argparse.ArgumentParser(
        description="Propose canonical place names for the unresolved rows.")
    ap.add_argument("--input", default=None, help=f"default: {INPUT_FILE}")
    ap.add_argument("--output", default=None, help=f"default: {OUTPUT_FILE}")
    ap.add_argument("--dry-run", action="store_true", help="No API calls; list the queries.")
    ap.add_argument("--limit", type=int, default=RESULTS_PER_QUERY)
    ap.add_argument("--sleep", type=float, default=0.2)
    a = ap.parse_args()

    here = Path(__file__).resolve().parent
    inp = Path(a.input) if a.input else here / INPUT_FILE
    outp = Path(a.output) if a.output else here / OUTPUT_FILE
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

    # Gather each unresolved string, who it belongs to, and the other endpoint.
    unresolved = {}
    for x in rows:
        for field, raw, other in (("Home", x["home"], x["work"]),
                                  ("Work", x["work"], x["home"])):
            if canonical(raw)[1] != REVIEW:
                continue
            e = unresolved.setdefault(norm(raw), {"raw": raw, "field": field,
                                                  "pids": [], "others": []})
            e["pids"].append(x["pid"])
            oc = canonical(other)[0]
            if oc and oc not in e["others"]:
                e["others"].append(oc)

    if not unresolved:
        print("\n Nothing unresolved - every area name already maps to a place.\n")
        return

    queries = {}
    for k, e in unresolved.items():
        qs = [f"{e['raw']}, Bengaluru, Karnataka"] + HINTS.get(k, [])
        seen, ded = set(), []
        for q in qs:
            if q.lower() not in seen:
                seen.add(q.lower())
                ded.append(q)
        queries[k] = ded

    others = sorted({o for e in unresolved.values() for o in e["others"]})
    n_q = sum(len(v) for v in queries.values())
    print(f"\n unresolved strings  {len(unresolved)}")
    print(f" queries to run      {n_q}")
    print(f" endpoints to locate {len(others)}")
    print(f" total search calls  {n_q + len(others)}")

    if a.dry_run:
        print("\n --dry-run: no API calls made, no output written.\n")
        for k in sorted(unresolved):
            e = unresolved[k]
            oth = ", ".join(e["others"]) or "(other end also unresolved)"
            print(f"   {e['raw']!r}  [{e['field']}, {', '.join(e['pids'])}]")
            print(f"      other end: {oth}")
            for j, q in enumerate(queries[k]):
                print(f"      {'raw' if j == 0 else 'hint':<5} -> {q}")
            if k in NEEDS_RESPONDENT:
                print(f"      NOTE: {NEEDS_RESPONDENT[k]}")
            print()
        return

    key = get_key()
    cpath = outp.parent / "search_cache.json"
    cache = load_cache(cpath)
    made = cached_n = 0

    print("\n locating the other end of each commute...")
    opos = {}
    for i, o in enumerate(others, 1):
        try:
            pos, was_cached = geocode_one(o, key, cache)
            if pos:
                opos[o] = pos
            made, cached_n = made + (not was_cached), cached_n + was_cached
            if not was_cached:
                time.sleep(a.sleep)
            print(f"   [{i}/{len(others)}] {o}")
        except Exception as e:
            print(f"   [{i}/{len(others)}] FAILED  {o}  ({e})")

    print("\n searching...")
    table, open_rows = [], []
    for k in sorted(unresolved):
        e = unresolved[k]
        pids = ", ".join(e["pids"])
        oth = ", ".join(e["others"]) or "(other end also unresolved)"

        if k in NEEDS_RESPONDENT:
            open_rows.append({
                "raw": e["raw"], "pids": pids, "field": e["field"], "other": oth,
                "why": NEEDS_RESPONDENT[k],
                "fix": "The respondent's site or branch address, from the "
                       "questionnaire or a follow-up with the field team.",
            })

        for j, q in enumerate(queries[k]):
            qfrom = "raw" if j == 0 else "hint"
            base = {"raw": e["raw"], "pids": pids, "field": e["field"],
                    "other": oth, "query": q, "qfrom": qfrom}
            try:
                hits, was_cached = search(q, key, cache, a.limit)
                made, cached_n = made + (not was_cached), cached_n + was_cached
                if not was_cached:
                    time.sleep(a.sleep)
            except Exception as ex:
                table.append({**base, "name": "SEARCH FAILED", "addr": str(ex),
                              "type": "", "score": None, "dist": None,
                              "verdict": "search failed", "paste": ""})
                print(f"   FAILED  {q}  ({ex})")
                continue

            if not hits:
                table.append({**base, "name": "no match", "addr": "", "type": "",
                              "score": None, "dist": None, "verdict": "no match",
                              "paste": ""})
                continue

            for h in hits:
                d = None
                for o in e["others"]:
                    if o in opos:
                        dd = haversine_km((h["lat"], h["lon"]), opos[o])
                        d = dd if d is None else min(d, dd)

                geo = h["type"].lower() == "geography"
                label = h["addr"] or h["name"]
                if k in NEEDS_RESPONDENT:
                    verdict = "needs respondent answer"
                elif repeats_input(e["raw"], label):
                    verdict = "confirm - match repeats the recorded spelling"
                elif d is not None and d > FAR_KM:
                    verdict = f"implausible - {d:.0f} km from other end"
                elif d is None:
                    verdict = "unverifiable - no distance check possible"
                elif geo and h["score"] >= 4:
                    verdict = "strong - a locality, plausible distance"
                elif geo:
                    verdict = "weak - a locality but low score"
                else:
                    verdict = f"weak - {h['type']}, not a locality"

                paste = f'    "{k}": ("{label}", MED),' \
                    if verdict.startswith("strong") else ""

                table.append({**base, "name": h["name"], "addr": h["addr"],
                              "type": h["type"] or h["etype"], "score": h["score"],
                              "dist": d, "verdict": verdict, "paste": paste})
        print(f"   {e['raw']!r} -> {len(queries[k])} queries")

    cpath.write_text(json.dumps(cache, indent=1, sort_keys=True))
    write_workbook(outp, table, open_rows, made, cached_n)

    print("\n" + "=" * 66)
    print(f" WROTE  {outp}")
    print("=" * 66)
    strong = [t for t in table if t["verdict"].startswith("strong")]
    print(f"   {len(table)} candidate rows from {made} new + {cached_n} cached calls")
    print(f"   {len(strong)} scored as 'strong'  -> still check each one on a map")
    print(f"   {len(open_rows)} strings need the respondent's answer -> 'Still open' sheet")

    if strong:
        print("\n Paste-ready lines for the STRONG candidates. Read the matched")
        print(" address first - a high score on the wrong place is common.\n")
        best = {}
        for t in strong:
            kk = norm(t["raw"])
            if kk not in best or (t["score"] or 0) > (best[kk]["score"] or 0):
                best[kk] = t
        for kk in sorted(best):
            t = best[kk]
            print(f"   # {t['raw']!r} [{t['pids']}], other end {t['other']},")
            print(f"   #   matched {t['addr']!r} score {t['score']}"
                  + (f", {t['dist']:.1f} km from other end" if t["dist"] is not None else ""))
            print(t["paste"])
            print()

    print(" Nothing here is a finding. Verify every match before it enters an output.\n")


if __name__ == "__main__":
    main()
