"""Preserve primary publisher-deposited metadata; no guessed bibliography entries."""
from pathlib import Path
import re,json,urllib.request,urllib.parse,concurrent.futures,time
R=Path(__file__).resolve().parents[1];old=R.parents[1]/'computing-strengthening-20261015/manuscript/manuscript.tex'
text=old.read_text(encoding='utf-8');items=dict(re.findall(r'\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem|\\end\{thebibliography\})',text,re.S))
used=set(k.strip() for x in re.findall(r'\\cite\{([^}]+)\}',(R/'manuscript/manuscript.tex').read_text(encoding='utf-8')) for k in x.split(','))
new={
'college':r"Panzarasa P, Opsahl T, Carley KM (2009) Patterns and dynamics of users' behavior and interaction: Network analysis of an online community. Journal of the American Society for Information Science and Technology 60:911--932. \url{https://doi.org/10.1002/asi.21015}",
'grqc':r'Leskovec J, Kleinberg J, Faloutsos C (2007) Graph evolution: densification and shrinking diameters. ACM Transactions on Knowledge Discovery from Data 1(1):2. \url{https://doi.org/10.1145/1217299.1217301}',
'signed':r'Leskovec J, Huttenlocher D, Kleinberg J (2010) Signed networks in social media. In: CHI, pp 1361--1370. \url{https://doi.org/10.1145/1753326.1753532}',
'links':r'Leskovec J, Huttenlocher D, Kleinberg J (2010) Predicting positive and negative links in online social networks. In: WWW, pp 641--650. \url{https://doi.org/10.1145/1772690.1772756}',
'snap':r'Leskovec J, Krevl A (2014) SNAP datasets: Stanford large network dataset collection. \url{https://snap.stanford.edu/data}. Accessed 15 October 2026',
'networkxpr':r'NetworkX developers (2025) PageRank, NetworkX 3.5 documentation. \url{https://networkx.org/documentation/networkx-3.5/reference/algorithms/generated/networkx.algorithms.link_analysis.pagerank_alg.pagerank.html}. Accessed 15 October 2026'}
items.update(new);order=list(dict.fromkeys(k.strip() for x in re.findall(r'\\cite\{([^}]+)\}',(R/'manuscript/manuscript.tex').read_text(encoding='utf-8')) for k in x.split(',')))
cachefile=R/'audit/reference_metadata.json'
records=json.loads(cachefile.read_text(encoding='utf-8')) if cachefile.exists() else {}
def fetch(k):
    if k in records and records[k]['status']=='metadata-retrieved': return k,records[k]
    entry=items[k].strip();m=re.search(r'https://doi.org/([^}]+)',entry)
    if not m:return k,{'entry':entry,'status':'official-web-reference','url':re.search(r'\\url\{([^}]+)',entry).group(1)}
    doi=m.group(1);url='https://api.crossref.org/works/'+urllib.parse.quote(doi,safe='')
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'LocalResearchAudit/1.0'})
            with urllib.request.urlopen(req,timeout=45) as f:md=json.load(f)['message']
            return k,{'entry':entry,'doi':doi,'status':'metadata-retrieved','metadata':{key:md.get(key) for key in ['title','author','published','container-title','volume','issue','page','article-number','DOI','URL']}}
        except Exception as e:
            error=repr(e)
            time.sleep(1)
    return k,{'entry':entry,'doi':doi,'status':'retrieval-failed','error':error}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for key,result in pool.map(fetch,order): records[key]=result;print(key,result['status'],result.get('metadata',{}).get('title'),flush=True)
(R/'audit/reference_metadata.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'manuscript/references.tex').write_text('\\begin{thebibliography}{99}\n'+'\n\n'.join('\\bibitem{'+k+'} '+items[k].strip() for k in order)+'\n\\end{thebibliography}\n',encoding='utf-8')
