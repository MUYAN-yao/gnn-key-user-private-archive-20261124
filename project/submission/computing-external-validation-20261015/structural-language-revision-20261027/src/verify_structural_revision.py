"""Read-only scientific preservation checks; write QA/diff, never import a runner."""
from pathlib import Path
from collections import Counter
import difflib, hashlib, json, re
R=Path(__file__).resolve().parents[1]
B=R.parent/'section-edited-revision-20261027'
M=R/'manuscript'; Q=R/'qa'
def read(p):return p.read_text(encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def normalized(s):
    for x in ('Degree','degree','PageRank','Weighted','random'):
        s=s.replace(x+'-',x+' ')
    return s
def nums(s):return re.findall(r'(?<![A-Za-z])-?\d+(?:\.\d+)?',normalized(s))
def section(s,a,b):return s.split('\\section{'+a+'}',1)[1].split('\\section{'+b+'}',1)[0]
old=read(B/'manuscript/manuscript.tex');new=read(M/'manuscript.tex')
checks={}
old_results=section(old,'Results','Discussion');new_results=section(new,'Results','Discussion')
# The precision caption repeats 10^-12 to specify the two compared cutoffs.
# Compare result prose exactly, and check captions for newly introduced values.
checks['result_prose_numeric_sequence_identical']=nums(re.sub(r'\\begin\{figure\}.*?\\end\{figure\}','',old_results,flags=re.S))==nums(re.sub(r'\\begin\{figure\}.*?\\end\{figure\}','',new_results,flags=re.S))
checks['result_caption_no_new_numeric_values']=set(nums(new_results))<=set(nums(old_results))
checks['displayed_equations_identical']=re.findall(r'\\begin\{equation\}(.*?)\\end\{equation\}',old,re.S)==re.findall(r'\\begin\{equation\}(.*?)\\end\{equation\}',new,re.S)
checks['methods_math_identical']=re.findall(r'\$(.*?)\$',section(old,'Methods','Experimental setup'),re.S)==re.findall(r'\$(.*?)\$',section(new,'Methods','Experimental setup'),re.S)
checks['author_identity_identical']=old.split('\\author{')[1].split('\\date{}')[0]==new.split('\\author{')[1].split('\\date{}')[0]
checks['declarations_identical']=old.split('\\section*{Statements and Declarations}')[1]==new.split('\\section*{Statements and Declarations}')[1]
checks['ai_disclosure_identical']=re.findall(r'\\footnote\{OpenAI Codex[^}]+\}',old)==re.findall(r'\\footnote\{OpenAI Codex[^}]+\}',new)
checks['preprocessing_numeric_sequence_identical']=nums(old.split('\\subsection{Networks and preprocessing}')[1].split('\\subsection')[0])==nums(new.split('\\subsection{Networks and preprocessing}')[1].split('\\subsection')[0])
checks['external_settings_table_identical']=old.split('\\label{tab:settings}')[1].split('\\end{table}')[0]==new.split('\\label{tab:settings}')[1].split('\\end{table}')[0]
tables={}
for p in sorted(M.glob('*table*.tex')):
    prev=B/'manuscript'/p.name
    if not prev.exists() or p.name=='related_work_table.tex':continue
    a=read(prev);b=read(p)
    # Only data rows, not column labels/captions; normalize method punctuation.
    def data(s):
        if '\\endhead' in s:return s.split('\\endfoot',1)[1].split('\\end{longtable}',1)[0]
        return '\n'.join(re.findall(r'\\midrule(.*?)\\bottomrule',s,re.S))
    tables[p.name]=nums(data(a))==nums(data(b))
checks['all_table_data_preserved']=all(tables.values())
protected={}
for p in (B/'analysis').rglob('*'):
    if p.is_file():protected[str(p.relative_to(B))]=sha(p)==sha(R/p.relative_to(B))
for p in (B/'manuscript').iterdir():
    if p.is_file() and (p.suffix in ('.png','.svg','.cls','.clo') or p.suffix=='.pdf' and p.stem not in ('manuscript','Online_Resource_1') or p.name=='numbers.tex'):
        protected[str(p.relative_to(B))]=sha(p)==sha(R/p.relative_to(B))
checks['all_saved_analysis_and_figure_assets_preserved']=all(protected.values())
text='\n'.join(read(p) for p in M.glob('*.tex') if p.name!='references.tex')
bad=['stricter ranking','disjoint utility','expected-optimality','Verify saving','Incremental spread subtracts five','The present integration','The earlier historical Fig4']
checks['targeted_ambiguous_phrases_removed']=not any(x in text for x in bad)
si=read(M/'Online_Resource_1.tex')
checks['relocated_hash_details_retained']=all(x in si for x in ['SHA-256','63 bits','namespace|dataset|path|family|i','default\\_rng'])
checks['replay_and_acceptance_details_retained']=all(x in si for x in ['representative','\\texttt{all}','\\texttt{none}','10,000 evaluation counts','10^{-12}','decoded PNG pixels','fresh \\texttt{--output}'])
checks['general_incremental_spread_definition_present']='For a seed set of size $k$, incremental spread is total spread minus $k$.' in si
checks['known_preprocessing_and_hash_limitations_retained']=all(x in si for x in ['retrospective comparison','12295','ambiguous about endpoint collection order'])
checks['pool_stability_not_vector_certificate']='not exact convergence of the PageRank vector' in new
diff=[]
for p in sorted(M.glob('*.tex')):
    prev=B/'manuscript'/p.name
    if prev.exists():diff.extend(difflib.unified_diff(read(prev).splitlines(True),read(p).splitlines(True),fromfile='section-edited/manuscript/'+p.name,tofile='structural-language/manuscript/'+p.name))
(R/'manuscript_changes.diff').write_text(''.join(diff),encoding='utf-8')
report={'status':'PASS' if all(checks.values()) else 'FAIL','baseline':str(B),'new_experiments':False,'runner_or_simulator_replay_executed':False,'analysis_regeneration_executed':False,'checks':checks,'table_numeric_data':tables,'protected_files':protected,'notes':['Checks compare this revision with the directly preceding saved revision.','Historical raw-array checks and representative reruns are inherited evidence, not repeated here.','Method-label hyphens are normalized before numerical token comparison.','Main hash-construction detail was relocated to the existing SI executable procedure; no experimental setting was changed.']}
(Q/'structural_revision_checks.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'status':report['status'],'checks':checks,'protected_files':len(protected),'numeric_tables':len(tables)},indent=2))
if report['status']!='PASS':raise SystemExit(1)
