from ledger_audit import audit_documents
"""Independent local workbook stores; legacy database remains in place."""
import copy,hashlib,json,re,threading,uuid
from pathlib import Path
from datetime import date
from store import Store,dump,now
from engine import D,late_ipt_issue_conflict
from year_link import traced_credit_conflict
from importer import import_pdf_documents,compare_import

class Workbooks:
    def __init__(self,legacy):
        self.legacy=legacy;self.directory=Path(legacy.path).parent/'workbooks'
        self.lock=threading.RLock();self.cache={'legacy':legacy}
        with legacy.db() as c:c.execute('CREATE TABLE IF NOT EXISTS workbooks(id TEXT PRIMARY KEY,data TEXT)')
    def list(self,include_deleted=False):
        with self.legacy.db() as c:
            rows=[json.loads(r[0]) for r in c.execute('SELECT data FROM workbooks ORDER BY rowid')]
        return rows if include_deleted else [r for r in rows if not r.get('deleted_at')]
    def metadata(self,id):
        if id=='legacy':return {'id':'legacy','name':'Existing calculations','state':'','legacy':True}
        if not re.fullmatch(r'[a-f0-9]{32}',id):raise ValueError('Invalid workbook')
        with self.legacy.db() as c:r=c.execute('SELECT data FROM workbooks WHERE id=?',(id,)).fetchone()
        if not r:raise ValueError('Workbook not found')
        return json.loads(r[0])
    def get(self,id='legacy',allow_deleted=False):
        meta=self.metadata(id)
        if meta.get('deleted_at') and not allow_deleted:raise ValueError('Workbook is deleted; restore it from Workbooks before opening')
        with self.lock:
            if id not in self.cache:self.cache[id]=Store(self.directory/(id+'.sqlite3'))
            return self.cache[id]
    def delete(self,id,restore=False,confirm=False,expected=None):
        if id=='legacy':raise ValueError('Existing calculations cannot be deleted as a workbook')
        with self.lock:
            meta=self.metadata(id);st=self.get(id,True);snapshot=st.backup();snapshot.pop('created_at',None)
            digest=hashlib.sha256(dump({'metadata':meta,'backup':snapshot}).encode()).hexdigest()
            if not confirm:return {'id':id,'name':meta['name'],'records':len(snapshot['records']),'expected':digest,'restore':restore}
            if expected!=digest:raise ValueError('Workbook changed; reload the deletion preview')
            if bool(meta.get('deleted_at'))!=bool(restore):raise ValueError('Workbook is already deleted/restored')
            safety=Path(self.legacy.path).parent/'workbook-safety';safety.mkdir(exist_ok=True)
            path=safety/(id+'-'+uuid.uuid4().hex+'.json');path.write_text(dump({'metadata':meta,'backup':st.backup()}),encoding='utf-8')
            if restore:meta.pop('deleted_at',None)
            else:meta['deleted_at']=now()
            with self.legacy.db() as c:c.execute('UPDATE workbooks SET data=? WHERE id=?',(dump(meta),id));self.legacy.audit(c,'restore_workbook' if restore else 'delete_workbook',id,meta)
            return {'restored' if restore else 'deleted':True,'safety_backup':str(path)}
    def create(self,b,source='legacy'):
        name=str(b.get('name','')).strip();state=str(b.get('state','')).strip();period=str(b.get('period','')).strip()
        if not name or not state or not period:raise ValueError('Enter workbook name, state and working-period name')
        start,end,cutoff=[date.fromisoformat(b[k]) for k in ('start','end','cutoff')]
        if not start<=end<=cutoff:raise ValueError('Working period must start before its end; cutoff must be on/after the end')
        mode=b.get('mode','copy')
        if mode not in ('copy','blank'):raise ValueError('Choose independent scheme copy or blank benefit setup')
        with self.lock:
            if any(x['name'].casefold()==name.casefold() for x in self.list(True)):raise ValueError('A workbook already has this name')
            source=b.get('source',source);cfg=copy.deepcopy(self.get(source).settings());id=uuid.uuid4().hex
            # Finding dispositions belong to the original workbook evidence, not scheme templates.
            cfg.pop('audit_finding_reviews',None)
            cfg['seasons']=[{'name':period,'start':start.isoformat(),'end':end.isoformat(),'cutoff':cutoff.isoformat(),'confirmed':True}]
            for sc in cfg['schemes']:
                sc.update(season=period,states=[state],confirmed=False,remark='Independent workbook setup; review state, billing, dates and benefit rates before confirming.')
                # Tombstones are preserved; copying never revives deleted schemes.
                if mode=='blank':
                    sc.update(benefits=[],quantity=[],extra=[],net=[],cd=[],billing=None,token=None,abs_rate=None,abs_start=None,abs_end=None,extended_end=None,cash=None,return_rate=None)
                    sc.pop('net_cn_rate',None)
            meta={'id':id,'name':name,'state':state,'created_at':now(),'copied_from':source,'mode':mode}
            store=Store(self.directory/(id+'.sqlite3'))
            # Initialise a private copy without imposing the reference catalogue's identities.
            cfg.update(version=1,saved_at=now())
            with store.db() as c:c.execute('UPDATE settings SET data=? WHERE version=1',(dump(cfg),))
            with self.legacy.db() as c:c.execute('INSERT INTO workbooks VALUES(?,?)',(id,dump(meta)));self.legacy.audit(c,'create_workbook',id,meta)
            self.cache[id]=store
            return meta
    def backup(self):
        with self.lock:return {'format':'all-crop-cn-workbooks-backup','version':1,'created_at':now(),'legacy':self.legacy.backup(),'workbooks':[{'metadata':m,'backup':self.get(m['id'],True).backup()} for m in self.list(True)]}
    def restore(self,b,confirm=False):
        if b.get('format')=='all-crop-cn-backup':
            out=self.legacy.restore(b,confirm)
            if not confirm:out['warning']='Restores Existing calculations only. Other workbooks stay unchanged; a safety backup is saved first.'
            return out
        if b.get('format')!='all-crop-cn-workbooks-backup' or b.get('version')!=1:raise ValueError('Unsupported workbook backup')
        import tempfile
        ids=set()
        with tempfile.TemporaryDirectory() as td:
            validator=Store(Path(td)/'validate.sqlite3');validator.restore(b['legacy'],False)
            for item in b['workbooks']:
                m=item['metadata'];id=m['id']
                if not re.fullmatch(r'[a-f0-9]{32}',id) or id in ids or not m.get('name') or not m.get('state'):raise ValueError('Invalid workbook identity in backup')
                ids.add(id);validator.restore(item['backup'],False)
        if not confirm:return {'records':len(b['legacy']['records'])+sum(len(x['backup']['records']) for x in b['workbooks']),'settings_versions':len(b['legacy']['settings'])+sum(len(x['backup']['settings']) for x in b['workbooks']),'warning':'Restores all workbook data. A complete safety backup is saved first.'}
        with self.lock:
            safety=self.backup();Path(self.legacy.path+'.workbooks-before-restore.json').write_text(dump(safety),encoding='utf-8')
            try:self._restore_validated(b)
            except BaseException:
                self._restore_validated(safety)
                raise
        return {'restored':True}
    def _restore_validated(self,b):
        self.legacy.restore(b['legacy'],True)
        # Removed workbook files are retained on disk; only manifest visibility changes.
        with self.legacy.db() as c:
            c.execute('DELETE FROM workbooks')
            for item in b['workbooks']:c.execute('INSERT INTO workbooks VALUES(?,?)',(item['metadata']['id'],dump(item['metadata'])))
        for item in b['workbooks']:self.get(item['metadata']['id'],True).restore(item['backup'],True)
    def issue(self,workbook,id,revision):
        with self.lock:
            target=self.get(workbook);record=target.get(id)
            season=next(s for s in record['frozen_settings']['seasons'] if s['name']==record['season'])
            proposed={cn['key'] for cn in record['result']['proposals']}
            for other in ['legacy']+[m['id'] for m in self.list(True)]:
                if other==workbook:continue
                for old in self.get(other,True).all():
                    if old.get('status')!='issued' or not Store.same_party(record,old):continue
                    if late_ipt_issue_conflict(record,old):raise ValueError('This IPT is already included in an issued period in another workbook; revise the original calculation before issuing it again')
                    prev=next((s for s in old['frozen_settings']['seasons'] if s['name']==old['season']),None)
                    if prev and prev.get('start') and prev.get('end') and season['start']<=prev['end'] and prev['start']<=season['end'] and proposed.intersection(cn['key'] for cn in old['result']['proposals']):
                        raise ValueError('A CN for this party/benefit overlaps an issued period in another workbook. Revise the original issued calculation.')
            all_records=[old for book in ['legacy']+[m['id'] for m in self.list(True)] for old in self.get(book,True).all()]
            if traced_credit_conflict(record,all_records):raise ValueError('Traced opening receipt is already allocated across issued workbooks beyond its confirmed remaining amount')
            return target.issue(id,revision)
    def link_year(self,workbook,b):
        from year_link import analyse_pair,attach_link
        if workbook=='legacy':raise ValueError('Select a workbook before saving a year link')
        with self.lock:
            current=self.get(workbook)
            analyse_pair(b['previous'],b['current'],b.get('identity_reason',''))
            # Validate confirmation amounts before creating a new party draft.
            attach_link({**b['current'],'status':'draft','opening_sources':[],'allocations':[]},b['previous'],b['current'],b.get('confirmed',{}),b.get('reason',''),b.get('identity_reason',''))
            season=next((s for s in current.settings()['seasons'] if s['name']==b['season']),None)
            if not season:raise ValueError('Select a working period')
            entry=self._store_document(workbook,{'filename':'Year link current PDF'},b['current'],current,season)
            if entry['status']=='Needs review':raise ValueError('Current statement needs ordinary import review before linking; open it from Bulk Import')
            saved=current.get(entry['record_id'])
            linked=attach_link(saved,b['previous'],b['current'],b.get('confirmed',{}),b.get('reason',''),b.get('identity_reason',''),b.get('replace_unused',False))
            return current.save(linked)
    def bulk_import(self,workbook,b):
        if workbook=='legacy':raise ValueError('Select a workbook before bulk importing')
        try:return self._bulk_import(workbook,b)
        except Exception as exc:
            st=self.get(workbook);id=hashlib.sha256((str(b.get('data',''))+'|'+str(b.get('season',''))).encode()).hexdigest()
            entry={'id':id,'filename':str(b.get('filename','Statement.pdf')),'party':'','season':b.get('season',''),'status':'Failed','message':str(exc),'time':now()}
            with st.db() as c:c.execute('INSERT OR REPLACE INTO bulk_imports VALUES(?,?)',(id,dump(entry)))
            return entry
    def _bulk_import(self,workbook,b):
        import base64
        if workbook=='legacy':raise ValueError('Select a workbook before bulk importing')
        with self.lock:
            st=self.get(workbook);settings=st.settings();season=next((s for s in settings['seasons'] if s['name']==b.get('season')),None)
            if not season:raise ValueError('Choose a working period in this workbook')
            raw=base64.b64decode(b['data'],validate=True);documents=import_pdf_documents(raw,settings);results=[]
            if not documents:raise ValueError('No party ledger was found')
            for doc in documents:
                try:
                    if doc.get('import_error'):raise ValueError(doc['import_error'])
                    results.append(self._store_document(workbook,b,doc,st,season))
                except (ValueError,ArithmeticError,KeyError) as exc:
                    logid=hashlib.sha256((hashlib.sha256(raw).hexdigest()+'|'+doc.get('party','')+'|'+season['name']).encode()).hexdigest()
                    entry={'id':logid,'filename':str(b.get('filename','Statement.pdf')),'party':doc.get('party',''),'season':season['name'],'status':'Failed','message':str(exc),'time':now()}
                    with st.db() as c:c.execute('INSERT OR REPLACE INTO bulk_imports VALUES(?,?)',(logid,dump(entry)))
                    results.append(entry)
            return results[0] if len(results)==1 else {'status':'Combined PDF','filename':b.get('filename','Statement.pdf'),'ledger_count':len(results),'results':results}
    def _store_document(self,workbook,b,doc,st,season):
        workbook_state=self.metadata(workbook)['state']
        state_warning=('Statement address state '+doc['state']+' differs from workbook '+workbook_state+'; imported with workbook schemes. Review the address if needed.' if doc.get('state') and doc['state']!=workbook_state else '')
        if not doc.get('party'):raise ValueError('Party name not recognised; import this statement individually for review')
        logid=hashlib.sha256((doc['source']['sha256']+'|'+season['name']).encode()).hexdigest()
        existing=[r for r in st.all() if not r.get('deleted_at') and Store.same_party(r,doc) and r.get('season')==season['name']]
        draft=[r for r in existing if r['status']=='draft'];candidates=draft or existing
        exact=next((r for r in existing if (r.get('source') or {}).get('sha256')==doc['source']['sha256']),None)
        entry={'id':logid,'filename':str(b.get('filename','Statement.pdf')),'party':doc['party'],'season':season['name'],'time':now(), 'ledger_audit':audit_documents([{**doc,'audit_filename':b.get('filename','Statement.pdf')}],season['start'],season['end'],st.settings())}
        if state_warning:entry['address_warning']=state_warning
        if exact and all(c['status']=='Already imported' for c in compare_import(exact['entries'],doc['entries'])) and D(exact['closing'])==D(doc['closing']):entry.update(status='Already imported',record_id=exact['id'])
        elif candidates:
            if len(candidates)>1:entry.update(status='Needs review',message='Multiple saved calculations match this party/period. Select the correct calculation and import this statement there.',document=doc)
            else:
                old=candidates[0];comparison=compare_import(old['entries'],doc['entries'])
                if all(c['status']=='Already imported' for c in comparison) and D(old['closing'])==D(doc['closing']):entry.update(status='Already imported',record_id=old['id'])
                else:entry.update(status='Needs review',record_id=old['id'],document=doc,message='Open the existing calculation and review changed/new vouchers. Issued records require a revision first.')
        else:
            r={**doc,'workbook_id':workbook,'annual_ledger':True,'workbook_scheme_state':workbook_state,'season':season['name'],'state':doc.get('state') or self.metadata(workbook)['state'],'old_dues':str(max(D(0),D(doc.get('opening') or 0))),'opening_dues_review_required':True,'allocations':[],'cash_splits':[],'opening_sources':[],'ledger_confirmed':False,'import_warnings':doc['warnings']}
            saved=st.save(r);entry.update(status='Imported',record_id=saved['id'])
        with st.db() as c:c.execute('INSERT OR REPLACE INTO bulk_imports VALUES(?,?)',(logid,dump(entry)))
        return {k:v for k,v in entry.items() if k!='document'}

def bulk_history(store):
    with store.db() as c:return [{k:v for k,v in json.loads(row[0]).items() if k!='document'} for row in c.execute('SELECT data FROM bulk_imports ORDER BY rowid DESC')]

def bulk_document(store,id):
    with store.db() as c:r=c.execute('SELECT data FROM bulk_imports WHERE id=?',(id,)).fetchone()
    if not r:raise ValueError('Import not found')
    out=json.loads(r[0])
    if not out.get('document'):raise ValueError('This import has no pending statement to review')
    return out

def resolve_bulk(store,id,record_id):
    pending=bulk_document(store,id);record=store.get(record_id)
    if not Store.same_party(record,pending['document']) or record['season']!=pending['season']:raise ValueError('Import and saved calculation do not match')
    comparison=compare_import(record['entries'],pending['document']['entries'])
    if not all(c['status']=='Already imported' for c in comparison) or D(record['closing'])!=D(pending['document']['closing']):
        return {'resolved':False}
    pending.update(status='Reviewed',record_id=record_id,message='Updated statement reviewed and saved.');pending.pop('document',None)
    with store.db() as c:c.execute('UPDATE bulk_imports SET data=? WHERE id=?',(dump(pending),id))
    return {'resolved':True}
