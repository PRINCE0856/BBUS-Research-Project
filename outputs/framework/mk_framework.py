from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

TEAL=RGBColor(0x00,0x6D,0x77); DARK=RGBColor(0x1A,0x1A,0x1A); GREY=RGBColor(0x55,0x55,0x55)
AMBER=RGBColor(0x9A,0x5B,0x00)

doc=Document()
s=doc.sections[0]
s.top_margin=Cm(2.0); s.bottom_margin=Cm(2.0); s.left_margin=Cm(2.2); s.right_margin=Cm(2.2)
n=doc.styles['Normal']; n.font.name='Calibri'; n.font.size=Pt(10.5); n.font.color.rgb=DARK
n.paragraph_format.space_after=Pt(6); n.paragraph_format.line_spacing=1.08

def shade(cell,hexcol):
    tcPr=cell._tc.get_or_add_tcPr(); sh=OxmlElement('w:shd')
    sh.set(qn('w:val'),'clear'); sh.set(qn('w:color'),'auto'); sh.set(qn('w:fill'),hexcol)
    tcPr.append(sh)

def h1(t):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(16); p.paragraph_format.space_after=Pt(5)
    r=p.add_run(t); r.font.size=Pt(14); r.bold=True; r.font.color.rgb=TEAL
    pPr=p._p.get_or_add_pPr(); pb=OxmlElement('w:pBdr'); bt=OxmlElement('w:bottom')
    bt.set(qn('w:val'),'single'); bt.set(qn('w:sz'),'6'); bt.set(qn('w:space'),'3'); bt.set(qn('w:color'),'006D77')
    pb.append(bt); pPr.append(pb)

def h2(t):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(11); p.paragraph_format.space_after=Pt(3)
    r=p.add_run(t); r.font.size=Pt(11.5); r.bold=True; r.font.color.rgb=DARK

def para(t,size=10.5,italic=False,color=DARK,after=6,bold=False):
    p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(after)
    r=p.add_run(t); r.font.size=Pt(size); r.italic=italic; r.font.color.rgb=color; r.bold=bold
    return p

def bullet(lead,txt,num=False):
    p=doc.add_paragraph(style='List Number' if num else 'List Bullet')
    p.paragraph_format.space_after=Pt(3); p.paragraph_format.left_indent=Cm(0.65)
    p.paragraph_format.first_line_indent=Cm(-0.3)
    if lead:
        r=p.add_run(lead); r.bold=True; r.font.size=Pt(10.5)
    r=p.add_run(txt); r.font.size=Pt(10.5)
    return p

def table(rows,widths,fontsize=8.6,header_fill='E8F2F2'):
    t=doc.add_table(rows=len(rows),cols=len(rows[0])); t.style='Table Grid'
    t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for i,row in enumerate(rows):
        for j,txt in enumerate(row):
            c=t.cell(i,j); c.width=widths[j]
            cp=c.paragraphs[0]; cp.paragraph_format.space_after=Pt(1); cp.paragraph_format.space_before=Pt(1)
            r=cp.add_run(txt); r.font.size=Pt(fontsize)
            if i==0:
                r.bold=True; r.font.color.rgb=TEAL; shade(c,header_fill)
            elif j==0:
                r.bold=True
    doc.add_paragraph().paragraph_format.space_after=Pt(2)
    return t

def callout(title,body,fill='FDF4E3',col=AMBER):
    t=doc.add_table(rows=1,cols=1); t.style='Table Grid'
    c=t.cell(0,0); c.width=Cm(16.6); shade(c,fill)
    cp=c.paragraphs[0]; cp.paragraph_format.space_after=Pt(2)
    r=cp.add_run(title); r.bold=True; r.font.size=Pt(10); r.font.color.rgb=col
    p2=c.add_paragraph(); p2.paragraph_format.space_after=Pt(1)
    r2=p2.add_run(body); r2.font.size=Pt(9.5)
    doc.add_paragraph().paragraph_format.space_after=Pt(2)

# ============ TITLE ============
p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(0)
r=p.add_run('Making the health and socio-economic case for bus investment')
r.font.size=Pt(19); r.bold=True; r.font.color.rgb=TEAL
p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(2)
r=p.add_run('An analytical framework for #BBUS Models 1 and 2, built around a passive-data-first design')
r.font.size=Pt(12); r.font.color.rgb=GREY
p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(12)
r=p.add_run('CEEW  ·  Working draft for internal discussion  ·  September 2026')
r.font.size=Pt(9); r.italic=True; r.font.color.rgb=GREY

callout('Status of this document',
 'This is a scaffolding document, not a CEEW publication. It sets out what has been done elsewhere, which '
 'methods fit the BBUS data position, and where the money should go. Under CEEW’s AI usage guidelines the '
 'analytical choices, the framing and the writing of any output remain yours to own. Every citation here was '
 'found by web search only; the session that produced it could not open a single paper in full text because the '
 'network policy blocked scholarly domains. No figure in this document has been verified against a primary source. '
 'Open and read every source before it enters a CEEW output.')

# ============ 1 ============
h1('1. The question, restated so it can be answered')
para('Your boss is asking a question that sounds like one question but is three. Separating them is the first '
     'analytical act, because each has a different method, a different data need and a different cost.')
table([
 ('','The question as asked','The question as it must be posed to be answerable','Method family'),
 ('Q1','Are people better off in money terms because of the bus?','Does living within walking distance of a bus stop change household transport spending, employment and time use, relative to comparable households that do not?','Causal inference on household outcomes'),
 ('Q2','Is the bus good for health?','Does a shift from two-wheelers, cars and autos to buses change walking, pollution exposure, injury risk and stress enough to move measurable disease burden?','Comparative risk assessment'),
 ('Q3','Is it worth the money?','What is the monetised value of those effects per rupee of public spend, and under what assumptions does that conclusion flip?','Cost-benefit analysis with switching values'),
], [Cm(1.0),Cm(4.4),Cm(7.4),Cm(3.8)])
para('Q1 and Q2 are empirical and your team is already well set up for them. Q3 is a valuation exercise and is '
     'where most transport studies quietly lose credibility, because the answer depends on assumptions that are '
     'never stated. Section 7 deals with that directly.')

# ============ 2 ============
h1('2. What has actually been done, globally and in India')
para('The honest summary is this. The methods are mature and settled. The Indian evidence base is nearly empty. '
     'A systematic review of transport-intervention health evaluations found only five of thirty-nine studies came '
     'from low and middle income settings. Your own M1 review found one India-specific co-benefit study out of '
     'twenty-seven. That thinness is not a weakness in the BBUS proposal. It is the entire justification for it.')

h2('2.1 The precedents worth copying')
table([
 ('Study','Where','Design','Why it matters for BBUS'),
 ('Halder & Jayadev 2025, Azim Premji University','Bengaluru, Shakti scheme','Route-level administrative trip records, 2.7 to 2.9 crore trips over 27 months','Uses operator data only. No survey cost at all. Bengaluru is already a Group A city. Reported women’s ridership up over 150 per cent'),
 ('Dasgupta & Datta 2023, Ashoka DP 105','Delhi Pink Pass','Difference-in-differences on scheme start, Time Use Survey','The exact Group B logic. Reported very large employment effects, large enough that they must be checked'),
 ('Rathore & Singh 2026, arXiv 2604.14758','Five Indian states','Triple difference and event study on staggered rollout','PM e-Bus Sewa has the same staggered structure. Triple difference is more robust than plain DiD to city-specific shocks'),
 ('Martinez et al. 2020, IZA DP 12020','Lima Metropolitano','Causal DiD on staggered BRT opening, estimated separately by sex','The international reference for transit and women’s employment. Gains found for women only'),
 ('Garlick, Field, Vyborny & Subramanian 2024, IZA DP 17883','Urban Pakistan','Randomised controlled trial of women-only versus mixed transport','The only true experiment in this space. Reported job applications more than doubled'),
 ('Borker 2021, World Bank PRWP 9731','Delhi','Route safety scored from crowdsourced audits, fed into a choice model','Turns safety from a soft perception into a route attribute that changes real decisions'),
 ('Goel, Guttikunda & Tiwari 2022, Active Travel Studies','New Delhi','ITHIM comparative risk assessment','An Indian ITHIM application already exists. Injury burden reported at roughly three times the traffic PM2.5 burden'),
 ('Rojas-Rueda et al. 2026','Seven BRT cities','Comparative risk assessment with Monte Carlo uncertainty','The current state of the art for BRT health assessment, and it publishes an honest uncertainty interval'),
 ('Mahendra & Rajagopalan 2015, TRR 2531','Indore','Health impact assessment from modal shift and vehicle-km','An Indian BRT health assessment already exists. A ready template'),
 ('Muralidharan & Prakash 2017, AEJ Applied','Bihar','Triple difference, bicycles for girls','The most rigorous transport-and-education study found. Design adapts directly to a student bus pass'),
], [Cm(4.3),Cm(2.7),Cm(4.6),Cm(5.0)])

callout('The one number that should worry you',
 'Dasgupta and Datta report female employment among marginalised groups rising by 24 percentage points after the '
 'Delhi Pink Pass. That is an enormous effect for a fare change. It may be real, it may be a short-run or '
 'composition artefact. Either way, if BBUS cites it uncritically and it does not hold, the whole report is '
 'discredited. Read the paper, check the specification, and if you use it, present it alongside the more '
 'conservative estimates.', fill='FBEAEA', col=RGBColor(0x99,0x22,0x22))

# ============ 3 ============
h1('3. The framework: one causal chain, five links')
para('Everything in M1 and M2 hangs off a single chain. Naming the links makes the data requirements fall out '
     'automatically, and makes it obvious which link each method serves.')
table([
 ('Link','What changes','How it is measured','Data source'),
 ('1','Bus deployment changes the generalised cost of travel: in-vehicle time, waiting, access walk, fare, reliability','Generalised cost function, calibrated per city','GPS traces for time and route; survey for fare and perceived reliability; GTFS for headway'),
 ('2','Travellers respond: some switch mode, some make trips they would not have made','Discrete choice model, jointly estimated on revealed and stated preference; elasticities as a cross-check','GPS as revealed preference; short stated-preference block as the counterfactual'),
 ('3','Aggregate travel changes: vehicle-km by mode, time in traffic, walking distance, jobs reachable','Network assignment and accessibility analysis','GPS plus GTFS plus ward employment data'),
 ('4a','Socio-economic outcomes move: spending, employment, women’s trip-making, school and clinic access','Difference-in-differences (Group B), cross-sectional regression with rich controls (Group A), vulnerability interaction throughout','Survey. Almost none of this is inferable from traces'),
 ('4b','Health outcomes move: physical activity, PM2.5 exposure, injury risk, commute stress','Comparative risk assessment (ITHIM), with WHO HEAT for the walking pathway','GPS for exposure duration and walking; existing Indian exposure factors; police and Global Burden of Disease records; survey for stress'),
 ('5','Effects become rupees, then become an investment case','Cost-benefit analysis with switching values, plus three SROI lenses','Value of statistical life, value of travel time, avoided treatment cost'),
], [Cm(1.0),Cm(5.0),Cm(5.4),Cm(5.2)])
para('Link 2 is the hinge of the whole project. It is the only place where the passive data and the survey have '
     'to be formally joined, and it is what converts a 6,000-household survey into a statement about a city.')

doc.add_page_break()

# ============ 4 ============
h1('4. Model 1: the socio-economic case')
h2('4.1 What to estimate')
para('Your second report already settles the identification strategy and it is the right one. Group A gets a '
     'cross-sectional regression with rich controls, because no pre-bus baseline exists. Group B gets a two-period '
     'difference-in-differences off the staggered PM e-Bus Sewa rollout. The vulnerability index enters as an '
     'interaction so that differential benefit is a headline coefficient rather than a subgroup footnote. Nothing '
     'below changes that. It adds three things.')
bullet('Add a triple difference where you can. ','Rathore and Singh use states that adopted at different times as '
       'a second comparison dimension. Your Group B cities receive buses at different dates under the same national '
       'scheme. That gives you the same structure and it is more robust than a plain two-group comparison to '
       'anything city-specific that happens at the same time as the buses.')
bullet('Add an accessibility outcome. ','Household outcomes are self-reported and contested. Jobs reachable within '
       '45 and 60 minutes by bus is computed from GTFS and ward employment data, is not self-reported at all, and '
       'is directly comparable to the World Bank’s eleven-city African benchmark. It is cheap and it is the most '
       'defensible single number M1 can produce.')
bullet('Add subsidy incidence. ','The Mumbai work found the poorest 27 per cent of the population received only 19 '
       'per cent of the bus subsidy. Repeating that calculation for six cities answers the question a finance '
       'ministry actually asks, which is not "is the bus good" but "is our money reaching the people we said it '
       'would".')

h2('4.2 The outcomes and where each comes from')
table([
 ('Outcome','Analysis','Source'),
 ('Household transport expenditure','Regression / DiD, full sample','Survey only'),
 ('Employment status, and female employment','Regression / DiD, women-only subsample','Survey only'),
 ('Women’s trip frequency, captive users','Regression on households without a private vehicle','Survey only'),
 ('Jobs reachable in 45 and 60 minutes','Accessibility computation, no survey needed','GTFS, ward employment, GPS travel times'),
 ('Value of travel time saved','Descriptive on bus users','GPS for time, survey for income to value it'),
 ('Education and healthcare access','Descriptive, bus-using subsample','Survey only'),
 ('Decongestion, marginal external congestion cost','Separate reporting, not household level','GPS flow and speed, survey counterfactual mode'),
 ('Agglomeration, effective density','Separate reporting, not household level','GPS cost matrix, Economic Census, PLFS'),
 ('Subsidy incidence','Descriptive by income decile','Survey plus operator fare and subsidy data'),
], [Cm(5.4),Cm(5.4),Cm(5.8)])
para('Note the pattern. Everything that requires knowing something about a person comes from the survey. '
     'Everything that requires knowing something about the network comes from the passive data and secondary '
     'sources. That division is what the budget should follow.')

# ============ 5 ============
h1('5. Model 2: the health case')
h2('5.1 Start with the cheap tool, then build the expensive one')
table([
 ('','WHO HEAT','ITHIM / ITHIM-Global'),
 ('Covers','Walking and cycling, monetised via value of statistical life','Physical activity, PM2.5 and road injury, producing deaths and years of life lost'),
 ('Needs','Aggregate walking volume, trip distance, a value of statistical life','Travel data by mode, distance, age and sex; injury records; baseline mortality by cause; population; physical activity levels'),
 ('Cost','Lowest. Spreadsheet level','Moderate. Needs the full stack'),
 ('Use it for','A defensible number within months, for the access and egress walking that bus use generates','The full four-pathway model and the publishable result'),
], [Cm(2.6),Cm(6.4),Cm(7.6)])
para('Run HEAT first. It gives the communications team something real while the full model is being built, and it '
     'uses data you will already have.')

h2('5.2 The four pathways and the honest position on each')
bullet('Physical activity. ','The strongest and least contestable pathway. Bus users walk to and from stops; '
       'private vehicle users do not. Bogota evidence reports BRT users about three times more likely to reach '
       'moderate-to-vigorous activity thresholds. Note that the study validated self-report against accelerometers '
       'in a subsample. Self-report alone overstates activity. If you want the objective arm, you must buy wearables '
       'for a subsample. That is the only place in M2 where instruments are genuinely unavoidable.')
bullet('Air pollution exposure. ','Handle with care. Indian measurements put in-bus PM2.5 in the middle of the '
       'range, above air-conditioned cars. The health case for buses does not rest on the individual rider breathing '
       'less. It rests on fewer vehicles on the road, and on the population-level concentration reduction. Say so '
       'explicitly, or a reviewer will use your own data against you.')
bullet('Road injury. ','The most uncomfortable pathway. Indian city crash data reports that vulnerable road users '
       'are 84 to 93 per cent of fatalities, and that the largest share of those deaths involves buses and trucks. '
       'Delhi’s BRT corridor is widely reported to have seen fatalities rise. A systematic review concludes global '
       'BRT safety evidence is mixed. The defensible claim is conditional: centre-lane alignment, no counterflow '
       'lanes, protected crossings. Design-contingent, not automatic.')
bullet('Commute stress and wellbeing. ','Survey only. GPS cannot see it. Use a validated short scale and an ordered '
       'logit or probit. Do not present the cross-study claim about bus versus car stress as a single finding; the '
       'literature conflicts.')

callout('Do not skip this',
 'You already have the exposure factors you need. Indian per-mode PM2.5 measurements exist for Delhi, Mumbai, '
 'Chennai and Kanpur. That means you do NOT need to buy portable monitors for stage one. You need them only if you '
 'want city-specific factors for your six cities. Combining published factors with your own GPS time-in-mode data '
 'is a legitimate, published approach and it saves a large amount of money.', fill='E8F2F2', col=TEAL)

doc.add_page_break()

# ============ 6 ============
h1('6. The data strategy: passive first, survey for what is left')
h2('6.1 The blocking problem')
para('The passive dataset examined for this note covers 89,836 airport trips from 17,756 devices in Bengaluru. It '
     'has origin, destination, timing, duration, length, speed and route traces. Route quality is good: 98.7 per '
     'cent of trips have three or more path points. It has no travel mode, no trip purpose and no demographics.')
para('Three of the four BBUS models depend on separating a bus trip from a car trip. Without mode, the passive data '
     'supports descriptive demand analysis and nothing more. Your own July data note reached the same conclusion. '
     'This is the single highest-priority technical problem in the project.')

h2('6.2 How to get mode without buying it')
para('Mode can be inferred from the traces. Speed percentiles, acceleration variability, stop ratio and detour '
     'ratio separate walking, two-wheeler, car and bus with published accuracies above ninety per cent on benchmark '
     'datasets. The hard pair is bus versus car, because both are motorised and share the road.')
para('The feature that resolves it is not in the speed profile. It is map-matching each trace against the GTFS bus '
     'network. Buses follow fixed alignments and stop at fixed points. A trace that stops repeatedly at known stops '
     'along a known route is a bus trip. Build this in from the start.')
callout('What this does to your survey design',
 'A classifier needs labelled training data. That means a subset of survey respondents must either consent to '
 'sharing location history, or complete a one-day travel diary that can be matched to traces by time and place. '
 'Budget for this explicitly. It is small, but it is the hinge on which the entire passive-data strategy turns. '
 'Without it, you have paid for data you cannot use for M1, M2 or M4.')

h2('6.3 Correcting the bias, before designing the survey')
para('Passive data over-represents smartphone owners, which in India means younger, richer, more male and more '
     'urban. Left uncorrected it will systematically understate precisely the vulnerable groups BBUS exists to '
     'measure. The correction is multilevel regression and poststratification against census strata, with the '
     'survey supplying ground truth.')
para('The sequence matters and it saves money. Diagnose which strata the passive data under-represents. Then target '
     'the survey at those strata. Then reweight. Designing the survey before running the diagnosis means paying for '
     'observations you did not need.')

h2('6.4 The formal join')
para('Treat the two sources as what they are. Passive traces are revealed preference: what people really did, at '
     'scale, without recall error, but with no attributes and no counterfactual. The survey is stated preference '
     'plus attributes: small, but it knows gender, income and disability, and it can ask about a bus that does not '
     'exist yet.')
para('Joint revealed-and-stated-preference estimation with a scale parameter, following Ben-Akiva and Morikawa, is '
     'the standard method for combining them. The scale parameter absorbs the different error variance between real '
     'and hypothetical choices, so hypothetical bias in the survey does not contaminate the shared taste parameters. '
     'This is what allows a survey of a few thousand households to speak for a city of millions. It is the most '
     'important methodological decision in the project.')

h2('6.5 Expanding to the city')
para('Iterative proportional fitting reweights the survey so its weighted margins match ward-level census '
     'distributions, producing a synthetic population. Expect zero-cell and rounding problems when a few thousand '
     'households are spread across many wards; the literature offers simulated annealing as the alternative. Where '
     'only zone totals are reliable, entropy maximisation distributes trips across zones using a GPS-derived cost '
     'matrix.')

# ============ 7 ============
h1('7. The survey that is actually left')
para('Applying the allocation above, the survey shrinks considerably. The travel diary, normally the longest and '
     'most expensive module, is largely replaced by traces for the subsample that consents to matching.')
table([
 ('Module','Keep or drop','Why'),
 ('Socio-demographics, vulnerability index','Keep, essential','Nothing in the traces knows gender, income, disability or age'),
 ('Household transport expenditure','Keep, essential','Primary M1 outcome. Not inferable'),
 ('Employment and female employment','Keep, essential','Primary M1 outcome. Not inferable'),
 ('Counterfactual questions: spend, trips and mode without the bus','Keep, essential','This is the counterfactual. Nothing else supplies it'),
 ('Health, stress and perceived safety items','Keep, essential','M2 fourth pathway. Survey only'),
 ('Short stated-preference block','Keep, essential','The stated-preference half of the joint estimation'),
 ('Consent to GPS matching, or a one-day diary','Keep, on a subsample','Trains and validates the mode classifier'),
 ('Full multi-day travel diary','Drop for most respondents','Replaced by traces. This is where the saving is'),
 ('Trip length, duration, route, time of day','Drop','Comes from the traces, and more accurately than recall'),
], [Cm(5.0),Cm(3.4),Cm(8.2)])

callout('A discrepancy that must be resolved before anything else',
 'The April inception report specifies 6,000 respondents across six cities, at 800 to 1,200 per city, with about '
 '450 users and 450 non-users tracked longitudinally in each Group B city. The figure circulating in discussion is '
 '60,000. That is a tenfold difference. It determines the budget, the statistical power, the minimum detectable '
 'effect, and how much weight the passive data must carry. Nothing else in the design can be finalised until this '
 'is settled.', fill='FBEAEA', col=RGBColor(0x99,0x22,0x22))

doc.add_page_break()

# ============ 8 ============
h1('8. From effects to rupees, and the traps in doing it')
h2('8.1 Monetisation inputs')
table([
 ('Quantity','Source','Warning'),
 ('Value of statistical life, India','Hedonic wage estimates from Indian samples','Published Indian estimates differ by roughly three times. Never write "the Indian VSL". Name the study, year and sample, and run the analysis at both values'),
 ('Official Indian method','Human capital, not value of statistical life','Value of statistical life gives much larger numbers. If you use it, report the human-capital figure alongside or the Ministry of Finance will discount the result'),
 ('Value of travel time','Indian stated-preference estimates by mode','Bus users’ time is reportedly valued at a small fraction of car users’ time. This is why time-savings-led appraisal always favours roads. Name the problem in the report'),
 ('Avoided treatment cost','Health system unit costs','Cheaper to defend than value of statistical life. Report both'),
 ('Social cost of carbon','India’s shadow carbon price','Feeds M3, not M1 or M2'),
], [Cm(3.6),Cm(4.4),Cm(8.6)])

h2('8.2 Cost-benefit analysis is not social return on investment')
para('Your four models produce effect sizes. Turning those into a single social-return ratio requires valuation '
     'choices that a strict cost-benefit analyst will contest, because social return on investment is '
     'stakeholder-driven and theory-of-change based, while cost-benefit analysis is an external efficiency test. '
     'They answer different questions.')
para('Report both. A conventional cost-benefit analysis with a benefit-cost ratio and net present value for the '
     'finance audience, and the three social-return lenses for the political audience. If a single social-return '
     'ratio is the only number in the report, a ministry economist will reject the whole thing.')

h2('8.3 Sensitivity, done the way funders expect')
bullet('Switching values. ','How far must each parameter move before the decision flips? This is the ADB format and '
       'it is the most persuasive presentation for a finance audience, because it converts an argument about '
       'assumptions into a testable threshold.')
bullet('Monte Carlo over the elasticity range. ','The meta-analytic range for transit fare elasticity spans roughly '
       'minus 0.01 to minus 1.3. Sample across it rather than picking a point estimate.')
bullet('Optimism bias. ','Ridership forecasts are systematically optimistic. Treasury guidance provides empirical '
       'uplift factors. Apply them and say you did.')
bullet('Publish the uncertainty interval. ','The seven-city BRT study reports a benefit interval that includes the '
       'possibility of net harm in the most pessimistic draw. Publishing that honesty is what made it credible.')

# ============ 9 ============
h1('9. Three findings that could go against us')
para('A framework that cannot lose is not evidence. These are the three results that would genuinely complicate the '
     'BBUS narrative, and each should be pre-committed to before the data comes in.')
bullet('Bus riders may not breathe less. ','Indian in-vehicle measurements put buses above air-conditioned cars. '
       'The population-level argument still holds, but the individual-level one does not. Decide now how to present it.')
bullet('Buses may not look safer at the corridor level. ','Vulnerable road user deaths involving buses are a large '
       'share of Indian city fatalities, and at least one Indian BRT corridor reportedly saw fatalities rise. The '
       'claim that survives is conditional on design.')
bullet('The subsidy may be regressive. ','Mumbai evidence suggests the poorest quarter of the population received '
       'well under their share of bus subsidy. If that repeats across the six cities, it is an uncomfortable '
       'finding, and it is also the most policy-useful thing BBUS could produce.')
para('Committing to report these before seeing the data is what separates research from advocacy, and it is what '
     'CEEW’s independence requires.')

# ============ 10 ============
h1('10. Sequencing')
table([
 ('Stage','What happens','Why in this order'),
 ('1','Settle the sample size question','Everything downstream depends on it'),
 ('2','Diagnose bias in the passive data against census strata','Tells you which strata the survey must over-sample'),
 ('3','Build and validate the mode classifier, with GTFS map-matching','Unlocks the passive data for M1, M2 and M4'),
 ('4','Finalise the survey instrument around the remaining gaps','Now the instrument can be short and cheap'),
 ('5','Run WHO HEAT on the walking pathway','Produces a defensible early number for communications'),
 ('6','Field Group A cross-section and Group B baseline','The core data collection'),
 ('7','Estimate joint revealed and stated preference choice model','The formal join between the two data sources'),
 ('8','Build ITHIM, run M1 regressions','The main analytical output'),
 ('9','Monetise, run switching values, build the three SROI lenses','The investment case'),
], [Cm(1.4),Cm(7.6),Cm(7.6)])

# ============ SOURCES ============
h1('Sources')
para('The full annotated evidence base sits alongside this document in three files: the socio-economic evidence for '
     'Model 1, the health evidence for Model 2, and the demand, elasticity and data-fusion methods. Each entry '
     'carries its link, the design used and the reported result.')
para('Every one of those sources was located by web search alone. Full-text retrieval was blocked throughout. Two '
     'specific problems are already known: a reported reduction in harassment near new Delhi Metro stations appears '
     'as both 29 and 32 per cent in different secondary sources, and a claim that transport reduces school dropout '
     'by 15 to 25 per cent traces only to a non-academic aggregator with no primary source and should not be used. '
     'Treat the whole set as a search map, not a bibliography, until a person has opened each one.',
     italic=True, color=GREY)

doc.save('BBUS_M1_M2_Analytical_Framework.docx')
print('saved')
