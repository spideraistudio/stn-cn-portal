"""Authenticated adapter for the unchanged Update35.2 Store and stateless maths.

Each request gets a private in-memory SQLite store. Only fixed table rows are
persisted, atomically with live authorisation and audit, in the web account DB.
The offline HTTP server, global project switcher and filesystem Store are never
started. There is no client-selectable owner or physical database path.
"""
import copy
import json
import sqlite3
import uuid
from .ledger_service import BASELINE, encode, digest, number
from .data_store import validate, fields
from .security import AuthError, require_permission, session_hash
from .statement_review import project_reviews
from store import Store, dump
from settings import initial_settings
from engine import validate_scheme, validate_input_limits
from allocation_review import review_allocation
from allocation_clear import clear_allocations

TABLES = {'records': ('id','revision','data'), 'settings': ('version','data'),
          'audit': ('id','time','action','target','data'),
          'issued': ('identity','total','record'), 'bulk_imports': ('id','data')}
ALLOCATION_FIELDS = ('allocations','cash_splits','manual_order','old_dues',
                     'opening_dues_review','opening_dues_review_required','opening_sources','reserved_sources','payment_history')
SCHEME_FIELDS = ('scheme_overrides','cash_deduction_rates','product_assignments')

class YearLinkEvidenceError(ValueError):
    pass

def validate_opening_sources(record, expected):
    """Undated opening credit is allocation metadata; traced receipts are proof."""
    sources=record.get('opening_sources',[])
    if not isinstance(sources,list):raise ValueError('Invalid opening-credit sources')
    linked=[]
    for source in sources:
        if not isinstance(source,dict):raise ValueError('Invalid opening-credit source')
        if source.get('year_link_receipt'):
            linked.append(source)
        elif source.get('conversion'):
            if set(source)-{'id','amount','date','conversion','crop','scheme','original_date'} or source.get('conversion') is not True or source.get('original_date') is not None:
                raise ValueError('Invalid carried-credit conversion')
            from datetime import date
            if date.fromisoformat(source['date']).isoformat()!=source['date'] or not source.get('crop') or not source.get('scheme'):
                raise ValueError('Choose conversion date, crop and scheme')
        elif set(source)-{'id','amount','date'} or source.get('date') is not None:
            raise ValueError('Use reviewed Year Link for dated opening-credit sources')
    if linked!=[s for s in expected if s.get('year_link_receipt')]:
        raise YearLinkEvidenceError('Year Link receipt evidence cannot be replaced through Save')

class Runtime(Store):
    def __init__(self, payload, ledger, service):
        self.connection = sqlite3.connect(':memory:')
        self.ledger, self.service, self.finance, self.source_finance = ledger, service, False, False
        self.owner=None;self.workbook=None
        super().__init__(':memory:')
        if payload:
            with self.db() as c:
                for table, columns in TABLES.items():
                    c.execute('DELETE FROM '+table)
                    c.executemany('INSERT INTO '+table+' VALUES('+','.join('?' for _ in columns)+')', payload[table])
        else:
            cfg = self.seed(ledger)
            with self.db() as c:
                c.execute('UPDATE settings SET data=? WHERE version=1', (dump(cfg),))

    def db(self):
        return self.connection

    @staticmethod
    def seed(s):
        cfg=initial_settings()
        cfg.update(products=[], schemes=[], seasons=[{'name':'Working season','start':None,'end':None,'cutoff':None,'confirmed':False}])
        if s['periods']:
            cfg['seasons']=[{**p,'confirmed':True} for p in s['periods']]
        if s['catalogue']:
            cfg['products']=[]; cfg['schemes']=[]
            groups={}
            for p in s['catalogue']:
                key=(p['crop'],p['segment'],p['packing_kg'])
                if key not in groups:
                    sc=copy.deepcopy(initial_settings()['schemes'][0])
                    sid='web-'+digest(key)[:24]
                    sc.update(id=sid,segment_id=sid, name=p['segment']+' — enter benefits',
                              crop=p['crop'],segment=p['segment'],packing_kg=p['packing_kg'],
                              products=[],season=cfg['seasons'][0]['name'],states=[],confirmed=False,
                              benefits=[],quantity=[],extra=[],net=[],cd=[],cash=None,billing=None,
                              token=None,abs_rate=None,return_rate=None,unit='kg',billing_unit='kg',
                              remark='Enter and confirm the scheme for this workbook before use.')
                    if p['segment']=='Awaiting scheme':sc['mapping_placeholder']=True
                    groups[key]=sc;cfg['schemes'].append(sc)
                sc=groups[key];sc['products'].append(p['id'])
                cfg['products'].append({**copy.deepcopy(p),'scheme':sc['id'],'segment_id':sc['segment_id'],**({'needs_assignment':True} if p['segment']=='Awaiting scheme' else {})})
        return cfg

    def settings(self):
        cfg=super().settings()
        if self.finance and self.source_finance:
            # Calculation envelope, not a rewrite of saved season dates. The
            # authoritative item mask below admits ONLY the selected season.
            for season in cfg['seasons']:
                p=next((x for x in self.ledger['periods'] if x['name']==season['name']),None)
                if p: season.update(start=p['start'],end=p['cutoff'],cutoff=p['cutoff'],confirmed=True)
        return cfg

    def get(self, rid):
        r=super().get(rid)
        return self.project(r) if self.finance else r

    def project(self, r):
        r=copy.deepcopy(r)
        if r.get('status') in ('finalised','issued'):return r
        binding=r.get('web_source')
        if not binding:return r
        source=self.service.ledger.ledger(self.ledger,binding['ledger_id'])
        if binding['revision'] != digest(source):
            raise AuthError('Source ledger/reviews changed. Reopen from Ledger & Seasons to refresh this draft.',409)
        if binding.get('year_link') != digest(self.ledger['year_links'].get(source['id'])) or binding.get('periods') != digest(self.ledger['periods']):
            raise AuthError('Season or Year Link changed; reopen a reviewed source calculation.',409)
        period=next((p for p in self.ledger['periods'] if p['name']==r['season']),None)
        if not period:
            configured=next((p for p in Store.settings(self)['seasons'] if p['name']==r['season']),None)
            if configured and not configured.get('confirmed'):
                return project_reviews(r, source['document'])  # Offline draft workflow: dates must be confirmed before finalisation.
            raise AuthError('Choose a saved season',400)
        by_id={e['id']:i for i,e in enumerate(source['document']['entries'])}
        for e in r['entries']:
            if e['id'] not in by_id:continue
            i=by_id[e['id']];review=source['reviews'].get(str(i),{})
            included=review.get('season')==period['name'] if review.get('season') else period['start']<=e['date']<=period['end']
            if e['kind'] in ('sale','return','ipt_in','ipt_out'):
                if included and not period['start']<=e['date']<=period['cutoff']:
                    raise AuthError('Reviewed stock is outside this calculation envelope; review its season/cutoff.',409)
                for item in e.get('items',[]):
                    if item.pop('_web_season_excluded',False):
                        item.pop('exclude',None);item.pop('review_reason',None)
                if not included:
                    for item in e.get('items',[]):item.update(_web_season_excluded=True,exclude=True,review_reason='Reviewed benefit season: '+str(review.get('season') or 'outside selected period'))
        # Late IPT remains validated in Phase 4; the envelope includes it once.
        r['late_ipt_reviews']={}
        return project_reviews(r, source['document'])

    def calculation_record(self,r):
        return self.project(super().calculation_record(r))

    def calculate(self,r):
        r=self.calculation_record(r)
        result=super().calculate(r)
        if r.get('web_source') and r.get('status') not in ('finalised','issued'):
            projected=self.project(r)
            for e in projected['entries']:
                if e.get('id') in result.get('stock_scope',{}) and e.get('items') and all(i.get('exclude') for i in e['items']):
                    result['stock_scope'][e['id']]=False
        return result

    def check_payment_usage(self,r):
        from prior_payments import conflicts
        others=self.all()
        # Parent account transaction serialises check and write across workbooks.
        if getattr(self,'account_db',None) is not None:
            for row in self.account_db.execute('SELECT workbook,payload FROM calculator_workspaces WHERE owner=?',(self.owner,)):
                if row['workbook']==self.workbook:continue
                payload=json.loads(row['payload'])
                others += [json.loads(x[2]) for x in payload.get('records',[])]
        conflicts(r,others)

    def save(self,r):
        r=self.project(r)
        self.check_payment_usage(r)
        return super().save(r)

    def payload(self):
        return {t:[list(row) for row in self.connection.execute('SELECT * FROM '+t)] for t in TABLES}


class CalculatorService:
    def __init__(self, store, ledger):
        self.store,self.ledger,self.accounts=store,ledger,store.accounts
        from .finish_service import FinishService
        self.finish=FinishService(self)
        from .native_interface import NativeInterface
        self.native=NativeInterface(self)
        with self.accounts._tx() as db:
            db.execute('CREATE TABLE IF NOT EXISTS calculator_workspaces(owner TEXT NOT NULL,workbook TEXT NOT NULL,revision INTEGER NOT NULL,payload TEXT NOT NULL,PRIMARY KEY(owner,workbook))')

    def scope(self,db,u,project,workbook):
        owner=u['id']
        if project=='main':
            rows=db.execute("SELECT * FROM workspace_documents WHERE owner=? AND kind='projects' AND deleted=0 ORDER BY rowid",(owner,)).fetchall()
            if not rows:raise AuthError('Create a project and workbook in My workspace first.',409)
            project=rows[0]['id']
        self.store.row(db,owner,project,kind='projects')
        if workbook=='legacy':
            rows=db.execute("SELECT * FROM workspace_documents WHERE owner=? AND project=? AND kind='workbooks' AND deleted=0 ORDER BY rowid",(owner,project)).fetchall()
            if not rows:raise AuthError('Create a workbook in My workspace first.',409)
            workbook=rows[0]['id']
        parent,_,s=self.ledger.load(db,owner,workbook)
        if parent['project']!=project:raise AuthError('Object not found',404)
        return project,workbook,parent,s

    def request(self,token,action,data,project,workbook,record_id=''):
        if action in self.native.TRANSFERS:return self.native.transfer(token,action,data,project,workbook)
        if action in self.native.IMPORTS:return self.native.import_request(token,action,data,project,workbook)
        with self.accounts._tx() as db:
            u=self.store.user(db,token)
            u["_session_key"]=session_hash(token)
            project,workbook,parent,s=self.scope(db,u,project,workbook)
            row=db.execute('SELECT * FROM calculator_workspaces WHERE owner=? AND workbook=?',(u['id'],workbook)).fetchone()
            runtime=Runtime(json.loads(row['payload']) if row else None,s,self)
            before=runtime.payload()
            try:
                result=self.execute(db,u,project,workbook,parent,s,runtime,action,data,record_id)
                after=runtime.payload()
                if after!=before:
                    # Live session/permissions are protected by this same write
                    # transaction. Any exception rolls the whole request back.
                    self.store.user(db,token)
                    db.execute('INSERT OR REPLACE INTO calculator_workspaces VALUES(?,?,?,?)',
                               (u['id'],workbook,(row['revision'] if row else 0)+1,encode(after)))
                    self.accounts.audit(db,u['id'],'calculator_'+action,workbook)
                return result
            except (ValueError,KeyError,TypeError,ArithmeticError) as exc:
                raise AuthError(str(exc) if isinstance(exc,ValueError) else 'Invalid calculator input',400) from None
            finally:runtime.connection.close()

    def guard_record(self,u,st,r,workbook):
        if not isinstance(r,dict):raise AuthError('Invalid calculation',400)
        if 'web_calculation_settings' in r:raise AuthError('Frozen proof is server-managed',400)
        if r.get('workbook_id',workbook)!=workbook:raise AuthError('Calculation belongs to another workbook',404)
        old=st.get(r['id']) if r.get('id') else {}
        if old.get('web_source')!=r.get('web_source') and old:
            raise AuthError('Source provenance cannot be changed',409)
        if r.get('web_source') and not old:
            raise AuthError('Open source ledgers through the reviewed source action',400)
        for key in ALLOCATION_FIELDS:
            if r.get(key)!=old.get(key) and (r.get(key) or old.get(key)):
                require_permission(u,'allocate_payments')
        for key in SCHEME_FIELDS:
            if r.get(key)!=old.get(key) and (r.get(key) or old.get(key)):
                require_permission(u,'edit_schemes')
        if old:
            previous={e['id']:e for e in old['entries']}
            for e in r.get('entries',[]):
                orig=previous.get(e['id'])
                if orig:
                    if e.get('date')!=orig.get('date'):raise AuthError('Original voucher dates cannot be changed',400)
                    if old.get('web_source'):
                        for ii, item in enumerate(e.get('items', [])):
                            original_item = (orig.get('items') or [])[ii] if ii < len(orig.get('items', [])) else None
                            if original_item and any(item.get(k) != original_item.get(k) for k in ('product', 'packing_kg', 'crop', 'segment')):
                                raise AuthError('Review saved PDF product mappings, then reopen the source calculation.', 409)
                    if (orig.get('kind')=='receipt' or e.get('kind')=='receipt') and e.get('kind')!=orig.get('kind'):raise AuthError('Source receipt type cannot be changed',400)
                    e['original']=copy.deepcopy(orig.get('original') or orig)
                else:e.pop('original',None)
            # Compare ledger fields separately from allocation-only changes.
            skip=set(ALLOCATION_FIELDS)|{'revision','saved_at','result','frozen_settings'}
            if {k:v for k,v in r.items() if k not in skip}!={k:v for k,v in old.items() if k not in skip}:require_permission(u,'edit_ledger')
            try:validate_opening_sources(r,old.get('opening_sources',[]))
            except YearLinkEvidenceError as exc:raise AuthError(str(exc),409) from None
            for key in ('prior_year_link','prior_issued','lineage','source','reserved_sources','payment_history'):
                if r.get(key)!=old.get(key):raise AuthError('Source and Year Link evidence cannot be replaced through Save',409)
        else:
            require_permission(u,'edit_ledger')
            validate_opening_sources(r,[])
            if r.get('prior_year_link') or r.get('reserved_sources') or r.get('payment_history'):raise AuthError('Use reviewed payment history / Year Link',400)
            for e in r.get('entries',[]):e.pop('original',None)
        # Cash deduction edits are configuration, including direct Save shortcuts.
        old_splits={ (x.get('scheme'),x.get('product')):x for x in old.get('cash_splits',[])}
        for split in r.get('cash_splits',[]):
            prior=old_splits.get((split.get('scheme'),split.get('product')), {})
            if split.get('deduction_rate')!=prior.get('deduction_rate') and (split.get('deduction_rate') is not None or prior.get('deduction_rate') is not None):
                require_permission(u,'edit_schemes')
        r.update(workbook_id=workbook,annual_ledger=True)
        return r

    def execute(self,db,u,project,workbook,parent,s,st,action,b,record_id):
        def need(p):require_permission(u,p)
        st.owner=u['id'];st.workbook=workbook;st.account_db=db
        meta={'id':workbook,**json.loads(parent['payload'])}
        if action.startswith('native-'):return self.native.execute(db,u,project,workbook,meta,s,st,action,b)
        if action=='state':
            rows=db.execute('SELECT * FROM workspace_documents WHERE owner=? AND deleted=0 ORDER BY rowid',(u['id'],)).fetchall()
            projects=[{'id':r['id'],**json.loads(r['payload'])} for r in rows if r['kind']=='projects']
            books=[{'id':r['id'],**json.loads(r['payload'])} for r in rows if r['kind']=='workbooks' and r['project']==project]
            return {'project':next(p for p in projects if p['id']==project),'projects':projects,'workbook':meta,'workbooks':books,'deleted_workbooks':[],
                    'settings':st.settings(),'records':st.all(),'bulk_history':__import__('workbooks').bulk_history(st), 'permissions':u['permissions'],
                    'source_ledgers':[{'id':r['id'],'party':r['document']['party'],'location':r['document'].get('location',''),
                      'state':r['document'].get('state',''),'entries':len(r['document']['entries']),
                      'report_period':self.ledger.report_period(r['document'])} for r in s['ledgers'] if not r['superseded_by']]}
        if action=='record':
            fields(b,{'id'});r=Store.get(st,b['id']);st.finance=True;st.source_finance=bool(r.get('web_source'))
            try:return {'record':r,'result':st.calculate(r)}
            except AuthError as e:
                binding=r.get('web_source',{});latest=binding.get('ledger_id')
                if latest:
                    source=self.ledger.current_source(s,latest)
                    latest=source['id']
                return {'record':r,'source_error':str(e),'source_ledger_id':latest}
        if action=='ui-preferences':return self.preferences(db,u,project,workbook,b,record_id,st)
        if action=='open-source':
            need('edit_ledger');fields(b,{'ledger_id','season','revision'})
            _,rev,_=self.ledger.load(db,u['id'],workbook);self.ledger.expected(rev,b['revision'])
            source=self.ledger.ledger(s,b['ledger_id']);doc=self.ledger.effective(source,s)
            if not any(p['name']==b['season'] for p in s['periods']):raise AuthError('Choose a saved working season',400)
            existing=next((r for r in st.all() if r.get('web_source',{}).get('ledger_id')==source['id'] and r['season']==b['season'] and r['status']=='draft' and not r.get('deleted_at')),None)
            if existing:
                if (existing['web_source']['revision']==digest(source) and existing['web_source'].get('year_link')==digest(s['year_links'].get(source['id'])) and existing['web_source'].get('periods')==digest(s['periods'])):
                    return existing
                # Changed source opens a separate new draft. Earlier saved edits
                # remain intact and cannot be silently overwritten or reused.
            r={**doc,'season':b['season'],'state':doc.get('state') or meta.get('state',''),'scheme_state':'',
               'workbook_id':workbook,'annual_ledger':True,'status':'draft','revision':0,
               'allocations':[],'cash_splits':[],'opening_sources':[],'old_dues':str(max(number(doc['opening']),0)),
               'ledger_confirmed':False,'manual_order':False,'web_source':{'ledger_id':source['id'],'revision':digest(source),'year_link':digest(s['year_links'].get(source['id'])),'periods':digest(s['periods'])}}
            r.pop('id',None)
            for e in r['entries']:
                if e.get('web_review'):e['correction_reason']=e['web_review']['reason']
            link=s['year_links'].get(source['id'])
            if link:
                if self.ledger.link_stale(s,link):raise AuthError('Year Link needs review',409)
                for key in ('opening_sources','prior_year_link'):r[key]=copy.deepcopy(link['record'][key])
            return st.save(r)
        if action=='sync-catalogue':
            need('edit_schemes')
            cfg=st.settings();seed=Runtime.seed(s)
            known={p['id'] for p in cfg['products']}
            for sc in seed['schemes']:
                new=[p for p in seed['products'] if p['scheme']==sc['id'] and p['id'] not in known]
                if not new:continue
                existing=next((x for x in cfg['schemes'] if x['id']==sc['id']),None)
                if existing:existing['products']+= [p['id'] for p in new]
                else:
                    sc['products']=[p['id'] for p in new];cfg['schemes'].append(sc)
                cfg['products']+=new
            for p in s['periods']:
                if not any(x['name']==p['name'] for x in cfg['seasons']):cfg['seasons'].append({**p,'confirmed':True})
            return st.save_settings(cfg)
        if action=='settings':
            need('edit_schemes')
            # Never reinterpret Phase 4 product/period identities via a shortcut.
            products={p['id']:p for p in b['products']}
            for p in s['catalogue']:
                q=products.get(p['id'])
                if not q or any(str(q[k])!=str(p[k]) for k in ('crop','segment','packing_kg')):raise AuthError('Keep Phase 4 product and packing identities',409)
            periods={p['name']:p for p in b['seasons']}
            for p in s['periods']:
                if not periods.get(p['name']) or any(periods[p['name']].get(k)!=p[k] for k in ('start','end','cutoff')):raise AuthError('Keep Phase 4 working-period dates',409)
            from .ledger_service import validate_config
            catalogue=[{'id':p['id'],'name':p['name'],'crop':p['crop'],'segment':p['segment'],
                        'packing_kg':str(p['packing_kg']),'aliases':p.get('aliases',[])} for p in b['products']]
            periods=[{k:p[k] for k in ('name','start','end','cutoff')} for p in b['seasons'] if p.get('confirmed')]
            validate_config(catalogue,periods,s)
            if periods!=s['periods']:need('edit_ledger')
            result=st.save_settings(b)
            if catalogue!=s['catalogue'] or periods!=s['periods']:
                _,rev,_=self.ledger.load(db,u['id'],workbook)
                s.update(catalogue=catalogue,periods=periods)
                self.ledger.save(db,u['id'],workbook,rev,s,'calculator_catalogue_synced')
            return result
        if action=='validate-scheme':return {'errors':validate_scheme(b['scheme'],b.get('production',False))}
        if action in ('product-delete','scheme-delete'):
            need('edit_schemes');need('delete_records')
            return (st.product_action if action=='product-delete' else st.scheme_action)(b['id'],b['version'],b.get('restore',False))
        if action=='party-delete':
            need('delete_records');return st.party_action(b['id'],b.get('restore',False),b.get('confirm',False),b.get('expected'))
        if action in ('save','calculate','validate-limits'):
            r=self.guard_record(u,st,copy.deepcopy(b),workbook) if action=='save' else copy.deepcopy(b)
            r['workbook_scheme_state']=meta.get('state','')
            if r.get('id'):st.get(r['id']) # owned record existence, even for previews
            if r.get('workbook_id',workbook)!=workbook:raise AuthError('Calculation belongs to another workbook',404)
            st.finance=True;st.source_finance=bool(r.get('web_source'))
            if action=='save':return st.save(r)
            if action=='calculate':return st.calculate(r)
            validate_input_limits(st.project(r),st.settings());return {'valid':True}
        if action.startswith(('abs-distribution-','cash-quantity-','cash-remove-','allocation-review-','allocation-clear-')):
            need('allocate_payments')
            if 'record' in b:
                b['record']=self.guard_record(u,st,copy.deepcopy(b['record']),workbook)
                b['record']['workbook_scheme_state']=meta.get('state','')
            if action.startswith('cash-quantity-'):
                previous=next((x for x in b['record'].get('cash_splits',[]) if x.get('scheme')==b.get('scheme') and x.get('product')==b.get('product')),{})
                if b.get('deduction_rate')!=previous.get('deduction_rate') and (b.get('deduction_rate') not in (None,'') or previous.get('deduction_rate') not in (None,'')):
                    need('edit_schemes')
            st.finance=True
            target=b.get('record') or st.get(b['id'])
            st.source_finance=bool(target.get('web_source'))
            apply=action.endswith('-apply')
            if 'record' in b:b['record']=st.project(b['record'])
            if action.startswith('abs-distribution-'):return st.preview_abs_distribution(b,apply)
            if action.startswith('cash-quantity-'):return st.preview_cash_quantity(b,apply)
            if action.startswith('cash-remove-'):return st.preview_cash_removal(b,apply)
            if action.startswith('allocation-review-'):return review_allocation(st,b,apply)
            return clear_allocations(st,b,apply)
        if action=='late-ipt-review':
            need('edit_ledger')
            if st.get(b['id']).get('web_source'):raise AuthError('Review this source IPT in Import PDF / Saved Ledgers, then open the reviewed calculation.',409)
            return st.review_late_ipt(b['id'],b['revision'],b['entry_id'],b.get('reason',''),b.get('remove',False))
        if action=='workbooks':
            need('edit_ledger');need('edit_schemes')
            from datetime import date
            if not b.get('name') or not b.get('state') or not b.get('period'):raise ValueError('Enter name, state and period')
            if not date.fromisoformat(b['start'])<=date.fromisoformat(b['end'])<=date.fromisoformat(b['cutoff']):raise ValueError('Invalid working period')
            oid=uuid.uuid4().hex
            db.execute('INSERT INTO workspace_documents VALUES(?,?,?,?,?,1,0,?)',(u['id'],oid,'workbooks',project,None,validate('workbooks',{'name':b['name'],'state':b['state'],'season':b['period']})))
            _,ledger_rev,ledger_state=self.ledger.load(db,u['id'],oid)
            ledger_state['periods']=[{'name':b['period'],'start':b['start'],'end':b['end'],'cutoff':b['cutoff']}]
            self.ledger.save(db,u['id'],oid,ledger_rev,ledger_state,'ledger_period_created')
            cfg=Runtime.seed({'catalogue':[],'periods':[]}) if b.get('mode')=='blank' else st.settings();cfg['version']=1;cfg['seasons']=[{'name':b['period'],'start':b['start'],'end':b['end'],'cutoff':b['cutoff'],'confirmed':True}]
            if b.get('mode')=='blank':
                cfg['products']=[];cfg['schemes']=[]
            for sc in cfg['schemes']:
                sc.update(season=b['period'],states=[b['state']],confirmed=False)
                if b.get('mode')=='blank':sc.update(benefits=[],quantity=[],extra=[],net=[],cd=[],cash=None,billing=None,token=None,abs_rate=None,return_rate=None)
            fresh=Runtime(None,{'catalogue':[],'periods':[]},self)
            try:
                fresh.connection.execute('UPDATE settings SET data=? WHERE version=1',(dump(cfg),));fresh.connection.commit()
                db.execute('INSERT INTO calculator_workspaces VALUES(?,?,1,?)',(u['id'],oid,encode(fresh.payload())))
            finally:fresh.connection.close()
            self.accounts.audit(db,u['id'],'calculator_workbook_created',oid)
            return {'id':oid,'name':b['name'],'state':b['state']}
        # Phase 4's provenance-aware imports/audit/year-link stay authoritative.
        # These routes deliberately never fall back to the offline HTTP handler.
        phase4={'import','bulk-import','audit-import','audit-check','audit-review','audit-map','audit-bulk-nrv','year-match','year-pair','year-link-save','reparse','compare-import'}
        if action in phase4:
            if action in {'import','bulk-import','audit-import','reparse'}:need('import_statements')
            raise AuthError('Use Ledger & Seasons for reviewed imports, audit and Year Link.',409)
        if action in {'finalise','issue','revise','report','territory-report','product-csv','workbook-print','workbook-review','print-record'}:
            return self.finish.execute(db,u,project,workbook,meta,st,action,b)
        if action in {'restore','project-import'}:
            need('import_statements');need('edit_schemes');need('edit_ledger')
            raise AuthError('Use the web project interchange; offline archive restore is not supported here.',409)
        if action in {'storage','purge'}:
            need('permanent_delete' if action=='purge' else 'view_workspace')
            raise AuthError('Storage enforcement and cleanup belong to Phase 7.',409)
        raise AuthError('Calculator action is not available',404)

    def preferences(self,db,u,project,workbook,b,rid,st):
        if b is not None:
            fields(b,set(),{'theme','record_id','layout','reset'})
            rid=b.get('record_id','')
        rows=db.execute("SELECT * FROM workspace_documents WHERE owner=? AND workbook=? AND kind='layouts' AND deleted=0 ORDER BY rowid",(u['id'],workbook)).fetchall()
        # Reuse Phase 3 layout records, including imported saved positions.
        selected=next((r for r in reversed(rows) if json.loads(r['payload']).get('record_id','')==rid),None)
        session=db.execute('SELECT appearance FROM sessions WHERE token_hash=?',(u['_session_key'],)).fetchone()
        theme=session['appearance'] if session else 'studio'
        if b is not None:
            if rid:st.get(rid.removesuffix('::classic'))
            if ('layout' in b or b.get('reset')) and not rid:raise ValueError('Save the calculation before saving a layout')
            layout=b.get('layout') or (json.loads(selected['payload']) if selected else {})
            value={'name':'Calculator layout','record_id':rid,'theme':b.get('theme',theme),
                   'positions':[] if b.get('reset') else layout.get('positions',[]),'locked':False if b.get('reset') else layout.get('locked',False)}
            payload=validate('layouts',value)
            if selected:db.execute('UPDATE workspace_documents SET payload=?,revision=revision+1 WHERE owner=? AND id=?',(payload,u['id'],selected['id']))
            else:db.execute('INSERT INTO workspace_documents VALUES(?,?,?,?,?,1,0,?)',(u['id'],uuid.uuid4().hex,'layouts',project,workbook,payload))
            db.execute('UPDATE sessions SET appearance=? WHERE token_hash=?',(value['theme'],u['_session_key']))
            self.accounts.audit(db,u['id'],'calculator_layout_saved',workbook)
            return {'theme':value['theme'],'record_id':rid,'layout':{'positions':value['positions'],'locked':value['locked']} if rid else None}
        layout=json.loads(selected['payload']) if selected else None
        return {'theme':theme,'record_id':rid,'layout':{'positions':layout['positions'],'locked':layout.get('locked',False)} if layout else None}

    def protect(self, db, owner, row):
        if row['kind'] not in {'projects','workbooks'}:return
        query='SELECT 1 FROM calculator_workspaces WHERE owner=? AND workbook=?' if row['kind']=='workbooks' else 'SELECT 1 FROM calculator_workspaces c JOIN workspace_documents d ON d.owner=c.owner AND d.id=c.workbook WHERE c.owner=? AND d.project=?'
        if db.execute(query,(owner,row['id'])).fetchone():
            raise AuthError('Saved calculator history protects this workbook/project from archive.',409)

    def export_bundle(self,db,owner,project):
        return [{'workbook':r['workbook'],'payload':json.loads(r['payload'])} for r in db.execute('SELECT c.* FROM calculator_workspaces c JOIN workspace_documents d ON d.owner=c.owner AND d.id=c.workbook WHERE c.owner=? AND d.project=?',(owner,project))]

    def validate_bundle(self,bundle,documents,ledger_bundle):
        if not isinstance(bundle,list) or len(bundle)>1000:raise AuthError('Invalid calculator backup',400)
        seen=set()
        ledgers={p['workbook']:p['state'] for p in ledger_bundle}
        for part in bundle:
            fields(part,{'workbook','payload'})
            doc=documents.get(part['workbook'])
            if not doc or doc['kind']!='workbooks' or part['workbook'] in seen:raise AuthError('Invalid calculator workbook',400)
            seen.add(part['workbook']);payload=part['payload'];fields(payload,set(TABLES))
            for table,columns in TABLES.items():
                if not isinstance(payload[table],list) or len(payload[table])>100000:raise AuthError('Invalid calculator table',400)
                for row in payload[table]:
                    if not isinstance(row,list) or len(row)!=len(columns):raise AuthError('Invalid calculator row',400)
            if not payload['settings']:raise AuthError('Missing financial settings',400)
            st=None
            try:
                state=ledgers.get(part['workbook'],{'catalogue':[],'periods':[],'ledgers':[],'year_links':{}})
                st=Runtime(payload,state,self)
                for _,raw in payload['settings']:
                    cfg=json.loads(raw)
                    if not isinstance(cfg,dict):raise ValueError('Invalid financial settings')
                    # Unchanged Store validator checks product/group identities,
                    # positive packing and confirmed financial schemes.
                    test=Runtime(None,{'catalogue':[],'periods':[]},self)
                    try:
                        with test.db() as c:
                            c.execute('DELETE FROM settings');c.execute('INSERT INTO settings VALUES(?,?)',(cfg['version'],dump(cfg)))
                        test.save_settings(cfg)
                    finally:test.connection.close()
                for rid,revision,raw in payload['records']:
                    r=json.loads(raw)
                    if r.get('id')!=rid or r.get('revision')!=revision or r.get('status') not in ('draft','finalised','issued'):
                        raise ValueError('Invalid calculation identity or status')
                    completed=r['status'] in ('finalised','issued')
                    if completed:
                        from .finish_service import frozen_result
                        if not r.get('frozen_settings') or not r.get('result') or not r.get('finalised_at'):
                            raise ValueError('Incomplete frozen snapshot')
                        expected=frozen_result(r)
                        if expected.get('issues') or digest(expected)!=digest(r['result']):
                            raise ValueError('Frozen arithmetic/proof differs from saved result')
                        if r['status']=='issued' and not r.get('issued_at'):raise ValueError('Missing issue evidence')
                    elif r.get('frozen_settings') or r.get('result') or r.get('web_calculation_settings'):
                        raise ValueError('Draft cannot supply a frozen result')
                    if r.get('workbook_id')!=part['workbook']:raise ValueError('Invalid record workbook')
                    st.finance=True;st.source_finance=bool(r.get('web_source'))
                    validate_input_limits(r,r.get('web_calculation_settings') or r.get('frozen_settings') or st.settings())
                    binding=r.get('web_source')
                    if binding:
                        source=self.ledger.ledger(state,binding['ledger_id'],False)
                        source_entries={e['id']:e for e in source['document']['entries']}
                        ids=[e['id'] for e in r['entries']]
                        if len(ids)!=len(set(ids)) or set(source_entries)-set(ids):raise ValueError('Missing or duplicate source vouchers')
                        link=state['year_links'].get(source['id'])
                        validate_opening_sources(r,link['record'].get('opening_sources',[]) if link else [])
                        proof=copy.deepcopy(r.get('prior_year_link'))
                        # Older native links retained an audit display filename.
                        # Compare all financial proof in its JSON representation
                        # (the canonical reparse contains Decimal values).
                        if proof:proof.get('previous_document',{}).pop('audit_filename',None)
                        if digest(proof)!=digest(link['record'].get('prior_year_link') if link else None):raise ValueError('Year Link source mismatch')
                        # Remember staleness before IDs change. Import must never
                        # turn an obsolete review into current source evidence.
                        part.setdefault('_stale_records',[])
                        if binding.get('revision')!=digest(source) or binding.get('year_link')!=digest(link) or binding.get('periods')!=digest(state['periods']):
                            part['_stale_records'].append(rid)
                        for e in r['entries']:
                            original=source_entries.get(e['id'])
                            if original and (e.get('original') != original.get('original',original) or e.get('date')!=original['date']):raise ValueError('Source original mismatch')
                    else:
                        validate_opening_sources(r,[])
                        if r.get('prior_year_link'):raise ValueError('Missing Year Link provenance')
                records={rid:json.loads(raw) for rid,_,raw in payload['records']}
                controls={}
                for ident,total,rid in payload['issued']:
                    if not isinstance(ident,str) or ident in controls or rid not in records or records[rid]['status']!='issued':raise ValueError('Invalid issued control')
                    r=records[rid]
                    matches=[cn for cn in r['result']['CNs'] if Store.identity(r,cn['key'])==ident and number(cn['rounded'])==number(total)]
                    if len(matches)!=1:raise ValueError('Issued total differs from frozen entitlement')
                    controls[ident]=number(total)
                for r in records.values():
                    if r.get('parent'):
                        parent=records.get(r['parent'])
                        if not parent or parent['status']=='draft' or not Store.same_party(r,parent) or r.get('lineage')!=parent.get('lineage'):raise ValueError('Invalid revision lineage')
                    elif r.get('prior_issued'):raise ValueError('Missing revision parent')
                    for key,value in r.get('prior_issued',{}).items():
                        if Store.identity(r,key) not in controls or number(value)>controls[Store.identity(r,key)]:raise ValueError('Unproven prior issued amount')
                    if r['status']=='issued':
                        for cn in r['result']['proposals']:
                            if Store.identity(r,cn['key']) not in controls:raise ValueError('Missing issued control')
            except (ValueError,KeyError,TypeError,sqlite3.Error):raise AuthError('Calculator backup failed validation',400) from None
            finally:
                if st:st.connection.close()
        return bundle

    def import_bundle(self,db,u,mapping,bundle):
        need=lambda p:require_permission(u,p)
        for p in ('edit_schemes','edit_ledger','allocate_payments','import_statements'):need(p)
        for part in bundle:
            payload=copy.deepcopy(part['payload']);wb=mapping[part['workbook']]
            statuses={json.loads(row[2]).get('status') for row in payload['records']}
            if statuses & {'finalised','issued'}:need('finalise')
            if 'issued' in statuses:need('issue_cn')
            _,_,state=self.ledger.load(db,u['id'],wb)
            record_map={row[0]:uuid.uuid4().hex for row in payload['records']}
            mapping.update(record_map)
            for row in payload['records']:
                r=json.loads(row[2]);was_stale=r['id'] in part.get('_stale_records',[])
                r['id']=record_map[r['id']];r['workbook_id']=wb
                for key in ('parent','lineage','selected_party_id'):
                    if r.get(key) in record_map:r[key]=record_map[r[key]]
                binding=r.get('web_source')
                if binding:
                    binding['ledger_id']=mapping[binding['ledger_id']]
                    source=self.ledger.ledger(state,binding['ledger_id'],False)
                    binding['revision']=('stale:' if was_stale else '')+digest(source)
                    binding['year_link']=digest(state['year_links'].get(source['id']))
                    binding['periods']=digest(state['periods'])
                    link=state['year_links'].get(source['id'])
                    if link:
                        manual=[x for x in r.get('opening_sources',[]) if not x.get('year_link_receipt')]
                        r['opening_sources']=manual+copy.deepcopy(link['record']['opening_sources'])
                        r['prior_year_link']=copy.deepcopy(link['record']['prior_year_link'])
                row[0]=r['id'];row[2]=dump(r)
            for issued in payload['issued']:issued[2]=record_map[issued[2]]
            db.execute('INSERT INTO calculator_workspaces VALUES(?,?,1,?)',(u['id'],wb,encode(payload)))
        imported_workbooks={mapping[p['workbook']] for p in bundle}
        # Phase 3 layouts can key Classic separately from Navy for the same ID.
        for row in db.execute("SELECT * FROM workspace_documents WHERE owner=? AND kind='layouts' AND deleted=0",(u['id'],)).fetchall():
            if row['workbook'] not in imported_workbooks:continue
            data=json.loads(row['payload']);rid=data.get('record_id','');base=rid.removesuffix('::classic')
            if base in mapping:
                data['record_id']=mapping[base]+('::classic' if rid.endswith('::classic') else '')
                db.execute('UPDATE workspace_documents SET payload=? WHERE owner=? AND id=?',(encode(data),u['id'],row['id']))
