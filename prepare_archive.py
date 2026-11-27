"""Preserve project files with hashes, exclusions, secret checks and chunking."""
import os, re, json, hashlib, zipfile, io, collections
from pathlib import Path

SOURCE = Path(r'D:\校创\基于GNN的关键用户识别')
DEST = Path(__file__).resolve().parent
SKIP = {'.git', 'node_modules', '__pycache__', '.venv', 'venv'}
PATTERNS = [rb'gh[pousr]_[A-Za-z0-9]{30,}', rb'github_pat_[A-Za-z0-9_]{50,}', rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', rb'AKIA[0-9A-Z]{16}', rb'sk-(?:proj-)?[A-Za-z0-9_-]{40,}']
SECRET = re.compile(b'|'.join(PATTERNS))
ASSIGN = re.compile(rb'''(?im)^\s*["']?(?:password|passwd|api_key|secret_key|access_token|auth_token)["']?\s*[:=]\s*["']([^"'\r\n]{8,})["']''')

def suspect(data, name, depth=0):
    if SECRET.search(data):
        return 'credential signature'
    if name.lower().endswith(('.json','.yaml','.yml','.toml','.ini','.env','.cfg')) and ASSIGN.search(data):
        return 'credential assignment; requires manual review'
    if depth < 4 and name.lower().endswith(('.zip','.docx','.pptx','.xlsx','.vsdx','.whl')):
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                for i in z.infolist():
                    if not i.is_dir():
                        found=suspect(z.read(i),i.filename,depth+1)
                        if found: return 'archive member: '+i.filename+'; '+found
        except zipfile.BadZipFile:
            if data.lstrip().lower().startswith((b'<!doctype html',b'<html')):return None
            return 'archive could not be inspected'
        except RuntimeError:return 'archive could not be inspected'
    return None

def main():
    inventory=[]; excluded=[]; chunks=[]; counts=collections.Counter()
    root='\\\\?\\'+str(SOURCE)
    for directory, dirs, files in os.walk(root):
        for n in list(dirs):
            if n in SKIP:
                excluded.append({'path':os.path.relpath(os.path.join(directory,n),root),'reason':'reinstallable dependencies or generated cache / Git metadata'})
                dirs.remove(n)
        for name in files:
            if '申报' in name or name=='temp_docx_content.txt':continue
            p=os.path.join(directory,name); rel=os.path.relpath(p,root).replace('\\','/')
            data=Path(p).read_bytes(); digest=hashlib.sha256(data).hexdigest()
            reason='local credential file' if name in ('.env','.npmrc','.pypirc','id_rsa','id_ed25519') and (name!='.npmrc' or b'_auth' in data) else suspect(data,name)
            if reason:
                excluded.append({'path':rel,'reason':reason,'size':len(data),'sha256':digest});continue
            record={'path':rel,'size':len(data),'sha256':digest,'storage':'project/'+rel}
            if len(data)>90*1024**2:
                pieces=[]
                for j,start in enumerate(range(0,len(data),48*1024**2)):
                    part=f'large-files/{digest}/part-{j:04d}';target=DEST/part;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data[start:start+48*1024**2]);pieces.append(part)
                record['storage']=pieces;chunks.append(record)
            else:
                target=Path('\\\\?\\'+str(DEST/'project'/rel));target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
            inventory.append(record);counts[rel.split('/')[0]]+=1
            if len(inventory)%1000==0: print('Archived',len(inventory),flush=True)
    for n,obj in [('inventory.json',inventory),('excluded.json',excluded),('large-files.json',chunks)]:
        (DEST/n).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'files':len(inventory),'bytes':sum(r['size'] for r in inventory),'excluded':len(excluded),'split':len(chunks),'groups':counts},ensure_ascii=True),flush=True)

if __name__=='__main__':main()
