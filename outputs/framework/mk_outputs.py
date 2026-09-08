from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

TEAL=RGBColor(0x00,0x6D,0x77); DARK=RGBColor(0x1A,0x1A,0x1A); GREY=RGBColor(0x55,0x55,0x55)
RED=RGBColor(0x99,0x22,0x22)
DUMMY_FILL='FFF6E5'   # every illustrative table gets this fill

doc=Document()
s=doc.sections[0]
s.top_margin=Cm(1.7); s.bottom_margin=Cm(1.7); s.left_margin=Cm(1.9); s.right_margin=Cm(1.9)
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

def h2(t):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(10); p.paragraph_format.space_after=Pt(2)
    r=p.add_run(t); r.font.size=Pt(11); r.bold=True; r.font.color.rgb=DARK

def para(t,size=10,italic=False,color=DARK,after=5,bold=False):
    p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(after)
    r=p.add_run(t); r.font.size=Pt(size); r.italic=italic; r.font.color.rgb=color; r.bold=bold
    return p

def eq(t):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(4); p.paragraph_format.space_after=Pt(5)
    p.paragraph_format.left_indent=Cm(0.6)
    r=p.add_run(t); r.font.name='Consolas'; r.font.size=Pt(9); r.font.color.rgb=RGBColor(0x22,0x44,0x66)
    r._element.rPr.rFonts.set(qn('w:eastAsia'),'Consolas')

def dummy_table(caption, rows, widths, fs=8.4):
    """Illustrative table: amber fill, ILLUSTRATIVE tag, caption below."""
    p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(1); p.paragraph_format.space_before=Pt(6)
    r=p.add_run('ILLUSTRATIVE OUTPUT — numbers are placeholders to show format only')
    r.font.size=Pt(7.5); r.bold=True; r.font.color.rgb=RED
    t=doc.add_table(rows=len(rows),cols=len(rows[0])); t.style='Table Grid'
    t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for i,row in enumerate(rows):
        for j,txt in enumerate(row):
            c=t.cell(i,j); c.width=widths[j]; shade(c, 'F5E3C3' if i==0 else DUMMY_FILL)
            cp=c.paragraphs[0]; cp.paragraph_format.space_after=Pt(1); cp.paragraph_format.space_before=Pt(1)
            rr=cp.add_run(txt); rr.font.size=Pt(fs)
            if i==0: rr.bold=True
            elif j==0: rr.bold=True
    p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(6)
    r=p.add_run(caption); r.font.size=Pt(8); r.italic=True; r.font.color.rgb=GREY

def real_table(rows,widths,fs=8.6):
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

def warnbox(title,body):
    t=doc.add_table(rows=1,cols=1); t.style='Table Grid'
    c=t.cell(0,0); c.width=Cm(17.2); shade(c,'FBEAEA')
    cp=c.paragraphs[0]; cp.paragraph_format.space_after=Pt(2)
    r=cp.add_run(title); r.bold=True; r.font.size=Pt(10); r.font.color.rgb=RED
    p2=c.add_paragraph(); p2.paragraph_format.space_after=Pt(1)
    r2=p2.add_run(body); r2.font.size=Pt(9.5)
    doc.add_paragraph().paragraph_format.space_after=Pt(3)

# ============ TITLE ============
p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(0)
r=p.add_run('#BBUS model outputs'); r.font.size=Pt(18); r.bold=True; r.font.color.rgb=TEAL
p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(8)
r=p.add_run('What each model produces, with the equation that produces it and a worked example of the output table  ·  CEEW  ·  September 2026')
r.font.size=Pt(9); r.italic=True; r.font.color.rgb=GREY

warnbox('Every number in this document is invented',
 'The tables below are format mock-ups. They exist so the team, and anyone being briefed, can see the shape of the '
 'result before the data is collected. No figure here is an estimate, a forecast or a finding, and none is drawn '
 'from any real dataset. Every illustrative table is shaded amber and carries a red tag. Do not lift a number from '
 'this document into a presentation, a proposal or a report.')

# ============ M1 ============
h1('M1  Socio-economic co-benefits')
h2('What is estimated')
para('Group A, cross-section with rich controls. Bus access is a binary indicator for living within a 500 metre '
     'walkshed of an operational stop.')
eq('Y_i  =  α  +  β₁·BusAccess_i  +  β₂·VI_i  +  β₃·(BusAccess_i × VI_i)  +  γ′X_i  +  δ_city  +  ε_i')
para('Group B, two-wave panel difference-in-differences. Post is the wave after buses begin operating.')
eq('Y_it =  α  +  β₁·Post_t  +  β₂·(Post_t × BusAccess_i)  +  β₃·(Post_t × BusAccess_i × VI_i)  +  γ′X_it  +  μ_i  +  ε_it')
para('β₂ is the average treatment effect on the treated. β₃ is the differential effect along the vulnerability '
     'index, which is the equity coefficient. Standard errors clustered at ward level throughout.')

h2('Output 1: the main regression table')
dummy_table('Table M1.1. Effect of bus access on household outcomes. This is the table that goes in the paper. '
            'Cluster-robust standard errors in parentheses. Stars denote significance.',
 [('','(1)\nTransport spend\nRs/month','(2)\nEmployed\n0/1','(3)\nFemale employed\n0/1','(4)\nWomen’s trips\ncount/day'),
  ('Bus access (β₁)','−214***\n(62)','0.031*\n(0.018)','0.048**\n(0.021)','0.29***\n(0.09)'),
  ('Vulnerability index (β₂)','−388***\n(74)','−0.142***\n(0.024)','−0.196***\n(0.028)','−0.44***\n(0.11)'),
  ('Bus access × VI (β₃)','−96\n(88)','0.022\n(0.026)','0.041\n(0.031)','0.18\n(0.13)'),
  ('Household controls','Yes','Yes','Yes','Yes'),
  ('City fixed effects','Yes','Yes','Yes','Yes'),
  ('Observations','2,946','2,946','1,502','1,338'),
  ('Clusters (wards)','138','138','136','131'),
  ('R-squared','0.31','0.24','0.27','0.22'),
 ], [Cm(4.2),Cm(3.4),Cm(3.1),Cm(3.1),Cm(3.2)])
para('Read the mock-up this way. β₁ is the headline: bus access is associated with lower household transport '
     'spending and higher female employment. β₃ is the equity result, and note that in this mock-up it is not '
     'significant. That is exactly the outcome the power analysis predicts at a sample of 6,000, and it is why the '
     'vulnerability design needs stratified over-sampling.', italic=True, color=GREY)

h2('Output 2: monetised benefit summary')
dummy_table('Table M1.2. Annual socio-economic benefit, one city. Individual and wider economic benefits are '
            'reported separately, following convention, to avoid double counting.',
 [('Benefit stream','Unit','Per household\nper year','City total\nRs crore/year','Confidence'),
  ('Household transport spend saved','Rs','2,568','41.2','Medium'),
  ('Travel time saved, valued','Rs','1,940','31.1','Medium'),
  ('Female earnings gain','Rs','3,110','18.7','Low'),
  ('Sub-total, individual benefits','Rs','7,618','91.0','—'),
  ('Decongestion (marginal external congestion cost)','Rs crore','—','27.4','Low'),
  ('Agglomeration (effective density)','Rs crore','—','19.8','Low'),
  ('Sub-total, wider economic benefits','Rs crore','—','47.2','—'),
  ('TOTAL M1','Rs crore','—','138.2','—'),
 ], [Cm(5.4),Cm(2.2),Cm(2.8),Cm(3.0),Cm(2.6)])

h2('Output 3: accessibility, the number that is not self-reported')
dummy_table('Table M1.3. Jobs reachable by bus within a travel time threshold, comparable across cities and to '
            'international benchmarks. Computed from GTFS and ward employment. No survey involved.',
 [('City','Jobs within 45 min\nbefore','Jobs within 45 min\nafter','Change','Population gaining\naccess'),
  ('City A (Group B)','84,000','131,000','+56%','212,000'),
  ('City B (Group B)','61,000','88,000','+44%','147,000'),
  ('City C (Group B)','109,000','142,000','+30%','268,000'),
 ], [Cm(3.4),Cm(3.6),Cm(3.6),Cm(2.4),Cm(3.2)])

doc.add_page_break()

# ============ M2 ============
h1('M2  Health co-benefits')
h2('What is estimated')
para('Comparative risk assessment. For each pathway, a change in exposure is converted into a change in disease '
     'burden using a dose-response relationship, then summed.')
eq('ΔDALY  =  Σ_pathway Σ_disease  [ RR(exposure_scenario) − RR(exposure_baseline) ]  ×  Burden_disease,age,sex')
para('Pathways are physical activity from access and egress walking, PM2.5 exposure, road injury exposure, and '
     'commute stress. The first three enter the comparative risk assessment. Stress is estimated separately by '
     'ordered logit on survey responses and reported alongside, not converted to DALYs.')

h2('Output 1: WHO HEAT, the fast result')
dummy_table('Table M2.1. Walking pathway only. This is the number available first, because it needs only walking '
            'volumes and a value of statistical life.',
 [('Quantity','Value','Note'),
  ('Additional walking per bus user','9.4 min/day','Access plus egress, versus private vehicle users'),
  ('Bus users in city','186,000','From ridership and survey'),
  ('Premature deaths averted per year','21','Central estimate'),
  ('Uncertainty interval','9 to 34','From the dose-response range'),
  ('Value at VSL, estimate A','Rs 94 crore/year','Using the higher Indian VSL estimate'),
  ('Value at VSL, estimate B','Rs 32 crore/year','Using the lower Indian VSL estimate'),
 ], [Cm(5.4),Cm(3.4),Cm(7.4)])
para('Two VSL rows, not one. Published Indian value-of-statistical-life estimates differ by about three times, so '
     'the result is reported as a band and never as a single figure.', italic=True, color=GREY)

h2('Output 2: full ITHIM pathway decomposition')
dummy_table('Table M2.2. DALYs averted per year by pathway, with uncertainty intervals from Monte Carlo. Negative '
            'values are harms and must be shown.',
 [('Pathway','DALYs averted\nper year','95% interval','Direction','Driver'),
  ('Physical activity (walking gained)','1,840','790 to 2,960','Benefit','Access and egress walking'),
  ('Air pollution, population level','620','140 to 1,180','Benefit','Fewer vehicle-km on the network'),
  ('Air pollution, rider exposure','−90','−310 to 60','Possible harm','In-bus PM2.5 above air-conditioned cars'),
  ('Road injury, mode shift','1,120','210 to 2,140','Benefit','Away from two-wheelers'),
  ('Road injury, pedestrian access','−340','−880 to 40','Possible harm','Walking to stops in unsafe environments'),
  ('NET','3,150','460 to 5,780','Benefit','Interval includes near-zero'),
 ], [Cm(5.0),Cm(2.8),Cm(2.8),Cm(2.8),Cm(3.8)])
warnbox('The two negative rows are deliberate',
 'A health model for buses that shows only benefits will not survive peer review. Indian measurements put in-bus '
 'particulate exposure above air-conditioned cars, and vulnerable road users are the large majority of Indian road '
 'deaths with buses involved in a substantial share. Reporting the harms explicitly, and letting the uncertainty '
 'interval approach zero, is what made the seven-city BRT study credible. Design the output table this way from '
 'the start.')

h2('Output 3: who benefits, disaggregated')
dummy_table('Table M2.3. DALYs averted per 100,000 population, by group. This is the equity result and the metric '
            'climate funds ask for.',
 [('Group','DALYs averted per\n100,000/year','Share of total\nbenefit','Share of\npopulation'),
  ('Lowest income tertile','78','44%','33%'),
  ('Middle income tertile','52','31%','33%'),
  ('Highest income tertile','39','25%','34%'),
  ('Women','64','51%','48%'),
  ('Men','58','49%','52%'),
  ('Households without a vehicle','91','38%','27%'),
 ], [Cm(4.6),Cm(3.8),Cm(3.4),Cm(3.4)])

h2('Output 4: commute stress, reported separately')
dummy_table('Table M2.4. Ordered logit on a five-point stress scale. Odds ratios. Not converted to DALYs.',
 [('Variable','Odds ratio','Interpretation'),
  ('Bus user (versus two-wheeler)','0.74**','Lower odds of reporting high commute stress'),
  ('Waiting time, per 5 min','1.19***','Waiting drives stress more than in-vehicle time'),
  ('Crowding, per unit','1.31***','The largest single stressor in this mock-up'),
  ('Perceived safety, per unit','0.68***','Feeling safe strongly reduces reported stress'),
  ('Female','1.42***','Women report higher stress at the same trip attributes'),
 ], [Cm(5.4),Cm(2.8),Cm(8.0)])

doc.add_page_break()

# ============ M3 M4 ============
h1('M3  GHG mitigation')
eq('ΔCO₂e  =  Σ_mode [ VKT_avoided,mode × EF_mode ]  −  [ Bus_VKT × EF_bus(grid, charging) ]')
dummy_table('Table M3.1. Annual GHG outcome under three grid scenarios. Scenario range, not a point estimate.',
 [('Scenario','Vehicle-km avoided\nmillion/year','Bus emissions\ntCO₂e/year','Net avoided\ntCO₂e/year','Per bus\ntCO₂e/year'),
  ('Current grid mix','142','18,400','31,200','156'),
  ('Stated policy grid, 2030','142','11,900','37,700','189'),
  ('Fully renewable grid','142','1,200','48,400','242'),
 ], [Cm(3.6),Cm(3.4),Cm(3.2),Cm(3.2),Cm(2.8)])

h1('M4  Resilience and adaptation')
dummy_table('Table M4.1. Resilience outcome per disruption event.',
 [('Indicator','Bus network','Private vehicle','Note'),
  ('Population still mobile during flood event','62%','24%','GIS routing on hazard-tagged network'),
  ('Economic downtime avoided','Rs 34 crore/event','—','Versus a no-bus counterfactual'),
  ('Median evacuation time to shelter','41 min','78 min','Routing optimisation'),
  ('Infrastructure restart cost','Rs 2.1 crore','—','Depot and fleet, post-event'),
  ('Critical corridors identified','7','—','Highest-volume ward pairs on hazard routes'),
 ], [Cm(5.0),Cm(3.2),Cm(3.2),Cm(5.6)])

# ============ INTEGRATED ============
h1('The integrated result: what the whole project produces')
h2('Output 1: the single table the boss will want')
dummy_table('Table INT.1. All four models, one city, one year. This is the headline table of the project.',
 [('Model','Benefit stream','Rs crore/year','Per bus\nRs lakh/year','Confidence'),
  ('M1','Household savings, time, earnings, decongestion, agglomeration','138.2','69.1','Medium'),
  ('M2','DALYs averted, valued','86.4','43.2','Low to medium'),
  ('M3','CO₂e avoided at shadow carbon price','12.7','6.4','Medium'),
  ('M4','Downtime and evacuation value','21.9','11.0','Low'),
  ('TOTAL','','259.2','129.6','—'),
  ('Public cost','Capital annuitised plus operating subsidy','96.0','48.0','High'),
  ('SROI ratio','Societal return per rupee of public spend','2.7 : 1','','—'),
 ], [Cm(2.2),Cm(6.2),Cm(2.8),Cm(3.0),Cm(2.8)])

h2('Output 2: the three SROI lenses, same data')
dummy_table('Table INT.2. The same underlying result, expressed for three different audiences.',
 [('Lens','Audience','Headline metric','Illustrative value'),
  ('Lens 1','Government, central and state','Societal return per rupee of public spend; return on the Rs 24/km PM e-Bus Sewa subsidy','2.7 : 1; Rs 65 of societal value per Rs 24 of subsidy per km'),
  ('Lens 2','Climate and development finance','tCO₂e avoided; vulnerable people benefited; DALYs averted per 10,000; resilience value','31,200 tCO₂e; 212,000 people; 21 DALYs; Rs 34 crore per event'),
  ('Lens 3','Private capital','Share of public savings available as a payment security mechanism','Rs 41 crore/year of health and productivity savings available to underwrite operator payments'),
 ], [Cm(1.8),Cm(3.4),Cm(6.0),Cm(6.0)])

h2('Output 3: sensitivity, presented as switching values')
dummy_table('Table INT.3. How far each assumption must move before the conclusion flips to a ratio below 1:1. '
            'This is the format finance institutions expect.',
 [('Assumption','Base value','Switching value','Margin','Plausible?'),
  ('Value of statistical life','Rs 44.7 million','Rs 12.1 million','−73%','Yes, the lower Indian estimate is close'),
  ('Modal shift from private vehicles','18%','7%','−61%','Possible'),
  ('Value of travel time, bus users','Rs 19/hour','Rs 6/hour','−68%','Unlikely'),
  ('Agglomeration elasticity','0.04','0.01','−75%','Possible'),
  ('Discount rate','8%','19%','+138%','No'),
 ], [Cm(4.4),Cm(2.8),Cm(2.8),Cm(2.0),Cm(5.0)])
para('The value of statistical life row is the one to watch. Because the two published Indian estimates differ by '
     'roughly three times, and the switching value sits inside that gap, the headline conclusion depends on which '
     'estimate is chosen. That has to be stated openly in the report, not buried in an annexe.', italic=True, color=GREY)

h1('How to use this document')
real_table([
 ('Purpose','How'),
 ('Briefing a funder or a ministry','Show the shape of Table INT.1 and INT.2. Say clearly that the numbers are placeholders and the structure is the commitment'),
 ('Designing the survey','Work backwards from Tables M1.1 and M2.4. Every coefficient in those tables needs a variable, and every variable needs a question'),
 ('Setting up the analysis code','Build the empty output tables first, then write the code that fills them. It prevents the analysis drifting away from what was promised'),
 ('Peer review readiness','Tables M2.2 and INT.3 are the ones reviewers will attack. Having the harms and the switching values already in the output design is what protects the result'),
], [Cm(5.0),Cm(12.2)])

doc.save('BBUS_Model_Outputs_Illustrative.docx')
print('saved')
