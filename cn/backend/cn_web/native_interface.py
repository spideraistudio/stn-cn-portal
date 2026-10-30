from decimal import Decimal
"""Secure transport for the preserved offline screens, without replacement UI."""
import base64
import copy
import gzip
import io
import hashlib
import json
import uuid
from .data_store import fields, validate
from .ledger_service import digest, encode, number, text, validate_config
from .security import AuthError, require_permission
from store import Store, dump, now
from importer import compare_import
from ledger_audit import audit_documents, save_audit_review, norm, cn_product_key
from year_link import match_years
from .statement_review import analyse_pair, same_issuer


class NativeInterface:
    TRANSFERS={'native-backup','native-restore','native-project-export','native-project-import'}
    IMPORTS={'native-import','native-bulk-import','native-audit-import','native-replace-import','native-reparse'}

    def __init__(self, calculator):
        self.calc=calculator
        self.ledger=calculator.ledger

    def metadata(self, token, project, workbook):
        """Link only already-authorised saved definitions, never infer PDF terms."""
        from .calculator_service import Runtime
        with self.calc.accounts._tx() as db:
            u=self.calc.store.user(db,token,'import_statements');require_permission(u,'edit_ledger')
            project,workbook,parent,s=self.calc.scope(db,u,project,workbook)
            row=db.execute('SELECT payload FROM calculator_workspaces WHERE owner=? AND workbook=?',(u['id'],workbook)).fetchone()
            st=Runtime(json.loads(row['payload']) if row else None,s,self.calc)
            try:cfg=st.settings()
            finally:st.connection.close()
            before=digest(s)
            known={p['id'] for p in s['catalogue']}
            for p in cfg['products']:
                if p['id'] not in known and not p.get('deleted_at'):
                    s['catalogue'].append({k:copy.deepcopy(p.get(k,[] if k=='aliases' else 'Awaiting scheme')) for k in ('id','name','crop','segment','packing_kg','aliases')})
            for p in cfg['seasons']:
                if p.get('confirmed') and p.get('start') and not any(x['name']==p['name'] for x in s['periods']):s['periods'].append({k:p[k] for k in ('name','start','end','cutoff')})
            if before!=digest(s):
                validate_config(s['catalogue'],s['periods']);_,rev,_=self.ledger.load(db,u['id'],workbook)
                self.ledger.save(db,u['id'],workbook,rev,s,'native_saved_definitions_linked')
            return project,workbook,cfg

    def import_request(self,token,action,b,project,workbook):
        if action=='native-reparse':
            fields(b,{'record_id','season'})
            source=self.calc.request(token,'native-source-file',{'id':b['record_id']},project,workbook)
            b={'data':source['data'],'filename':source['filename'],'season':b['season']}
        fields(b,{'data'},{'filename','season','replacement','reason','expected','record_id'})
        project,workbook,cfg=self.metadata(token,project,workbook)
        state=self.ledger.state(token,workbook)
        request={'revision':state['revision'],'files':[{'name':b.get('filename') or 'Statement.pdf','content_base64':b['data']}]}
        preview=self.ledger.import_files(token,workbook,request)
        if action=='native-audit-import':
            # Store the exact uploaded bytes as owned evidence. Audit documents
            # are reparsed server-side from this scoped file on every operation.
            raw=base64.b64decode(b['data'],validate=True)
            docs=self.ledger.parse(raw,{'catalogue':state['catalogue'],'periods':state['periods']})
            file=self.calc.store.request(token,'POST','files',data={'project':project,'workbook':workbook,'data':{'name':b.get('filename') or 'Audit statement.pdf','content_base64':b['data']}})
            return {'documents':[{**d,'web_file_id':file['id'],'web_document_index':i} for i,d in enumerate(docs)]}
        if action=='native-import' and len(preview['results'])!=1:
            return {'combined_ledgers':True,'ledger_count':len(preview['results']),'parties':[{'party':x['party']} for x in preview['results']]}
        changes=[r for r in preview['results'] if r['candidates']]
        if action=='native-bulk-import':
            file=self.calc.store.request(token,'POST','files',data={'project':project,'workbook':workbook,'data':{'name':b.get('filename') or 'Statement.pdf','content_base64':b['data']}})
            return self.calc.request(token,'native-bulk-register',{'file_id':file['id'],'season':b.get('season') or cfg['seasons'][0]['name']},project,workbook)
        if changes and action!='native-replace-import':
            return {'native_import_review':True,'preview':preview,'request':b}
        if changes:
            if b.get('expected')!=preview['preview_digest']:raise AuthError('Statement changed. Import it again to review.',409)
            if len(changes)!=1 or b.get('replacement') not in changes[0]['candidates']:raise AuthError('Choose the existing statement being replaced',400)
            request.update(replacements={changes[0]['key']:b['replacement']},reason=b.get('reason',''))
        result=self.ledger.import_files(token,workbook,{**request,'preview_digest':preview['preview_digest']},True)
        season=b.get('season') or cfg['seasons'][0]['name']
        opened=[]
        for row in result['results']:
            saved=self.calc.request(token,'native-open',{'ledger_id':row['id'],'season':season},project,workbook)
            opened.append(saved)
            self.calc.request(token,'native-log',{'record_id':saved['id'],'filename':b.get('filename','Statement.pdf'),'status':row['status']},project,workbook)
        if action=='native-bulk-import':
            state=self.calc.request(token,'state',None,project,workbook)
            ids={r['id'] for r in opened}
            return {'results':[r for r in state['bulk_history'] if r.get('record_id') in ids]}
        return {'native_record':opened[0]}

    def documents(self,db,u,workbook,values,s):
        if not isinstance(values,list) or len(values)>1000:raise AuthError('Invalid documents',400)
        parsed={};out=[]
        for value in values:
            if not isinstance(value,dict):raise AuthError('Invalid document reference',400)
            if value.get('web_ledger_id'):
                doc=self.ledger.effective(self.ledger.ledger(s,value['web_ledger_id'],False),s)
            else:
                file=self.calc.store.row(db,u['id'],value.get('web_file_id'),kind='files')
                if file['workbook']!=workbook:raise AuthError('Source file not found',404)
                if file['id'] not in parsed:parsed[file['id']]=self.ledger.parse(base64.b64decode(json.loads(file['payload'])['content_base64']),s)
                index=value.get('web_document_index')
                if type(index) is not int or not 0<=index<len(parsed[file['id']]):raise AuthError('Invalid source document',400)
                doc=copy.deepcopy(parsed[file['id']][index])
            doc['audit_filename']=str(value.get('audit_filename') or 'Statement.pdf')[:500]
            out.append(doc)
        return out

    def bind(self,s,source):
        return {'ledger_id':source['id'],'revision':digest(source),'year_link':digest(s['year_links'].get(source['id'])),'periods':digest(s['periods'])}

    def open(self,st,meta,workbook,s,b):
        fields(b,{'ledger_id','season'})
        source=self.ledger.current_source(s,b['ledger_id'])
        if not any(p['name']==b['season'] for p in st.settings()['seasons']):raise AuthError('Choose a working period from this workbook',400)
        binding=self.bind(s,source)
        existing=next((r for r in st.all() if r.get('web_source',{}).get('ledger_id')==source['id'] and r['season']==b['season'] and not r.get('deleted_at') and r['status']=='draft' and r['web_source']==binding),None)
        if existing:return existing
        related=[r for r in st.all() if r.get('web_source') and r.get('season')==b['season'] and not r.get('deleted_at') and self.ledger.current_source(s,r['web_source']['ledger_id'])['id']==source['id']]
        draft=next((r for r in related if r['status']=='draft'),None)
        if draft:return self.refresh(st,s,draft)
        completed=next((r for r in related if r['status'] in ('finalised','issued')),None)
        if completed:
            if completed['web_source']['ledger_id']==source['id']:return completed
            raise AuthError('Create a revision of the completed calculation before replacing this statement.',409)
        doc=self.ledger.effective(source,s);link=s['year_links'].get(source['id'])
        if link and self.ledger.link_stale(s,link):raise AuthError('Year Link needs review',409)
        r={**doc,'workbook_id':workbook,'annual_ledger':True,'workbook_scheme_state':meta.get('state',''),
           'season':b['season'],'state':doc.get('state') or meta.get('state',''),'old_dues':str(max(number(doc['opening']),0)),
           'opening_dues_review_required':True,'allocations':[],'cash_splits':[],'opening_sources':[],
           'ledger_confirmed':False,'status':'draft','revision':0,'web_source':binding,'manual_order':False}
        r.pop('id',None)
        if link:
            for key in ('opening_sources','prior_year_link'):r[key]=copy.deepcopy(link['record'][key])
        return st.save(r)

    def execute(self,db,u,project,workbook,meta,s,st,action,b):
        need=lambda p:require_permission(u,p)
        if action.startswith('native-payment-history-'):
            from prior_payments import party_match, analyse, attach
            need('allocate_payments')
            r=Store.get(st,b['id'])
            if r.get('revision')!=b.get('revision'):raise AuthError('Record changed; reopen payment history',409)
            if r.get('status')!='draft' or not r.get('web_source'):raise AuthError('Open an imported draft statement first',400)
            st.project(r)
            current=self.ledger.ledger(s,r['web_source']['ledger_id'])['document']
            if action=='native-payment-history-match':
                docs=self.documents(db,u,workbook,b['documents'],s)
                matches=[i for i,d in enumerate(docs) if party_match(d,current)['matched']]
                if len(matches)!=1:raise AuthError('Expected exactly one prior statement with the same seller name and full address; found '+str(len(matches))+'. Wrong/missing/ambiguous identity is blocked.',400)
                i=matches[0];previous=docs[i]
                from year_link import period
                _,end=period(previous)
                start=str(end.year)+'-01-01'
                return {'previous':b['documents'][i],'match':party_match(previous,current),'plan':analyse(previous,current,start,end.isoformat())}
            if action=='native-payment-history-unlink':
                need('edit_ledger')
                import copy
                candidate=copy.deepcopy(r)
                ids={x['id'] for x in r.get('reserved_sources',[])}|{x['id'] for x in r.get('opening_sources',[]) if x.get('year_link_receipt')}
                if any(a.get('source') in ids for a in r.get('allocations',[])):
                    raise AuthError('Remove allocations using linked prior-year receipts before unlinking. Other opening-credit allocations can stay.',400)
                candidate['reserved_sources']=[]
                candidate['opening_sources']=[x for x in candidate.get('opening_sources',[]) if x['id'] not in ids]
                candidate.pop('payment_history',None)
                candidate.pop('prior_year_link',None)
                candidate['old_dues']=str(max(0,Decimal(str(candidate['opening']))))
                candidate.pop('opening_dues_review',None)
                candidate['opening_dues_review_required']=True
                return st.save(candidate)
            previous=self.documents(db,u,workbook,[b['previous']],s)[0]
            if action=='native-payment-history-preview':return analyse(previous,current,b['start'],b['end'],b.get('approvals',[]))
            if action=='native-payment-history-save':
                need('edit_ledger')
                allowed={p['crop'] for p in st.settings()['products']}|set(st.settings().get('crops',[]))
                if any(x.get('crop') not in allowed for x in b.get('selections',[])):raise AuthError('Choose an existing workbook crop',400)
                candidate=attach(r,previous,current,b['start'],b['end'],b.get('approvals',[]),b.get('selections',[]))
                return st.save(candidate)
            raise AuthError('Unknown payment history action',404)
        if action.startswith('native-billing-'):
            from . import billing_audit as billing
            cfg=s.get('billing_audit',billing.empty())
            _,revision,_=self.ledger.load(db,u['id'],workbook)
            if action in ('native-billing-config','native-billing-rates'):
                refs=cfg['sources']+[{'web_ledger_id':r['id']} for r in s['ledgers'] if not r['superseded_by']]
                if action=='native-billing-config':
                    fields(b,set(),{'documents'})
                    if not isinstance(b.get('documents',[]),list):raise AuthError('Invalid documents',400)
                    refs += b.get('documents',[])
                docs=self.documents(db,u,workbook,refs,s)
                states=billing.recorded_states(cfg,docs,meta,st.settings(),st.all())
                context={'products':s['catalogue'],'states':states,
                         'scheme_rates':[{k:copy.deepcopy(sc.get(k)) for k in ('name','products','states','season','billing','billing_unit')} for sc in st.settings().get('schemes',[]) if not sc.get('deleted_at')]}
            if action=='native-billing-config':
                return {'revision':revision,'configuration':cfg,**context}
            if action=='native-billing-rates':
                need('edit_schemes');fields(b,{'revision','rates'})
                self.ledger.expected(revision,b['revision'])
                billing.validate({**cfg,'rates':b['rates']},s['catalogue'])
                cfg=billing.validate({**cfg,'rates':billing.canonical_rates(b['rates'],cfg['rates'],states)},s['catalogue'])
                s['billing_audit']=cfg
                revision=self.ledger.save(db,u['id'],workbook,revision,s,'billing_rates_saved')
                return {'revision':revision,'configuration':cfg,**context}
            fields(b,{'documents','start','end'},{'include_saved','matches','revision','evidence','review','row_id'})
            if not isinstance(b['documents'],list) or len(b['documents'])>1000 or any(not isinstance(v,dict) for v in b['documents']):raise AuthError('Invalid billing documents',400)
            refs=copy.deepcopy(cfg['sources'])
            for value in b['documents']:
                ref=({'web_ledger_id':value['web_ledger_id']} if value.get('web_ledger_id') else
                     {'web_file_id':value.get('web_file_id'),'web_document_index':value.get('web_document_index')})
                if ref not in refs:refs.append(ref)
            if b.get('include_saved',True):
                for r in s['ledgers']:
                    ref={'web_ledger_id':r['id']}
                    if not r['superseded_by'] and ref not in refs:refs.append(ref)
            docs=self.documents(db,u,workbook,refs,s)
            if not docs:raise AuthError('Import the PDFs to audit, or include saved ledgers',400)
            if action=='native-billing-run':
                report=billing.run(docs,s,b['start'],b['end'])
                report['revision']=revision
                from .audit_mapping import targets
                report['mapping_targets']=targets(docs,refs,s,b['start'],b['end'])
                return report
            if action=='native-billing-review':
                need('edit_ledger');self.ledger.expected(revision,b.get('revision'))
                report=billing.run(docs,s,b['start'],b['end'])
                if report['evidence']!=b.get('evidence'):raise AuthError('Billing evidence changed. Run the audit again.',409)
                row=next((r for r in report['rows'] if r['id']==b.get('row_id')),None)
                if not row:raise AuthError('Billing line not found',404)
                review=b.get('review');fields(review,{'status','reason'})
                cfg={**cfg,'sources':refs,'reviews':{**cfg.get('reviews',{}),row['id']:{**review,'evidence':row['review_evidence']}}}
                s['billing_audit']=billing.validate(cfg,s['catalogue'])
                revision=self.ledger.save(db,u['id'],workbook,revision,s,'billing_finding_reviewed')
                report=billing.run(docs,s,b['start'],b['end']);report['revision']=revision
                from .audit_mapping import targets
                report['mapping_targets']=targets(docs,refs,s,b['start'],b['end'])
                return report
            if action=='native-billing-match':
                need('edit_ledger');self.ledger.expected(revision,b.get('revision'))
                current=billing.run(docs,s,b['start'],b['end'])
                if current['evidence']!=b.get('evidence'):raise AuthError('Billing evidence changed. Run the audit again.',409)
                matches=b.get('matches')
                if not isinstance(matches,dict):raise AuthError('Return selections are required',400)
                merged={**cfg['matches'],**matches}
                # Explicit empty selection removes a previously chosen match.
                merged={k:v for k,v in merged.items() if v}
                billing.run(docs,s,'0001-01-01','9999-12-31',merged,strict=True)
                s['billing_audit']=billing.validate({**cfg,'matches':merged,'sources':refs},s['catalogue'])
                revision=self.ledger.save(db,u['id'],workbook,revision,s,'billing_original_bills_saved')
                report=billing.run(docs,s,b['start'],b['end']);report['revision']=revision
                from .audit_mapping import targets
                report['mapping_targets']=targets(docs,refs,s,b['start'],b['end'])
                return report
            raise AuthError('Unknown billing action',404)
        if action=='native-state':
            out=self.calc.execute(db,u,project,workbook,{'payload':encode(meta)},s,st,'state',None,'')
            for source in s['ledgers']:
                if source['superseded_by'] or any(r.get('web_source',{}).get('ledger_id')==source['id'] for r in out['records']):continue
                doc=self.ledger.effective(source,s)
                out['records'].append({**doc,'id':'source:'+source['id'],'revision':0,'status':'draft','season':st.settings()['seasons'][0]['name'],'allocations':[],'cash_splits':[],'opening_sources':[],'native_saved_source':True})
            return out
        if action=='native-bulk-register':
            need('import_statements');need('edit_ledger');fields(b,{'file_id','season'})
            file=self.calc.store.row(db,u['id'],b['file_id'],kind='files')
            if file['workbook']!=workbook:raise AuthError('Source file not found',404)
            value=json.loads(file['payload']);docs=self.ledger.parse(base64.b64decode(value['content_base64']),s);results=[]
            if not any(p['name']==b['season'] for p in st.settings()['seasons']):raise AuthError('Choose a saved working period',400)
            for i,doc in enumerate(docs):
                try:
                    existing=next((r for r in s['ledgers'] if not r['superseded_by'] and Store.same_party(r['document'],doc) and same_issuer(r['document'],doc) and self.ledger.report_period(r['document'])==self.ledger.report_period(doc)),None)
                    sha=hashlib.sha256(base64.b64decode(value['content_base64'])).hexdigest()
                    if existing and (existing['file_sha256']!=sha or existing['source_index']!=i):
                        pending=self.execute(db,u,project,workbook,meta,s,st,'native-pending',{'source':existing['id'],'data':value['content_base64'],'filename':value['name'],'season':b['season']});results.append(pending);continue
                    source=self.register(db,u,workbook,s,doc,{'web_file_id':file['id'],'web_document_index':i})
                    record=self.open(st,meta,workbook,s,{'ledger_id':source['id'],'season':b['season']})
                    results.append(self.execute(db,u,project,workbook,meta,s,st,'native-log',{'record_id':record['id'],'filename':value['name'],'status':'Already imported' if existing else 'Imported'}))
                except (ValueError,AuthError) as e:
                    results.append({'id':digest((file['id'],i)),'filename':value['name'],'party':doc['party'],'season':b['season'],'status':'Failed','message':str(e)})
            _,rev,_=self.ledger.load(db,u['id'],workbook);self.ledger.save(db,u['id'],workbook,rev,s,'native_bulk_imported')
            return {'results':results}
        if action=='native-source-file':
            need('import_statements');fields(b,{'id'});r=Store.get(st,b['id'])
            source=self.ledger.ledger(s,r['web_source']['ledger_id'],False)
            file=self.calc.store.row(db,u['id'],source['file_id'],kind='files')
            if file['workbook']!=workbook:raise AuthError('Source file not found',404)
            value=json.loads(file['payload']);return {'data':value['content_base64'],'filename':value['name']}
        if action=='native-stale-result':
            fields(b,{'id'});r=Store.get(st,b['id'])
            if not r.get('web_source'):raise AuthError('No saved source',400)
            if r.get('status') in ('finalised','issued'):return copy.deepcopy(r['result'])
            from engine import compute
            result=compute(r,Store.settings(st));result['issues'].insert(0,'Saved source changed: review the updated ledger before saving or finalising.')
            result['can_finalise']=False;return result
        if action=='native-refresh':
            need('edit_ledger');fields(b,{'id','revision'});r=Store.get(st,b['id'])
            if r['status']!='draft' or r['revision']!=b['revision']:raise AuthError('Reopen the current draft',409)
            return self.refresh(st,s,r)
        if action=='native-open':
            need('edit_ledger');return self.open(st,meta,workbook,s,b)
        if action=='native-log':
            need('import_statements');need('edit_ledger');fields(b,{'record_id','filename','status'})
            if b['status'] not in ('Imported','Already imported'):raise AuthError('Invalid import status',400)
            text(b['filename'],'filename',500)
            r=Store.get(st,b['record_id']);key=digest((r['web_source']['ledger_id'],r['season']))
            sc=next(p for p in st.settings()['seasons'] if p['name']==r['season'])
            row={'id':key,'filename':b['filename'],'party':r['party'],'season':r['season'],'status':b['status'],'record_id':r['id'],'time':now()}
            if sc.get('start') and sc.get('end'):row['ledger_audit']=audit_documents([r],sc['start'],sc['end'],st.settings())
            with st.db() as c:c.execute('INSERT OR REPLACE INTO bulk_imports VALUES(?,?)',(key,dump(row)))
            return row
        if action=='native-pending':
            need('import_statements');need('edit_ledger')
            source=self.ledger.ledger(s,b['source']);r=next((r for r in st.all() if r.get('web_source',{}).get('ledger_id')==source['id'] and r.get('season')==b['season'] and not r.get('deleted_at')),None)
            key=digest((source['id'],b['season'],'pending'))
            row={'id':key,'filename':b['filename'],'party':source['document']['party'],'season':b['season'],'status':'Needs review','record_id':r['id'] if r else None,'message':'Review the changed statement before replacing saved vouchers.','native_data':b['data']}
            with st.db() as c:c.execute('INSERT OR REPLACE INTO bulk_imports VALUES(?,?)',(key,dump(row)))
            return {k:v for k,v in row.items() if k!='native_data'}
        if action=='native-bulk-document':
            fields(b,{'id'})
            with st.db() as c:row=c.execute('SELECT data FROM bulk_imports WHERE id=?',(b['id'],)).fetchone()
            if not row:raise AuthError('Import not found',404)
            return json.loads(row[0])
        if action=='native-late-ipt-review':
            need('edit_ledger');fields(b,{'id','revision','entry_id','reason'},{'remove'})
            r=Store.get(st,b['id'])
            if not r.get('web_source'):return st.review_late_ipt(b['id'],b['revision'],b['entry_id'],b['reason'],b.get('remove',False))
            if r['status']!='draft' or r['revision']!=b['revision']:raise AuthError('Reopen the current draft',409)
            st.project(r);source=self.ledger.ledger(s,r['web_source']['ledger_id']);ei=next((i for i,e in enumerate(source['document']['entries']) if e['id']==b['entry_id']),None)
            if ei is None or source['document']['entries'][ei]['kind'] not in ('ipt_in','ipt_out'):raise AuthError('Choose a source IPT',400)
            review={**source['reviews'].get(str(ei),{}),'reason':b['reason']}
            if b.get('remove'):review.pop('season',None)
            else:review['season']=r['season']
            self.ledger.validate_review(source,s,ei,review);source['reviews'][str(ei)]=review
            _,rev,_=self.ledger.load(db,u['id'],workbook);self.ledger.save(db,u['id'],workbook,rev,s,'native_late_ipt_reviewed',source['id'])
            r['web_source']=self.bind(s,source);r['ledger_confirmed']=False
            for e in r['entries']:
                if e['id']==b['entry_id']:e['web_review']=copy.deepcopy(review);e['correction_reason']=b['reason']
            return st.save(r)
        if action=='native-map':return self.mapping(db,u,workbook,s,st,b)
        if action in ('native-audit-product-context','native-audit-product-save'):
            fields(b,{'source','entry_id','item_index'},{'revision','evidence','crop','name','packing'})
            if not isinstance(b['source'],dict):raise AuthError('Choose a statement product line',400)
            doc=self.documents(db,u,workbook,[b['source']],s)[0]
            entry=next((e for e in doc['entries'] if e['id']==b['entry_id']),None)
            if not entry or entry['kind'] not in ('sale','return','ipt_in','ipt_out'):raise AuthError('Original stock entry not found',404)
            from .ledger_service import index
            item=index(b['item_index'],entry.get('items',[]))
            proof=digest([doc.get('party'),doc.get('location'),entry['id'],item])
            _,rev,_=self.ledger.load(db,u['id'],workbook)
            if action=='native-audit-product-context':
                return {'revision':rev,'evidence':proof,'item':item,'party':doc.get('party',''),'entry':{k:entry.get(k) for k in ('date','reference','kind')},'products':s['catalogue'],'crops':list(dict.fromkeys(st.settings().get('crops',[])+[p['crop'] for p in s['catalogue']]))}
            fields(b,{'source','entry_id','item_index','revision','evidence','crop','name','packing'})
            need('edit_ledger');self.ledger.expected(rev,b.get('revision'))
            if proof!=b.get('evidence'):raise AuthError('Statement mapping evidence changed. Reopen the line.',409)
            product=self.mapping_product(u,s,st,item,b)
            source=self.register(db,u,workbook,s,doc,b['source'])
            from .product_mapping import identity
            for ei,e in enumerate(source['document']['entries']):
                for ii,other in enumerate(e.get('items',[])):
                    if identity(other)==identity(item):source['mappings'][f'{ei}:{ii}']=product['id']
            revision=self.ledger.save(db,u['id'],workbook,rev,s,'audit_source_product_mapped',source['id'])
            return {'revision':revision,'product_id':product['id']}
        if action=='native-audit-check':
            docs=self.documents(db,u,workbook,b['documents'],s)
            result=self.audit_report(docs,b['documents'],s,st,b)
            if b.get('coverage_errors'):
                from ledger_nrv import mark_incomplete
                mark_incomplete(result['posted_CN_NRV'],'Some uploaded PDFs failed; combined averages withheld')
                result['warnings'] += [{'party':'Upload coverage','message':str(e)} for e in b['coverage_errors']]
            return result
        if action=='native-audit-bulk-nrv':
            docs=[{**self.ledger.effective(r,s),'audit_filename':'Saved statement.pdf'} for r in s['ledgers'] if not r['superseded_by']]
            refs=[{'web_ledger_id':r['id']} for r in s['ledgers'] if not r['superseded_by']]
            return self.audit_report(docs,refs,s,st,b)
        if action=='native-audit-review':
            need('edit_ledger')
            docs=self.documents(db,u,workbook,b['documents'],s) if b.get('documents') else [self.ledger.effective(r,s) for r in s['ledgers'] if not r['superseded_by']]
            report=audit_documents(docs,b['start'],b['end'],st.settings())
            if not any(f.get('review_id')==b.get('review_id') for f in report['findings']):raise AuthError('Finding evidence changed. Run the ledger check again.',409)
            return save_audit_review(st,b)
        if action=='native-audit-map':
            need('edit_schemes');need('edit_ledger')
            cfg=st.settings()
            if b['version']!=cfg['version']:raise AuthError('Settings changed; refresh first',409)
            key=norm(b['narration']);crop=str(b['crop']).strip();classification=b.get('classification','scheme' if crop else 'unclassified')
            if not key or classification not in ('unclassified','scheme','freight','other','material_return'):raise AuthError('Invalid CN classification',400)
            if crop and crop not in {p['crop'] for p in cfg['products']}|set(cfg.get('crops',[])):raise AuthError('Choose a saved crop',400)
            if classification!='scheme':crop=''
            product=b.get('product') or ''
            from ledger_audit import voucher_view
            docs=self.documents(db,u,workbook,b['documents'],s) if b.get('documents') else [self.ledger.effective(r,s) for r in s['ledgers'] if not r['superseded_by']]
            evidence=[voucher_view(doc,e) for doc in docs for e in doc['entries'] if e['kind']=='posted_cn']
            candidates=[v for v in evidence if norm(v['narration'])==key]
            if not candidates:raise AuthError('Narration evidence changed. Rerun the ledger check.',409)
            if b.get('product_mapping_key') and not any(cn_product_key(v)==b['product_mapping_key'] for v in candidates):raise AuthError('Product evidence changed. Rerun the ledger check.',409)
            if product:
                p=next((p for p in cfg['products'] if p['id']==product and not p.get('deleted_at')),None)
                if not p or p['crop']!=crop or classification!='scheme':raise AuthError('Choose a product in this crop',400)
                evidence=b.get('voucher',{})
                if norm(evidence.get('narration'))!=key or cn_product_key(evidence)!=b.get('product_mapping_key'):raise AuthError('Rerun source audit before attributing a product',409)
                cfg.setdefault('audit_product_mappings',{})[b['product_mapping_key']]=product
            elif b.get('product_mapping_key'):cfg.setdefault('audit_product_mappings',{}).pop(b['product_mapping_key'],None)
            cfg.setdefault('audit_cn_classifications',{})[key]=classification
            if crop:cfg.setdefault('audit_crop_mappings',{})[key]=crop
            else:cfg.setdefault('audit_crop_mappings',{}).pop(key,None)
            return st.save_settings(cfg)
        if action in {'native-year-match','native-year-pair','native-year-link-save'}:
            if action=='native-year-match':return match_years(self.documents(db,u,workbook,b['previous'],s),self.documents(db,u,workbook,b['current'],s))
            previous,current=self.documents(db,u,workbook,[b['previous'],b['current']],s)
            if action=='native-year-pair':return analyse_pair(previous,current,b.get('identity_reason',''))
            need('edit_ledger')
            # Register immutable source evidence in the existing ledger store.
            previous_source=self.register(db,u,workbook,s,previous,b['previous'])
            current_source=self.register(db,u,workbook,s,current,b['current'])
            previous,current=previous_source['document'],current_source['document']
            result=analyse_pair(previous,current,b.get('identity_reason',''))
            from year_link import attach_link
            linked=attach_link({**current,'status':'draft','allocations':[],'opening_sources':[]},previous,current,b.get('confirmed',{}),b.get('reason',''),b.get('identity_reason',''))
            s['year_links'][current_source['id']]={'previous_id':previous_source['id'],'current_id':current_source['id'],'previous_signature':result['previous_signature'],'current_signature':result['current_signature'],'record':linked}
            _,rev,_=self.ledger.load(db,u['id'],workbook);self.ledger.save(db,u['id'],workbook,rev,s,'native_year_linked',current_source['id'])
            existing=next((r for r in st.all() if not r.get('deleted_at') and r.get('web_source',{}).get('ledger_id')==current_source['id'] and r.get('season')==b['season']),None)
            if existing:
                if existing['status']!='draft':raise AuthError('Create a revision before changing a completed Year Link',409)
                linked_record=attach_link(existing,previous,current,b.get('confirmed',{}),b.get('reason',''),b.get('identity_reason',''),b.get('replace_unused',False))
                linked_record['web_source']=self.bind(s,current_source);linked_record['ledger_confirmed']=False
                return st.save(linked_record)
            return self.open(st,meta,workbook,s,{'ledger_id':current_source['id'],'season':b['season']})
        raise AuthError('Native action not available',404)

    def register(self,db,u,workbook,s,doc,reference):
        if reference.get('web_ledger_id'):return self.ledger.ledger(s,reference['web_ledger_id'])
        file=self.calc.store.row(db,u['id'],reference['web_file_id'],kind='files')
        if file['workbook']!=workbook:raise AuthError('Source file not found',404)
        raw=base64.b64decode(json.loads(file['payload'])['content_base64']);sha=hashlib.sha256(raw).hexdigest();index=reference['web_document_index']
        existing=next((r for r in s['ledgers'] if r['file_sha256']==sha and r['source_index']==index and not r['superseded_by']),None)
        if existing:return existing
        if any(not r['superseded_by'] and Store.same_party(r['document'],doc) and same_issuer(r['document'],doc) and self.ledger.report_period(r['document'])==self.ledger.report_period(doc) for r in s['ledgers']):raise AuthError('Current statement needs ordinary repeat-import review first.',409)
        party_id=uuid.uuid4().hex
        db.execute('INSERT INTO workspace_documents VALUES(?,?,?,?,?,1,0,?)',(u['id'],party_id,'parties',file['project'],workbook,validate('parties',{'name':doc['party'],'reference':doc.get('location','')})))
        original=copy.deepcopy(doc);original.pop('audit_filename',None)
        source={'id':uuid.uuid4().hex,'file_id':file['id'],'file_sha256':sha,'source_index':index,'party_id':party_id,'document':original,'reviews':{},'mappings':{},'superseded_by':None,'replacement_reason':''}
        from .product_mapping import plan as mapping_plan
        source['mappings']={k:v['product_id'] for k,v in mapping_plan(original,s).items() if v['product_id']}
        s['ledgers'].append(source);return source

    def audit_report(self,docs,refs,s,st,b):
        from .audit_mapping import targets,nrv_for_audit
        result=audit_documents(docs,b['start'],b['end'],st.settings())
        result['posted_CN_NRV']=nrv_for_audit(docs,s,st.settings(),b['start'],b['end'])
        result['mapping_targets']=targets(docs,refs,s,b['start'],b['end'])
        result['posted_CN_NRV']['mapping_targets']=result['mapping_targets']
        return result

    def mapping_product(self,u,s,st,item,b):
        from .product_mapping import compatible as packing_compatible
        cfg=st.settings();crop=' '.join(text(b['crop'],'crop',200).split());name=text(b['name'],'product name',200);packing=str(number(b['packing']))
        if crop.casefold()=='all' or number(packing)<=0:raise AuthError('Enter a real crop and positive packing',400)
        crop=next((p['crop'] for p in cfg['products']+s['catalogue'] if p['crop'].casefold()==crop.casefold()),crop)
        matches=[p for p in s['catalogue'] if p['name'].casefold()==name.casefold() and p['crop']==crop and number(p['packing_kg'])==number(packing)]
        if len(matches)>1:raise AuthError('Choose a unique saved product/packing',409)
        if matches:product=matches[0]
        else:
            require_permission(u,'edit_schemes')
            product={'id':uuid.uuid4().hex,'name':name,'crop':crop,'segment':'Awaiting scheme','packing_kg':packing,'aliases':[item['name']]}
            validate_config([*s['catalogue'],product],s['periods'],s);s['catalogue'].append(product)
        if not packing_compatible(item,product):raise AuthError('Source packing differs; keep packing variants separate',400)
        # Existing source identities may be reused without granting scheme edits.
        if not any(p['id']==product['id'] for p in cfg['products']):
            from .calculator_service import Runtime
            seed=Runtime.seed({'catalogue':[product],'periods':s['periods']})
            cfg['products']+=seed['products']
            for sc in seed['schemes']:
                existing=next((v for v in cfg['schemes'] if v['id']==sc['id']),None)
                if existing:existing['products']+=sc['products']
                else:cfg['schemes'].append(sc)
            cfg['crops']=list(dict.fromkeys(cfg.get('crops',[])+[crop]));st.save_settings(cfg)
        return product

    def mapping(self,db,u,workbook,s,st,b):
        require_permission(u,'edit_ledger');fields(b,{'id','revision','entry_id','item_index','crop','name','packing'})
        r=Store.get(st,b['id'])
        if r['status']!='draft' or r.get('deleted_at') or r['revision']!=b['revision']:raise AuthError('Reopen the current draft before mapping',409)
        st.project(r)
        source=self.ledger.ledger(s,r['web_source']['ledger_id'])
        ei=next((i for i,e in enumerate(source['document']['entries']) if e['id']==b['entry_id']),None)
        if ei is None:raise AuthError('Original item not found',404)
        from .ledger_service import index
        from .product_mapping import identity as mapping_identity, compatible as packing_compatible
        item=index(b['item_index'],source['document']['entries'][ei].get('items',[]))
        product=self.mapping_product(u,s,st,item,b)
        for i,e in enumerate(source['document']['entries']):
            for j,other in enumerate(e.get('items',[])):
                if mapping_identity(other)==mapping_identity(item):source['mappings'][f'{i}:{j}']=product['id']
        _,rev,_=self.ledger.load(db,u['id'],workbook);self.ledger.save(db,u['id'],workbook,rev,s,'native_product_mapped',source['id'])
        effective=self.ledger.effective(source,s);by_id={e['id']:e for e in effective['entries']}
        for e in r['entries']:
            if e['id'] not in by_id:continue
            for old,new in zip(e.get('items',[]),by_id[e['id']].get('items',[])):
                for key in ('product','packing_kg','crop','segment','mapping_confirmed'):
                    if key in new:old[key]=new[key]
        r.update(web_source=self.bind(s,source),ledger_confirmed=False)
        return {'record':st.save(r),'product_id':product['id']}

    def refresh(self,st,s,r):
        original=self.ledger.ledger(s,r['web_source']['ledger_id'],False)
        source=self.ledger.current_source(s,original['id']);doc=self.ledger.effective(source,s)
        from importer import source_content
        old={e['id']:e for e in original['document']['entries']};edited={e['id']:e for e in r['entries']};fresh=[]
        changed=source['id']!=original['id']
        for entry in doc['entries']:
            previous=edited.get(entry['id']);raw=old.get(entry['id'])
            if previous and raw and digest(source_content(raw))==digest(source_content(entry)):
                retained=copy.deepcopy(previous)
                if previous.get('web_review')!=entry.get('web_review'):retained['kind']=entry['kind']
                retained['web_review']=entry.get('web_review',{})
                for a,v in zip(retained.get('items',[]),entry.get('items',[])):
                    for key in ('product','packing_kg','crop','segment','mapping_confirmed'):
                        if key in v:a[key]=v[key]
                fresh.append(retained)
            else:fresh.append(entry)
        fresh += [e for e in r['entries'] if e['id'] not in old]
        link=s['year_links'].get(source['id'])
        if link and self.ledger.link_stale(s,link):raise AuthError('Review Year Link first',409)
        if doc['opening']!=original['document']['opening']:r['opening']=doc['opening']
        if doc['closing']!=original['document']['closing']:r['closing']=doc['closing']
        r.update(entries=fresh,source=doc['source'],web_source=self.bind(s,source),ledger_confirmed=False,import_warnings=doc.get('warnings',[]))
        if changed:
            r['id']=uuid.uuid4().hex;r['revision']=0
            with st.db() as c:c.execute('INSERT INTO records VALUES(?,?,?)',(r['id'],0,dump(r)))
        if link and not r.get('payment_history'):
            manual=[x for x in r.get('opening_sources',[]) if not x.get('year_link_receipt')]
            r['opening_sources']=manual+copy.deepcopy(link['record']['opening_sources']);r['prior_year_link']=copy.deepcopy(link['record']['prior_year_link'])
        return st.save(r)

    def transfer(self,token,action,b,project,workbook):
        with self.calc.accounts._tx() as db:
            u=self.calc.store.user(db,token)
            project,workbook,_,_=self.calc.scope(db,u,project,workbook)
            require_permission(u,'export_print' if action in ('native-backup','native-project-export') else 'import_statements')
        if action=='native-backup':return self.calc.store.export(token,project)
        b=b or {}
        if 'confirm' in b and type(b['confirm']) is not bool:raise AuthError('Invalid confirmation',400)
        if action=='native-restore':
            fields(b,{'backup'},{'confirm'})
            backup=b['backup'];preview=self.transfer_counts(backup)
            if not b.get('confirm'):return {**preview,'settings_versions':sum(len(x['payload']['settings']) for x in backup.get('calculator_bundle',[])),'warning':'Open as a new independent project; existing work is unchanged.'}
            return self.calc.store.import_project(token,{'backup':backup})
        if action=='native-project-export':
            fields(b,set(),{'confirm','expected','name','sender'})
            if 'sender' in b:text(b['sender'],'sender',500,True)
            backup=self.calc.store.export(token,project);sha=digest(backup);preview=self.transfer_counts(backup)
            if not b.get('confirm'):return {**preview,'sha256':sha,'scope':'Selected independent project, including saved source evidence and calculation history.'}
            if b.get('expected')!=sha:raise AuthError('Project changed; review the export again',409)
            if b.get('name'):next(d for d in backup['documents'] if d['kind']=='projects')['data']['name']=text(b['name'],'project name',500)
            wrapper={'format':'cn-web-share','backup':backup,'sender':str(b.get('sender',''))[:500],'exported_at':now()}
            raw=gzip.compress(encode(wrapper).encode(),mtime=0)
            return {'filename':'All-Crop-CN-Project.cnwork','data':base64.b64encode(raw).decode()}
        fields(b,{'data'},{'confirm','expected'})
        try:
            raw=base64.b64decode(b['data'],validate=True)
            if len(raw)>64*1024*1024:raise ValueError()
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:decoded=stream.read(64*1024*1024+1)
            if len(decoded)>64*1024*1024:raise ValueError()
            wrapper=json.loads(decoded)
            if wrapper['format']!='cn-web-share':raise ValueError()
            backup=wrapper['backup'];preview=self.transfer_counts(backup)
        except (ValueError,KeyError,TypeError,OSError):raise AuthError('Choose a web-calculator project export',400) from None
        sha=hashlib.sha256(raw).hexdigest()
        if not b.get('confirm'):return {**preview,'expected':sha,'sender':wrapper.get('sender',''),'exported_at':wrapper.get('exported_at',''),'warning':'Opens a new independent project. Existing work is never merged.'}
        if b.get('expected')!=sha:raise AuthError('Import file changed; preview it again',409)
        imported=self.calc.store.import_project(token,{'backup':backup})
        return {'project':{'id':imported['project_id']}}

    @staticmethod
    def transfer_counts(backup):
        try:
            fields(backup,{'format','version','documents'},{'ledger_bundle','calculator_bundle'})
            if backup['format']!='cn-web-project' or backup['version'] not in (1,2,3):raise ValueError()
            docs=backup['documents']
            if not isinstance(docs,list) or not 1<=len(docs)<=10000:raise ValueError()
            records=[json.loads(r[2]) for w in backup.get('calculator_bundle',[]) for r in w['payload']['records']]
            root=next(d for d in docs if d['kind']=='projects')
            return {'name':root['data']['name'],'workbooks':sum(d['kind']=='workbooks' for d in docs),'parties':len({(r['party'],r.get('location','')) for r in records}),'records':len(records),'drafts':sum(r['status']=='draft' for r in records),'completed':sum(r['status']!='draft' for r in records),'deleted_records':sum(bool(r.get('deleted_at')) for r in records)}
        except (ValueError,KeyError,TypeError,AttributeError,StopIteration):raise AuthError('Choose a valid web-calculator backup',400) from None
