from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

TEAL=RGBColor(0x00,0x6D,0x77); DARK=RGBColor(0x1A,0x1A,0x1A); GREY=RGBColor(0x55,0x55,0x55); RED=RGBColor(0x99,0x22,0x22)
doc=Document(); s=doc.sections[0]
s.top_margin=Cm(1.4); s.bottom_margin=Cm(1.4); s.left_margin=Cm(1.6); s.right_margin=Cm(1.6)
n=doc.styles['Normal']; n.font.name='Calibri'; n.font.size=Pt(9.5); n.font.color.rgb=DARK
n.paragraph_format.space_after=Pt(4); n.paragraph_format.line_spacing=1.0

def shade(c,h):
    tcPr=c._tc.get_or_add_tcPr(); sh=OxmlElement('w:shd')
    sh.set(qn('w:val'),'clear'); sh.set(qn('w:color'),'auto'); sh.set(qn('w:fill'),h); tcPr.append(sh)

p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(0)
r=p.add_run('#BBUS  ·  possible outputs and what they look like'); r.font.size=Pt(15); r.bold=True; r.font.color.rgb=TEAL
p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(6)
r=p.add_run('All values normalised to per year, per 100 buses, where meaningful. Sample of 6,000 across 6 cities.')
r.font.size=Pt(8.5); r.italic=True; r.font.color.rgb=GREY
p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(7)
r=p.add_run('EXAMPLE VALUES ARE INVENTED. They show the unit and order of magnitude only, not a finding.')
r.font.size=Pt(8.5); r.bold=True; r.font.color.rgb=RED

W=[Cm(6.0),Cm(5.4),Cm(2.4),Cm(3.6)]
rows=[
 ('Output','Example value','Model','Comes from'),
 ('__M1  SOCIO-ECONOMIC','','',''),
 ('Decongestion benefit','Rs 150 crore/year','M1','Passive'),
 ('Travel time saved','42 lakh person-hours/year  =  Rs 80 crore','M1','Passive + survey income'),
 ('Household transport spend saved','Rs 2,600 per household/year','M1','Survey'),
 ('Share of income saved, poorest third','6.4% of household income','M1','Survey'),
 ('Trips that would not happen without bus','21% of all bus trips','M1','Survey'),
 ('Female employment effect','+4.8 percentage points','M1','Survey'),
 ('Women’s daily trips','+0.29 trips per day','M1','Survey'),
 ('Jobs reachable in 45 minutes','31% now, 58% with 3 new corridors','M1','Passive + GTFS + jobs data'),
 ('People gaining job access','212,000 people','M1','Passive + GTFS + jobs data'),
 ('Agglomeration benefit','Rs 20 crore/year','M1','Passive + Economic Census'),
 ('Subsidy reaching the poorest third','19% of total subsidy','M1','Survey + operator data'),
 ('Demand with no bus within 500 m','40% of motorised trips, 12 corridors','M1','Passive'),
 ('__M2  HEALTH','','',''),
 ('Extra walking per bus user','+9.4 minutes/day','M2','Passive + survey'),
 ('Deaths averted, walking pathway','21 deaths/year','M2','Passive + survey'),
 ('DALYs averted, all pathways','3,150 DALYs/year','M2','Passive + survey'),
 ('Road injuries averted','34 injuries/year','M2','Survey counterfactual + police records'),
 ('PM2.5 exposure avoided, shifting riders','−8% inhaled dose','M2','Passive + published exposure factors'),
 ('Time in traffic per commuter','47 minutes/day','M2','Passive'),
 ('High-stress commuters reduced','−18%','M2','Survey'),
 ('Health value in rupees','Rs 32 to 94 crore/year (VSL band)','M2','Passive + survey'),
 ('__M3  GHG','','',''),
 ('Vehicle-km avoided','142 million km/year','M3','Survey counterfactual + passive'),
 ('CO2e avoided','31,200 tonnes/year  =  312 t per bus','M3','Survey counterfactual + passive'),
 ('Carbon value','Rs 13 crore/year','M3','Both + shadow carbon price'),
 ('Trips within single-charge e-bus range','78% under 12 km, 96% under 25 km','M3','Passive'),
 ('__M4  RESILIENCE','','',''),
 ('Economic downtime avoided','Rs 34 crore per flood event','M4','Passive + secondary'),
 ('Critical corridors identified','7 ward pairs carry 34% of trips','M4','Passive'),
 ('Evacuation time saved','37 minutes, median','M4','Passive + GIS'),
 ('Population still mobile in a flood','62% by bus vs 24% by private vehicle','M4','Passive + hazard maps'),
 ('__ALL FOUR TOGETHER','','',''),
 ('Total societal benefit','Rs 259 crore/year  =  Rs 130 lakh per bus','All','All'),
 ('Public cost','Rs 96 crore/year','—','Operator and scheme data'),
 ('SROI ratio','2.7 : 1','All','All'),
]

t=doc.add_table(rows=len(rows),cols=4); t.style='Table Grid'; t.alignment=WD_TABLE_ALIGNMENT.CENTER
for i,row in enumerate(rows):
    if row[0].startswith('__'):
        c=t.cell(i,0); c.merge(t.cell(i,3)); shade(c,'D6E8E8')
        cp=c.paragraphs[0]; cp.paragraph_format.space_after=Pt(1); cp.paragraph_format.space_before=Pt(1)
        r=cp.add_run(row[0][2:]); r.bold=True; r.font.size=Pt(8.6); r.font.color.rgb=TEAL
        continue
    for j,txt in enumerate(row):
        c=t.cell(i,j); c.width=W[j]
        if i==0: shade(c,'E8F2F2')
        elif j==1: shade(c,'FFF6E5')
        cp=c.paragraphs[0]; cp.paragraph_format.space_after=Pt(1); cp.paragraph_format.space_before=Pt(1)
        r=cp.add_run(txt); r.font.size=Pt(8.4)
        if i==0: r.bold=True; r.font.color.rgb=TEAL
        elif j==0: r.bold=True

doc.add_paragraph().paragraph_format.space_after=Pt(4)
p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(2)
r=p.add_run('Three things to know'); r.bold=True; r.font.size=Pt(10); r.font.color.rgb=TEAL
for txt in [
 'Everything marked Passive can start now. No survey, no extra cost.',
 'Everything in M2 and M3 depends on one survey question: what would you do on this trip if the bus did not run. Without it, no modal shift and no health or carbon number.',
 'Anything comparing bus against car needs travel mode, which the passive data does not yet have. It must be inferred from the traces first.',
]:
    pp=doc.add_paragraph(style='List Bullet'); pp.paragraph_format.space_after=Pt(2)
    pp.paragraph_format.left_indent=Cm(0.5); pp.paragraph_format.first_line_indent=Cm(-0.25)
    rr=pp.add_run(txt); rr.font.size=Pt(9)

p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(6); p.paragraph_format.space_after=Pt(2)
r=p.add_run('What 6,000 across 6 cities can and cannot support'); r.bold=True; r.font.size=Pt(10); r.font.color.rgb=TEAL
W2=[Cm(8.6),Cm(8.8)]
rows2=[('Can do','Cannot do'),
 ('All six cities pooled, with city fixed effects','Separate results for each city'),
 ('Effects down to about 5 percentage points','Effects smaller than about 5 points'),
 ('Split by sex, and by income tertile','Testing whether the poor benefit MORE, unless vulnerable households are over-sampled'),
 ('All Passive outputs at full city scale','Nothing extra needed'),
]
t2=doc.add_table(rows=len(rows2),cols=2); t2.style='Table Grid'; t2.alignment=WD_TABLE_ALIGNMENT.CENTER
for i,row in enumerate(rows2):
    for j,txt in enumerate(row):
        c=t2.cell(i,j); c.width=W2[j]
        if i==0: shade(c,'E8F2F2')
        cp=c.paragraphs[0]; cp.paragraph_format.space_after=Pt(1); cp.paragraph_format.space_before=Pt(1)
        r=cp.add_run(txt); r.font.size=Pt(8.4)
        if i==0: r.bold=True; r.font.color.rgb=TEAL

doc.save('BBUS_Possible_Outputs.docx')
print('saved')
