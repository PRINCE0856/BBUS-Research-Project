from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

TEAL=RGBColor(0x00,0x6D,0x77); DARK=RGBColor(0x1A,0x1A,0x1A); GREY=RGBColor(0x55,0x55,0x55)
doc=Document()
s=doc.sections[0]
s.top_margin=Cm(1.8); s.bottom_margin=Cm(1.8); s.left_margin=Cm(2.0); s.right_margin=Cm(2.0)
n=doc.styles['Normal']; n.font.name='Calibri'; n.font.size=Pt(10); n.font.color.rgb=DARK
n.paragraph_format.space_after=Pt(5); n.paragraph_format.line_spacing=1.05

def shade(cell,hexcol):
    tcPr=cell._tc.get_or_add_tcPr(); sh=OxmlElement('w:shd')
    sh.set(qn('w:val'),'clear'); sh.set(qn('w:color'),'auto'); sh.set(qn('w:fill'),hexcol); tcPr.append(sh)

def h1(t):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(14); p.paragraph_format.space_after=Pt(4)
    r=p.add_run(t); r.font.size=Pt(13); r.bold=True; r.font.color.rgb=TEAL
    pPr=p._p.get_or_add_pPr(); pb=OxmlElement('w:pBdr'); bt=OxmlElement('w:bottom')
    bt.set(qn('w:val'),'single'); bt.set(qn('w:sz'),'6'); bt.set(qn('w:space'),'3'); bt.set(qn('w:color'),'006D77')
    pb.append(bt); pPr.append(pb)

def para(t,size=10,italic=False,color=DARK,after=5):
    p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(after)
    r=p.add_run(t); r.font.size=Pt(size); r.italic=italic; r.font.color.rgb=color
    return p

def tbl(rows,widths,fs=8.6):
    t=doc.add_table(rows=len(rows),cols=len(rows[0])); t.style='Table Grid'
    t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for i,row in enumerate(rows):
        for j,txt in enumerate(row):
            c=t.cell(i,j); c.width=widths[j]
            cp=c.paragraphs[0]; cp.paragraph_format.space_after=Pt(1); cp.paragraph_format.space_before=Pt(1)
            r=cp.add_run(txt); r.font.size=Pt(fs)
            if i==0: r.bold=True; r.font.color.rgb=TEAL; shade(c,'E8F2F2')
            elif j==0: r.bold=True
    doc.add_paragraph().paragraph_format.space_after=Pt(2)

# TITLE
p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(0)
r=p.add_run('#BBUS at a glance'); r.font.size=Pt(18); r.bold=True; r.font.color.rgb=TEAL
p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(10)
r=p.add_run('Every model, method and data source in one place  ·  CEEW  ·  September 2026')
r.font.size=Pt(9); r.italic=True; r.font.color.rgb=GREY

h1('1. The project in three lines')
para('BBUS measures what a city bus system is worth beyond fares and ridership.')
para('It builds four models covering socio-economic, health, climate and resilience benefits, then converts them '
     'into a rupee value.')
para('The output is a pre-investment appraisal tool and a social return on investment framework that cities can use '
     'to defend budgets and apply for climate finance.')

h1('2. The four co-benefit models')
tbl([
 ('Model','What it measures','Main method','Key outputs'),
 ('M1\nSocio-economic','Money and opportunity gains, especially for women, low-income and vulnerable road users',
  'Difference-in-differences (Group B), cross-sectional regression with controls (Group A), vulnerability index interaction',
  'Household transport spend saved, female employment, women’s trip frequency, time saved, jobs reachable, decongestion value, agglomeration value'),
 ('M2\nHealth','Health value of shifting from two-wheelers, cars and autos to buses',
  'Comparative risk assessment (ITHIM), with WHO HEAT for the walking pathway',
  'DALYs averted, walking gained, PM2.5 exposure avoided, road injuries avoided, commute stress reduced, treatment costs saved'),
 ('M3\nGHG','Carbon avoided by bus deployment',
  'Bottom-up emissions model on ITF-OECD and UNFCCC lines, with scenario analysis',
  'Vehicle-km avoided, tonnes CO2e per year, scenario range by grid mix and charging pattern'),
 ('M4\nResilience','What the bus network is worth during floods, heat and disruption',
  'GIS disaster routing, economic resilience comparison, infrastructure downtime analysis',
  'Economic downtime avoided, evacuation time saved, infrastructure damage and restart cost by mode'),
], [Cm(2.5),Cm(3.6),Cm(4.6),Cm(6.3)])

h1('3. The cities')
tbl([
 ('Group','Cities','Why','Design used'),
 ('Group A\nBuses already running','Bengaluru, Jaipur, Bhubaneswar','Mature systems. No pre-bus baseline exists',
  'Cross-sectional regression with rich controls. Bus access is a 500 metre walkshed of a stop'),
 ('Group B\nBuses arriving','Jodhpur, Haridwar, Gaya, Bilaspur, Tirupati, Puducherry, Gandhinagar (final list with MoHUA)',
  'PM e-Bus Sewa rollout is staggered, so it works as a natural experiment',
  'Two-wave panel difference-in-differences. Survey before deployment, again after service stabilises'),
], [Cm(3.4),Cm(4.6),Cm(4.4),Cm(4.6)])

h1('4. The sample')
tbl([
 ('Item','Number'),
 ('Total respondents','6,000'),
 ('Cities','6'),
 ('Per city','About 1,000'),
 ('Group B longitudinal cohort per city','About 450 bus users and 450 non-users'),
 ('Wards per city, recommended','40 to 50, at 20 to 25 households each'),
 ('Primary specification','Pooled across cities with city fixed effects'),
 ('Not feasible','Separate city-level estimates, and the vulnerability interaction unless the sample is stratified'),
], [Cm(7.0),Cm(10.0)])
para('Why more wards: bus access is defined geographically, so the treatment is assigned to wards rather than '
     'households. Spreading the same 1,000 households across 50 wards instead of 25 cuts the smallest detectable '
     'effect by about a third at no extra cost.', italic=True, color=GREY)

doc.add_page_break()

h1('5. The statistical methods, in plain terms')
tbl([
 ('Method','What it does','Where it is used'),
 ('Difference-in-differences','Compares the before-and-after change for people who got the bus against the change for people who did not. The difference between the two changes is the effect of the bus','M1 and M2, Group B cities'),
 ('Triple difference','Adds a second comparison, such as cities that got buses at different dates. More robust than plain difference-in-differences','M1, if the staggered rollout allows'),
 ('Cross-sectional regression with rich controls','Compares households near a stop with households far from one at a single point in time, holding other differences constant','M1 and M2, Group A cities'),
 ('Vulnerability index interaction','Puts a four-part index of income, vehicle ownership, disability and elderly status into the equation as an interaction, so differential benefit is a direct coefficient','Every M1 regression'),
 ('Discrete choice model (logit, nested logit, mixed logit)','Models how a traveller picks between bus, two-wheeler, car and auto given time, cost and comfort','Modal shift, feeds M2 and M3'),
 ('Joint revealed and stated preference estimation','Formally combines what people actually did (GPS traces) with what they say they would do (survey). A scale parameter stops survey hypothetical bias contaminating the result','The join between passive data and survey. The key method of the project'),
 ('Demand elasticity','How much ridership changes when fare or service frequency changes','Cross-check on the choice model, and scenario analysis'),
 ('Comparative risk assessment (ITHIM)','Converts changes in walking, pollution exposure and injury risk into deaths and years of life lost','M2, the main health model'),
 ('WHO HEAT','Converts extra walking into avoided deaths and a money value. Much lighter data need than ITHIM','M2, the walking pathway. Run this first'),
 ('Ordered logit or probit','Analyses ranked survey answers such as stress level, perceived safety and satisfaction','M2, the commute stress pathway'),
 ('GIS accessibility analysis','Counts jobs, schools and clinics reachable within 45 or 60 minutes by bus','M1, and the strongest single non-self-reported number available'),
 ('Marginal external congestion cost','Values the delay each extra vehicle imposes on everyone else, using the standard road performance function','M1, decongestion benefit'),
 ('Effective density and agglomeration','Values the productivity gain from a bigger reachable labour market, following the UK wider economic impacts approach','M1, wider economic benefit'),
 ('Four-step travel demand model','Trip generation, distribution, mode choice and assignment. The traditional transport planning structure','Network assignment feeding M3 and congestion. Not the centrepiece'),
 ('Iterative proportional fitting','Reweights a small survey so it matches census totals, creating a synthetic population for the whole city','Expanding 6,000 households to city scale'),
 ('Multilevel regression and poststratification','Corrects passive data for over-representing smartphone owners','Bias correction on the GPS dataset'),
 ('GPS mode classification','Infers travel mode from speed, acceleration, stop pattern and route matching against the bus network','Unlocks the passive data for M1, M2 and M4'),
 ('Cost-benefit analysis','Compares monetised benefits with costs. Gives a benefit-cost ratio and net present value','The finance-facing result'),
 ('Social return on investment','Stakeholder-driven valuation of social outcomes per rupee invested','The policy-facing result. Report alongside cost-benefit analysis, never alone'),
 ('Switching values and Monte Carlo','Tests how far each assumption must move before the conclusion flips, and samples across uncertainty ranges','Sensitivity analysis for every model'),
], [Cm(4.0),Cm(7.4),Cm(5.6)])
para('Structural equation modelling was considered for M1 and set aside. It recovers hidden constructs such as '
     'perceived safety, whereas M1 measures things that are directly observable. It remains useful in M2 for '
     'service quality and stress.', italic=True, color=GREY)

doc.add_page_break()

h1('6. Where the data comes from')
tbl([
 ('Source','What it gives','Used by'),
 ('Passive mobile GPS traces','Origin and destination, trip length, duration, speed, route path, time of day','M1 travel time and congestion, M2 exposure duration, M3 vehicle-km, M4 baseline mobility'),
 ('Primary household and commuter survey','Gender, age, income, disability, vehicle ownership, expenditure, employment, health, stress, counterfactual questions, stated preference','M1 and M2. Everything that requires knowing something about a person'),
 ('In-depth interviews and focus groups','Thematic priorities, lived experience, instrument design','Precedes and shapes the survey'),
 ('GIS and GTFS','Bus routes, stops, headways, walksheds, ward boundaries, hazard maps','M1 accessibility, M2 exposure mapping, M4 routing, and mode classification'),
 ('Census, PLFS, Economic Census','Ward population, employment, gross value added, income distribution','M1 agglomeration and survey expansion weights'),
 ('Air quality networks and published exposure factors','Concentrations, and per-mode exposure already measured in Delhi, Mumbai, Chennai and Kanpur','M2 pollution pathway. Avoids buying monitors'),
 ('Police and health records, Global Burden of Disease','Crashes, injuries, baseline mortality by cause and age','M2 injury and disease burden'),
 ('Operator and scheme data','Ridership, fares, subsidy, fleet, PM e-Bus Sewa detailed project reports','All four models, and subsidy incidence analysis'),
], [Cm(4.0),Cm(6.6),Cm(6.4)])

h1('7. Tools')
tbl([
 ('Tool','Purpose'),
 ('ITHIM / ITHIM-Global','Main health impact model for M2'),
 ('WHO HEAT','Walking benefit, monetised. Lightest and fastest'),
 ('WHO AirQ+ and BenMAP-CE','Air pollution health burden and valuation'),
 ('QGIS','Catchments, accessibility, exposure surfaces, crash hotspots'),
 ('iRAP / ViDA','Road safety rating of walking routes around stops'),
 ('R or Stata','Regression, difference-in-differences, discrete choice, ordered response, structural equation models'),
], [Cm(5.0),Cm(12.0)])

h1('8. What the project delivers')
tbl([
 ('Output','Description'),
 ('Pre-investment appraisal tool','Open access and online. A city official enters fleet size, population, modal share and grid emission factor, and gets projected GHG savings, health co-benefits, a social return ratio, eligible finance instruments and a monitoring dashboard. Formatted to meet GCF, ADB and World Bank project preparation requirements'),
 ('Healthy Cities SROI framework','Three lenses on the same dataset. For government, the societal return per rupee of public spend. For climate and development finance, structured to GCF and ADB results frameworks. For private capital, co-benefits sized as a payment security mechanism'),
 ('Evidence base','First multi-city Indian quantification of bus co-benefits, addressing a literature where only one of twenty-seven socio-economic studies and five of thirty-nine health studies come from comparable settings'),
], [Cm(4.6),Cm(12.4)])

h1('9. Open items')
tbl([
 ('Item','Status'),
 ('Travel mode missing from passive data','Blocks M1, M2 and M4. Fix by inferring mode from traces plus route matching against the bus network. Needs a labelled subsample from the survey'),
 ('Vulnerability interaction underpowered','Needs stratified over-sampling of low-income, no-vehicle, disabled and elderly households, or a binary split instead of a four-part index'),
 ('Ward spread not yet fixed','Move to 40 to 50 wards per city. Free improvement in precision'),
 ('Pilot not yet run','Needs to produce the intra-cluster correlation and the wave-to-wave correlation before ward counts are final'),
 ('Group B city list','To be finalised with MoHUA against PM e-Bus Sewa deployment timelines'),
 ('Literature not yet verified','All sources gathered so far were found by search only. Each must be opened and read before use'),
], [Cm(5.2),Cm(11.8)])

doc.save('BBUS_At_A_Glance.docx')
print('saved')
