import sqlite3,json,uuid,copy,hashlib
from datetime import datetime,timezone
from pathlib import Path
from decimal import Decimal
from engine import compute,validate_scheme,validate_input_limits,validate_abs_assignment_changes,D,stock_fingerprint,late_ipt_error,late_ipt_issue_conflict
from settings import initial_settings
from year_link import traced_credit_conflict

def dump(x):return json.dumps(x,default=lambda v:str(v) if isinstance(v,Decimal) else v,ensure_ascii=False)
def now():return datetime.now(timezone.utc).isoformat()
class Store:
    def __init__(self,path):
        self.path=str(path);Path(self.path).parent.mkdir(parents=True,exist_ok=True)
        with self.db() as c:
            c.executescript('CREATE TABLE IF NOT EXISTS records(id TEXT PRIMARY KEY, revision INTEGER, data TEXT); CREATE TABLE IF NOT EXISTS settings(version INTEGER PRIMARY KEY, data TEXT); CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY, time TEXT, action TEXT, target TEXT, data TEXT); CREATE TABLE IF NOT EXISTS issued(identity TEXT PRIMARY KEY, total TEXT, record TEXT); CREATE TABLE IF NOT EXISTS bulk_imports(id TEXT PRIMARY KEY,data TEXT);')
            if not c.execute('SELECT 1 FROM settings').fetchone():c.execute('INSERT INTO settings VALUES(?,?)',(1,dump(initial_settings())))
    def db(self):return sqlite3.connect(self.path,timeout=10)
    def audit(self,c,action,target,data):c.execute('INSERT INTO audit(time,action,target,data) VALUES(?,?,?,?)',(now(),action,target,dump(data)))
    def settings(self):
        with self.db() as c:return json.loads(c.execute('SELECT data FROM settings ORDER BY version DESC LIMIT 1').fetchone()[0])
    def save_settings(self,s):
        for key,field,label in [('schemes','id','scheme IDs'),('seasons','name','season names')]:
            values=[str(x.get(field) or '').strip() for x in s[key]]
            if any(not v for v in values) or len(values)!=len(set(values)):raise ValueError('Duplicate/missing '+label)
        for sc in s['schemes']:
            errors=validate_scheme(sc,False)
            if errors and sc.get('confirmed'):raise ValueError('; '.join(errors))
        ids=[p['id'] for p in s['products']]
        if len(ids)!=len(set(ids)):raise ValueError('Duplicate product IDs')
        with self.db() as c:
            c.execute('BEGIN IMMEDIATE');latest=c.execute('SELECT MAX(version) FROM settings').fetchone()[0]
            if s.get('version')!=latest:raise ValueError('Settings changed: reload before saving')
            s=copy.deepcopy(s)
            old=json.loads(c.execute('SELECT data FROM settings WHERE version=?',(latest,)).fetchone()[0]);previous={x['id']:x for x in old['schemes']}
            if set(previous)-{x['id'] for x in s['schemes']}:raise ValueError('Use Delete Scheme to preserve saved scheme identities and history')
            old_products={p['id']:p for p in old['products']};new_products={p['id']:p for p in s['products']};new_schemes={sc['id']:sc for sc in s['schemes']}
            for pid,prev in old_products.items():
                current=new_products.get(pid)
                if not current or any(current.get(k)!=prev.get(k) for k in ('crop','segment','segment_id','packing_kg','scheme')):raise ValueError('Keep existing product crop, packing and group identity; add a separate product for a new packing/group')
            for product in s['products']:
                if not product.get('name','').strip() or D(product.get('packing_kg'))<=0:raise ValueError('Product needs a name and positive packing')
                base=new_schemes.get(product.get('scheme'))
                if not base or product['crop']!=base['crop'] or product.get('segment_id',product['segment'])!=base.get('segment_id',base['segment']) or D(product['packing_kg'])!=D(base['packing_kg']) or product['id'] not in base['products']:raise ValueError('Product must belong to its matching crop and packing group')

            for scheme in s['schemes']:
                prev=previous.get(scheme['id']);scheme['version']=(prev.get('version',1)+1 if prev and scheme!=prev else prev.get('version',1) if prev else 1)
            s['version']=latest+1;s['saved_at']=now()
            c.execute('INSERT INTO settings VALUES(?,?)',(s['version'],dump(s)));self.audit(c,'settings',str(s['version']),s)
        return s
    def all(self):
        with self.db() as c:return [json.loads(x[0]) for x in c.execute('SELECT data FROM records ORDER BY rowid DESC')]
    def get(self,id):
        with self.db() as c:row=c.execute('SELECT data FROM records WHERE id=?',(id,)).fetchone()
        if not row:raise ValueError('Record not found')
        return json.loads(row[0])
    def save(self,r):
        r=copy.deepcopy(r);r.pop('frozen_settings',None);r.pop('result',None);id=r.get('id') or uuid.uuid4().hex
        with self.db() as c:
            c.execute('BEGIN IMMEDIATE');row=c.execute('SELECT revision,data FROM records WHERE id=?',(id,)).fetchone()
            if row:
                old=json.loads(row[1])
                if old.get('deleted_at'):raise ValueError('Party is deleted. Restore it from Deleted Parties before editing.')
                if old['status']!='draft':raise ValueError('Finalised records are read-only; create a revision')
                if r.get('revision')!=row[0]:raise ValueError('Record changed: reload before saving')
                # A source original is immutable. Review edits must remain separate.
                originals={e['id']:e.get('original') for e in old.get('entries',[]) if e.get('original')}
                for e in r.get('entries',[]):
                    if e['id'] in originals:e['original']=originals[e['id']]
                if set(originals)-{e['id'] for e in r.get('entries',[])}:raise ValueError('Imported vouchers cannot be deleted; record a reviewed correction')
                r.pop('deleted_at',None);r.pop('deleted_batch',None)
                r['source']=old.get('source',r.get('source'));r['prior_issued']=old.get('prior_issued',{});r['lineage']=old.get('lineage',id)
            else:
                r.pop('deleted_at',None);r.pop('deleted_batch',None)
                r['prior_issued']={};r['lineage']=id
            validate_input_limits(r,self.settings())
            validate_abs_assignment_changes(r,self.settings(),old if row else None)
            for entry in r.get('entries',[]):
                if (entry.get('reviewed') or r.get('ledger_confirmed')) and entry.get('date') and not entry.get('original'):entry['original']=copy.deepcopy(entry)
            r.update(id=id,status='draft',revision=(row[0] if row else 0)+1,saved_at=now())
            c.execute('INSERT OR REPLACE INTO records VALUES(?,?,?)',(id,r['revision'],dump(r)));self.audit(c,'save',id,r)
        return r
    @staticmethod
    def same_party(a,b):
        if not str(a.get('party') or '').strip() or not str(b.get('party') or '').strip():return a.get('id')==b.get('id')
        return (str(a['party']).strip().casefold(),str(a.get('location') or '').strip().casefold())==(str(b['party']).strip().casefold(),str(b.get('location') or '').strip().casefold())
    def party_action(self,id,restore=False,confirm=False,expected=None):
        with self.db() as c:
            c.execute('BEGIN IMMEDIATE')
            rows=[json.loads(x[0]) for x in c.execute('SELECT data FROM records')]
            base=next((x for x in rows if x['id']==id),None)
            if not base:raise ValueError('Party not found')
            selected=[x for x in rows if self.same_party(base,x) and bool(x.get('deleted_at'))==bool(restore)]
            if not selected:raise ValueError('Party has already been deleted/restored; reload the list')
            fingerprint=hashlib.sha256(dump(sorted((x['id'],x['revision']) for x in selected)).encode()).hexdigest()
            if not confirm:return {'party':base.get('party') or 'Unnamed draft','location':base.get('location',''),'records':len(selected),'issued':sum(x['status']=='issued' for x in selected),'expected':fingerprint}
            if expected!=fingerprint:raise ValueError('Party records changed. Reload and review before deleting/restoring.')
            stamp=now();batch=uuid.uuid4().hex
            for record in selected:
                if restore:record.pop('deleted_at',None);record.pop('deleted_batch',None)
                else:record.update(deleted_at=stamp,deleted_batch=batch)
                record['revision']+=1
                c.execute('UPDATE records SET revision=?,data=? WHERE id=?',(record['revision'],dump(record),record['id']))
            self.audit(c,'restore_party' if restore else 'delete_party',id,{'records':[x['id'] for x in selected],'party':base.get('party')})
            return {'restored' if restore else 'deleted':True,'records':len(selected)}
    def product_action(self,id,version,restore=False):
        settings=self.settings()
        if settings['version']!=version:raise ValueError('Settings changed: reload before changing products')
        product=next((p for p in settings['products'] if p['id']==id),None)
        if not product:raise ValueError('Product not found')
        if restore:product.pop('deleted_at',None)
        else:product['deleted_at']=now()
        return self.save_settings(settings)
    def scheme_action(self,id,version,restore=False):
        settings=self.settings()
        if settings.get('version')!=version:raise ValueError('Settings changed. Reload before deleting/restoring a scheme.')
        scheme=next((x for x in settings['schemes'] if x['id']==id),None)
        if not scheme:raise ValueError('Scheme not found')
        if restore:
            if not scheme.get('deleted_at'):raise ValueError('Scheme is already active')
            scheme.pop('deleted_at',None)
        else:
            if scheme.get('deleted_at'):raise ValueError('Scheme is already deleted')
            scheme['deleted_at']=now()
        return self.save_settings(settings)
    def review_late_ipt(self,id,expected,entry_id,reason='',remove=False):
        record=self.get(id)
        if record.get('deleted_at') or record['status']!='draft':raise ValueError('Late IPT can only be reviewed in an active draft')
        if record['revision']!=expected:raise ValueError('Record changed: reload before reviewing IPT')
        entry=next((e for e in record['entries'] if e['id']==entry_id),None)
        if not entry:raise ValueError('IPT voucher not found')
        reviews=record.setdefault('late_ipt_reviews',{})
        if remove:reviews.pop(entry_id,None)
        else:
            season=next((s for s in self.settings()['seasons'] if s['name']==record['season']),None)
            reviews[entry_id]={'season':record['season'],'start':season.get('start') if season else None,'end':season.get('end') if season else None,'reason':str(reason).strip(),'fingerprint':stock_fingerprint(entry),'reviewed_at':now()}
            error=late_ipt_error(record,entry,season)
            if error:raise ValueError(error)
        record['ledger_confirmed']=False
        return self.save(record)
    def preview_abs_distribution(self,payload,apply=False):
        from abs_distribution import preview
        record=copy.deepcopy(payload['record']);cfg=self.settings()
        if record.get('status','draft')!='draft':raise ValueError('Only draft allocations can be distributed')
        if record.get('id'):
            old=self.get(record['id'])
            if old.get('deleted_at') or old['status']!='draft':raise ValueError('Restore the party or create a draft revision before distributing ABS')
            if record.get('revision')!=old['revision']:raise ValueError('Record changed; reload before distributing ABS')
            originals={e['id']:e['original'] for e in old.get('entries',[]) if e.get('original')}
            for entry in record.get('entries',[]):
                if entry['id'] in originals:entry['original']=copy.deepcopy(originals[entry['id']])
        if apply and payload.get('settings_version')!=cfg['version']:raise ValueError('Scheme settings changed; preview the ABS split again')
        args={k:payload[k] for k in ('crop','scheme','source','amount','replace_id','approved','remark','options') if k in payload}
        plan=preview(record,cfg,**args)
        if not apply:return plan
        if args.get('options'):raise ValueError('Preview an amount before applying a distribution')
        record['allocations']=[a for a in record.get('allocations',[]) if a['id']!=plan['replace_id']]+plan['allocations']
        return self.save(record)

    def preview_cash_quantity(self,payload,apply=False):
        from cash_quantity import preview
        r=copy.deepcopy(payload['record']);cfg=self.settings()
        if r.get('status','draft')!='draft':raise ValueError('Create a draft revision before changing Cash quantity')
        if r.get('id'):
            old=self.get(r['id'])
            if old.get('deleted_at') or old['status']!='draft':raise ValueError('Restore the party or create a draft revision')
            if r.get('revision')!=old['revision']:raise ValueError('Record changed; preview Cash quantity again')
            originals={e['id']:e['original'] for e in old.get('entries',[]) if e.get('original')}
            for e in r.get('entries',[]):
                if e['id'] in originals:e['original']=copy.deepcopy(originals[e['id']])
        r.pop('frozen_settings',None);r.pop('result',None)
        if apply and payload.get('settings_version')!=cfg['version']:raise ValueError('Scheme settings changed; preview Cash quantity again')
        keys=('scheme','product','source','amount','supplied','returned','replace_id','deduction_rate','remark','cash_sales_value','cash_returns_value','billing_split_reason')
        plan=preview(r,cfg,**{k:payload[k] for k in keys if k in payload})
        if apply:return self.save(plan['candidate'])
        plan.pop('candidate',None)
        return plan

    def preview_cash_removal(self,payload,apply=False):
        """Remove one product's Cash split and funding together; keep all sources."""
        r=copy.deepcopy(payload['record']);cfg=self.settings()
        if r.get('status','draft')!='draft':raise ValueError('Create a draft revision before removing Cash scheme')
        if r.get('id'):
            old=self.get(r['id'])
            if old.get('deleted_at') or old['status']!='draft':raise ValueError('Restore the party or create a draft revision')
            if r.get('revision')!=old['revision']:raise ValueError('Record changed; preview Cash removal again')
            originals={e['id']:e['original'] for e in old.get('entries',[]) if e.get('original')}
            for e in r.get('entries',[]):
                if e['id'] in originals:e['original']=copy.deepcopy(originals[e['id']])
        if apply and payload.get('settings_version')!=cfg['version']:raise ValueError('Scheme settings changed; preview Cash removal again')
        r.pop('frozen_settings',None);r.pop('result',None)
        sid,pid=payload['scheme'],payload['product']
        rows=[a for a in r.get('allocations',[]) if a.get('type')=='Cash' and a.get('scheme')==sid and a.get('product')==pid]
        splits=[x for x in r.get('cash_splits',[]) if x.get('scheme')==sid and x.get('product')==pid]
        if not rows and not splits:raise ValueError('No Cash scheme allocation remains for this product')
        before=compute(r,cfg)
        r['allocations']=[a for a in r.get('allocations',[]) if a not in rows]
        r['cash_splits']=[x for x in r.get('cash_splits',[]) if x not in splits]
        validate_input_limits(r,cfg);after=compute(r,cfg)
        amounts={}
        for a in rows:amounts[a['source']]=amounts.get(a['source'],D(0))+D(a['amount'])
        if apply:return self.save(r)
        return {'settings_version':cfg['version'],'scheme':sid,'product':pid,'removed_rows':len(rows),
                'released_by_source':amounts,'released_total':sum(amounts.values(),D(0)),
                'previous_CN':before['new_CN_total'],'new_CN':after['new_CN_total'],
                'regular_net':next((p['regular_net'] for p in after['product_CNs'] if p['scheme']==sid and p['product_id']==pid),D(0)),
                'unit':next((p['unit'] for p in after['product_CNs'] if p['scheme']==sid and p['product_id']==pid),''),
                'issues':after['issues']}

    def calculation_record(self,r):
        # The stored status owns frozen history; a stale client cannot unfreeze it.
        saved=None
        if r.get('id'):
            with self.db() as c:row=c.execute('SELECT data FROM records WHERE id=?',(r['id'],)).fetchone()
            if row:saved=json.loads(row[0])
        if saved and saved.get('status') in ('finalised','issued'):
            if saved.get('result') is None:raise ValueError('Saved frozen calculation is unavailable; reload the record')
            return saved
        if r.get('status') in ('finalised','issued'):raise ValueError('Saved frozen calculation is unavailable; reload the record')
        draft=copy.deepcopy(r);draft.pop('frozen_settings',None);draft.pop('result',None)
        return draft
    def calculate(self,r):
        r=self.calculation_record(r)
        if r.get('status') in ('finalised','issued'):return copy.deepcopy(r['result'])
        return compute(r,self.settings())
    def finalise(self,id,expected):
        with self.db() as c:
            c.execute('BEGIN IMMEDIATE');row=c.execute('SELECT revision,data FROM records WHERE id=?',(id,)).fetchone()
            if not row:raise ValueError('Record not found')
            r=json.loads(row[1])
            if r.get('deleted_at'):raise ValueError('Restore the deleted party before finalising')
            if row[0]!=expected or r['status']!='draft':raise ValueError('Stale or read-only record')
            s=json.loads(c.execute('SELECT data FROM settings ORDER BY version DESC LIMIT 1').fetchone()[0]);result=compute(r,s)
            if result['issues']:raise ValueError('Cannot finalise: '+'; '.join(result['issues']))
            r.update(status='finalised',frozen_settings=s,result=result,finalised_at=now(),revision=r['revision']+1)
            c.execute('UPDATE records SET revision=?,data=? WHERE id=?',(r['revision'],dump(r),id));self.audit(c,'finalise',id,r)
        return json.loads(dump(r))
    @staticmethod
    def identity(r,key):return r['party'].strip().casefold()+'|'+r.get('location','').strip().casefold()+'|'+r['season']+'|'+key
    def issue(self,id,expected):
        with self.db() as c:
            c.execute('BEGIN IMMEDIATE');row=c.execute('SELECT revision,data FROM records WHERE id=?',(id,)).fetchone()
            if not row:raise ValueError('Record not found')
            r=json.loads(row[1])
            if r.get('deleted_at'):raise ValueError('Restore the deleted party before issuing')
            if row[0]!=expected or r['status']!='finalised':raise ValueError('Only a current finalised record can be marked issued')
            others=[json.loads(row[0]) for row in c.execute('SELECT data FROM records WHERE id<>?',(id,))]
            if traced_credit_conflict(r,others):raise ValueError('Traced opening receipt is already allocated in issued calculations beyond its confirmed remaining amount')
            for other_row in c.execute('SELECT data FROM records WHERE id<>?',(id,)):
                other=json.loads(other_row[0])
                if other.get('status')=='issued' and self.same_party(r,other) and late_ipt_issue_conflict(r,other):raise ValueError('This IPT is already included in another issued period; revise the original calculation before issuing it again')
            for cn in r['result']['proposals']:
                if Decimal(cn['proposed'])<=0:raise ValueError('Cannot issue zero/negative adjustment')
                ident=self.identity(r,cn['key']);prev=c.execute('SELECT total,record FROM issued WHERE identity=?',(ident,)).fetchone()
                actual=Decimal(prev[0]) if prev else Decimal(0)
                if actual!=Decimal(cn['previous_issued']):raise ValueError('Duplicate or changed issued entitlement; create revised version')
                c.execute('INSERT OR REPLACE INTO issued VALUES(?,?,?)',(ident,cn['rounded'],id))
            r.update(status='issued',issued_at=now(),revision=r['revision']+1)
            c.execute('UPDATE records SET revision=?,data=? WHERE id=?',(r['revision'],dump(r),id));self.audit(c,'issue',id,r)
        return r
    def revise(self,id):
        old=self.get(id)
        if old.get('deleted_at'):raise ValueError('Restore the deleted party before creating a revision')
        if old['status']=='draft':raise ValueError('Continue existing draft')
        r=copy.deepcopy(old);r['id']=uuid.uuid4().hex;r['parent']=id;r['status']='draft';r['revision']=1;r['saved_at']=now();r.pop('frozen_settings',None);r.pop('result',None)
        for key in ('issued_at','finalised_at'):r.pop(key,None)
        with self.db() as c:
            prior={}
            for cn in old['result']['CNs']:
                row=c.execute('SELECT total FROM issued WHERE identity=?',(self.identity(old,cn['key']),)).fetchone()
                if row:prior[cn['key']]=row[0]
            r['prior_issued']=prior;r['ledger_confirmed']=False;r['revision_ledger_confirmed']=False
            c.execute('INSERT INTO records VALUES(?,?,?)',(r['id'],1,dump(r)));self.audit(c,'revise',r['id'],{'parent':id})
        return r
    def backup(self):
        with self.db() as c:
            return {'format':'all-crop-cn-backup','version':1,'created_at':now(),'records':[dict(zip(['id','revision','data'],r)) for r in c.execute('SELECT * FROM records')],'settings':[dict(zip(['version','data'],r)) for r in c.execute('SELECT * FROM settings')],'issued':[dict(zip(['identity','total','record'],r)) for r in c.execute('SELECT * FROM issued')],'audit':[dict(zip(['id','time','action','target','data'],r)) for r in c.execute('SELECT * FROM audit')],'bulk_imports':[dict(zip(['id','data'],r)) for r in c.execute('SELECT * FROM bulk_imports')]}
    def restore(self,b,confirm=False):
        if b.get('format')!='all-crop-cn-backup' or b.get('version')!=1:raise ValueError('Unsupported backup')
        for row in b['records']:
            r=json.loads(row['data'])
            if r['id']!=row['id'] or r['revision']!=row['revision']:raise ValueError('Backup record identity mismatch')
            if r.get('status') in ('issued','finalised') and (not r.get('frozen_settings') or not r.get('result')):raise ValueError('Incomplete frozen snapshot')
        for row in b['settings']:json.loads(row['data'])
        for row in b.get('bulk_imports',[]):json.loads(row['data'])
        if not b['settings']:raise ValueError('Backup missing settings')
        if not confirm:return {'records':len(b['records']),'settings_versions':len(b['settings']),'warning':'Restoring replaces current data; automatic safety backup is created first.'}
        safety=self.backup();Path(self.path+'.before-restore.json').write_text(dump(safety),encoding='utf-8')
        with self.db() as c:
            c.execute('BEGIN IMMEDIATE')
            for table,cols in [('records',['id','revision','data']),('settings',['version','data']),('issued',['identity','total','record']),('audit',['id','time','action','target','data']),('bulk_imports',['id','data'])]:
                c.execute('DELETE FROM '+table)
                for row in b.get(table,[]):c.execute('INSERT INTO '+table+' VALUES('+','.join('?' for _ in cols)+')',[row[k] for k in cols])
            self.audit(c,'restore','database',{'records':len(b['records'])})
        return {'restored':True}
