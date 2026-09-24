import pathlib,json,hashlib,subprocess,shutil

sources=json.loads(pathlib.Path('migration/sources.json').read_text())
mapping=json.loads(pathlib.Path('migration/mapping.json').read_text())
records=[]
for repo,prefix in mapping.items():
    source=sources[repo]
    checkout=pathlib.Path('/tmp/lab-import')/repo
    subprocess.run(['git','clone','--quiet','https://github.com/yunsBRB/'+repo+'.git',str(checkout)],check=True)
    subprocess.run(['git','-C',str(checkout),'checkout','--quiet',source['commit']],check=True)
    files=[]
    for e in source['tree']:
        if e['type']!='blob': continue
        p=e['path'];parts=pathlib.PurePosixPath(p).parts
        if any(x in parts for x in ['bin','obj','.idea','.vs','.github']):continue
        if p.endswith(('.iml','.class','.slnx','.slnf')) or p.startswith('.') or p.lower()=='readme.md':continue
        if repo=='2048-game':p=p.removeprefix('2048 game/')
        if repo=='ExoCompteCourant':p=p.removeprefix('ExoCompteCourant/')
        content=(checkout/e['path']).read_bytes()
        sha=hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
        if sha!=e['sha']:raise ValueError('Source changed: '+repo+'/'+e['path'])
        dest=pathlib.Path(prefix)/p
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(content)
        files.append({'source':e['path'],'destination':str(dest),'git_blob_sha':sha})
    records.append({'repository':'https://github.com/yunsBRB/'+repo,'commit':source['commit'],'files':files})
pathlib.Path('SOURCES.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
print('Verified and imported',sum(len(r['files']) for r in records),'files')
