"""Explicit, scoped storage maintenance. Financial protections are never discarded."""
import copy,hashlib,json,sqlite3
from pathlib import Path
from store import dump,now

def hash_value(v):return hashlib.sha256(dump(v).encode()).hexdigest()
def references(v,ids):
    if isinstance(v,str):return v in ids
    if isinstance(v,list):return any(references(x,ids) for x in v)
    if isinstance(v,dict):return any(k in ids or references(x,ids) for k,x in v.items())
    return False

def snapshot(books):
    data=books.backup();data.pop('created_at',None)
    for b in [data['legacy']]+[w['backup'] for w in data['workbooks']]:b.pop('created_at',None)
    return data

def protected(st):
    records=st.all()
    with st.db() as c:issued=c.execute('SELECT COUNT(*) FROM issued').fetchone()[0]
    return bool(issued or any(r.get('status')=='issued' or r.get('prior_issued') or r.get('issued_at') for r in records))

def compact(st):
    c=sqlite3.connect(st.path,timeout=10)
    try:c.execute('PRAGMA secure_delete=ON');c.execute('VACUUM')
    finally:c.close()

def archived(books,workbook):
    st=books.get(workbook);parties={}
    for r in st.all():
        if r.get('deleted_at'):
            key=(r.get('party','').strip().casefold(),r.get('location','').strip().casefold())
            parties.setdefault(key,{'kind':'party','id':r['id'],'name':r.get('party') or 'Unnamed draft','location':r.get('location','')})
    return list(parties.values())+[{'kind':'scheme','id':s['id'],'name':s['name']} for s in st.settings()['schemes'] if s.get('deleted_at')]+[{'kind':'workbook','id':m['id'],'name':m['name']} for m in books.list(True) if m.get('deleted_at')]

def purge(books,workbook,b):
    kind=b.get('kind');id=b.get('id');st=books.get(workbook);blockers=[];target_ids=set();products=set();selected=[];recovery=[]
    if kind=='party':
        base=st.get(id)
        if not base.get('deleted_at'):raise ValueError('Move the party to Deleted Parties first')
        selected=[r for r in st.all() if st.same_party(base,r) and r.get('deleted_at')];name=base.get('party') or 'Unnamed draft';target_ids={r['id'] for r in selected}
        with st.db() as c:issued={x[0] for x in c.execute('SELECT record FROM issued')}
        if target_ids&issued or any(r.get('status')=='issued' or r.get('prior_issued') or r.get('issued_at') for r in selected):blockers.append('Issued CN history is retained for duplicate-issue and receipt protection.')
        for book in ['legacy']+[m['id'] for m in books.list(True)]:
            for r in books.get(book,True).all():
                if book==workbook and r['id'] in target_ids:continue
                if references(r,target_ids):blockers.append('Another calculation references this party history.');break
    elif kind=='scheme':
        cfg=st.settings();scheme=next((s for s in cfg['schemes'] if s['id']==id),None)
        if not scheme or not scheme.get('deleted_at'):raise ValueError('Move the scheme to Deleted Schemes first')
        name=scheme['name'];products={p['id'] for p in cfg['products'] if p.get('scheme')==id}
        if any(s['id']!=id and references(s,products) for s in cfg['schemes']):blockers.append('Another saved scheme uses this scheme’s product group.')
        for r in st.all():
            working={k:v for k,v in r.items() if k!='frozen_settings'}
            if references(working,{id}|products):blockers.append('Saved calculations use this scheme or its products; retain their rules.');break
        # A frozen snapshot keeps a complete independent copy of its original settings.
    elif kind=='workbook':
        if id=='legacy':raise ValueError('My existing calculations cannot be permanently deleted as a workbook')
        meta=books.metadata(id)
        if not meta.get('deleted_at'):raise ValueError('Move the workbook to Deleted Workbooks first')
        st=books.get(id,True);recovery=[p for p in (Path(books.legacy.path).parent/'workbook-safety').glob(id+'-*.json') if p.is_file() and not p.is_symlink()]
        if Path(st.path+'.before-restore.json').is_file():recovery.append(Path(st.path+'.before-restore.json'))
        selected=st.all();target_ids={r['id'] for r in selected};name=meta['name']
        if protected(st):blockers.append('This workbook holds issued CN history and cannot be purged.')
        for book in ['legacy']+[m['id'] for m in books.list(True) if m['id']!=id]:
            for r in books.get(book,True).all():
                if references(r,target_ids|{id}):blockers.append('Another workbook references this workbook’s history.');break
    else:raise ValueError('Choose a deleted party, scheme or workbook')
    expected=hash_value({'kind':kind,'id':id,'workbook':workbook,'backup':snapshot(books),'recovery':[(p.name,p.stat().st_size,p.stat().st_mtime_ns) for p in recovery]})
    out={'kind':kind,'id':id,'name':name,'records':len(selected),'products':len(products),'safety_backups':len(recovery),'blockers':sorted(set(blockers)),'expected':expected,
         'warning':'Permanent deletion cannot be undone here. Dedicated recovery files of a purged workbook are also removed. Other exported files and backups remain separate; remove unwanted safety backups in Storage Cleanup.'}
    if not b.get('confirm'):return out
    if b.get('expected')!=expected:raise ValueError('Data changed; preview permanent deletion again')
    if b.get('typed_name')!=name:raise ValueError('Type the exact name to confirm permanent deletion')
    if blockers:raise ValueError(' '.join(out['blockers']))
    before=Path(st.path).stat().st_size
    if kind=='workbook':
        with books.legacy.db() as c:
            c.execute('DELETE FROM workbooks WHERE id=?',(id,));books.legacy.audit(c,'purge_workbook',id,{'name':name,'records':len(selected)})
        books.cache.pop(id,None)
        for suffix in ('','-wal','-shm','-journal','.before-restore.json'):
            Path(st.path+suffix).unlink(missing_ok=True)
        for p in (Path(books.legacy.path).parent/'workbook-safety').glob(id+'-*.json'):
            if p.is_file() and not p.is_symlink():p.unlink()
        compact(books.legacy)
    else:
        with st.db() as c:
            c.execute('BEGIN IMMEDIATE');c.execute('PRAGMA secure_delete=ON')
            if kind=='party':
                for rid in target_ids:
                    c.execute('DELETE FROM records WHERE id=?',(rid,));c.execute('DELETE FROM audit WHERE target=?',(rid,))
                for bid,raw in c.execute('SELECT id,data FROM bulk_imports').fetchall():
                    if references(json.loads(raw),target_ids):c.execute('DELETE FROM bulk_imports WHERE id=?',(bid,));c.execute('DELETE FROM audit WHERE target=?',(bid,))
            else:
                def clean(cfg):
                    cfg['schemes']=[s for s in cfg['schemes'] if s['id']!=id];cfg['products']=[p for p in cfg['products'] if p['id'] not in products]
                    return cfg
                for version,raw in c.execute('SELECT version,data FROM settings').fetchall():c.execute('UPDATE settings SET data=? WHERE version=?',(dump(clean(json.loads(raw))),version))
                latest=clean(copy.deepcopy(cfg));latest.update(version=cfg['version']+1,saved_at=now());c.execute('INSERT INTO settings VALUES(?,?)',(latest['version'],dump(latest)))
                for aid,raw in c.execute("SELECT id,data FROM audit WHERE action='settings'").fetchall():
                    saved=json.loads(raw)
                    if isinstance(saved,dict) and 'schemes' in saved and 'products' in saved:c.execute('UPDATE audit SET data=? WHERE id=?',(dump(clean(saved)),aid))
            st.audit(c,'purge_'+kind,id,{'name':name,'records':len(selected),'products':len(products)})
        compact(st)
    return {'purged':True,'kind':kind,'records':len(selected),'bytes_reclaimed':max(0,before-(Path(st.path).stat().st_size if Path(st.path).exists() else 0))}

class Cleanup:
    def __init__(self,books,code_root):self.books=books;self.root=Path(books.legacy.path).parent;self.code=Path(code_root)
    def files(self):
        out=[]
        paths=[(p,'cache') for p in (self.code/'__pycache__').glob('*.pyc')]
        paths += [(Path(self.books.legacy.path+s),'backup') for s in ('.before-restore.json','.workbooks-before-restore.json')]
        paths += [(p,'backup') for p in (self.root/'workbook-safety').glob('*.json')]
        paths += [(p,'backup') for p in (self.root/'workbooks').glob('*.sqlite3.before-restore.json')]
        for p,kind in paths:
            if not p.is_file() or p.is_symlink() or any(x.is_symlink() for x in [p.parent,p.parent.parent]):continue
            stat=p.stat();key=hash_value(str(p.resolve()))
            out.append({'id':key,'name':p.name,'kind':kind,'bytes':stat.st_size,'mtime':stat.st_mtime_ns,'path':p})
        return sorted(out,key=lambda x:x['id'])
    def run(self,b):
        files=self.files();ids=b.get('backup_ids',[])
        if not isinstance(ids,list) or set(ids)-{f['id'] for f in files if f['kind']=='backup'}:raise ValueError('Backup list changed; scan storage again')
        selected=[f for f in files if f['kind']=='cache' or f['id'] in ids]
        dbs=[self.books.legacy]+[self.books.get(m['id'],True) for m in self.books.list(True)]
        unused=0
        for st in dbs:
            c=sqlite3.connect(st.path)
            try:unused+=c.execute('PRAGMA freelist_count').fetchone()[0]*c.execute('PRAGMA page_size').fetchone()[0]
            finally:c.close()
        inventory=[{k:v for k,v in f.items() if k!='path'} for f in files]
        expected=hash_value({'files':inventory,'backup_ids':sorted(ids),'unused':unused})
        out={'files':inventory,'cache_bytes':sum(f['bytes'] for f in files if f['kind']=='cache'),'selected_bytes':sum(f['bytes'] for f in selected),'unused_database_bytes':unused,'expected':expected,
             'note':'Cache files are regenerated as needed. Backups are only deleted when explicitly selected. Database compaction keeps all remaining calculations and settings.'}
        if not b.get('confirm'):return out
        if b.get('expected')!=expected:raise ValueError('Storage changed; scan and preview again')
        if ids and b.get('typed_confirmation')!='DELETE BACKUPS':raise ValueError('Type DELETE BACKUPS to remove selected safety copies')
        removed=0
        for f in selected:f['path'].unlink();removed+=f['bytes']
        for st in dbs:compact(st)
        return {'cleaned':True,'removed_bytes':removed,'compacted_databases':len(dbs)}
