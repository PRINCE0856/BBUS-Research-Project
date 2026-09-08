from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

TEAL=RGBColor(0x00,0x6D,0x77); DARK=RGBColor(0x1A,0x1A,0x1A); GREY=RGBColor(0x55,0x55,0x55); RED=RGBColor(0x99,0x22,0x22)
BLUE=RGBColor(0x1F,0x4E,0x79); GREEN=RGBColor(0x1E,0x6B,0x3A)
doc=Document(); s=doc.sections[0]
s.top_margin=Cm(1.6); s.bottom_margin=Cm(1.6); s.left_margin=Cm(1.7); s.right_margin=Cm(1.7)
n=doc.styles['Normal']; n.font.name='Calibri'; n.font.size=Pt(10); n.font.color.rgb=DARK
n.paragraph_format.space_after=Pt(5); n.paragraph_format.line_spacing=1.05

def shade(c,h):
    tcPr=c._tc.get_or_add_tcPr(); sh=OxmlElement('w:shd')
    sh.set(qn('w:val'),'clear'); sh.set(qn('w:color'),'auto'); sh.set(qn('w:fill'),h); tcPr.append(sh)
def h1(t,col=TEAL):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(15); p.paragraph_format.space_after=Pt(4)
    r=p.add_run(t); r.font.size=Pt(13.5); r.bold=True; r.font.color.rgb=col
    pPr=p._p.get_or_add_pPr(); pb=OxmlElement('w:pBdr'); bt=OxmlElement('w:bottom')
    bt.set(qn('w:val'),'single'); bt.set(qn('w:sz'),'6'); bt.set(qn('w:space'),'3')
    bt.set(qn('w:color'),'%02X%02X%02X'%(col[0],col[1],col[2]) if isinstance(col,tuple) else '006D77')
    pb.append(bt); pPr.append(pb)
def h2(t):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(10); p.paragraph_format.space_after=Pt(2)
    r=p.add_run(t); r.font.size=Pt(11); r.bold=True; r.font.color.rgb=DARK
def para(t,size=10,italic=False,color=DARK,after=5,bold=False):
    p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(after)
    r=p.add_run(t); r.font.size=Pt(size); r.italic=italic; r.font.color.rgb=color; r.bold=bold

def finding_card(tag, tagcol, finding, use, model, how, need):
    """One finding, results-first: the sentence, then what it's for, then the machinery."""
    t=doc.add_table(rows=5,cols=2); t.style='Table Grid'
    t.alignment=WD_TABLE_ALIGNMENT.CENTER
    labels=['THE FINDING','WHO USES IT, AND FOR WHAT','MODEL','HOW IT IS PRODUCED','DATA NEEDED']
    vals=[finding,use,model,how,need]
    for i,(lab,val) in enumerate(zip(labels,vals)):
        c0=t.cell(i,0); c1=t.cell(i,1); c0.width=Cm(3.6); c1.width=Cm(13.6)
        shade(c0,'EFEFEF')
        if i==0: shade(c1,'FFF6E5')
        p0=c0.paragraphs[0]; p0.paragraph_format.space_after=Pt(1); p0.paragraph_format.space_before=Pt(1)
        r0=p0.add_run(lab); r0.bold=True; r0.font.size=Pt(7.6); r0.font.color.rgb=GREY
        p1=c1.paragraphs[0]; p1.paragraph_format.space_after=Pt(1); p1.paragraph_format.space_before=Pt(1)
        r1=p1.add_run(val); r1.font.size=Pt(9.4 if i==0 else 8.8)
        if i==0: r1.bold=True; r1.font.color.rgb=BLUE
    # tag above
    doc.paragraphs[-1]
    doc.add_paragraph().paragraph_format.space_after=Pt(5)

def tag_line(tag,col):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(8); p.paragraph_format.space_after=Pt(1)
    r=p.add_run(tag); r.bold=True; r.font.size=Pt(9.5); r.font.color.rgb=col

def tbl(rows,widths,fs=8.3):
    t=doc.add_table(rows=len(rows),cols=len(rows[0])); t.style='Table Grid'; t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for i,row in enumerate(rows):
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
    c=t.cell(0,0); c.width=Cm(17.2); shade(c,fill)
    cp=c.paragraphs[0]; cp.paragraph_format.space_after=Pt(2)
    r=cp.add_run(title); r.bold=True; r.font.size=Pt(10); r.font.color.rgb=col
    p2=c.add_paragraph(); p2.paragraph_format.space_after=Pt(1)
    r2=p2.add_run(body); r2.font.size=Pt(9.5)
    doc.add_paragraph().paragraph_format.space_after=Pt(3)

# ===== TITLE =====
p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(0)
r=p.add_run('What #BBUS will be able to say'); r.font.size=Pt(19); r.bold=True; r.font.color.rgb=TEAL
p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(3)
r=p.add_run('The findings first. The model that produces each one, second.')
r.font.size=Pt(11.5); r.font.color.rgb=GREY
p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(9)
r=p.add_run('CEEW  ·  September 2026  ·  Read this before the framework documents')
r.font.size=Pt(8.5); r.italic=True; r.font.color.rgb=GREY

box('Every number in this document is invented',
 'These are the SHAPES of findings, not findings. They exist so a decision-maker can look at a sentence, say '
 '"yes, that is what I want" or "no, that is useless", and only then commit to the model that produces it. Every '
 'illustrative figure sits in an amber cell. Nothing here is an estimate, a forecast or a result, and no figure '
 'comes from any dataset. Do not put a number from this document on a slide.')

para('Two things determine everything that follows.')
para('First, findings split cleanly by data source. Some come from the passive GPS data alone and need no survey at '
     'all. Those are available quickly and cheaply. Others can only come from asking people, and no amount of '
     'passive data will substitute. Knowing which is which is what lets the survey budget go to the right place.')
para('Second, most of the passive-data findings do not need travel mode. That matters, because mode is the one thing '
     'the current dataset lacks. The gap analysis and the congestion work can start now.')

# ===== PART A =====
h1('Part A  ·  What the passive GPS data alone can tell us')
para('No survey. No interviews. In most cases below, not even mode inference. This is what is already paid for.',
     italic=True, color=GREY)

tag_line('A1  ·  The strongest single finding from passive data',GREEN)
finding_card('A1',GREEN,
 'Four in ten motorised trips in the city run on corridors with no bus route within 500 metres of either end.',
 'This is a map of where the demand already is and the bus is not. A state transport undertaking uses it to choose '
 'which corridors to open first. MoHUA uses it as a defensible allocation rule for PM e-Bus Sewa, instead of '
 'allocating by city population or by who lobbies hardest. It is the most directly actionable thing the project '
 'can produce.',
 'M1, network gap and accessibility component.',
 'Overlay the origin-destination flows from the traces onto a 500 metre buffer around every existing bus stop from '
 'the GTFS feed. Count the trip volume that falls outside it, and rank the unserved corridors by volume.',
 'Passive traces plus the GTFS route and stop file. No survey. No mode inference.')

tag_line('A2  ·  The congestion number',GREEN)
finding_card('A2',GREEN,
 'Peak-hour trips on the ten busiest corridors take 61 per cent longer than the same trip off-peak. The city loses '
 '2.9 crore person-hours a year to that delay.',
 'This is the decongestion benefit in the cost-benefit analysis, and separately the argument for bus priority '
 'lanes. Person-hours converts directly into rupees once a value of time is applied, which is the number a finance '
 'department responds to.',
 'M1, marginal external congestion cost.',
 'Compute trip duration and average speed by time bucket for each corridor from the traces, take the off-peak '
 'time as free-flow, and apply the standard road performance function to get the delay each additional vehicle '
 'imposes on the rest.',
 'Passive traces only. No survey. No mode inference.')

tag_line('A3  ·  The accessibility number, and the most comparable one',GREEN)
finding_card('A3',GREEN,
 'The bus network puts 31 per cent of the city’s jobs within 45 minutes of the average resident. Opening three '
 'corridors would raise that to 58 per cent, and 212,000 people would gain access.',
 'This is the strongest number in M1 because nothing about it is self-reported, so nobody can dispute it as survey '
 'bias. It is also directly comparable to World Bank city benchmarks, which lets BBUS place Indian cities on an '
 'international scale. Climate funds ask for "number of vulnerable people benefited" and this answers it.',
 'M1, accessibility component.',
 'Route every ward-to-ward pair on the GTFS network, count jobs reachable inside a time threshold, weight by '
 'distance decay, then re-run with the planned corridors added.',
 'GTFS plus ward employment from the Economic Census. Passive traces improve the travel times. No survey.')

tag_line('A4  ·  The finding that removes a procurement objection',GREEN)
finding_card('A4',GREEN,
 'Seventy-eight per cent of trips are under 12 kilometres and 96 per cent under 25. The entire demand pattern sits '
 'inside a single-charge electric bus range.',
 'It kills the range-anxiety objection to electrification before it is raised, and it sizes the charging '
 'infrastructure. Useful to a state transport undertaking writing a detailed project report, and to M3.',
 'M3, and the cost side of the appraisal.',
 'Trip length distribution from the traces, plotted as a cumulative curve against candidate vehicle ranges.',
 'Passive traces only. No survey. No mode inference.')

tag_line('A5  ·  The exposure number that feeds the health model',GREEN)
finding_card('A5',GREEN,
 'The average commuter spends 47 minutes a day inside traffic. On the worst corridor it is 82 minutes.',
 'This is the denominator of the air pollution exposure calculation in M2. Combined with published Indian per-mode '
 'concentration factors, it gives an exposure estimate without buying a single monitor.',
 'M2, air pollution pathway.',
 'Sum trip duration per device per day from the traces, and break it down by corridor and time of day.',
 'Passive traces only. Published exposure factors from existing Indian studies. No survey, no monitors.')

tag_line('A6  ·  The resilience finding',GREEN)
finding_card('A6',GREEN,
 'Seven ward pairs carry 34 per cent of all inter-ward trips. Four of those routes cross flood-prone roads.',
 'It tells a municipal disaster management office which corridors to protect and where to stage buses before a '
 'monsoon event. This is the concrete form of M4, and it is the kind of output that gets a city a hearing at an '
 'adaptation fund.',
 'M4, resilience and adaptation.',
 'Build the ward-to-ward origin-destination matrix from the traces, rank pairs by volume, then overlay municipal '
 'hazard maps.',
 'Passive traces plus ward boundaries and hazard maps. No survey.')

tag_line('A7  ·  Only if operator fleet GPS can be obtained',GREEN)
finding_card('A7',GREEN,
 'Actual headway on route 12 varies by plus or minus 7 minutes against a 12-minute published schedule.',
 'Unreliability suppresses ridership independently of average frequency, and Indian evidence for that effect exists '
 'but is thin. Quantifying it would be a genuine research contribution, and operationally it tells an operator '
 'that fixing reliability may buy more riders than adding buses.',
 'M1 demand side, and a candidate standalone paper.',
 'Compare arrival times from operator automatic vehicle location data against the published schedule, and relate '
 'the variability to boardings by stop.',
 'Operator fleet GPS or automatic vehicle location data, which the project does not currently hold. Worth asking for.')

box('The one thing to take from Part A',
 'The demand-supply gap map, finding A1. It requires no survey, no mode inference and no new data purchase, and it '
 'answers the only question a transport department actually has to decide: where do the buses go. Everything else '
 'in the project explains why buses are worth it. A1 says where. Lead with it.',
 fill='E8F5EC', col=GREEN)

box('What the passive data cannot do in its current state',
 'Nothing above needs travel mode except A7. But the moment a finding compares a bus trip with a car trip, mode '
 'becomes essential, and the dataset does not have it. That rules out modal shift, avoided vehicle-kilometres, '
 'mode-specific exposure and injury risk by mode until a classifier is built and validated. Those four are the '
 'core of M2 and M3, which is why mode inference is the top technical priority.')

doc.add_page_break()

# ===== PART B =====
h1('Part B  ·  What only the survey can tell us')
para('No amount of passive data substitutes for these. Each one is a question that has to be asked of a person.',
     italic=True, color=GREY)

tag_line('B1  ·  The single most important question in the whole survey',BLUE)
finding_card('B1',BLUE,
 'Without the bus, 38 per cent of current riders would use a two-wheeler, 24 per cent an auto-rickshaw, 17 per cent '
 'would walk, and 21 per cent would not make the trip at all.',
 'Everything depends on this. Avoided vehicle-kilometres in M3 come from it. The change in pollution exposure and '
 'injury risk in M2 come from it. The suppressed-trip equity finding in M1 comes from it. Without a counterfactual '
 'mode there is no counterfactual at all, and every benefit number in the project collapses to a description of '
 'who rides the bus.',
 'Feeds M1, M2 and M3. It is the hinge of the entire framework.',
 'A direct stated-preference question, asked of every bus user, about what they would do on the same trip if the '
 'bus did not run. Cross-checked against the observed mode split from the traces.',
 'Survey only. Nothing in the passive data can reveal a choice that was never made.')

tag_line('B2  ·  The most quotable finding in the project',BLUE)
finding_card('B2',BLUE,
 'Bus-using households spend Rs 2,568 a year less on transport than comparable non-using households. For the '
 'poorest third, that saving is 6.4 per cent of household income.',
 'This is money in a household’s pocket, and it is the sentence that travels furthest in a press release or a '
 'minister’s speech. It is also the affordability argument for continuing the subsidy, and it feeds the household '
 'savings line of the social return calculation.',
 'M1, household expenditure outcome.',
 'Regression of monthly transport spending on a bus-access indicator with household controls in Group A, and '
 'difference-in-differences across the two waves in Group B.',
 'Survey only. Expenditure is not observable in trip traces.')

tag_line('B3  ·  The equity headline',BLUE)
finding_card('B3',BLUE,
 'One in five bus trips would not happen at all if there were no bus.',
 'This converts the bus from a convenience into a precondition for economic and social participation. It is the '
 'strongest available answer to "why not just let people use two-wheelers", and it is the finding that justifies '
 'treating bus investment as social protection rather than as transport spending.',
 'M1, and it reframes the whole narrative.',
 'Derived from the same counterfactual question as B1, isolating the share who answer that they would not travel.',
 'Survey only.')

tag_line('B4  ·  The gender finding',BLUE)
finding_card('B4',BLUE,
 'Women in bus-access wards are 4.8 percentage points more likely to be employed, and the effect is concentrated in '
 'households with no private vehicle.',
 'This is what unlocks gender-lens investment, corporate social responsibility funding and state social protection '
 'budgets, none of which respond to a transport argument but all of which respond to a female employment argument. '
 'It is also the finding with the most international precedent, from Lima and from the Indian fare-free schemes.',
 'M1, female employment outcome, estimated on the women-only subsample.',
 'Binary employment regression on bus access with controls, restricted to women, with the vulnerability '
 'interaction. Note that the interaction is underpowered at a sample of 6,000 unless vulnerable households are '
 'deliberately over-sampled.',
 'Survey only.')

tag_line('B5  ·  The finding that makes every other number credible',BLUE)
finding_card('B5',BLUE,
 'Sixty-two per cent of riders are in the bottom two income tertiles, 48 per cent are women, and 11 per cent report '
 'a disability.',
 'On its own this is just a description. Its value is that it lets every other finding in the project be broken '
 'down by who benefits. The Green Climate Fund and the Asian Development Bank both require benefits reported by '
 'vulnerable group, and without this block none of the other numbers can be disaggregated at all.',
 'All four models. It is the disaggregation layer.',
 'Standard socio-demographic module, plus the four-part vulnerability index covering income, vehicle ownership, '
 'disability and elderly status.',
 'Survey only. Passive traces are anonymous by design and carry no demographics.')

tag_line('B6  ·  The finding that brings in the health ministry',BLUE)
finding_card('B6',BLUE,
 'Thirteen per cent of households delayed or skipped a healthcare visit because of transport difficulty. Nine per '
 'cent of school-going children missed days for the same reason.',
 'This is what makes a health department or an education department co-finance a bus scheme, because it is stated '
 'in their own outcome language rather than in transport language. It is the practical basis for the '
 'health-transport convergence funding named in the project design.',
 'M1 descriptive, and it supports the M2 investment case.',
 'Direct recall questions over a three-month window, reported descriptively on the bus-using subsample rather than '
 'by regression, because the meaningful subsample is self-selected.',
 'Survey only.')

tag_line('B7  ·  The service design finding',BLUE)
finding_card('B7',BLUE,
 'At identical trip attributes, women report 1.4 times the odds of high commute stress. Crowding is the largest '
 'single stressor, ahead of waiting time and journey length.',
 'It tells an operator what to fix first, and it is the fourth health pathway in M2. It also gives the safety and '
 'dignity argument a number, which it usually lacks.',
 'M2, commute stress pathway.',
 'Ordered logit on a five-point stress scale against trip attributes, service quality items and demographics.',
 'Survey only.')

tag_line('B8  ·  The fare policy finding',BLUE)
finding_card('B8',BLUE,
 'Riders would pay Rs 6 more per trip for a five-minute headway, but only Rs 4 more for a guaranteed seat.',
 'It tells the operator and the state where fare revenue can realistically come from, and which service '
 'improvement buys the most goodwill per rupee. It also supplies the stated-preference half of the choice model.',
 'M1 demand side, and the joint estimation with the passive data.',
 'A short stated-choice block with fare, headway, crowding and access time as attributes, estimated as a '
 'multinomial or mixed logit.',
 'Survey only, and it is the piece that formally joins the survey to the passive data.')

box('The one thing to take from Part B',
 'The counterfactual question, finding B1. Ask every bus user what they would do on that same trip if the bus did '
 'not run. It is one question. It produces the modal shift that drives M3, the exposure and injury change that '
 'drives M2, and the suppressed-trip finding that drives the equity narrative in M1. If the instrument had to be '
 'cut to a single question, this is the one to keep.',
 fill='EAF0F8', col=BLUE)

doc.add_page_break()

# ===== PART C =====
h1('Part C  ·  Passive versus survey, side by side')
tbl([
 ('What we want to know','Passive GPS','Survey','Verdict'),
 ('Where trips happen, and where buses do not go','Yes, completely','Not needed','Passive wins outright'),
 ('How long trips take, and how much delay','Yes, completely','Worse than traces, recall is poor','Passive wins outright'),
 ('Trip length and time-of-day profile','Yes, completely','Not needed','Passive wins outright'),
 ('Jobs and services reachable','Yes, with GTFS and jobs data','Not needed','Passive wins outright'),
 ('Which corridors are critical in a disaster','Yes, with hazard maps','Not needed','Passive wins outright'),
 ('Which mode a trip used','Only after building a classifier','Yes, directly','Survey trains, passive scales'),
 ('What people would do without the bus','No. The choice was never made','Yes','Survey only'),
 ('What households spend on transport','No','Yes','Survey only'),
 ('Whether someone is employed','No','Yes','Survey only'),
 ('Who the traveller is: sex, income, disability','No, anonymous by design','Yes','Survey only'),
 ('Trips people did not make','No, an absent trip leaves no trace','Yes','Survey only'),
 ('Stress, safety, satisfaction','No','Yes','Survey only'),
 ('Willingness to pay for service change','No','Yes','Survey only'),
], [Cm(6.0),Cm(3.8),Cm(3.6),Cm(3.8)])
para('The pattern is simple enough to state in one line. The passive data knows everything about the trip and '
     'nothing about the person. The survey knows everything about the person and less about the trip than the traces '
     'do. Design the survey to stop asking about trips.', italic=True, color=GREY)

# ===== PART D =====
h1('Part D  ·  M1 framework, reverse-engineered from the findings')
para('Read this table from the left. Start with the finding the project wants to be able to state, and the method '
     'and data fall out of it.')
tbl([
 ('The finding we want (Part A/B ref)','Indicator','Method','Data source'),
 ('Households save money (B2)','Monthly transport expenditure, Rs','Cross-sectional regression with controls, Group A; two-wave difference-in-differences, Group B','Survey'),
 ('Bus enables trips that would not happen (B3)','Share of trips suppressed without bus','Descriptive, from the counterfactual question','Survey'),
 ('Women work more (B4)','Employment, binary, women-only subsample','Regression on bus access with vulnerability interaction','Survey'),
 ('Women move more (B4)','Daily out-of-home trips by women in vehicle-less households','Count regression','Survey'),
 ('Buses reach jobs (A3)','Jobs within 45 and 60 minutes, and population gaining access','Network routing with distance decay','GTFS, Economic Census, traces for travel time'),
 ('Time is saved (A2)','Person-hours of delay, and its rupee value','Delay from off-peak baseline, valued at a value of travel time','Traces, plus survey income to set the value'),
 ('Roads are less congested (A2)','Marginal external congestion cost per vehicle-km','Road performance function on observed flow and speed, with passenger car equivalents','Traces, plus survey counterfactual mode'),
 ('The city is more productive','Effective density, and welfare uplift','Employment weighted by generalised travel cost, times an agglomeration elasticity','Traces for the cost matrix, Economic Census, PLFS'),
 ('The subsidy reaches the poor','Subsidy received by income decile','Incidence analysis','Survey plus operator fare and subsidy data'),
 ('Buses go where demand is not served (A1)','Unserved trip volume by corridor','Origin-destination overlay on stop buffers','Traces plus GTFS'),
], [Cm(4.6),Cm(3.8),Cm(5.0),Cm(3.8)])

h1('Part E  ·  M2 framework, reverse-engineered from the findings')
tbl([
 ('The finding we want','Indicator','Method','Data source'),
 ('Bus users walk more, and it saves lives','Extra walking minutes per day; deaths averted; rupee value','WHO HEAT dose-response on walking volume, monetised at a value of statistical life','Traces for access and egress distance; survey for habits; published dose-response'),
 ('Fewer vehicles means cleaner air','Population PM2.5 reduction; years of life lost averted','Comparative risk assessment on the concentration change from avoided vehicle-km','Survey counterfactual mode (B1), traces, published Indian exposure factors'),
 ('Riders are exposed while commuting (A5)','Time in traffic; inhaled dose by mode','Time in mode from traces, times published per-mode concentration','Traces, published factors. No monitors needed'),
 ('Shifting off two-wheelers avoids injury','Injuries and deaths averted','Exposure-adjusted injury model: person-km by mode against crash records','Survey counterfactual mode, traces for exposure, police records'),
 ('Walking to stops carries its own risk','Pedestrian injury exposure near stops','Road safety rating of access routes, combined with crash locations','GIS, crash records, stop locations'),
 ('Buses reduce commute stress (B7)','Odds of reporting high stress','Ordered logit on trip attributes, service quality and demographics','Survey only'),
 ('Health benefit is largest for the poorest','Years of life lost averted per 100,000, by income, sex, disability','Disaggregation of the comparative risk assessment using survey weights','Survey demographics (B5) plus all of the above'),
 ('The health value in rupees','Rupee value per year, reported as a band','Value of statistical life and avoided treatment cost, run at both published Indian estimates','Published valuation studies, health system unit costs'),
], [Cm(4.6),Cm(3.8),Cm(5.0),Cm(3.8)])

h1('Part F  ·  How to use this in the meeting')
tbl([
 ('Step','What to do'),
 ('1','Put Part A and Part B in front of them. Fifteen findings, each one sentence. Ask which ones they want to be able to say.'),
 ('2','Expect them to strike some out. That is the point. A finding nobody wants is a survey module you do not pay for.'),
 ('3','For the ones they keep, Parts D and E give the method and the data. That is the framework, derived rather than asserted.'),
 ('4','Flag the two dependencies. Nothing in M2 or M3 works without the counterfactual question B1. Nothing comparing modes works until mode inference is built.'),
 ('5','Lead with A1, the gap map. It needs no survey, it can start now, and it answers the question a transport department actually has to decide.'),
], [Cm(1.4),Cm(15.8)])

doc.save('BBUS_Findings_First_M1_M2.docx')
print('saved')
