# Sample size note: what 6,000 households can and cannot detect

Settled: 6,000 respondents across 6 cities, about 1,000 per city.
Group B longitudinal cohort about 450 bus users and 450 non-users per city.

Assumptions used throughout: alpha 0.05 two-sided, power 0.80, equal split
between treatment and control, R-squared of 0.30 from controls where stated.
Female employment baseline taken at 25 per cent. Monthly household transport
spend taken at mean Rs 1,500, standard deviation Rs 1,200. These are indicative
figures for scoping; replace them with your own pilot estimates.

---

## 1. The finding that should change the sampling plan

Bus access is defined geographically: within a 500-metre walkshed of a stop.
That means the treatment is assigned to WARDS, not to households. Households in
the same ward share the treatment and share unobserved neighbourhood
characteristics. Statistically the sample behaves as if it were much smaller
than 1,000 per city.

How much smaller, holding 1,000 households per city:

| Wards per city | Households per ward | Effective sample at ICC 0.05 |
|---|---|---|
| 10 | 100 | 168 |
| 20 | 50 | 290 |
| 25 | 40 | 339 |
| 40 | 25 | 455 |
| 50 | 20 | 513 |

Spreading the same 1,000 households across 50 wards instead of 25 raises the
effective sample by about half and cuts the minimum detectable effect by roughly
a third. It costs nothing in sample size. It costs field logistics.

**Recommendation: sample fewer households in more wards.** Target 40 to 50
wards per city at 20 to 25 households each, rather than 25 wards at 40. This is
the single cheapest improvement available to the design.

---

## 2. What the design can detect

### Group A, cross-section, 3 cities pooled, 3,000 households

Minimum detectable effect, female employment, in percentage points:

| Design | ICC 0.02 | ICC 0.05 | ICC 0.10 |
|---|---|---|---|
| 25 wards per city, no controls | 5.9 | 7.6 | 9.8 |
| 25 wards per city, with controls | 4.9 | 6.4 | 8.2 |
| 50 wards per city, with controls | 4.4 | 5.2 | 6.3 |
| Single city, 25 wards, with controls | 8.6 | 11.0 | 14.2 |

Minimum detectable effect, monthly transport spend, rupees per month:

| Design | ICC 0.02 | ICC 0.05 | ICC 0.10 |
|---|---|---|---|
| 25 wards per city, with controls | 137 | 176 | 227 |
| 50 wards per city, with controls | 121 | 143 | 175 |
| Single city, 25 wards, with controls | 237 | 306 | 394 |

### Group B, two-wave panel difference-in-differences, 2,700 followed

Panel data helps only if the same person's outcome is correlated across waves.
Write that correlation as r. Panel DiD beats a same-sized cross-section only
when r exceeds 0.5. For employment status r is plausibly 0.6 to 0.8. For
transport expenditure it is likely lower.

Female employment, percentage points, pooled, 25 wards per city, with controls:

| | ICC 0.02 | ICC 0.05 | ICC 0.10 |
|---|---|---|---|
| r = 0.3 | 6.0 | 7.7 | 9.8 |
| r = 0.5 | 5.1 | 6.5 | 8.3 |
| r = 0.7 | 3.9 | 5.0 | 6.4 |
| r = 0.8 | 3.2 | 4.1 | 5.2 |
| r = 0.7, single city | 6.8 | 8.7 | 11.1 |

Monthly transport spend, rupees, pooled:

| | ICC 0.02 | ICC 0.05 | ICC 0.10 |
|---|---|---|---|
| r = 0.5 | 141 | 180 | 230 |
| r = 0.7 | 109 | 139 | 178 |

---

## 3. Three consequences you must accept

### 3.1 City-level estimates are not credible. Pooled is the primary result.

A single city gives a minimum detectable effect of roughly 11 percentage points
on employment and roughly Rs 300 a month on spending. Effects that large are
implausible. Any city-specific coefficient will be a noisy null and should not
be presented as a finding.

Your second report already anticipated this: it says that where the achievable
per-city sample is too thin, the pooled specification with city fixed effects
becomes the primary report rather than the secondary. At 6,000 that is no longer
a contingency. It is the plan. Say so in the methods section before anyone asks
for a city ranking.

### 3.2 The vulnerability interaction is underpowered. This is the real problem.

The four-part vulnerability index enters every regression as an interaction, and
the differential effect along vulnerability is described as a headline
coefficient of direct policy interest. A subgroup-difference test needs roughly
four times the sample of a main effect to reach the same precision, so the
detectable interaction is about twice the main-effect size.

| | Main effect | Vulnerability interaction |
|---|---|---|
| Group A pooled, ICC 0.05 | 6.4 pp | about 12.7 pp |
| Group B DiD pooled, ICC 0.05, r = 0.7 | 5.0 pp | about 10.0 pp |

An interaction of 10 to 13 percentage points is not a plausible size. At 6,000
the study is very unlikely to detect the differential benefit to vulnerable
groups even if it is real and policy-relevant.

Three options, in order of preference:

1. **Stratify and over-sample.** Deliberately over-sample low-income, no-vehicle,
   disabled and elderly households so the interaction is estimated on a balanced
   design rather than on whatever the population happens to yield. This is the
   cheapest fix and it costs only sampling design, not sample size.
2. **Reduce the index to a binary split.** A continuous four-part index spends
   power on gradations the sample cannot resolve. A single vulnerable versus
   non-vulnerable split, pre-registered, is far better powered.
3. **Report the interaction descriptively.** Present stratified estimates with
   confidence intervals and state plainly that the study is not powered to test
   the difference. This is honest and defensible; presenting an underpowered null
   as evidence of no differential benefit would not be.

Do not simply run the interaction and report a null. With this design a null is
uninformative, and a policy audience will read it as "buses do not help the poor
more", which the data cannot support either way.

### 3.3 Calibrate expectations against the published effects

The Delhi Pink Pass study reports female employment among marginalised groups
rising by 24 percentage points. If effects in your cities are anywhere near that
size, this design will find them comfortably. If the true effect is a more
ordinary 3 to 5 percentage points, the pooled design is marginal and the
single-city and interaction tests will fail.

Plan for the smaller number.

---

## 4. What to do before fielding

1. Pilot to estimate the intra-cluster correlation for your main outcomes. Every
   number above moves with it, and the range from 0.02 to 0.10 changes the
   minimum detectable effect by about 60 per cent. This is the highest-value
   pilot output.
2. Pilot to estimate the wave-to-wave correlation r for employment and
   expenditure. It decides whether the panel is worth its cost.
3. Re-run this analysis with the piloted values before finalising ward counts.
4. Pre-register the primary specification, the pooled one, and the reduced
   vulnerability split. Pre-registration is what protects an underpowered
   interaction from being read as a finding.
