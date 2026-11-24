"""Apply the author's annotated section-heading correction; preserve prior PDFs."""
from pathlib import Path
import shutil,json,hashlib,sys,subprocess,re
from pypdf import PdfReader
R=Path(__file__).resolve().parents[1]
Q=R/'qa/heading-amendment-20261029'
pairs=[('english','manuscript/manuscript','What a budget comparison can establish','Interpretation and limits of reference-budget effects'),('chinese','chinese/manuscript/manuscript_zh','预算比较能够支持什么判断','参照预算效应的解释边界')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if '--apply' in sys.argv:
    Q.mkdir(parents=True,exist_ok=False)
    for lang,stem,old,new in pairs:
        for suffix in ['.tex','.pdf']:shutil.copy2(R/(stem+suffix),Q/(lang+'_before'+suffix))
        p=R/(stem+'.tex');t=p.read_text(encoding='utf-8');assert t.count('\\subsection{'+old+'}')==1
        p.write_text(t.replace('\\subsection{'+old+'}','\\subsection{'+new+'}'),encoding='utf-8')
if '--verify' in sys.argv:
    checks={}
    for lang,stem,old,new in pairs:
        source=(R/(stem+'.tex')).read_text(encoding='utf-8');prior=(Q/(lang+'_before.tex')).read_text(encoding='utf-8')
        assert source==prior.replace('\\subsection{'+old+'}','\\subsection{'+new+'}')
        pdf=R/(stem+'.pdf');pages=PdfReader(pdf).pages
        log=(R/(stem+'.log')).read_text(encoding='utf-8',errors='replace')
        issues=[l for l in log.splitlines() if re.search(r'Overfull|Missing character|undefined|Rerun to get|Fatal error',l)]
        assert not issues,issues
        matched=[]
        for i,p in enumerate(pages,1):
            t=p.extract_text() or ''
            assert '??' not in t
            if new in t or new.replace('-','') in t.replace('-',''):matched.append(i)
        assert len(matched)==1,matched
        pg=matched[0]
        subprocess.run(['pdftoppm','-f',str(pg),'-l',str(pg),'-r','120','-png',str(pdf),str(Q/lang)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        checks[lang]={'only_heading_changed':True,'pages':len(pages),'changed_heading_page':pg,'pdf_sha256':sha(pdf),'compile_issues':issues}
    checks['new_experiments']=False
    (Q/'verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(checks,ensure_ascii=True))
