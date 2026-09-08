# Methods: demand, elasticity, modal shift, and getting the most from passive data
## The answer to "we bought passive data, how do we survey as little as possible"

READ `VERIFICATION_WARNING.md` FIRST. Nothing here has been read in full text.

---

## 1. The central idea: your GPS data is revealed preference

Treat the two data sources as what they actually are.

- **Passive GPS traces are revealed preference.** They record what people
  really did. Large sample, no recall error, no social desirability bias. But
  no attributes, no attitudes, no counterfactual, and biased toward
  smartphone owners.
- **A survey is stated preference plus attributes.** Small sample, but it can
  ask about a bus that does not exist yet, and it knows the respondent's
  gender, income and disability status.

The method that joins them is **joint RP-SP estimation with a scale parameter**.
It is forty years old and completely standard.

| Reference | What it gives |
|---|---|
| Ben-Akiva & Morikawa (1990), Transportation Research Part A 24(6), 485-495 | The foundational method. A scale parameter absorbs the different error variance between real and hypothetical choices, so stated-preference hypothetical bias does not contaminate the shared taste parameters |
| Ben-Akiva, Bradley, Morikawa et al. (1994), Marketing Letters 5(4), 335-350 | Generalises it. The standard citation for justifying the fusion |
| Polydoropoulou & Ben-Akiva (2001), Transportation Research Record 1771 | A worked transit example: nested logit combining RP and SP across multiple transit modes and access modes |
| Hensher, Rose & Greene, Applied Choice Analysis, 2nd ed., 2015 | The practical how-to for your econometrician |
| Train, Discrete Choice Methods with Simulation, 2nd ed., 2009 | Needed if you want mixed logit for unobserved taste heterogeneity |
| arXiv 2604.15564, mobility of immigrants in Canada | Mixed logit estimated directly from a GPS panel. The closest published analogue to what you are doing |

This is the single most important methodological decision in the project. It is
what lets a 6,000-household survey speak for a city of millions.

---

## 2. Getting mode out of the traces

Without mode your passive data cannot serve M1, M2 or M4. Three references.

| Reference | What it gives |
|---|---|
| Zheng, Liu, Wang & Xie (2008), WWW '08, 247-256 | The foundational GPS mode-detection method using speed and acceleration segment features. Introduced the GeoLife labelled dataset, 182 users in Beijing, which you can use as an external benchmark |
| Sensors 24(12), 3884 (2024), DOI 10.3390/s24123884 | Modern machine-learning pipeline. Random forest about 91 per cent, decision tree about 94.6 per cent on GeoLife. Documents the features that work: 95th-percentile speed to split low from high speed modes, stop ratio and acceleration variability to separate bus from car |
| Toole, Colak, Sturt, Alexander, Evsukoff & Gonzalez (2015), Transportation Research Part C 58(B), 162-177 | End-to-end: passive data to home and work inference to origin-destination matrix to network assignment |

**The known hard problem: bus versus car.** Both are motorised, both use the
same roads, similar speeds. The feature that resolves it is not in the speed
profile. It is **map-matching each trace against the GTFS bus network**. Buses
follow fixed alignments and stop at fixed points. A trace that stops repeatedly
at known bus stops along a known route is a bus trip. Build this in from the
start rather than trying to fix accuracy later.

**You need a labelled subsample to train and validate.** This changes your
survey design: a subset of respondents must either consent to sharing their own
location history, or complete a one-day travel diary that can be matched to
traces by time and place. Budget for this explicitly. It is the hinge on which
the whole passive-data strategy turns.

---

## 3. Correcting the bias in passive data

Passive data over-represents smartphone owners, which in India means younger,
richer, more male and more urban. Uncorrected, it will systematically understate
exactly the vulnerable groups BBUS exists to measure. This is not a detail.

| Reference | What it gives |
|---|---|
| arXiv 2604.16193, correcting socioeconomic bias in mobile phone mobility estimates | Multilevel regression and poststratification applied to mobility metrics. Reported about 17 per cent bias reduction on radius of gyration. Shows partial correction is possible from geography alone when socio-demographic microdata is missing |
| arXiv 2509.02603, machine learning approach to measuring bias in mobile phone population data | Diagnoses which demographic and geographic strata are over or under represented. Run this first, then target your survey at the under-represented strata |
| Alexander, Jiang, Murga & Gonzalez (2015), Transportation Research Part C 58(B) | Inferring trip purpose and time-of-day origin-destination patterns, validated against a travel survey |
| Calabrese et al. (2013), Transportation Research Part C | Cross-validates mobile-derived trip counts against a national travel survey and vehicle odometer data. Documents where passive data over and under counts |
| Springer, Transportation (2025), DOI 10.1007/s11116-025-10708-4 | Recent direct empirical comparison of mobile-phone-derived travel behaviour against matched survey metrics. The closest reference to your own planned validation |

The sequence is: diagnose the bias, then let the survey fill the gaps the
diagnosis reveals, then reweight. Do not design the survey before running the
diagnosis. That order saves money.

---

## 4. Expanding a small survey to a whole city

| Reference | What it gives |
|---|---|
| Procedia Computer Science, population synthesis using iterative proportional fitting: a review | Iterative proportional fitting is the workhorse. Reweight your survey so its weighted margins match ward-level census distributions on age, household size, income. Produces a synthetic population |
| Computers, Environment and Urban Systems (2018), IPF versus simulated annealing | How to handle rounding and zero-cell problems. You will hit these with 6,000 households spread over many wards |
| ResearchGate 229520409, combining sample and census data in small area estimates | Practical implementation guide in standard software |
| ResearchGate 345770527, synthetic population from small-sample travel survey plus raster census | Matches your exact situation |
| Wilson (1969), Journal of Transport Economics and Policy | Entropy maximisation, the theoretical basis for gravity-model trip distribution. Distributes a survey-estimated trip total across zones using a GPS-derived cost matrix |

---

## 5. Elasticities: benchmarks to check your results against

Do not estimate these from scratch if you can avoid it. Estimate your own, then
check them against the literature. A wildly different number means an error.

| Source | Value to check against |
|---|---|
| Balcombe et al. (2004), TRL Report 593, and Paulley et al. (2006), Transport Policy 13(4), 295-306 | The standard reference on fare, service, income and car-ownership elasticities by trip purpose, time period and journey length |
| Holmgren (2007), Transportation Research Part A 41(10) | Meta-analysis, 186 elasticities from 81 studies. Mean fare elasticity about minus 0.38, range minus 0.009 to minus 1.32. Service-level elasticity up to about 1.9. Use the RANGE for your Monte Carlo bounds |
| TCRP Report 95, Chapter 12 | Bus fare elasticity minus 0.2 to minus 0.3 short run, minus 0.4 to minus 0.6 long run |
| TCRP Report 95, Chapter 9 | Frequency and headway elasticity about 0.5, service expansion 0.6 to 1.0 |
| Deb & Filippini (2013), Journal of Transport Economics and Policy 47(3), 419-436 | INDIA. State panel, 22 states, 1990 to 2001. Demand fare-inelastic. Service density matters more than fare. Income elasticity insignificant or negative, masked by rising private vehicle ownership |
| Deepa, Pinjari, Nirmale, Srinivasan & Rambha (2022), Transportation Research Part A 163, 126-147 | INDIA, BENGALURU. Stop-level direct demand model handling frequency endogeneity and metro competition. The closest local methodological template |
| Transport Policy (2023), headway variability in Bengaluru | Headway VARIABILITY suppresses ridership independently of mean headway. Your GPS fleet traces can compute this directly. A reliability elasticity is a novel, defensible contribution |

The Deb and Filippini finding matters politically: in India, service supply
moves ridership more than fare does. That supports investment over subsidy, and
it is the argument BBUS is being asked to make.

---

## 6. Four-step model: use it, but know its limits

| Source | Note |
|---|---|
| NCHRP Report 716, Travel Demand Forecasting: Parameters and Techniques | Default parameters when local calibration data is thin |
| MoHUA Comprehensive Mobility Plan toolkit and terms of reference | India's own guidance explicitly allows a SIMPLIFIED modelling technique with reduced origin-destination sample and larger zones for resource-constrained cities. This is official cover for exactly the budget position you are in. Cite it |
| ResearchGate 263423775, shortcomings of the four-step process | Sequential steps do not feed back, cannot capture induced demand, aggregate zones, weak on non-motorised modes |
| FHWA Travel Model Improvement Program | When to move to activity-based modelling |

For BBUS the four-step model is not the right centrepiece. Your questions are
about who benefits and by how much, which is a causal-inference question, not a
forecasting question. Use the four-step structure for the network assignment
step that feeds GHG and congestion, and use difference-in-differences and
discrete choice for everything else.

---

## 7. Sensitivity, uncertainty and the appraisal frame

| Source | Note |
|---|---|
| UK DfT TAG Unit M4, Forecasting and Uncertainty | Requires an uncertainty log and structured sensitivity tests. Adopt the log format |
| HM Treasury Green Book | Discounting, optimism bias, scenario and Monte Carlo analysis |
| HM Treasury supplementary guidance on optimism bias | Empirical uplift factors. Ridership forecasts are systematically optimistic |
| ADB Guidelines for the Economic Analysis of Projects (2017) | Switching-value analysis: how far must a parameter move to flip the decision. This is the most persuasive sensitivity format for a finance audience |
| ADB ex-post accuracy study of transport CBAs, 59 completed road projects | Empirical forecast error magnitudes for the region |
| UK DfT TAG Unit A2.1, Wider Economic Impacts | Where agglomeration and labour-market effects sit relative to core user benefits. This is the guidance your M1 agglomeration work already follows |

---

## 8. CBA is not SROI, and the difference will be questioned

| Source | Note |
|---|---|
| Social Value International, A Guide to Social Return on Investment | The principles. Stakeholder-driven, theory-of-change based |
| Evaluation and Program Planning (2017), comparing CBA and SROI | CBA is an externally applied economic efficiency test. SROI is internally oriented and stakeholder-driven. They answer different questions |

Practical implication for BBUS. Your four models produce effect sizes. Turning
those into a single SROI ratio requires valuation choices that a strict
cost-benefit analyst will contest. Report both: a conventional CBA with a
benefit-cost ratio and net present value for the finance audience, and the SROI
lenses for the political audience. Do not let the SROI ratio be the only number,
or a Ministry of Finance economist will reject the whole thing.
