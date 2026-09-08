from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

TEAL=RGBColor(0x00,0x6D,0x77); DARK=RGBColor(0x1A,0x1A,0x1A); GREY=RGBColor(0x55,0x55,0x55); RED=RGBColor(0x99,0x22,0x22)
doc=Document(); s=doc.sections[0]
s.top_margin=Cm(1.7); s.bottom_margin=Cm(1.7); s.left_margin=Cm(1.9); s.right_margin=Cm(1.9)
n=doc.styles['Normal']; n.font.name='Calibri'; n.font.size=Pt(10); n.font.color.rgb=DARK
n.paragraph_format.space_after=Pt(5); n.paragraph_format.line_spacing=1.05

def shade(c,h):
    tcPr=c._tc.get_or_add_tcPr(); sh=OxmlElement('w:shd')
    sh.set(qn('w:val'),'clear'); sh.set(qn('w:color'),'auto'); sh.set(qn('w:fill'),h); tcPr.append(sh)
def h1(t):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(14); p.paragraph_format.space_after=Pt(4)
    r=p.add_run(t); r.font.size=Pt(13); r.bold=True; r.font.color.rgb=TEAL
    pPr=p._p.get_or_add_pPr(); pb=OxmlElement('w:pBdr'); bt=OxmlElement('w:bottom')
    bt.set(qn('w:val'),'single'); bt.set(qn('w:sz'),'6'); bt.set(qn('w:space'),'3'); bt.set(qn('w:color'),'006D77')
    pb.append(bt); pPr.append(pb)
def h2(t):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(10); p.paragraph_format.space_after=Pt(2)
    r=p.add_run(t); r.font.size=Pt(11); r.bold=True; r.font.color.rgb=DARK
def para(t,size=10,italic=False,color=DARK,after=5):
    p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(after)
    r=p.add_run(t); r.font.size=Pt(size); r.italic=italic; r.font.color.rgb=color
def tbl(rows,widths,fs=8.4,fills=None):
    t=doc.add_table(rows=len(rows),cols=len(rows[0])); t.style='Table Grid'; t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for i,row in enumerate(rows):
        for j,txt in enumerate(row):
            c=t.cell(i,j); c.width=widths[j]
            if i==0: shade(c,'E8F2F2')
            elif fills and fills.get(i): shade(c,fills[i])
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

p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(0)
r=p.add_run('#BBUS publication strategy'); r.font.size=Pt(18); r.bold=True; r.font.color.rgb=TEAL
p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(8)
r=p.add_run('Journal quartiles, and which paper comes out of which model  ·  CEEW  ·  September 2026')
r.font.size=Pt(9); r.italic=True; r.font.color.rgb=GREY

box('These quartiles are not yet verified',
 'Scimago itself was blocked by network policy, so no quartile below was read off a Scimago journal page directly. '
 'Each comes from search results quoting Scimago, cross-checked against at least one aggregator such as Resurchify '
 'or journalmetrics. Before this guides a submission decision, open scimagojr.com, search the journal, and read the '
 'quartile chart with its year. Quartiles also move year to year and differ by subject category, so always state '
 'which category and which year you are quoting.')

h1('1. Quartiles, as far as they could be checked')
tbl([
 ('Journal','Best quartile and category','Year','Confidence'),
 ('Nature Sustainability','Q1, several categories','2024','High'),
 ('Applied Energy','Q1, energy and several others','2024','High'),
 ('The Lancet Planetary Health','Q1, environmental science and public health','2024','Medium'),
 ('Environment International','Q1, environmental science and pollution','2024','Medium'),
 ('Environmental Health Perspectives','Q1, toxicology and public health','2024','Medium-high'),
 ('Journal of Urban Health','Q1, public health and urban studies','2025','Medium-high'),
 ('Accident Analysis and Prevention','Q1, safety, human factors, public health','2024','Medium-high'),
 ('Environmental Research','Q1, environmental science general','2024','Medium'),
 ('Atmospheric Environment','Q1, atmospheric science','2025','Medium'),
 ('Scientific Reports','Q1, multidisciplinary','2024','Medium'),
 ('American Economic Review','Q1, economics','2025','Medium'),
 ('AEJ: Applied Economics','Q1, economics','2024','Medium'),
 ('World Development','Q1, development and economics','2024','Medium'),
 ('Cities','Q1, urban studies and development','2025','Medium'),
 ('Transportation Research Part A','Q1, transportation and civil engineering','2024','Medium'),
 ('Transportation Research Part C','Q1, transportation','2024','Medium-high'),
 ('Transportation Research Part D','Q1, transportation and environmental studies','2025','Medium'),
 ('Journal of Transport Geography','Q1, geography, planning, transportation','2024','Medium-high'),
 ('Travel Behaviour and Society','Q1, transportation','2024','Medium-high'),
 ('Sustainable Cities and Society','Q1, several categories','2024','Medium-high'),
 ('Research in Transportation Economics','Q1, transportation and economics','2024','Medium'),
 ('Case Studies on Transport Policy','Q1 in geography and urban studies, Q2 in transportation','2024','Medium-high'),
 ('Energy Policy','Q1, energy policy and law','—','Medium-high'),
 ('Transport Policy','Q1 on Clarivate; Scimago page not retrieved','—','Low-medium'),
 ('Transportation (Springer)','Q1 on Clarivate; Scimago page not retrieved','—','Low-medium'),
 ('Journal of Transport and Health','Q2 in geography and urban studies, Q3 in transportation','2024-25','Medium'),
 ('Air Quality, Atmosphere and Health','Q2 in earth sciences, Q3 in atmospheric science','—','Medium'),
 ('Transportation Research Record','Q2 in mechanical engineering, Q3 in civil engineering','—','Medium'),
 ('Int. J. Environmental Research and Public Health','Q2, but see the warning below','2024','Medium'),
 ('Journal of Transport Economics and Policy','Sources conflict, Q2 versus Q3','—','Not confirmed'),
], [Cm(6.0),Cm(6.4),Cm(1.9),Cm(2.5)])

box('Two findings that change plans',
 'First, the Journal of Transport and Health is NOT Q1. It sits at Q2 in its best category and Q3 in transportation. '
 'It is the natural disciplinary home for ITHIM-style work and a perfectly respectable venue, but if the '
 'requirement is genuinely Q1 then the M2 paper has to go to Environment International, Journal of Urban Health or '
 'Environmental Health Perspectives instead. Second, the International Journal of Environmental Research and Public '
 'Health was delisted from Web of Science by Clarivate in February 2023. It may still show a Scopus quartile. Do '
 'not submit there.')

doc.add_page_break()

h1('2. One paper per model, and where each goes')
para('Four papers come out of this project. Each maps to a model, draws on specific output tables, and has a '
     'different natural home. Ranked first choice downwards.')

h2('Paper 1  ·  from M1  ·  socio-economic and gender co-benefits')
tbl([
 ('','Detail'),
 ('Question','Does bus access change household transport spending, employment and women’s mobility in Indian cities, and for whom most?'),
 ('Method','Difference-in-differences in Group B, cross-sectional regression with rich controls in Group A, vulnerability index interaction throughout'),
 ('Outputs it uses','Tables M1.1 regression, M1.2 monetised benefits, M1.3 accessibility'),
 ('First choice','Journal of Transport Geography, Q1. There is direct precedent: it published an India gendered bus-subsidy paper in February 2026, which is already in our evidence file'),
 ('Second','Transportation Research Part A, Q1. Policy-facing flagship, has carried Indian bus and BRT case studies'),
 ('Third','World Development, Q1, if framed as development economics with the identification strategy foregrounded rather than as a transport paper'),
 ('Fallback','Case Studies on Transport Policy. Q1 in geography and urban studies, explicitly welcomes developing-country case studies, and the cheapest article charge of the group'),
], [Cm(3.2),Cm(14.0)])

h2('Paper 2  ·  from M2  ·  health co-benefits')
tbl([
 ('','Detail'),
 ('Question','What is the health value, in years of life lost averted, of shifting Indian urban travel from two-wheelers, cars and autos to buses?'),
 ('Method','ITHIM-style comparative risk assessment across physical activity, air pollution and road injury, with Monte Carlo uncertainty; WHO HEAT for the walking pathway'),
 ('Outputs it uses','Tables M2.1 HEAT, M2.2 pathway decomposition, M2.3 equity disaggregation'),
 ('First choice','Environment International, Q1. Best realistic high-impact home for a quantitative environmental health burden paper'),
 ('Second','Journal of Urban Health, Q1, or Environmental Health Perspectives, Q1. Both explicitly urban and public health facing'),
 ('Third','Journal of Transport and Health. The natural disciplinary home and where most ITHIM applications sit, but it is Q2, so only if the Q1 requirement is soft'),
 ('Aspirational','The Lancet Planetary Health, Q1. Very high bar and a large article charge, though discounts for authors in India are likely'),
 ('Avoid','IJERPH, regardless of quartile shown, because of the 2023 Web of Science delisting'),
], [Cm(3.2),Cm(14.0)])

h2('Paper 3  ·  from the data method  ·  fusing passive GPS with a household survey')
tbl([
 ('','Detail'),
 ('Question','Can a large passive GPS trip dataset and a small household survey be jointly estimated to recover mode choice and travel demand for an Indian city?'),
 ('Method','GPS mode classification with route matching, joint revealed and stated preference estimation with a scale parameter, bias correction by multilevel regression and poststratification, expansion by iterative proportional fitting'),
 ('Outputs it uses','The mode classifier validation, the choice model coefficients, and the bias diagnostic'),
 ('First choice','Transportation Research Part C, Q1. Data-driven and methods-facing; this is precisely its remit'),
 ('Second','Transportation, Springer, Q1 on Clarivate. The home journal for travel survey methodology, and it recently published closely related GPS travel-diary work'),
 ('Third','Travel Behaviour and Society, Q1, or Journal of Transport Geography, Q1, if the paper leans behavioural rather than methodological'),
 ('Note','No India-based GPS and household-survey mode choice paper was found in any of these. That is a genuine gap and a strong claim to novelty, though it also means there is no precedent to point to in the cover letter'),
], [Cm(3.2),Cm(14.0)])

h2('Paper 4  ·  from the integration  ·  cost-benefit and social return framework')
tbl([
 ('','Detail'),
 ('Question','How should the full social return to bus investment be appraised in a developing country, and what does it come to across six Indian cities?'),
 ('Method','Cost-benefit analysis with switching values, three social-return lenses, Monte Carlo sensitivity'),
 ('Outputs it uses','Tables INT.1 headline summary, INT.2 three lenses, INT.3 switching values'),
 ('First choice','Transportation Research Part A, Q1. The standard home for transport appraisal methodology with policy relevance'),
 ('Second','Transport Policy, Q1 on Clarivate. Policy-facing and receptive to appraisal-framework papers'),
 ('Third','Research in Transportation Economics, Q1, if framed as an economic valuation contribution'),
 ('Fallback','Case Studies on Transport Policy, if framed as an applied case study'),
 ('Note','No social-return-specific transport paper from a developing country was found in these venues. The existing literature is almost entirely high income. Another genuine gap'),
], [Cm(3.2),Cm(14.0)])

doc.add_page_break()

h1('3. Practical notes on the target journals')
tbl([
 ('Journal','Access','Article charge','Facing','India transport precedent'),
 ('Journal of Transport Geography','Hybrid','Geo-priced, no fixed figure found','Policy and methods','Yes, a 2026 India gender and bus subsidy paper'),
 ('Transportation Research Part A','Hybrid','Geo-priced','Policy','Yes, Indian BRT case studies'),
 ('Environment International','Gold open access only','Geo-priced, India discount tier likely','Health science','Not confirmed for transport health'),
 ('Journal of Urban Health','Hybrid','Not confirmed','Public health','Not confirmed'),
 ('The Lancet Planetary Health','Gold open access only','About USD 5,800 to 7,900, sources disagree','High visibility, exacting','Not confirmed'),
 ('Transportation Research Part C','Hybrid','About USD 3,840','Methods','Not confirmed'),
 ('Transportation, Springer','Hybrid','About USD 2,790','Methods','A recent GPS travel-diary paper, not India'),
 ('Transport Policy','Hybrid','Geo-priced','Policy','Not confirmed'),
 ('Research in Transportation Economics','Gold open access','About USD 2,490','Economics','Not confirmed'),
 ('Case Studies on Transport Policy','Hybrid','About USD 1,950, cheapest here','Case study, developing-country friendly','Scope favours it, specifics not retrieved'),
 ('World Development','Hybrid','Geo-priced','Development economics','Not confirmed'),
], [Cm(4.4),Cm(2.2),Cm(3.6),Cm(3.2),Cm(4.0)])
para('Time to first decision could not be established for any of these. Check each journal’s own insights page '
     'before committing, because it varies from weeks to many months and it matters for the project timeline.',
     italic=True, color=GREY)

h1('4. Sequencing the four papers')
tbl([
 ('Order','Paper','Why this order'),
 ('1','Paper 3, the data method','It can be written from the passive data and a pilot alone, before the main survey completes. It establishes the method the other papers rely on, so it should be in review first'),
 ('2','Paper 1, socio-economic','Group A cross-section can be analysed as soon as the first wave lands. It does not wait for Group B follow-up'),
 ('3','Paper 2, health','Needs the same survey plus injury and mortality data assembly. WHO HEAT results can support an earlier policy brief while the full model is built'),
 ('4','Paper 4, integration','Requires all four models, so it comes last. It is also the one most likely to become the flagship, so it benefits from the earlier papers being citable'),
], [Cm(1.6),Cm(4.4),Cm(11.2)])

h1('5. Before any of this is acted on')
tbl([
 ('Check','Why'),
 ('Open Scimago for every journal on the shortlist','No quartile in this document was read directly from Scimago. Confirm the quartile, the category and the year'),
 ('Confirm the Journal of Transport and Health position','It is the natural home for the health paper but appears to be Q2. If the Q1 requirement is firm, the target changes'),
 ('Resolve the Journal of Transport Economics and Policy quartile','Sources conflict between Q2 and Q3'),
 ('Check article charges against the project budget','Two of the strongest health targets are gold open access only, which means the charge is unavoidable rather than optional'),
 ('Check co-authorship and data-sharing terms','Several target journals require a data availability statement. Passive GPS data licensing may restrict what can be shared, and that needs settling before submission, not after'),
], [Cm(6.4),Cm(10.8)])

doc.save('BBUS_Publication_Strategy.docx')
print('saved')
