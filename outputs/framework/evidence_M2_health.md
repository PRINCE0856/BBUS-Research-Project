# M2 evidence base: health co-benefits of bus transport
## Global and Indian precedent, with the data each method needs

READ `VERIFICATION_WARNING.md` FIRST. Nothing here has been read in full text.

---

## A. The decision that matters most

There are two established health-impact methods. They differ enormously in cost.

| | WHO HEAT | ITHIM / ITHIM-Global |
|---|---|---|
| What it does | Converts a change in walking or cycling volume into avoided mortality, monetised via value of statistical life | Full comparative risk assessment across physical activity, PM2.5 and road injury, producing deaths and years of life lost |
| Data needed | Aggregate walking volumes, average trip distance, a value of statistical life | Travel survey with mode, distance, duration by age and sex; injury records; baseline mortality by cause, age and sex; population; a physical-activity survey |
| Pathways covered | Walking and cycling, with adaptable pollution and crash modules | Three pathways plus CO2 |
| Cost | Lowest. Spreadsheet-level | Moderate. Needs the full data stack |
| Fit for BBUS | Good for the access and egress walking that bus use generates | Better. Covers the pathways your M2 framework already names |

Recommendation: run HEAT first as a fast, defensible number for the walking
pathway, then build ITHIM for the full four-pathway model. HEAT gives you
something to show in months, ITHIM gives you the publishable result.

---

## B. The five studies to build on

| Rank | Study | Why it matters |
|---|---|---|
| 1 | Goel, Guttikunda & Tiwari (2022), Active Travel Studies 2(1), New Delhi | An ITHIM application to an Indian city already exists. Reported road injury dominates at about 170,000 DALYs against about 64,000 from traffic PM2.5, and baseline active travel prevents about 90,000 DALYs. Rahul Goel at IIT Delhi is a potential collaborator, not a competitor |
| 2 | Rojas-Rueda et al. (2026), seven-city BRT health impact study | The first standardised, uncertainty-quantified BRT comparative risk assessment. Bogota, Brisbane, Helsinki, Istanbul, Mexico City, Miami, Paris. Reported about 160 deaths prevented annually, interval minus 30 to 374. The honest uncertainty interval is the thing to copy |
| 3 | Mahendra & Rajagopalan (2015), Transportation Research Record 2531, Indore | An Indian BRT health impact assessment already exists. Reported about 14 lives saved per year. A ready template at city scale |
| 4 | Goel (2018), Accident Analysis & Prevention | India-wide exposure-adjusted road injury model by mode. This is the denominator method your GPS data can feed directly |
| 5 | de Sa et al. (2017), Environment International, Sao Paulo | ITHIM in a Global South megacity. Sustainable scenario 63,600 DALYs avoided, car-dominant scenario 54,900 DALYs lost. Shows how to frame two scenarios against a baseline |

---

## C. The four pathways, and what each needs

### Pathway 1: physical activity from access and egress walking
- WHO HEAT is the tool. Lightest data requirement of anything in this file.
- Evidence: Lemoine et al. (2016), Journal of Urban Health, Bogota TransMilenio.
  BRT users were 3.1 times more likely to reach 22 minutes a day of moderate to
  vigorous activity, and 1.5 times more likely to walk 150 minutes a week for
  transport.
- Caution: that study validated self-report against accelerometers in a
  250-person subsample. Self-report alone overstates activity. If you want the
  objective arm you must buy wearables for a subsample. That is the one place
  in M2 where instruments are unavoidable.

### Pathway 2: air pollution exposure
This is a two-stage problem and the stages have very different costs.
- Stage one, exposure factors by mode, REQUIRES portable monitors. You cannot
  get micrograms per cubic metre from GPS.
- Stage two, population exposure, is GPS-native: time in mode by route, from
  traces, multiplied by the factor.

You may not need stage one. Indian per-mode exposure factors already exist:

| Study | City | Reported |
|---|---|---|
| Goel, Gani, Guttikunda et al. (2015), Atmospheric Environment | Delhi, 11 microenvironments | Lowest in air-conditioned cars and metro. PM2.5 inhaled per km about 9 times higher cycling than in an AC car |
| Six-mode comparison (2020), ScienceDirect S1309104220303457 | Delhi | Rickshaw 266, walking 259, non-AC car 149, bus 113, AC car 89, metro 72 micrograms per cubic metre |
| Mumbai in-cabin study (2025) | Mumbai, 7 modes, 194 trips | First Indian black-carbon figures for motorbike, metro and suburban train |
| Chennai study, Environmental Engineering Research | Chennai | Maximum 709 in bus, minimum 29 in closed car. THIS IS AN OUTLIER against the Delhi numbers. Check measurement conditions before using |
| Verma, Parmar & Ganguly (2026), Air Quality Atmosphere & Health | Kanpur | Rail-adjacent layout. Figures not retrieved |

Note the awkward finding: bus sits mid-range, above air-conditioned cars. The
health case for buses does not rest on the individual rider breathing less. It
rests on fewer vehicles on the road, lower injury risk, and more walking. Frame
it that way or a critic will take the argument apart.

### Pathway 3: road injury
| Study | Reported |
|---|---|
| Goel (2018), Accident Analysis & Prevention | Exposure-adjusted, six modes, national. Auto-rickshaws the only motorised mode associated with higher safety. More walking and cycling associated with a safer system |
| Six mid-sized Indian cities study, IATSS Research | Agra, Amritsar, Bhopal, Ludhiana, Vadodara, Visakhapatnam. Two-wheeler occupant fatality 2 to 3 times car rate, shared three-wheeler 3 to 5 times. Vulnerable road users are 84 to 93 per cent of all fatalities. Largest share of those deaths involved buses and trucks |
| Duduta et al. (2012), Transportation Research Record 2317 | Nine BRT systems including Delhi. Centre-lane safer than curbside. Counterflow bus lanes the single most dangerous feature |
| Vecino-Ortiz & Hyder (2015), Journal of Urban Health | Systematic review. Global BRT safety evidence is mixed and sparse. Do not assume the benefit |

The uncomfortable fact to confront directly: buses and trucks are involved in
the largest share of vulnerable road user deaths, and Delhi's BRT corridor is
widely reported to have seen fatalities rise. If BBUS claims a safety benefit
without addressing this, it will not survive review. The defensible claim is
about design: centre-lane, no counterflow, protected pedestrian crossings.

### Pathway 4: commute stress and wellbeing
- Liu, Ettema & Helbich (2022), Travel Behaviour and Society 28, systematic
  review. Evidence heterogeneous. Emotional response during the commute
  moderates the effect more than duration or mode alone.
- Survey-only. GPS cannot see this. A validated short stress or wellbeing scale
  is required, and ordered logit or probit is the right estimator.
- Do not present the cross-study claim that bus commuting is more or less
  stressful than driving as a single citation. It is a synthesis and the
  findings conflict.

---

## D. Monetisation: turning DALYs into rupees

| Source | Gives you |
|---|---|
| Majumder & Madheswaran, ISEC Working Paper 407 | Hedonic wage, 430 workers in Ahmedabad. Value of statistical life about Rs 44.69 million, value of statistical injury about Rs 1.67 million |
| Madheswaran (2007), Social Indicators Research | Earlier estimate about Rs 15 million, Chennai and Mumbai samples |
| SAE Technical Paper 2021-26-0012 | Compares human capital (India's official method), willingness to pay, and iRAP rule of thumb. Road accident loss 0.55 to 1.35 per cent of GDP in 2019 |
| Scientific Reports 11 (2021), non-attainment cities | Global Exposure Mortality Model plus value of statistical life across 31 Indian cities. The monetisation method transfers directly |
| Kushwaha, Saxena & Kumar (2025), Scientific Reports 15:26832, Agra | WHO AirQ+ plus value of statistical life at city scale. Note the January 2026 author correction |

Warning: the two Indian value-of-statistical-life estimates differ by about
three times. Never write "the Indian VSL". Name the study, the year and the
sample, and run the CBA at both values as a sensitivity band.

India's official method is human capital, not value of statistical life. Value
of statistical life gives much larger numbers. If BBUS uses it, say so
explicitly and report the human-capital figure alongside, or the Ministry of
Finance will discount the whole result.

---

## E. Tools you can pick up today

| Tool | Use |
|---|---|
| WHO HEAT | Walking benefit, monetised. Start here |
| ITHIM / ITHIM-Global | Full three-pathway comparative risk assessment |
| WHO AirQ+ | Air pollution attributable burden |
| BenMAP-CE | Air pollution health impact and valuation |
| QGIS | Catchments, exposure surfaces, crash hotspots |
| iRAP / ViDA | Road safety rating of access routes around stops |
| R or Stata | Ordered response models, regression, structural equation models |

## F. Gaps found, which are opportunities

1. No India-specific cost per DALY averted for a transport intervention. This
   appears to be a genuine gap in the literature, not a search failure. BBUS
   could produce the first one.
2. No confirmed WHO HEAT application to an Indian city.
3. No dedicated health study for Guangzhou BRT or Rea Vaya Johannesburg.
4. Only 5 of 39 studies in the Stankov et al. (2020) systematic review of
   transport-intervention health evaluations were from low and middle income
   settings. The thinness of the evidence base is itself the argument for BBUS.
