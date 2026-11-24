from pathlib import Path
import urllib.request, json, zipfile, concurrent.futures
work=Path(__file__).parent
def fetch(url, path):
    req=urllib.request.Request(url,headers={'User-Agent':'Codex manuscript formatting'})
    with urllib.request.urlopen(req,timeout=45) as r:
        data=r.read()
    path.write_bytes(data)
    return len(data)
def template():
    path=work/'springer-svjour3.zip'
    urls=[
      'https://static.springer.com/sgw/documents/468198/application/zip/LaTeX_DL_468198_240419.zip',
      'https://static-content.springer-cdn.com/author-guidelines/LaTeX_DL_468198_240419.zip',
      'https://resource-cms.springernature.com/springer-cms/rest/v1/content/468198/data/v1',
    ]
    for url in urls:
        try:
            size=fetch(url,path)
            with zipfile.ZipFile(path) as z:
                names=z.namelist()
                assert any(n.endswith('svjour3.cls') for n in names),names
                z.extractall(work/'springer-template')
            (work/'springer-template-source.txt').write_text(url,encoding='utf-8')
            return {'template':url,'bytes':size,'files':names}
        except Exception as e: print('Template attempt:',url,str(e),flush=True)
    raise RuntimeError('No official svjour3 archive retrieved')
def pandoc():
    meta=work/'pandoc-release.json'
    fetch('https://api.github.com/repos/jgm/pandoc/releases/latest',meta)
    release=json.loads(meta.read_text(encoding='utf-8'))
    asset=next(a for a in release['assets'] if a['name'].endswith('windows-x86_64.zip'))
    path=work/'pandoc.zip'
    size=fetch(asset['browser_download_url'],path)
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if name.endswith('pandoc.exe'):
                z.extract(name,work/'pandoc')
    return {'pandoc':release['tag_name'],'bytes':size,'path':str(next((work/'pandoc').rglob('pandoc.exe')))}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    futures=[pool.submit(template),pool.submit(pandoc)]
    for future in concurrent.futures.as_completed(futures):
        try: print(json.dumps(future.result(),ensure_ascii=False),flush=True)
        except Exception as e: print('DOWNLOAD FAILED:',str(e),flush=True)
