from pathlib import Path
import re
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
out=Path('submission/SPIE-conference-20261113')
qa=out/'qa'
d=Document(qa/'template.docx')
b=d.element.body
for x in list(b):
 if x.tag!=qn('w:sectPr'): b.remove(x)
def par(s,style='SPIE body text',size=10,bold=False,align=None,before=0,after=5,keep=False):
 p=d.add_paragraph(style=style)
 fmt=p.paragraph_format
 fmt.space_before=Pt(before);fmt.space_after=Pt(after);fmt.line_spacing=1.06
 fmt.keep_with_next=keep;fmt.keep_together=True
 fmt.first_line_indent=Pt(0)
 p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY if align is None else align
 for a in re.split(r'(\{[^}]+\})',s):
  if not a:continue
  r=p.add_run(a.strip('{}'));r.font.name='Times New Roman';r.font.size=Pt(size);r.bold=bold;r.font.superscript=a.startswith('{')
 return p
center=WD_ALIGN_PARAGRAPH.CENTER
def heading(s):return par(s,'SPIE abstract title',11,True,center,6,5,True)
def small(s):return par(s,'SPIE body text',10,True,None,5,3,True)
def page(s):
 p=heading(s);p.paragraph_format.page_break_before=True
def fig(name,cap,w):
 p=d.add_paragraph();p.alignment=center;p.paragraph_format.space_after=Pt(0);p.paragraph_format.keep_with_next=True
 p.add_run().add_picture(str(qa/(name+'.png')), width=Inches(w))
 par(cap,'SPIE figure caption',9,False,None,3,5)
def table(cap,rows):
 par(cap,'SPIE table caption',9,False,None,2,3,True)
 t=d.add_table(rows=0,cols=len(rows[0]));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=True
 for i,row in enumerate(rows):
  cells=t.add_row().cells
  for j,txt in enumerate(row):
   p=cells[j].paragraphs[0];p.alignment=WD_ALIGN_PARAGRAPH.LEFT if j==0 else center
   f=p.paragraph_format;f.space_after=Pt(2);f.space_before=Pt(2);f.first_line_indent=Pt(0);f.line_spacing=1
   r=p.add_run(txt);r.font.name='Times New Roman';r.font.size=Pt(9);r.bold=i==0
   if i in (0,len(rows)-1):
    border=OxmlElement('w:tcBorders')
    for edge in (('top','bottom') if i==0 else ('bottom',)):
     e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'5');e.set(qn('w:color'),'555555');border.append(e)
    cells[j]._tc.get_or_add_tcPr().append(border)
par('Evaluating candidate restriction in influence maximization across selection budgets and ranking precisions','SPIE paper title',16,True,center,0,11)
par('Jiayue Sun{a}, Binbin Yong{b*}, Junjie An{c}, Tianyu Bo{c}, and Shuai Li{c}','SPIE Authors-Affils',12,False,center,0,3)
for a in ('{a}School of Artificial Intelligence, Lanzhou University, Lanzhou 730000, China','{b}School of Information Science and Engineering, Lanzhou University, Lanzhou 730000, China','{c}Lanzhou University, Lanzhou, China'):
 par(a,'SPIE Authors-Affils',12,False,center,0,1)
par('*Corresponding author: yongbb14@lzu.edu.cn','SPIE body text',10,False,center,2,7)
heading('ABSTRACT')
par('Restricting greedy influence maximization to highly ranked vertices saves computation, but its measured cost in spread depends on how the reference seeds and the candidate pool are obtained. We compare full and restricted searches on the same sampled diffusion worlds and evaluate their seeds on 10,000 separate worlds. On three networks with five seeds and a three-round diffusion horizon, a 20-vertex degree pool reproduces all 15 full-reference seed sequences at the largest tested selection budget. A PageRank pool of the same size loses 5–73% of incremental spread. On ca-GrQc, its mean difference from full search changes from +0.236 to −0.251 nodes as the budget increases. In a post-hoc comparison, tightening the PageRank tolerance exchanges two candidates and leaves the mean difference positive at all three budgets. These results show why evaluations should identify the vertices admitted at the ranking cutoff and measure spread independently of seed selection.','SPIE abstract body text')
par('Keywords: influence maximization, candidate selection, PageRank, Monte Carlo evaluation, network diffusion','SPIE keywords',10)
heading('1.  INTRODUCTION')
par('Choosing a small set of initial adopters is a search problem: a vertex is valuable when it reaches people the other seeds would miss. Greedy influence maximization estimates that contribution for each eligible vertex in turn.{1} Lazy evaluation reduces repeated scoring, and StaticGreedy reuses sampled worlds across rounds.{2,3} Restricting eligibility to the top vertices in a ranking saves work earlier, but it can exclude a useful seed before the search begins.')
par('A benchmark that compares a restricted search with a full search must account for sampling on both sides. Increasing the selection budget can change either seed set. The ranking is computed before selection, so tightening a numerical tolerance can independently change who is eligible. We study both effects and ask when a change of seeds has a measurable consequence for spread. Figure 1 shows the comparison.')
fig('mechanism','Figure 1. Paired seed selection and independent evaluation. Both searches use the same network and selection worlds. Eligibility differs, and the final sets are compared on a shared, separate sample of diffusion worlds.',5.95)
page('2.  EXPERIMENTAL DESIGN')
par('We use three networks from the Stanford Large Network Dataset Collection.{4} CollegeMsg represents messages from sender to recipient.{5} We retain the earliest 65% of distinct timestamps, remove self-messages and collapse repeated arcs. For ca-GrQc, coauthorship links are represented in both directions.{6} Removing self-loops leaves 5,241 vertices because one author occurs only in a self-loop. On wiki-Vote, arcs run from voter to recipient of the vote.{7} We retain all weak components. Every method propagates on the entire processed graph.')
par('Each seed set contains five vertices. Under independent-cascade diffusion, each newly active vertex can activate an inactive out-neighbour with probability 0.01, up to three rounds. In each round of seed selection, greedy search scores every remaining eligible vertex by its total spread across W selection worlds. The full reference admits every vertex. Restricted search admits the top 20 vertices (4k) or the top 5% rounded up. Degree counts distinct out-neighbours. PageRank uses damping 0.85 and default tolerance 10⁻⁶. Ties are resolved by lexicographic order of the original vertex IDs.')
par('Five replicates per graph use nested prefixes of 80, 320 and 1,280 selection worlds. Within a replicate, both searches use the same prefix at each budget. Random draws in the primary design are indexed by world, step and directed edge. A control fixes each edge outcome for the whole world. Both designs use exhaustive enumeration. Evaluation uses 10,000 independent worlds shared across methods and budgets within each graph, replicate and coupling.')
par('We measure incremental spread as the number reached beyond the five seeds. The signed gap is restricted minus full mean spread, in nodes. Percentage loss is minus this gap divided by the reference incremental spread, multiplied by 100 and averaged over replicates. An identical sequence requires all five selections to agree in order. We use the standard deviation across replicates to describe selection variability. Within a replicate the Monte Carlo standard error of a fixed-set gap is the standard deviation of paired world differences divided by the square root of 10,000.')
heading('3.  WHICH CANDIDATES RETAIN THE REFERENCE SPREAD?')
par('At 1,280 selection worlds, the degree pool reproduces every reference sequence across the three networks. Default PageRank with the same 20 candidates reproduces none. Table 1 reports the five-replicate averages. Widening the PageRank pool recovers the reference on ca-GrQc and reduces the loss on both directed graphs.')
table('Table 1. Seed selection at W = 1,280. Spread excludes the five seeds. Gaps are relative to full search, in nodes. Agreement counts exact seed sequences out of five replicates. PR denotes default PageRank.',[
['Graph','Method','Candidates','Spread','Gap','Agreement'],
['ca-GrQc','Full','5,241','4.934','—','—'],['','Degree','20','4.934','0.000','5/5'],['','PR','20','4.683','−0.251','0/5'],['','PR','263','4.934','0.000','5/5'],
['CollegeMsg','Full','1,438','10.072','—','—'],['','Degree','20','10.072','0.000','5/5'],['','PR','20','9.164','−0.908','0/5'],['','PR','72','9.641','−0.431','0/5'],
['wiki-Vote','Full','7,115','55.736','—','—'],['','Degree','20','55.736','0.000','5/5'],['','PR','20','15.043','−40.693','0/5'],['','PR','356','42.206','−13.530','0/5']])
par('At this budget, PageRank-4k and the mean of three random 20-vertex pools each trail full search on all five replicates of every graph. The pre-specified two-sided sign tests give p = 0.0625 before correction and p = 0.1875 after Holm correction within each graph. These comparisons are not statistically significant.')
page('4.  WHEN DOES RANKING PRECISION CHANGE THE COMPARISON?')
par('On ca-GrQc, default PageRank appears to move from a small advantage to a small deficit as the selection budget grows. We revisited this result after inspecting the primary comparisons. Holding each budget, replicate and full reference fixed, we tightened the PageRank tolerance from 10⁻⁶ to 10⁻¹² and raised the iteration cap from 100 to 1,000. Two vertices left the 20-vertex pool (1488 and 19865) and two entered (17655 and 6610). Pool membership stayed the same at 10⁻¹⁴. The exchange changed the final seed set on all five replicates at each budget.')
table('Table 2. Post-hoc PageRank comparison on ca-GrQc. Entries give the mean paired spread gap in nodes (standard deviation across the same five replicates). Positive gaps favour restricted search.',[
['Selection worlds','Default tolerance','Tight tolerance'],['80','+0.236 (0.274)','+0.486 (0.250)'],['320','−0.126 (0.181)','+0.138 (0.174)'],['1,280','−0.251 (0.076)','+0.026 (0.092)']])
par('With the tighter tolerance, the mean gap stays positive, although the final seeds still change in three replicates from 80 to 320 worlds and in two from 320 to 1,280. At the highest budget the individual gaps range from −0.041 to +0.179 nodes. The small positive mean at that budget does not establish a spread advantage. On CollegeMsg both tolerances produce the same pool. On wiki-Vote the strict 20-vertex pool still loses about 74% of incremental spread at each budget (Figure 2).')
fig('precision','Figure 2. Post-hoc PageRank sensitivity across all three networks and budgets. Top panels use 20 candidates and bottom panels use 5% of the vertices. Points show means and bars show standard deviations across the five original replicates. Positive loss indicates lower incremental spread than full search.',6.05)
page('5.  SEED AGREEMENT AND COMPUTATIONAL COST')
small('Changes in the full reference')
par('Between 320 and 1,280 worlds, all five full-reference sets change on ca-GrQc. The mean change in independently evaluated spread is +0.127 nodes, with replicate differences from −0.027 to +0.241. On wiki-Vote some selection orders change, yet the final sets and every paired evaluation count agree. On four smaller contact graphs from the same project, 16 of 40 reference sets change between 1,280 and 5,120 worlds under step coupling, with a mean change of +0.011 nodes. Under fixed-edge coupling, 29 of 40 change between 320 and 1,280 worlds, with a mean change of +0.062 nodes. These two controls cover different budget ranges.')
small('Selection time under candidate restriction')
par('At W = 1,280, searching 20 degree-ranked candidates cuts measured selection time by 98.40–99.67% against exhaustive full search (Table 3). Selection is timed once per method per replicate after warm-up. A separate timing check repeats each method five times in random order at W = 320 on replicate 1101. Adding graph setup, method-specific ranking, both world samples and independent evaluation reduces the estimated saving. These totals combine separately measured components and exclude compilation, downloads and output writing.')
table('Table 3. Mean selection time over five replicates at W = 1,280. The last column gives estimated warm-process savings including preparation and evaluation.',[['Graph','Full (s)','Degree (s)','Selection saving','Assembled saving'],['ca-GrQc','23.53','0.109','99.54%','92.77%'],['CollegeMsg','5.89','0.094','98.40%','86.59%'],['wiki-Vote','158.94','0.520','99.67%','96.26%']])
small('Coverage and seed identity on wiki-Vote')
par('For example, in replicate 1101, full search and the 20-vertex degree pool both choose 2565, 766, 11, 457 and 2688 in that order. Both reach 60.85 vertices on average, including the seeds. A 20-vertex PageRank pool selects 3352, 2237, 2328, 2654 and 1297, reaching 19.94 vertices. Expanding it to 356 vertices admits seed 2565 and raises mean spread to 47.21. This example gives the actual selection output for one run; Table 1 summarises all five replicates.')
par('Pool composition helps explain why two equally sized pools can return different seeds. On wiki-Vote, the top 20 PageRank vertices have mean out-degree 56, compared with 489 for the top 20 degree vertices. Diffusion follows outgoing votes. The PageRank pool omits all five reference seeds on each replicate. Expanding it to 356 vertices admits only one reference seed but raises mean incremental spread from 15.043 to 42.206 nodes. This pattern is consistent with the direction of propagation. Reversing the direction would test that interpretation.')
page('6.  DISCUSSION AND CONCLUSION')
small('Scope of the comparison')
par('The networks are observed, but activation is simulated. The three-round horizon and low activation probability limit inference about longer cascades. Under the fixed-edge control at W = 320, Degree-4k matches one of three full sequences on ca-GrQc and all three on each directed graph. The five primary replicates measure variation on each fixed graph. The measured savings apply to exhaustive greedy selection; the relative costs of a lazy implementation would require a separate comparison.')
small('Implications for evaluation')
par('In these local diffusion experiments, degree screening retained every highest-budget reference sequence, while an equally sized PageRank pool lost up to 40.693 nodes of mean spread. On ca-GrQc, exchanging two candidates removed an apparent change of sign across selection budgets. Reporting the IDs around the ranking cutoff makes that sensitivity inspectable. Evaluating the selected seeds on separate worlds then distinguishes a different search trajectory from a consequential change in spread.')
heading('ACKNOWLEDGEMENTS')
par('This work was supported by a provincial undergraduate innovation and entrepreneurship training project. OpenAI Codex assisted with basic code development and manuscript drafting. The authors take responsibility for the final manuscript.')
heading('REFERENCES')
refs=['Kempe, D., Kleinberg, J. and Tardos, É., “Maximizing the spread of influence through a social network,” Proc. ACM SIGKDD, 137–146 (2003). doi:10.1145/956750.956769.',
'Leskovec, J., Krause, A., Guestrin, C., Faloutsos, C., VanBriesen, J. and Glance, N., “Cost-effective outbreak detection in networks,” Proc. KDD, 420–429 (2007). doi:10.1145/1281192.1281239.',
'Cheng, S., Shen, H., Huang, J., Zhang, G. and Cheng, X., “StaticGreedy: solving the scalability-accuracy dilemma in influence maximization,” Proc. CIKM, 509–518 (2013). doi:10.1145/2505515.2505541.',
'Leskovec, J. and Krevl, A., “SNAP datasets: Stanford large network dataset collection,” Stanford University (2014), https://snap.stanford.edu/data.',
'Panzarasa, P., Opsahl, T. and Carley, K. M., “Patterns and dynamics of users’ behavior and interaction: Network analysis of an online community,” J. Am. Soc. Inf. Sci. Technol. 60, 911–932 (2009). doi:10.1002/asi.21015.',
'Leskovec, J., Kleinberg, J. and Faloutsos, C., “Graph evolution: densification and shrinking diameters,” ACM Trans. Knowl. Discov. Data 1(1), 2 (2007). doi:10.1145/1217299.1217301.',
'Leskovec, J., Huttenlocher, D. and Kleinberg, J., “Signed networks in social media,” Proc. CHI, 1361–1370 (2010). doi:10.1145/1753326.1753532.']
for i,s in enumerate(refs,1):par('['+str(i)+']  '+s,'SPIE body text',10,False,None,0,2)
d.core_properties.title=d.paragraphs[0].text;d.core_properties.author='Jiayue Sun, Binbin Yong, Junjie An, Tianyu Bo, Shuai Li'
d.core_properties.subject='Candidate-restricted influence maximization';d.core_properties.comments=''
d.save(out/'Candidate_restriction.docx')

