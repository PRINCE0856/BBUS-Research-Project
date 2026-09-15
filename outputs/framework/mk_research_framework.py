from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

TEAL=RGBColor(0x00,0x6D,0x77); DARK=RGBColor(0x1A,0x1A,0x1A); GREY=RGBColor(0x55,0x55,0x55); RED=RGBColor(0x99,0x22,0x22)
doc=Document(); s=doc.sections[0]
s.top_margin=Cm(1.5); s.bottom_margin=Cm(1.5); s.left_margin=Cm(1.6); s.right_margin=Cm(1.6)
n=doc.styles['Normal']; n.font.name='Calibri'; n.font.size=Pt(9.5); n.font.color.rgb=DARK
n.paragraph_format.space_after=Pt(4); n.paragraph_format.line_spacing=1.03

def shade(c,h):
    tcPr=c._tc.get_or_add_tcPr(); sh=OxmlElement('w:shd')
    sh.set(qn('w:val'),'clear'); sh.set(qn('w:color'),'auto'); sh.set(qn('w:fill'),h); tcPr.append(sh)
def h1(t):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(13); p.paragraph_format.space_after=Pt(3)
    r=p.add_run(t); r.font.size=Pt(12.5); r.bold=True; r.font.color.rgb=TEAL
    pPr=p._p.get_or_add_pPr(); pb=OxmlElement('w:pBdr'); bt=OxmlElement('w:bottom')
    bt.set(qn('w:val'),'single'); bt.set(qn('w:sz'),'6'); bt.set(qn('w:space'),'3'); bt.set(qn('w:color'),'006D77')
    pb.append(bt); pPr.append(pb)
def para(t,size=9.5,italic=False,color=DARK,after=4):
    p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(after)
    r=p.add_run(t); r.font.size=Pt(size); r.italic=italic; r.font.color.rgb=color
def tbl(rows,widths,fs=7.9,secrows=()):
    t=doc.add_table(rows=len(rows),cols=len(rows[0])); t.style='Table Grid'; t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for i,row in enumerate(rows):
        if i in secrows:
            c=t.cell(i,0); c.merge(t.cell(i,len(rows[0])-1)); shade(c,'D6E8E8')
            cp=c.paragraphs[0]; cp.paragraph_format.space_after=Pt(1); cp.paragraph_format.space_before=Pt(1)
            r=cp.add_run(row[0]); r.bold=True; r.font.size=Pt(8.2); r.font.color.rgb=TEAL
            continue
        for j,txt in enumerate(row):
            c=t.cell(i,j); c.width=widths[j]
            if i==0: shade(c,'E8F2F2')
            cp=c.paragraphs[0]; cp.paragraph_format.space_after=Pt(1); cp.paragraph_format.space_before=Pt(1)
            r=cp.add_run(txt); r.font.size=Pt(fs)
            if i==0: r.bold=True; r.font.color.rgb=TEAL
            elif j==0: r.bold=True
    doc.add_paragraph().paragraph_format.space_after=Pt(2)
def box(title,body,fill='FBEAEA',col=RED):
    t=doc.add_table(rows=1,cols=1); t.style='Table Grid'
    c=t.cell(0,0); c.width=Cm(17.8); shade(c,fill)
    cp=c.paragraphs[0]; cp.paragraph_format.space_after=Pt(2)
    r=cp.add_run(title); r.bold=True; r.font.size=Pt(9.5); r.font.color.rgb=col
    p2=c.add_paragraph(); p2.paragraph_format.space_after=Pt(1)
    r2=p2.add_run(body); r2.font.size=Pt(9)
    doc.add_paragraph().paragraph_format.space_after=Pt(3)

p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(0)
r=p.add_run('#BBUS research framework'); r.font.size=Pt(18); r.bold=True; r.font.color.rgb=TEAL
p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(2)
r=p.add_run('Hypotheses, data strategy and the policy recommendation each test produces')
r.font.size=Pt(11); r.font.color.rgb=GREY
p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(8)
r=p.add_run('Models M1 socio-economic and M2 health  ·  CEEW  ·  September 2026')
r.font.size=Pt(8.5); r.italic=True; r.font.color.rgb=GREY

h1('1. The policy question')
para('Indian cities are receiving the largest bus investment since JNNURM through PM e-Bus Sewa, but the appraisal '
     'case rests on farebox revenue, operating cost and in-vehicle time saved. Everything else a bus delivers goes '
     'unpriced, so bus budgets lose to road budgets by default.')
para('This framework asks one question. What is a city bus worth beyond its fares, and what should a government do '
     'differently once that number exists?')
para('The design constraint is fixed. We hold large passive mobile GPS trip data already paid for, and we can field '
     '6,000 household surveys across six cities. The framework is built so that passive data carries everything it '
     'can, and the survey is spent only on what cannot be observed.')

h1('2. The causal chain being tested')
tbl([
 ('Link','What changes','Observed by'),
 ('1','Bus deployment lowers the generalised cost of travel: time, fare, waiting, access walk','Passive traces, GTFS, survey for fare'),
 ('2','Travellers respond: some switch mode, some make trips they otherwise would not','Survey counterfactual, joined to traces'),
 ('3','Aggregate travel changes: vehicle-km by mode, time in traffic, walking, jobs reachable','Passive traces plus GTFS and jobs data'),
 ('4a','Socio-economic outcomes move: spending, employment, women’s mobility, access to services','Survey'),
 ('4b','Health outcomes move: physical activity, pollution exposure, injury risk, stress','Passive plus survey plus secondary records'),
 ('5','Effects become rupees and become a policy instrument','Valuation and appraisal'),
], [Cm(1.1),Cm(8.6),Cm(8.1)])
para('Link 2 is the hinge. It is the only point where passive data and survey must be formally joined, and it is '
     'what allows 6,000 households to speak for six cities.', italic=True, color=GREY)

h1('3. Hypotheses')
para('Thirteen hypotheses. Each is stated so it can fail. The final column is the honest one: what result would '
     'force us to abandon or rewrite the claim.')
tbl([
 ('#','Hypothesis','Data','Test','What would refute it'),
 ('PASSIVE DATA ALONE — testable now, no survey required','','','',''),
 ('H1','A material share of urban motorised travel occurs on corridors with no bus service within walking distance',
  'Passive + GTFS','Share of OD flow falling outside a 500 m stop buffer, ranked by corridor',
  'Unserved share is small, or unserved corridors carry trivial volume'),
 ('H2','Peak congestion on main corridors imposes a large, measurable time cost',
  'Passive','Delay against a free-flow baseline from high-percentile observed speed, by corridor and hour',
  'Peak and off-peak times are close, meaning congestion is not the binding problem'),
 ('H3','Bus network expansion materially raises the number of jobs reachable within 45 minutes, most of all from low-income wards',
  'Passive + GTFS + Economic Census','Cumulative opportunity accessibility, before and after planned corridors',
  'Accessibility gain is small, or accrues mainly to already well-served wards'),
 ('H4','Observed trip lengths sit within single-charge electric bus range',
  'Passive','Cumulative trip length distribution against candidate vehicle ranges',
  'A large share of demand exceeds feasible range, implying depot or opportunity charging'),
 ('H5','A small number of ward pairs carry a disproportionate share of travel, and some cross hazard-prone roads',
  'Passive + hazard maps','Ward-to-ward OD matrix ranked by volume, overlaid on municipal hazard layers',
  'Flows are diffuse, so no corridor is critical enough to prioritise'),
 ('SURVEY REQUIRED — M1 socio-economic','','','',''),
 ('H6','Households with bus access spend less on transport than comparable households without it',
  'Survey','DiD in Group B, cross-sectional regression with controls in Group A',
  'No significant difference, or higher spending among bus-access households'),
 ('H7','That saving is a larger share of income for poorer households',
  'Survey','Vulnerability interaction, and spend as a share of income by tertile',
  'Saving is flat or regressive across income groups'),
 ('H8','A material share of bus trips would not be made at all without the bus',
  'Survey','Descriptive, from the stated counterfactual question',
  'Nearly all riders report an alternative, meaning the bus substitutes rather than enables'),
 ('H9','Bus access is associated with higher female employment and trip-making, concentrated in households without a private vehicle',
  'Survey','Regression on the women-only subsample, interacted with vehicle ownership',
  'No association, or an association that disappears once household income is controlled'),
 ('H10','The current bus subsidy is not captured proportionally by the poorest households',
  'Survey + operator data','Benefit incidence analysis by income decile',
  'Subsidy is proportional or progressive, which would itself be a finding worth reporting'),
 ('SURVEY REQUIRED — M2 health','','','',''),
 ('H11','Bus users accumulate enough additional daily walking to shift health risk measurably',
  'Passive + survey','WHO HEAT on access and egress walking volumes',
  'Walking gain is too small to move the dose-response relationship'),
 ('H12','Mode shift to bus lowers population pollution exposure, even though it may not lower the individual rider’s exposure',
  'Passive + survey + published exposure factors','Comparative risk assessment on the concentration change from avoided vehicle-km',
  'Avoided vehicle-km are too small to change ambient concentration measurably'),
 ('H13','Shifting from two-wheelers to buses lowers injury risk per passenger-km, conditional on safe pedestrian access',
  'Survey + passive + police records','Exposure-adjusted injury model, person-km by mode against crash records',
  'Added pedestrian exposure at stops offsets the in-vehicle safety gain'),
], [Cm(0.9),Cm(5.0),Cm(2.4),Cm(4.6),Cm(4.9)], secrows=(1,7,13))

box('One hypothesis we are deliberately not making a headline',
 'That benefits are significantly LARGER for vulnerable groups, as a tested difference. A subgroup-difference test '
 'needs roughly four times the sample of a main effect, which puts the detectable interaction near 10 to 13 '
 'percentage points at a sample of 6,000. Unless vulnerable households are deliberately over-sampled, H7 and H9 '
 'should be reported as stratified estimates with confidence intervals, not as a significance test. Reporting an '
 'underpowered null would be read as "buses do not help the poor more", which the data cannot support either way.')

doc.add_page_break()

h1('4. Data strategy: passive first, survey for the remainder')
tbl([
 ('Question','Passive GPS','Survey','Decision'),
 ('Where trips happen, and where buses do not go','Complete','Not needed','Passive'),
 ('Travel time, delay, congestion','Complete','Recall is worse than traces','Passive'),
 ('Trip length and time-of-day profile','Complete','Not needed','Passive'),
 ('Jobs and services reachable','With GTFS and jobs data','Not needed','Passive'),
 ('Critical corridors in a disaster','With hazard maps','Not needed','Passive'),
 ('Which mode a trip used','Only after building a classifier','Directly','Survey trains, passive scales'),
 ('What people would do without the bus','Impossible, the choice was never made','Directly','Survey'),
 ('Household transport spending','Impossible','Directly','Survey'),
 ('Employment status','Impossible','Directly','Survey'),
 ('Sex, income, disability of traveller','Impossible, data is anonymous','Directly','Survey'),
 ('Trips people did not make','Impossible, leaves no trace','Directly','Survey'),
 ('Stress, safety, satisfaction','Impossible','Directly','Survey'),
], [Cm(5.4),Cm(4.4),Cm(3.6),Cm(4.4)])
para('The rule that follows: the passive data knows everything about the trip and nothing about the person; the '
     'survey knows everything about the person and less about the trip than the traces do. So the survey stops '
     'asking about trips. The multi-day travel diary, normally the longest and costliest module, is dropped for '
     'most respondents.', italic=True, color=GREY)

box('The blocking dependency',
 'Travel mode is absent from the passive dataset. H12 and H13, and all of M3, require separating a bus trip from a '
 'car trip. Mode must be inferred from the traces using speed, acceleration, stop pattern and route matching '
 'against the GTFS network. That needs a labelled training set, which means a subset of survey respondents must '
 'consent to GPS matching or complete a one-day diary. Budget for it explicitly. Without it, five hypotheses cannot '
 'be tested and the passive data stays descriptive.')

h1('5. Sample, and what it can support')
tbl([
 ('Parameter','Decision','Reason'),
 ('Total sample','6,000 across six cities','Fixed'),
 ('Per city','About 1,000','Fixed'),
 ('Wards per city','40 to 50, at 20 to 25 households each','Bus access is assigned to wards, not households, so power comes from the number of wards. Spreading across 50 wards instead of 25 cuts the detectable effect by about a third at no extra cost'),
 ('Primary specification','Pooled across cities with city fixed effects','A single city detects only about 11 percentage points on employment, which is not a plausible effect size'),
 ('Stratification','Over-sample low income, no vehicle, disabled and elderly','The only way to rescue the equity interaction in H7 and H9'),
 ('Group B panel','450 users and 450 non-users tracked per city','Attrition of 20 to 30 per cent means wave one must recruit above this. Resolve before fielding'),
 ('Detectable effect, pooled','About 5 percentage points on employment; about Rs 140 to 180 per month on spending','At ICC 0.05 with controls'),
], [Cm(3.4),Cm(5.4),Cm(9.0)])

h1('6. Analysis plan')
tbl([
 ('Hypotheses','Method','Output unit'),
 ('H1, H5','Origin-destination overlay on stop buffers and hazard layers','Share of trips, ranked corridor list'),
 ('H2','Marginal external congestion cost from a fitted speed-flow relationship','Person-hours, then Rs crore per year'),
 ('H3','Cumulative opportunity accessibility with distance decay','Per cent of jobs, and persons gaining access'),
 ('H4','Cumulative trip length distribution','Per cent of trips within range'),
 ('H6, H7','Difference-in-differences with household fixed effects (Group B); log-linear cross-section with rich controls (Group A); ward-clustered standard errors','Rs per household per year, Rs crore per year, per cent of income'),
 ('H8','Descriptive on the stated counterfactual','Per cent of trips suppressed'),
 ('H9','Linear probability or logit on the women-only subsample; count model for trip frequency','Percentage points; trips per day'),
 ('H10','Benefit incidence analysis by income decile','Per cent of subsidy by decile'),
 ('H11','WHO HEAT dose-response, monetised at value of statistical life','Deaths averted, Rs crore per year'),
 ('H12, H13','Comparative risk assessment across pathways, with Monte Carlo uncertainty','DALYs averted with intervals'),
 ('All monetised','Cost-benefit analysis with switching values, plus three social return lenses','Benefit-cost ratio, net present value, social return ratio'),
], [Cm(2.6),Cm(8.6),Cm(6.6)])
para('Report the counterfactual mode from the survey against the observed mode split from the classified traces. '
     'Where they disagree, the survey is probably flattering the bus. That comparison is a validity check, and it '
     'belongs in the paper rather than in a footnote.', italic=True, color=GREY)

doc.add_page_break()

h1('7. From finding to policy recommendation')
para('This is the column the framework exists for. Each confirmed hypothesis produces a specific recommendation, '
     'directed at a specific institution, attached to a specific instrument.')
tbl([
 ('From','Recommendation','Who acts','Instrument'),
 ('H1','Allocate bus corridors by measured unserved demand rather than by city population or political weight. Publish the corridor ranking',
  'MoHUA, state transport departments','PM e-Bus Sewa phase two allocation criteria'),
 ('H2','Fund bus priority lanes on the corridors where measured delay is highest, and treat avoided congestion cost as a justification for operating support',
  'Municipal corporations, state transport undertakings','Capital works; operating subsidy case'),
 ('H3','Plan routes to maximise jobs reachable, not only ridership. Adopt an accessibility target alongside the ridership target',
  'State transport undertakings, city planning departments','Comprehensive Mobility Plan targets'),
 ('H4','Proceed with full electrification on these corridors; size charging to the observed trip length distribution rather than to worst-case assumptions',
  'State transport undertakings','Detailed project reports; procurement specification'),
 ('H5','Pre-position fleet and protect the identified critical corridors ahead of monsoon and heat events',
  'Municipal disaster management authorities','City disaster management plan; adaptation finance'),
 ('H6, H7','Set fare and concession policy on measured household burden by income group rather than on uniform fares',
  'State governments, transport undertakings','Fare policy; targeted concession design'),
 ('H8','Treat bus service in underserved wards as social infrastructure, with a coverage obligation rather than a commercial viability test',
  'State governments','Route licensing; viability gap funding'),
 ('H9','Invest in service attributes that women identify as binding, and report female ridership and employment as scheme indicators',
  'Transport undertakings, state women and child development departments','Gender-responsive budgeting; gender-lens investment'),
 ('H10','Redesign subsidy targeting where incidence analysis shows leakage away from the poorest',
  'State finance and transport departments','Subsidy design; direct benefit transfer options'),
 ('H11','Fund footpaths and last-mile access as health expenditure, not as transport decoration',
  'Municipal corporations, health departments','Health-transport convergence funding'),
 ('H12','Accelerate fleet electrification and set cabin air quality standards; present the pollution case at population level, not rider level',
  'MoHUA, state pollution control boards','National Clean Air Programme convergence'),
 ('H13','Mandate centre-lane alignment, prohibit counterflow lanes, and require protected crossings at every stop',
  'MoRTH, Indian Roads Congress, municipal corporations','Design standards; scheme eligibility conditions'),
 ('All','Publish the four-in-one appraisal tool so any city can generate its own investment case in the format GCF, ADB and the World Bank require',
  'CEEW, MoHUA','Open-access tool; project preparation'),
], [Cm(1.6),Cm(8.0),Cm(4.4),Cm(3.8)])

h1('8. What we will not claim')
tbl([
 ('Limit','Why'),
 ('No city-level causal estimates','At 1,000 households per city the detectable effect is implausibly large. Pooled with city fixed effects is the primary specification'),
 ('No significance test on the equity interaction, unless stratified sampling is adopted','Underpowered at 6,000. Stratified estimates with intervals will be reported instead'),
 ('No claim that bus riders breathe less than car occupants','Indian measurements put in-bus particulate levels above air-conditioned cars. The pollution case is made at population level'),
 ('No unconditional road safety claim','Vulnerable road users are the large majority of Indian road deaths and buses are involved in a substantial share. The safety claim is conditional on corridor design'),
 ('No single social return figure presented alone','Valuation choices are contestable. A conventional cost-benefit ratio will be reported alongside, and the value of statistical life will be shown as a band across the published Indian estimates'),
 ('No transfer of international effect sizes','The evidence base is thin for India precisely because transferability is untested. International studies inform design, not results'),
], [Cm(6.4),Cm(11.4)])
para('Committing to these limits before the data arrives is what separates the framework from advocacy, and it is '
     'what CEEW’s independence requires.', italic=True, color=GREY)

h1('9. Sequence')
tbl([
 ('Stage','Action'),
 ('1','Pilot to estimate intra-cluster correlation and wave-to-wave correlation; fix ward counts and resolve the Group B attrition gap'),
 ('2','Test H1 to H5 on passive data alone. These need no survey and produce the first policy output'),
 ('3','Build and validate the mode classifier with GTFS route matching; recruit the labelled subsample'),
 ('4','Finalise the survey instrument around the hypotheses that survive'),
 ('5','Field Group A cross-section and Group B baseline'),
 ('6','Run WHO HEAT for an early health number while the full model is built'),
 ('7','Group B follow-up wave once service has run six to twelve months'),
 ('8','Estimate M1 and M2, monetise, run switching values, publish the tool'),
], [Cm(1.4),Cm(16.4)])

doc.save('BBUS_Research_Framework.docx')
print('saved')
