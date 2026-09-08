"""Shared sourced mechanics. Authored JSON/prose is authority; SQLite FTS is disposable."""
import json,re,sqlite3
from pathlib import Path
from .core import Error,atomic_json,digest,lock,now,read_json,require_fields,slug

STATUSES={'sourced','corroborated','disputed','retired'}

def validate(record):
    require_fields(record,('id','title','kind','topics','summary','body','sources','applicability','status','reviewed_at','review'))
    slug(record['id'])
    if record['kind'] not in ('game_mechanic','tool_contract','general_guidance') or record['status'] not in STATUSES:
        raise Error('Explicit mechanics kind and evidence status required.')
    if not isinstance(record['topics'],list) or not record['topics'] or not all(isinstance(t,str) and t for t in record['topics']):
        raise Error('Supply searchable topics.')
    if not isinstance(record['applicability'],dict):raise Error('Record game/DLC/mod applicability.')
    if not isinstance(record['sources'],list) or not record['sources']:raise Error('Mechanics require sources, not recollection alone.')
    for s in record['sources']:
        if not isinstance(s,dict) or not s.get('source') or not s.get('checked_at') or not s.get('supports'):
            raise Error('Each source needs source, checked_at and supported claim.')
    if any(not isinstance(record[k],str) or not record[k].strip() for k in ('title','summary','body','reviewed_at','review')):
        raise Error('Mechanics need substantive prose and review.')
    if any(k in record for k in ('campaign_id','session_id','pawn_id','current_state')):
        raise Error('Campaign state belongs in campaign evidence, not global mechanics.')
    if record['status']=='corroborated' and len({s['source'] for s in record['sources']})<2:
        raise Error('Corroborated mechanics need independent sources; review independence explicitly.')
    return record

def save(root,record):
    record = {k:v for k,v in record.items() if k != "revision"}
    validate(record);base=Path(root)/'knowledge/mechanics';base.mkdir(parents=True,exist_ok=True)
    with lock(base/'.bank.lock'):
        path=base/(record['id']+'.json')
        old=read_json(path) if path.exists() else None
        if old:
            archive=base/'revisions'/record['id']/(digest(old)+'.json')
            atomic_json(archive,old)
        value=dict(record,revision=digest(record));atomic_json(path,value)
    return {'id':value['id'],'revision':value['revision'],'path':str(path),'game_changed':False}

def applicability(record,environment=None):
    a=record['applicability'];env=environment or {};reasons=[]
    versions=a.get('game_versions',[]);version=env.get('game_version')
    if versions and (not version or not any(str(version)==v or str(version).startswith(v+'.') for v in versions)):
        reasons.append('Game version compatibility unverified')
    for key,envkey in [('required_dlc','dlc'),('required_mods','mods')]:
        required={str(x).lower() for x in a.get(key,[])};actual={str(x).lower() for x in env.get(envkey,[])}
        if required-actual:reasons.append('Required '+envkey+' unverified: '+', '.join(sorted(required-actual)))
    if a.get('mod_caveat'):reasons.append(a['mod_caveat'])
    return {'status':'check_required' if reasons else 'declared_scope_matches','cautions':reasons,
            'basis':'Declared applicability, not live mechanical verification'}

def _connect(root):
    root=Path(root);base=root/'knowledge/mechanics';base.mkdir(parents=True,exist_ok=True)
    cache=root/'.runtime/mechanics.sqlite';cache.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(cache,timeout=15)
    try:
        db.execute('CREATE TABLE IF NOT EXISTS docs (id TEXT PRIMARY KEY, mtime INTEGER, size INTEGER, value TEXT)')
        db.execute('CREATE VIRTUAL TABLE IF NOT EXISTS search USING fts5(id UNINDEXED,title,topics,summary,body)')
        paths={p.stem:p for p in base.glob('*.json')}
        prior={row[0]:row[1:] for row in db.execute('SELECT id,mtime,size FROM docs')}
        with db:
            for id in set(prior)-set(paths):
                db.execute('DELETE FROM docs WHERE id=?',(id,));db.execute('DELETE FROM search WHERE id=?',(id,))
            for id,p in paths.items():
                st=p.stat()
                if prior.get(id)==(st.st_mtime_ns,st.st_size):continue
                r=validate(read_json(p))
                if r['id']!=id:raise Error('Mechanics filename/id mismatch: '+id)
                db.execute('INSERT OR REPLACE INTO docs VALUES (?,?,?,?)',(id,st.st_mtime_ns,st.st_size,json.dumps(r)))
                db.execute('DELETE FROM search WHERE id=?',(id,))
                db.execute('INSERT INTO search VALUES (?,?,?,?,?)',(id,r['title'],' '.join(r['topics']),r['summary'],r['body']))
        return db
    except BaseException:
        db.close();raise

def search(root,query='',id=None,limit=8,environment=None):
    if type(limit) is not int or not 1<=limit<=100:raise Error('Use an explicit 1–100 result limit.')
    base=Path(root)/'knowledge/mechanics';base.mkdir(parents=True,exist_ok=True)
    with lock(base/'.bank.lock'):
        db=_connect(root)
        try:
            if id:
                slug(id);row=db.execute('SELECT value FROM docs WHERE id=?',(id,)).fetchone()
                if not row:raise Error('Mechanics record not found: '+id)
                r=json.loads(row[0]);return {'record':r,'revision':r.get('revision',digest(r)),'applicability_check':applicability(r,environment),'live_checked':False}
            terms=re.findall(r'\w+',query.lower())
            match=' OR '.join('"'+t+'"' for t in terms)
            if terms:
                sql='SELECT d.value FROM search s JOIN docs d ON d.id=s.id WHERE search MATCH ? ORDER BY bm25(search),d.id'
                values=(match,)
                count=db.execute('SELECT count(*) FROM search WHERE search MATCH ?',values).fetchone()[0]
            else:sql='SELECT value FROM docs ORDER BY id';values=();count=db.execute('SELECT count(*) FROM docs').fetchone()[0]
            rows=db.execute(sql+' LIMIT ?',(*values,limit)).fetchall()
            cards=[]
            for row in rows:
                r=json.loads(row[0]);cards.append({k:r[k] for k in ('id','title','kind','summary','status','reviewed_at')})
                cards[-1].update(revision=r.get('revision',digest(r)),sources=r['sources'],applicability_check=applicability(r,environment))
            return {'query':query,'matches':cards,'total_matches':count,'remaining':max(0,count-len(cards)),
                    'live_checked':False,'detail':'mechanics --id ID; disputed/retired entries are cautions, never active recommendations'}
        finally:db.close()
