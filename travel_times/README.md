# Bengaluru non-shifters — travel time estimation

Scripts for filling the three travel-time columns in the non-shifters OD file
(`Non_Shifters_120_Improved_Approx_Travel_Times.xlsx`, 120 respondents).

| File | What it does |
|---|---|
| `travel_times.py` | Fills the 2-Wheeler / Bus / Auto-Cab columns from TomTom routing, traffic-aware. Needs a free TomTom key. Writes `Travel_Times_FILLED.xlsx`. |
| `travel_times_free.py` | Same output, **no API key**: Nominatim geocoding + Valhalla routing on OSM data. **No traffic model** — free-flow times only. Writes `Travel_Times_FILLED_free.xlsx`. |
| `resolve_places.py` | Companion. Proposes canonical names for the area strings that could not be matched, as an evidence table. Needs a TomTom key. Writes `Place_Candidates.xlsx`. |
| `_mocktest.py`, `_mocktest_free.py` | Offline test scaffolds. Fake API responses, so logic changes can be checked without network or quota. |

`travel_times_free.py` and `resolve_places.py` both import the `PLACES`
dictionary from `travel_times.py` rather than keeping a copy, so fixing a place
name once fixes it everywhere. All three must stay in the same folder.

## Which version to use

`travel_times.py` (TomTom) is traffic-aware. `travel_times_free.py` is not, and
that difference matters more than the cost:

| | TomTom | Nominatim + Valhalla |
|---|---|---|
| API key | free, email signup | none |
| Traffic | yes, and `--depart` models a chosen time | **none** — free-flow only |
| Traffic delay column | yes | not produced, because there is nothing to put in it |
| Modes | car, motorcycle, capped motorcycle, bus | auto, motorcycle, capped motorcycle, bus |
| Geocoder strength on Bengaluru localities | stronger | weaker, so every match is logged for audit |
| Run time for this file | ~2 min | ~8 min (self-rate-limited) |

Free-flow times understate real Bengaluru peak travel substantially, and
unevenly — a congested arterial is hit harder than a quiet side road, so the
gap is not a constant you can multiply away. If the analysis turns on why
people do not switch modes, congestion is close to the centre of the question.
Use the keyless version for pipeline testing, for trip geometry, or where
free-flow time is genuinely what is wanted; use the traffic-aware one for
anything published, and say which service produced the numbers.

All of them need `requests` and `openpyxl`. The TomTom scripts need a free key
(https://developer.tomtom.com/ — email signup, no credit card). The keyless
script needs a contact address instead, because Nominatim's usage policy
requires callers to identify themselves.

```bash
python3 -m pip install requests openpyxl
export TOMTOM_API_KEY=your_key_here      # travel_times.py, resolve_places.py
export OSM_CONTACT=you@ceew.in           # travel_times_free.py
```

## Run it, keyless

```bash
cd travel_times
python3 travel_times_free.py --dry-run   # no requests made
python3 travel_times_free.py             # ~8 min, then Travel_Times_FILLED_free.xlsx
```

Nominatim and Valhalla are volunteer-run and donation-funded. Their usage
policies are conditions of access: Nominatim allows a maximum of 1 request per
second and requires an identifying User-Agent. The script rate-limits itself
and caches everything, so re-runs cost no requests. Do not raise the rate.

- Nominatim policy: https://operations.osmfoundation.org/policies/nominatim/
- FOSSGIS OSM services: https://www.fossgis.de/arbeitsgruppen/osm-server/

Read the `Geocoding` sheet in the output. It records what Nominatim matched for
every place, whether it fell back to a shortened query, and how far the result
sits from the city centre. A wrong point there is a wrong travel time
everywhere it appears.

## Run it, with TomTom

```bash
cd travel_times
# preview, no API calls, no quota spent
python3 travel_times.py --dry-run --input Non_Shifters_120_Improved_Approx_Travel_Times.xlsx

# the real run
python3 travel_times.py --input Non_Shifters_120_Improved_Approx_Travel_Times.xlsx \
                        --output Travel_Times_FILLED.xlsx

# model a specific departure instead of traffic at run time
python3 travel_times.py --depart 2026-09-21T09:00:00+05:30 ...
```

`travel_times.py` also has `INPUT_FILE` / `OUTPUT_FILE` set to absolute
`~/Downloads` paths at the top, so with the xlsx in Downloads it runs with no
arguments at all.

Caches (`geocode_cache.json`, `route_cache.json`, `search_cache.json`) are
written beside the output so re-runs cost no quota. Safe to delete.

## Status of the 2026-09-17 run

`--dry-run` completed and the input file matched the expected layout exactly
(sheet `Travel Times`, 120 rows, columns A–F, D/E/F blank):

```
 respondents        120
 ready to route     108
 need your decision  12
 unique places       66   -> geocoding calls
 unique OD pairs     92   -> 368 routing calls
```

368 routing + 66 geocoding calls is roughly 1.8% of TomTom's 20,000/month free
tier.

**The live run has not been made.** It cannot run from a Claude Code remote
session: `api.tomtom.com:443` is denied by the egress policy (403 to CONNECT),
and general web egress is blocked too. Run it locally. Nothing in the repo is
filled with estimated or placeholder travel times.

### The 12 rows needing a decision

`travel_times.py` leaves an area name blank rather than guessing it. These are
the strings it would not resolve, with the other end of each commute:

| PID | Home | Work | Unresolved |
|---|---|---|---|
| P11 | `tilakpura` | mahadevpura | home |
| P32 | BTM stage 2 | `ECT` | work |
| P33 | `bilekhadi` | sarjapur | home |
| P38 | `billekhadi` | whitefield | home |
| P41 | Tumkur | `Punjab Sind Bank` | work |
| P55 | BTM 2nd stage | `Besant Technologies` | work |
| P98 | Singasandra | `Infosys` | work |
| P129 | `kottapalya` | marathahali | home |
| P171 | s g palya | `chalagata, jayanagar` | work |
| P207 | `konamapagarha` | `Electricity Board` | both |
| P208 | Silk Board | `Infosys` | work |
| P212 | `Belekhalli` | whitefield | home |

To clear them, run `resolve_places.py` (47 search calls) and work from
`Place_Candidates.xlsx`. It puts each unresolved string to TomTom's search API,
alongside alternative spellings worth testing, and reports every candidate with
its score, its type, and its straight-line distance from the other end of that
respondent's commute — that distance column is the most useful thing on the
sheet, because a candidate 80 km from a daily commute is almost certainly wrong.

Accepting a candidate means pasting the generated line into the `PLACES`
dictionary in `travel_times.py`, changing `REVIEW` to `MED`, and re-running.

Four of the twelve cannot be settled by searching at all — `Infosys` (×2),
`Besant Technologies`, `Punjab Sind Bank` and `Electricity Board` record an
employer or institution with many Bengaluru sites, not a locality. Those need
the respondent's answer or the site address from the field team. They land on
the `Still open` sheet. Leaving them blank is a defensible result.

The alternative spellings in the `HINTS` block of `resolve_places.py` are
unverified readings based on spelling similarity — guesses about what to *ask*,
not answers. Only TomTom's reply is evidence, and it still needs checking on a
map before it enters any output.

## Read before using any figure

These carry over from the header comments in `travel_times.py` and belong in the
methodology, not just in the code:

- **Auto/Cab** is TomTom `motorcycle` mode capped at 45 km/h. No routing API has
  an auto-rickshaw travel mode. The cap is an **assumption, not a finding** —
  calibrate it against observed trips and state it. Car time is output in a
  separate column so the effect of the mode choice is visible.
- **Bus** is in-vehicle road time for a bus-sized vehicle. It is **not a BMTC
  journey time**: it excludes waiting, stop dwell time and transfers, which are
  often the majority of a real bus trip. A true bus time needs BMTC route and
  headway (GTFS) data. Do not present this column as a bus journey time.
- Every trip end is a **locality centroid**, not a respondent address — that is
  all the source file records. Trips under 3 km are flagged, because the
  centroid error is then a large share of the trip.
- Routing, traffic, geocoding and search data © TomTom. Verify before
  publication.
