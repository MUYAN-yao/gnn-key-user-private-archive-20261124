"""Read-only publisher/API fetches; writes provenance into the working package."""
from pathlib import Path
import json
import concurrent.futures
import requests
import re
import html
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def get(url):
    session=requests.Session()
    session.mount("https://",HTTPAdapter(max_retries=Retry(total=3,backoff_factor=1,status_forcelist=[429,500,502,503])))
    return session.get(url,timeout=30)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"manuscript/resolution_aware_candidate_truncation_submission_v0_1/literature"
OUT.mkdir(exist_ok=True)
DOIS=[
 "10.1145/1281192.1281239", "10.1145/2505515.2505541",
 "10.1109/TKDE.2018.2807843", "10.1145/3604559",
 "10.1007/s41109-024-00625-3", "10.1007/s00607-019-00778-5",
 "10.1007/s00607-023-01207-4", "10.1007/s40747-024-01666-y",
 "10.1038/s41562-018-0346-z", "10.1145/3035918.3035924",
]
def fetch(doi):
    key=doi.replace("/","_")
    url="https://api.crossref.org/works/"+doi
    if (OUT/(key+".json")).exists():
        meta=json.loads((OUT/(key+".json")).read_text(encoding="utf-8"))
    else:
        r=get(url);r.raise_for_status()
        meta=r.json()["message"]
    (OUT/(key+".json")).write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
    if not (OUT/(key+".bib")).exists():
        try:
            bib=get(url+"/transform/application/x-bibtex")
            if bib.ok: (OUT/(key+".bib")).write_text(bib.text,encoding="utf-8")
        except requests.RequestException as exc:
            print(json.dumps({"bibtex_error":doi,"error":str(exc)}),flush=True)
    return {"doi":doi,"title":meta["title"],"year":meta.get("published"),"abstract":meta.get("abstract",""),
            "authors":meta.get("author"),"venue":meta.get("container-title"),"volume":meta.get("volume"),
            "page":meta.get("page"),"article-number":meta.get("article-number"),"bibtex":(OUT/(key+".bib")).exists()}

results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for doi,r in zip(DOIS,pool.map(fetch,DOIS)):
        results.append(r);print(json.dumps({"doi":doi,"title":r["title"],"bibtex":r["bibtex"]}),flush=True)
(OUT/"verified_metadata.json").write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding="utf-8")
(OUT/"references_added.bib").write_text("\n".join((OUT/(d.replace("/","_")+".bib")).read_text(encoding="utf-8") for d in DOIS if (OUT/(d.replace("/","_")+".bib")).exists()),encoding="utf-8")

for doi in ["10.1007/s00607-019-00778-5","10.1007/s00607-023-01207-4","10.1007/s00607-025-01429-8"]:
    r=get("https://link.springer.com/article/"+doi)
    if not r.ok: continue
    key=doi.replace("/","_")
    (OUT/(key+".html")).write_text(r.text,encoding="utf-8")
    text=html.unescape(re.sub("<[^>]+>"," ",r.text))
    (OUT/(key+".txt")).write_text(text,encoding="utf-8")
    images=re.findall(r'<img[^>]+src="([^"]+)"',r.text)
    images=[s for s in images if "Fig" in s]
    for i,src in enumerate(images[:2]):
        if src.startswith("//"):src="https:"+src
        if not src.startswith("https://media.springernature.com/"):continue
        data=get(src)
        if data.ok:(OUT/(key+f"_style_reference_{i+1}.png")).write_bytes(data.content)
    print(json.dumps({"style_paper":doi,"images":len(images),"headings":[html.unescape(re.sub("<[^>]+>","",h)) for h in re.findall(r"<h2[^>]*>(.*?)</h2>",r.text,re.S)]}),flush=True)
