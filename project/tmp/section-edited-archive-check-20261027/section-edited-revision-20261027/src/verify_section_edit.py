"""Check editorial preservation against the immediately preceding revision.
No experiment, propagation replay, analysis regeneration or statistical test.
"""
from pathlib import Path
from collections import Counter
import hashlib,json,re,difflib
from PIL import Image

R=Path(__file__).resolve().parents[1]
B=R.parent/'historical-evidence-revision-20261027'
Q=R/'qa'; Q.mkdir(exist_ok=True)
def text(p): return p.read_text(encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def section(x,s,t): return x.split('\\section{'+s+'}')[1].split('\\section{'+t+'}')[0]
def numbers(x):
    # Ignore extra mentions of method names (e.g. PageRank-4k), not data values.
    return Counter(re.findall(r'(?<![A-Za-z])\d+(?:\.\d+)?',re.sub(r'\b[248]k\b','',x)))
def maths(x): return Counter(re.findall(r'\$(.*?)\$|\\begin\{equation\}(.*?)\\end\{equation\}',x,re.S))
def refs(x): return {m.group(1):m.group(0).strip() for m in re.finditer(r'\\bibitem\{([^}]+)\}.*?(?=\\bibitem|\\end\{thebibliography\})',x,re.S)}
def pixels(p):
    with Image.open(p) as im:return (im.size,hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest())
a=text(B/'manuscript/manuscript.tex');z=text(R/'manuscript/manuscript.tex')
report={'status':'PASS','base_revision':str(B),'new_experiments':False,'new_analysis_or_simulation_replay':False}
for s,t in [('Methods','Experimental setup'),('Experimental setup','Results'),('Results','Discussion')]:
    x,y=section(a,s,t),section(z,s,t)
    assert numbers(x)==numbers(y),(s,numbers(x)-numbers(y),numbers(y)-numbers(x))
    report[s]={'numeric_token_multiset_identical':True,'old_whitespace_tokens':len(x.split()),'new_whitespace_tokens':len(y.split())}
    if s!='Results':
        assert maths(x)==maths(y),s
        report[s]['math_expressions_identical']=True
for s,t in [('Introduction','Related work'),('Related work','Methods'),('Discussion','Conclusion')]:
    report[s]={'old_whitespace_tokens':len(section(a,s,t).split()),'new_whitespace_tokens':len(section(z,s,t).split())}
for token,end in [(r'\begin{abstract}',r'\end{abstract}'),(r'\author{',r'\date{}'),(r'\section*{Statements and Declarations}',r'\end{document}')]:
    assert a.split(token)[1].split(end)[0]==z.split(token)[1].split(end)[0],token
report['abstract_authors_and_declarations_unchanged']=True
assert refs(text(B/'manuscript/references.tex'))==refs(text(R/'manuscript/references.tex'))
report['bibliography_metadata_identical']=True
protected={}
for folder in ['analysis','manuscript']:
    for p in (B/folder).rglob('*'):
        if not p.is_file():continue
        relative=p.relative_to(B)
        if folder=='manuscript' and (p.name in ['manuscript.tex','manuscript.pdf','references.tex','Online_Resource_1.pdf'] or p.suffix in ['.aux','.log','.out']):continue
        q=R/relative; assert q.exists() and sha(p)==sha(q),str(relative)
        protected[str(relative)]=sha(p)
report['protected_files_sha256']=protected
required=['same-budget full reference','mean high-minus-low budget gain','within-graph Holm $p=.1875$',
          'neither statistical equivalence nor absence of loss','conditional Monte Carlo','does not isolate a causal mechanism',
          'repeated computations, not independent success trials','do not test the joint effect',
          'Strict-tolerance results are used only for quality sensitivity','neither expected-optimality nor convergence']
assert all(s in z for s in required)
report['result_comparator_and_boundary_checks']=required
report['supplement_source_identical']=sha(B/'manuscript/Online_Resource_1.tex')==sha(R/'manuscript/Online_Resource_1.tex')
oldrender=B/'qa/render-final/Online_Resource_1';newrender=Q/'render-final/Online_Resource_1'
if newrender.exists():
    checked=[]
    for i in range(1,27):
        name=f'page-{i:02}.png';assert pixels(oldrender/name)==pixels(newrender/name),name;checked.append(i)
    report['supplement_render_pixels_identical_pages']=checked
diff=[]
for n in ['manuscript.tex','references.tex']:
    diff.extend(difflib.unified_diff(text(B/'manuscript'/n).splitlines(True),text(R/'manuscript'/n).splitlines(True),fromfile='historical-evidence-revision-20261027/manuscript/'+n,tofile='section-edited-revision-20261027/manuscript/'+n))
(R/'manuscript_changes.diff').write_text(''.join(diff),encoding='utf-8')
(Q/'section_edit_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='protected_files_sha256'},ensure_ascii=False,indent=2))
