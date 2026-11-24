"""Author-approved title change only; archive previous sources and PDFs."""
from pathlib import Path
import sys,shutil,json,hashlib,re,subprocess
from pypdf import PdfReader
R=Path(__file__).resolve().parents[1];Q=R/'qa/title-amendment-20261029'
OLD='Reference Budgets and Ranking Precision in Candidate-Restricted Influence Maximization'
NEW='Evaluating Candidate-Restricted Influence Maximization: Effects of Reference Budget and Ranking Precision'
OZH='候选受限影响力最大化中的参照预算与排名精度'
NZH='候选受限影响力最大化的评价：参照预算与排名精度的影响'
items=[('english','manuscript/manuscript',OLD,NEW,'Reference budgets and ranking precision','Evaluating candidate-restricted influence maximization'),('chinese','chinese/manuscript/manuscript_zh',OZH,NZH,'参照预算与排名精度','候选受限影响力最大化的评价'),('supplement','manuscript/Online_Resource_1',OLD,NEW,None,None)]
def update(t,a,b,c,d):
    t=t.replace(a,b)
    return t.replace('\\titlerunning{'+c+'}','\\titlerunning{'+d+'}') if c else t
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if '--apply' in sys.argv:
    Q.mkdir(parents=True,exist_ok=False)
    for lang,stem,a,b,c,d in items:
        for ext in ['.tex','.pdf']:shutil.copy2(R/(stem+ext),Q/(lang+'_before'+ext))
        p=R/(stem+'.tex');t=p.read_text(encoding='utf-8');assert a in t
        p.write_text(update(t,a,b,c,d),encoding='utf-8')
    for name in ['summary_for_editor.txt','cover_letter_draft.txt']:
        p=R/name;shutil.copy2(p,Q/name);t=p.read_text(encoding='utf-8');assert OLD in t;p.write_text(t.replace(OLD,NEW),encoding='utf-8')
    with (R/'README.md').open('a',encoding='utf-8') as f:f.write('\n## 2026-10-29 作者确认题名\n\n英文：'+NEW+'\n\n中文：'+NZH+'\n\n正文、中文译稿、英文补充材料、editor summary 与 cover letter 已同步题名。仅改题名和页眉短标题；研究内容不变。当前PDF核验见 qa/title-amendment-20261029/verification.json，之前的QA和PDF哈希属于对应历史版本。更名前文件保存在本次QA目录。\n')
if '--verify' in sys.argv:
    checks={}
    for lang,stem,a,b,c,d in items:
        source=(R/(stem+'.tex')).read_text(encoding='utf-8');prior=(Q/(lang+'_before.tex')).read_text(encoding='utf-8')
        assert source==update(prior,a,b,c,d)
        pdf=R/(stem+'.pdf');reader=PdfReader(pdf);text='\n'.join(p.extract_text() or '' for p in reader.pages)
        normalized=lambda x:re.sub(r'\s+','',x)
        assert normalized(b) in normalized(reader.pages[0].extract_text())
        assert '??' not in text
        log=(R/(stem+'.log')).read_text(encoding='utf-8',errors='replace')
        issues=[l for l in log.splitlines() if re.search(r'Overfull|Missing character|undefined|Rerun to get|Fatal error',l)]
        assert not issues,issues
        subprocess.run(['pdftoppm','-f','1','-l','2','-r','110','-png',str(pdf),str(Q/lang)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        checks[lang]={'only_title_and_running_title_changed':True,'pages':len(reader.pages),'prior_pages':len(PdfReader(Q/(lang+'_before.pdf')).pages),'pdf_sha256':sha(pdf),'compile_issues':issues}
    checks['editorial_titles_match']=all(NEW in (R/n).read_text(encoding='utf-8') and OLD not in (R/n).read_text(encoding='utf-8') for n in ['summary_for_editor.txt','cover_letter_draft.txt'])
    assert checks['editorial_titles_match']
    (Q/'verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(checks))
