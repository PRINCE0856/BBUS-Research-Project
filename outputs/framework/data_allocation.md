# Working note: what the passive GPS data can and cannot carry

Source dataset examined: `trip-summary-airport.csv` (Bengaluru airport trips),
89,836 trips, 17,756 devices, 20 columns, 484 MB.

## Columns actually present

Identifiers: trip_id, did (hashed device).
Time: trip_start_time_ist, trip_end_time_ist, trip_duration_seconds.
Volume: total_pings.
Distance: trip_total_length_meters, trip_straight_line_distance_meters.
Speed: trip_avg_speed, trip_max_speed_bw_pings.
Geography: start/end point lat-lon, start/end zone lat-lon (rounded).
Class: trip_direction (Starting / Ending / Passing Thru / 422 blank).
Geometry: LINESTRING or MULTILINESTRING path.

## Quality facts that matter for modelling

- 98.68% of trips have 3+ path points, so route traces are genuinely usable.
- 1.32% (1,183 trips) are 2-point straight lines and must be dropped from any
  route-based analysis. Loss is even across directions, so dropping them does
  not bias by direction.
- 13.67% are MULTILINESTRING, meaning the trace is split. These need stitching
  or flagging before route-matching.
- trip_avg_speed max is 361 kmph and trip_max_speed_bw_pings max is 472 kmph.
  These are physically impossible and indicate ping noise or teleportation
  between towers. A speed-based outlier filter is required before any mode
  inference, or the classifier will learn from garbage.
- trip_straight_line_distance_meters has a minimum of 0, meaning some trips
  start and end at the same point. These are loops or noise.
- Detour ratio (total_length / straight_line_distance) is computable and is a
  strong feature for mode inference and for congestion measurement.

## The decisive gap

There is no mode, no trip purpose, and no demographics. Three of the four
BBUS models depend on separating a bus trip from a car trip:

- M1 needs mode to attribute expenditure and time savings to bus access.
- M2 needs mode to compare exposure and injury risk across modes. This is the
  entire content of the model.
- M4 needs mode to compare bus users against private vehicle users under
  restricted mobility.

Without mode, the passive data supports descriptive travel demand analysis
only. That conclusion matches the team's own July data-collection note.

## Three routes to mode, in ascending cost

1. Procure mode-tagged passive data, or a panel where device owners have
   declared their usual mode. Highest cost, cleanest result.
2. Infer mode from the traces. Speed percentiles, acceleration variability,
   stop ratio and detour ratio separate walk, two-wheeler, car and bus with
   reasonable accuracy. Bus versus car is the hard pair. Route-matching each
   trace against the GTFS bus network is the feature that resolves it, because
   buses follow fixed alignments and stop at fixed points.
   Requires a labelled subsample for training and validation.
3. Do not infer. Use passive data only for network-level demand, congestion
   and OD, and get all mode-specific quantities from the survey. Cheapest in
   analysis, most expensive in survey sample.

Route 2 is the intended path and it changes the survey design: a subset of
survey respondents must consent to sharing GPS or must complete a one-day
travel diary that can be matched to traces. That labelled subsample is what
converts the whole passive dataset into a mode-aware asset.

## Variable-by-variable source allocation

P = passive GPS, S = primary survey, G = GIS/secondary, D = derived.

### M1 socio-economic
| Quantity | Source | Note |
|---|---|---|
| Trip length, duration, time of day | P | Direct |
| OD matrix by zone | P | Direct, needs expansion weights |
| Congestion / detour ratio | P | Direct |
| Value of travel time saved | P + S | P gives time, S gives income to value it |
| Generalised travel cost | P + S | P gives time, S gives fare and access time |
| Household transport expenditure | S | Not inferable |
| Counterfactual spend without bus | S | Stated preference, survey only |
| Employment status | S | Not inferable |
| Female labour force participation | S | Not inferable |
| Women's trip frequency | S | P has no gender |
| Education and healthcare access | S | Not inferable |
| Vulnerability index components | S | Income, disability, elderly, vehicle ownership |
| Effective density / agglomeration | P + G | P gives travel cost matrix, G gives jobs per ward |
| Marginal external congestion cost | P + G + S | P gives flow and speed, S gives counterfactual mode |

### M2 health
| Quantity | Source | Note |
|---|---|---|
| Access and egress walking | P + G | Trace ends to stop locations, or S if no mode |
| Time spent in traffic | P | Direct, drives exposure duration |
| Exposure concentration | G | Air quality network, dispersion or land-use regression |
| Mode-specific exposure | P(mode) + S | Requires mode inference or survey |
| Road injury exposure | P + G | Vehicle-km by mode against crash records |
| Commute stress, perceived safety | S | Ordered response items, survey only |
| Self-reported health | S | Survey only |
| Physical activity gained | P + S | Walking distance from traces, habits from survey |
| DALYs averted | D | Comparative risk assessment on the above |

### Practical implication for survey budget
Every row marked S alone is a question the survey must carry. Every row marked
P alone is a question the survey can drop. The rows marked P + S are where the
saving happens: the survey collects a short valuation or attribute item rather
than a full travel diary, because the trace supplies the behaviour.

The survey therefore shrinks from a full travel-diary instrument to:
socio-demographics, expenditure, employment, counterfactual questions, health
and stress items, and a short stated-preference block. The travel diary,
normally the longest and most expensive module, is largely replaced by traces
for the subsample that consents to matching.
