# Bengaluru non-shifters — travel time estimation

Scripts for filling the three travel-time columns in the non-shifters OD file
(`Non_Shifters_120_Improved_Approx_Travel_Times.xlsx`, 120 respondents).

| File | What it does |
|---|---|
| `travel_times.py` | Fills the 2-Wheeler / Bus / Auto-Cab columns from TomTom routing. Writes `Travel_Times_FILLED.xlsx`. |
| `resolve_places.py` | Companion. Proposes canonical names for the area strings `travel_times.py` could not match, as an evidence table. Writes `Place_Candidates.xlsx`. |
| `_mocktest.py` | Offline test scaffold for `resolve_places.py`. Fake TomTom responses, so logic changes can be checked without network or API quota. |

Both scripts need `requests` and `openpyxl`, and a free TomTom key
(https://developer.tomtom.com/ — email signup, no credit card).

```bash
python3 -m pip install requests openpyxl
export TOMTOM_API_KEY=your_key_here
```

## Run it

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
