"""Original offline-screen transport: canonical owned PDFs, no replacement UI."""
import copy
import unittest
import test_accounts_http as helpers
import test_calculator_http as calc_tests
import test_ledger_http as ledger_tests
from cn_web.security import PERMISSIONS

class NativeInterfaceTests(unittest.TestCase):
    setUp=helpers.AccountHTTPTests.setUp
    stop=helpers.AccountHTTPTests.stop
    create=helpers.AccountHTTPTests.create
    user_browser=helpers.AccountHTTPTests.user_browser
    setup_book=ledger_tests.LedgerHTTPTests.setup_book
    config=ledger_tests.LedgerHTTPTests.config
    state=ledger_tests.LedgerHTTPTests.state
    url=ledger_tests.LedgerHTTPTests.url
    file=ledger_tests.LedgerHTTPTests.file
    detail=ledger_tests.LedgerHTTPTests.detail
    calc=calc_tests.CalculatorHTTPTests.calc
    saved=calc_tests.CalculatorHTTPTests.saved

    def imported(self,b,w,name='two_seasons.pdf',season='Kharif'):
        code,out,_=self.calc(b,w,'native-import',{'data':self.file(name)['content_base64'],'filename':name,'season':season})
        self.assertEqual(code,200,out);return out['native_record']

    def test_opening_credit_save_permissions_limits_and_backup(self):
        u,b=self.user_browser();_,w=self.setup_book(b);self.config(b,w)
        r=self.imported(b,w,'current_year.pdf')
        r['opening_sources']=[{'id':'opening-credit','date':None,'amount':'10000'}]
        r['allocations']=[{'id':'settled','source':'opening-credit','type':'Settlement','amount':'5000','scheme':'','product':''}]
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS-{'edit_ledger'})},'PATCH')
        code,r,_=self.calc(b,w,'save',r);self.assertEqual(code,200,r)
        for source in [dict(r['opening_sources'][0],date='2026-04-01'),dict(r['opening_sources'][0],year_link_receipt='forged'),dict(r['opening_sources'][0],amount='10001')]:
            changed=copy.deepcopy(r);changed['opening_sources']=[source]
            self.assertEqual(self.calc(b,w,'save',changed)[0],409 if source.get('year_link_receipt') else 400)
            self.assertEqual(self.calc(b,w,'record',{'id':r['id']})[1]['record']['opening_sources'],r['opening_sources'])
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS-{'allocate_payments'})},'PATCH')
        changed=copy.deepcopy(r);changed['opening_sources'][0]['amount']='9999'
        self.assertEqual(self.calc(b,w,'save',changed)[0],403)
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS)},'PATCH')
        backup=b.request('/api/projects/'+w['project']+'/export')[1]
        code,out,_=b.request('/api/projects/import',{'backup':backup});self.assertEqual(code,201,out)
        w2=next(x for x in b.request('/api/data/workbooks')[1]['items'] if x['project']==out['project_id'])
        imported=self.saved(b,w2)['records'][0]
        self.assertEqual(imported['opening_sources'],r['opening_sources']);self.assertEqual(imported['allocations'],r['allocations'])

    def test_traced_opening_receipts_remain_immutable(self):
        from cn_web.calculator_service import validate_opening_sources
        linked={'id':'fy-original','date':'2026-03-01','amount':'20','year_link_receipt':'prior-r1','year_link_signature':'proof','label':'Prior FY receipt'}
        manual={'id':'manual','date':None,'amount':'10'}
        validate_opening_sources({'opening_sources':[linked,manual]},[linked])
        for sources in [[],[dict(linked,amount='21')],[dict(linked,date='2026-01-01')],[dict(linked,year_link_signature='fake')],[dict(manual,date='2026-03-01')]]:
            with self.assertRaises(ValueError):validate_opening_sources({'opening_sources':sources},[linked])

    def test_manual_credit_with_reviewed_year_link_survives_refresh_and_transfer(self):
        _,b=self.user_browser();_,w=self.setup_book(b);self.config(b,w)
        docs=[]
        for name in ['prior_year.pdf','current_year.pdf']:
            code,out,_=self.calc(b,w,'native-audit-import',{'data':self.file(name)['content_base64'],'filename':name});self.assertEqual(code,200,out);docs.append(out['documents'][0])
        pair=self.calc(b,w,'native-year-pair',{'previous':docs[0],'current':docs[1]})[1]
        code,r,_=self.calc(b,w,'native-year-link-save',{'previous':docs[0],'current':docs[1],'confirmed':{pair['receipts'][0]['id']:'1000'},'reason':'Reviewed earlier receipt','season':'Kharif','replace_unused':False});self.assertEqual(code,200,r)
        linked=copy.deepcopy(r['opening_sources'][0]);r['opening_sources'].append({'id':'manual','amount':'9000','date':None})
        r['allocations']=[{'id':'a','type':'Settlement','source':'manual','amount':'500','scheme':'','product':''}]
        code,r,_=self.calc(b,w,'save',r);self.assertEqual(code,200,r)
        for key,value in [('date','2026-01-01'),('amount','1001'),('year_link_signature','fake')]:
            bad=copy.deepcopy(r);bad['opening_sources'][0][key]=value
            self.assertEqual(self.calc(b,w,'save',bad)[0],409)
        code,r,_=self.calc(b,w,'native-refresh',{'id':r['id'],'revision':r['revision']});self.assertEqual(code,200,r)
        self.assertIn(linked,r['opening_sources']);self.assertIn({'id':'manual','amount':'9000','date':None},r['opening_sources'])
        backup=b.request('/api/projects/'+w['project']+'/export')[1]
        code,out,_=b.request('/api/projects/import',{'backup':backup});self.assertEqual(code,201,out)
        w2=next(x for x in b.request('/api/data/workbooks')[1]['items'] if x['project']==out['project_id'])
        restored=self.saved(b,w2)['records'][0]
        self.assertEqual(restored['opening_sources'],r['opening_sources']);self.assertEqual(restored['allocations'],r['allocations'])

    def test_single_repeat_bulk_and_existing_saved_source_directory(self):
        _,b=self.user_browser();_,w=self.setup_book(b);self.config(b,w)
        r=self.imported(b,w);self.assertEqual(len(r['entries']),10)
        r['allocations']=[{'id':'retained','source':next(e['id'] for e in r['entries'] if e['kind']=='receipt'),'type':'Settlement','scheme':'','product':'','amount':'50'}]
        code,r,_=self.calc(b,w,'save',r);self.assertEqual(code,200,r)
        repeated=self.imported(b,w);self.assertEqual(repeated['id'],r['id']);self.assertEqual(repeated['allocations'],r['allocations'])
        code,out,_=self.calc(b,w,'native-bulk-import',{'data':self.file('mapping_a.pdf')['content_base64'],'filename':'mapping_a.pdf','season':'Kharif'});self.assertEqual(code,200,out)
        self.assertTrue(out['results'][0]['record_id']);self.assertTrue(self.saved(b,w)['bulk_history'])
        # Old source ledgers without drafts appear through the ordinary party list.
        p=ledger_tests.LedgerHTTPTests.imported(self,b,w,'mapping_b.pdf')
        native=self.calc(b,w,'native-state')[1]
        self.assertTrue(any(x.get('native_saved_source') and x['id']=='source:'+p for x in native['records']))
        self.assertFalse(any(x.get('native_saved_source') for x in self.saved(b,w)['records']))

    def test_unconfirmed_period_import_is_draft_only(self):
        _,b=self.user_browser();_,w=self.setup_book(b)
        season=self.saved(b,w)['settings']['seasons'][0]['name'];r=self.imported(b,w,season=season)
        self.assertEqual(len(r['entries']),10)
        code,result,_=self.calc(b,w,'calculate',r);self.assertEqual(code,200,result)
        self.assertFalse(result['can_finalise']);self.assertTrue(result['issues'])
        self.assertNotEqual(self.calc(b,w,'finalise',{'id':r['id'],'revision':r['revision']})[0],200)
        self.assertEqual(self.state(b,w)['periods'],[])
        cfg=self.saved(b,w)['settings'];cfg['seasons'][0].update(start='2026-04-01',end='2026-08-31',cutoff='2026-11-15',confirmed=False)
        self.assertEqual(self.calc(b,w,'settings',cfg)[0],200)
        r=self.imported(b,w,season=season)
        code,result,_=self.calc(b,w,'calculate',r);self.assertEqual(code,200,result);self.assertFalse(result['can_finalise'])

    def test_inline_mapping_atomic_permissions_and_saved_reuse(self):
        u,b=self.user_browser();_,w=self.setup_book(b);self.config(b,w);r=self.imported(b,w,'mapping_a.pdf')
        e=next(e for e in r['entries'] if e.get('items'));item=e['items'][0]
        body={'id':r['id'],'revision':r['revision'],'entry_id':e['id'],'item_index':0,'crop':'Maize','name':item['name'],'packing':item.get('mapping_suggestion',{}).get('detected_packing_kg') or '4'}
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS-{'edit_schemes'})},'PATCH')
        before=self.saved(b,w);self.assertEqual(self.calc(b,w,'native-map',body)[0],403);self.assertEqual(self.saved(b,w),before)
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS)},'PATCH')
        code,out,_=self.calc(b,w,'native-map',body);self.assertEqual(code,200,out)
        r=out['record'];self.assertEqual([e['date'] for e in r['entries']],[e['date'] for e in before['records'][0]['entries']])
        cfg=self.saved(b,w)['settings'];p=next(p for p in cfg['products'] if p['id']==out['product_id']);sc=next(s for s in cfg['schemes'] if s['id']==p['scheme'])
        self.assertTrue(p['needs_assignment']);self.assertFalse(sc['benefits']);self.assertIsNone(sc['billing'])
        code,r,_=self.calc(b,w,'save',r);self.assertEqual(code,200,r)
        self.assertEqual(self.calc(b,w,'native-map',body)[0],409)
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS-{'edit_schemes'})},'PATCH')
        code,reused,_=self.calc(b,w,'native-map',{**body,'revision':r['revision']});self.assertEqual(code,200,reused)
        self.assertEqual(reused['product_id'],p['id'])
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS)},'PATCH')
        second=self.imported(b,w,'mapping_b.pdf');self.assertTrue(any(i.get('product')==p['id'] for e in second['entries'] for i in e.get('items',[])))

    def test_audit_and_year_link_use_canonical_owned_files(self):
        _,b=self.user_browser();_,w=self.setup_book(b);self.config(b,w)
        docs=[]
        for name in ['prior_year.pdf','current_year.pdf']:
            code,out,_=self.calc(b,w,'native-audit-import',{'data':self.file(name)['content_base64'],'filename':name});self.assertEqual(code,200,out);docs.append(out['documents'][0])
        forged=copy.deepcopy(docs[0]);forged['closing']='99999999';forged['entries']=[]
        code,a,_=self.calc(b,w,'native-year-pair',{'previous':docs[0],'current':docs[1]});self.assertEqual(code,200,a)
        self.assertEqual(self.calc(b,w,'native-year-pair',{'previous':forged,'current':docs[1]})[1],a)
        code,out,_=self.calc(b,w,'native-year-link-save',{'previous':docs[0],'current':docs[1],'confirmed':{},'reason':'Reviewed original receipts; no carried amounts','season':'Kharif','replace_unused':False});self.assertEqual(code,200,out)
        self.assertTrue(out['prior_year_link']);self.assertEqual(out['opening_sources'],[])
        self.assertEqual(self.calc(b,w,'calculate',out)[0],200)
        code,audit,_=self.calc(b,w,'native-audit-check',{'documents':docs,'start':'2025-04-01','end':'2027-03-31'});self.assertEqual(code,200,audit)
        self.assertIn('findings',audit);self.assertIn('posted_CN_NRV',audit)
        _,other=self.user_browser('other');_,w2=self.setup_book(other)
        self.assertNotEqual(self.calc(other,w2,'native-audit-check',{'documents':docs,'start':'2025-04-01','end':'2027-03-31'})[0],200)

    def test_replacement_refresh_and_source_ipt_preserve_allocations(self):
        _,b=self.user_browser();_,w=self.setup_book(b);self.config(b,w);r=self.imported(b,w)
        r['allocations']=[{'id':'retained','source':next(e['id'] for e in r['entries'] if e['kind']=='receipt'),'type':'Settlement','scheme':'','product':'','amount':'50'}]
        code,r,_=self.calc(b,w,'save',r);self.assertEqual(code,200,r)
        ipt=next(e for e in r['entries'] if e['kind']=='ipt_out')
        code,r,_=self.calc(b,w,'native-late-ipt-review',{'id':r['id'],'revision':r['revision'],'entry_id':ipt['id'],'reason':'Late Kharif source transfer','remove':False});self.assertEqual(code,200,r)
        self.assertEqual(r['allocations'][0]['amount'],'50')
        code,pending,_=self.calc(b,w,'native-import',{'data':self.file('two_seasons_changed.pdf')['content_base64'],'season':'Kharif'});self.assertEqual(code,200,pending);self.assertTrue(pending['native_import_review'])
        body={**pending['request'],'replacement':pending['preview']['results'][0]['candidates'][0],'expected':pending['preview']['preview_digest'],'reason':'Reviewed changed source statement'}
        code,updated,_=self.calc(b,w,'native-replace-import',body);self.assertEqual(code,200,updated)
        fresh=updated['native_record'];self.assertEqual(fresh['allocations'],r['allocations'])
        self.assertEqual(self.calc(b,w,'record',{'id':r['id']})[1]['record']['entries'],r['entries'])

    def test_native_ownership_revocation_csrf_and_original_dates(self):
        u,b=self.user_browser();_,w=self.setup_book(b);self.config(b,w);r=self.imported(b,w)
        _,other=self.user_browser('other');_,w2=self.setup_book(other)
        for action,body in [('native-open',{'ledger_id':r['web_source']['ledger_id'],'season':'Kharif'}),('native-refresh',{'id':r['id'],'revision':r['revision']}),('native-source-file',{'id':r['id']}),('native-stale-result',{'id':r['id']})]:
            self.assertNotEqual(self.calc(other,w2,action,body)[0],200,action)
        altered=copy.deepcopy(r);altered['entries'][0]['date']='2026-01-01';self.assertEqual(self.calc(b,w,'save',altered)[0],400)
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':['view_workspace']},'PATCH')
        self.assertEqual(self.calc(b,w,'native-import',{'data':self.file('mapping_a.pdf')['content_base64'],'season':'Kharif'})[0],403)
        self.assertEqual(self.calc(b,w,'native-refresh',{'id':r['id'],'revision':r['revision']})[0],403)
        self.assertEqual(self.calc(b,w,'record',{'id':r['id']})[0],200)
        code,_,_=b.request('/api/calculator/native-refresh',{'id':r['id'],'revision':r['revision']},headers={'X-CN-Project':w['project'],'X-CN-Workbook':w['id'],'X-CSRF-Token':''});self.assertEqual(code,403)

    def test_original_backup_and_independent_project_transfer(self):
        _,b=self.user_browser();p,w=self.setup_book(b);self.config(b,w);r=self.imported(b,w)
        code,backup,_=self.calc(b,w,'native-backup',{});self.assertEqual(code,200,backup)
        self.assertEqual(backup['format'],'cn-web-project')
        code,preview,_=self.calc(b,w,'native-project-export',{});self.assertEqual(code,200,preview)
        code,file,_=self.calc(b,w,'native-project-export',{'confirm':True,'expected':preview['sha256'],'name':'Shared native project','sender':'Test'});self.assertEqual(code,200,file)
        code,preview,_=self.calc(b,w,'native-project-import',{'data':file['data']});self.assertEqual(code,200,preview)
        self.assertEqual(preview['records'],1)
        self.assertNotEqual(self.calc(b,w,'native-project-import',{'data':file['data'],'expected':'bad','confirm':True})[0],200)
        code,result,_=self.calc(b,w,'native-project-import',{'data':file['data'],'expected':preview['expected'],'confirm':True});self.assertEqual(code,200,result)
        self.assertNotEqual(result['project']['id'],p['id']);self.assertEqual(self.calc(b,w,'record',{'id':r['id']})[0],200)
