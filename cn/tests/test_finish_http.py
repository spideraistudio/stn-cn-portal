"""Phase 6: real HTTP transitions, frozen evidence, reports and party reopening."""
import copy
import json
import sys
import unittest
from decimal import Decimal

import test_accounts_http as helpers
import test_calculator_http as calculator_tests
import test_ledger_http as ledger_tests
from cn_web.accounts import Accounts
from cn_web.http_app import AccountApp
from cn_web.security import PERMISSIONS
from engine import compute


class FinishHTTPTests(unittest.TestCase):
    setUp = helpers.AccountHTTPTests.setUp
    stop = helpers.AccountHTTPTests.stop
    create = helpers.AccountHTTPTests.create
    user_browser = helpers.AccountHTTPTests.user_browser
    setup_book = ledger_tests.LedgerHTTPTests.setup_book
    url = ledger_tests.LedgerHTTPTests.url
    state = ledger_tests.LedgerHTTPTests.state
    file = ledger_tests.LedgerHTTPTests.file
    imported = ledger_tests.LedgerHTTPTests.imported
    detail = ledger_tests.LedgerHTTPTests.detail
    review = ledger_tests.LedgerHTTPTests.review
    config = ledger_tests.LedgerHTTPTests.config
    calc = calculator_tests.CalculatorHTTPTests.calc
    saved = calculator_tests.CalculatorHTTPTests.saved
    mapped_source = calculator_tests.CalculatorHTTPTests.mapped_source

    def case(self, b, w):
        sys.path.append(str(helpers.ROOT/'offline_baseline/tests'))
        from test_calculator import example
        record, cfg = example()
        code, saved, _ = self.calc(b, w, 'settings', cfg); self.assertEqual(code, 200, saved)
        record.update(workbook_id=w['id'], status='draft', revision=0, annual_ledger=True)
        code, record, _ = self.calc(b, w, 'save', record); self.assertEqual(code, 200, record)
        code, result, _ = self.calc(b, w, 'calculate', record); self.assertEqual(code, 200, result)
        self.assertEqual(result['issues'], [])
        return record, saved, result

    def finish(self, b, w, r, issue=False):
        code, frozen, _ = self.calc(b, w, 'finalise', {'id':r['id'], 'revision':r['revision']})
        self.assertEqual(code, 200, frozen)
        if issue:
            code, frozen, _ = self.calc(b, w, 'issue', {'id':frozen['id'], 'revision':frozen['revision']})
            self.assertEqual(code, 200, frozen)
        return frozen

    def test_finish_frozen_history_separate_rounding_and_revision(self):
        u,b=self.user_browser(); p,w=self.setup_book(b); r,cfg,result=self.case(b,w)
        self.assertEqual(Decimal(result['new_CN_total']), Decimal(38561))
        frozen=self.finish(b,w,r,True)
        self.assertEqual(frozen['result'], result)
        changed=copy.deepcopy(cfg); changed['schemes'][2]['extra'][1]['rate']='26000'
        self.assertEqual(self.calc(b,w,'settings',changed)[0],200)
        self.assertEqual(self.calc(b,w,'calculate',{**r,'party':'Forged browser name'})[1],result)
        self.assertNotEqual(self.calc(b,w,'save',frozen)[0],200)
        self.assertNotEqual(self.calc(b,w,'issue',{'id':frozen['id'],'revision':frozen['revision']})[0],200)
        code,revision,_=self.calc(b,w,'revise',{'id':frozen['id']});self.assertEqual(code,200,revision)
        self.assertEqual(revision['parent'],frozen['id']);self.assertTrue(revision['prior_issued'])
        self.assertNotIn('result',revision);self.assertFalse(revision['ledger_confirmed'])
        self.assertEqual(self.calc(b,w,'record',{'id':frozen['id']})[1]['result'],result)
        # A revision issues only its incremental entitlement; the parent stays frozen.
        revision.update(ledger_confirmed=True,revision_ledger_confirmed=True)
        code,revision,_=self.calc(b,w,'save',revision);self.assertEqual(code,200,revision)
        code,delta,_=self.calc(b,w,'calculate',revision);self.assertEqual(code,200,delta)
        self.assertTrue(any('Negative revised' in x for x in delta['issues']))
        self.assertNotEqual(self.calc(b,w,'finalise',{'id':revision['id'],'revision':revision['revision']})[0],200)
        current=self.saved(b,w)['settings'];current['schemes'][2]['extra'][1]['rate']=cfg['schemes'][2]['extra'][1]['rate']
        self.assertEqual(self.calc(b,w,'settings',current)[0],200)
        code,delta,_=self.calc(b,w,'calculate',revision);self.assertEqual(code,200,delta);self.assertEqual(delta['issues'],[])
        self.assertLess(Decimal(delta['new_CN_total']),Decimal(result['new_CN_total']))
        revised=self.finish(b,w,revision,True);self.assertEqual(revised['parent'],frozen['id'])
        self.assertEqual(self.calc(b,w,'record',{'id':frozen['id']})[1]['result'],result)

    def test_party_details_saved_pdf_draft_restart_and_stale_review(self):
        u,b=self.user_browser();p,w=self.setup_book(b);lid=self.imported(b,w)
        from cn_web.security import AuthError
        cycle={'ledgers':[{'id':'a'*32,'superseded_by':'b'*32},{'id':'b'*32,'superseded_by':'a'*32}]}
        with self.assertRaises(AuthError):self.app.ledger.current_source(cycle,'a'*32)
        state=self.saved(b,w);self.assertEqual(state['records'],[])
        source=state['source_ledgers'][0];self.assertEqual(source['id'],lid);self.assertGreater(source['entries'],0)
        self.config(b,w)
        code,r,_=self.calc(b,w,'open-source',{'ledger_id':lid,'season':'Kharif','revision':self.state(b,w)['revision']});self.assertEqual(code,200,r)
        self.accounts=Accounts(self.tmp.name,clock=lambda:self.now[0]);self.app=AccountApp(self.accounts,origin=self.origin,development=True);self.server.set_app(self.app)
        code,opened,_=self.calc(b,w,'record',{'id':r['id']});self.assertEqual(code,200,opened)
        self.assertEqual(opened['record']['entries'],r['entries']);self.assertEqual(opened['record']['party'],r['party'])
        self.review(b,w,lid,0,{'kind':'sale','reason':'Review note changed'})
        code,opened,_=self.calc(b,w,'record',{'id':r['id']});self.assertEqual(code,200,opened)
        self.assertIn('source_error',opened);self.assertEqual(len(opened['record']['entries']),len(r['entries']))
        other,c=self.user_browser('other-user');p2,w2=self.setup_book(c)
        self.assertEqual(self.saved(c,w2)['source_ledgers'],[])
        self.assertNotEqual(self.calc(c,w,'record',{'id':r['id']})[0],200)

    def test_reports_csv_print_canonical_data_and_requested_only(self):
        u,b=self.user_browser();p,w=self.setup_book(b);r,cfg,result=self.case(b,w)
        key=result['product_CNs'][0]['key'];old_total=result['new_CN_total']
        r['cn_requests']={key:{'direction':'increase','rate':'9','unit':'packet','remark':'Requested only'}}
        code,r,_=self.calc(b,w,'save',r);self.assertEqual(code,200,r)
        result=self.calc(b,w,'calculate',r)[1];self.assertEqual(result['new_CN_total'],old_total)
        frozen=self.finish(b,w,r)
        before=self.saved(b,w)
        code,report,_=self.calc(b,w,'report',{});self.assertEqual(code,200,report);self.assertTrue(report['rows'])
        row=report['rows'][0]
        self.assertGreater(Decimal(row['requested_delta_display_only']),0)
        self.assertEqual(Decimal(row['net_realisation']),Decimal(row['net_kg'] if row['billing_unit']=='kg' else row['net_packets'])*Decimal(row['billing_rate'])-Decimal(row['total_CN']))
        forged=copy.deepcopy(frozen);forged['party']='=FORGED';forged['result']['new_CN_total']='999999'
        code,csv,_=self.calc(b,w,'product-csv',{'record':forged});self.assertEqual(code,200,csv)
        self.assertTrue(csv['csv'].startswith('\ufeff'));self.assertNotIn('FORGED',csv['csv'])
        code,printed,_=self.calc(b,w,'print-record',{'id':frozen['id'],'revision':frozen['revision']});self.assertEqual(code,200,printed);self.assertEqual(printed['result'],result)
        code,preview,_=self.calc(b,w,'workbook-print',{});self.assertEqual(code,200,preview)
        code,combined,_=self.calc(b,w,'workbook-print',{'expected':preview['expected'],'record_ids':[frozen['id']]});self.assertEqual(code,200,combined)
        self.assertEqual(combined['items'][0]['result'],result)
        code,territory,_=self.calc(b,w,'territory-report',{});self.assertEqual(code,200,territory);self.assertIn('hierarchy',territory)
        self.assertEqual(before,self.saved(b,w))

    def test_permissions_direct_bypasses_revocation_and_csrf(self):
        u,b=self.user_browser();p,w=self.setup_book(b);r,cfg,result=self.case(b,w)
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS-{'finalise'})},'PATCH')
        self.assertEqual(self.calc(b,w,'finalise',{'id':r['id'],'revision':r['revision']})[0],403)
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS)},'PATCH');f=self.finish(b,w,r)
        for permission,actions in [('issue_cn',['issue']),('export_print',['report','territory-report','product-csv','print-record','workbook-print']),('finalise',['revise'])]:
            self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS-{permission})},'PATCH')
            for action in actions:
                self.assertEqual(self.calc(b,w,action,{'id':f['id'],'revision':f['revision']})[0],403,action)
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS)},'PATCH')
        status,_,_=b.request('/api/calculator/finalise',{'id':r['id'],'revision':r['revision']},headers={'X-CN-Project':p['id'],'X-CN-Workbook':w['id'],'X-CSRF-Token':''});self.assertEqual(status,403)
        other,c=self.user_browser('other-user');p2,w2=self.setup_book(c)
        for action in ['issue','finalise','revise','report','print-record','product-csv','workbook-print']:
            self.assertEqual(self.calc(c,w,action,{'id':f['id'],'revision':f['revision']})[0],404,action)

    def test_cross_workbook_duplicate_and_frozen_backup_validation(self):
        u,b=self.user_browser();p,w=self.setup_book(b);r,cfg,result=self.case(b,w);issued=self.finish(b,w,r,True)
        from cn_web.finish_service import selected_stock
        reformatted=copy.deepcopy(issued)
        for entry in reformatted['entries']:
            for item in entry.get('items',[]):
                for key in ['qty','amount','rate']:
                    if key in item:
                        value=format(Decimal(item[key]),'f');item[key]=value+'0000' if '.' in value else value+'.0000'
        self.assertEqual(selected_stock(reformatted),selected_stock(issued))
        p2,w2=self.setup_book(b);r2,_,_=self.case(b,w2);f2=self.finish(b,w2,r2)
        self.assertEqual(self.calc(b,w2,'issue',{'id':f2['id'],'revision':f2['revision']})[0],409)
        backup=b.request('/api/projects/'+p['id']+'/export')[1]
        other,c=self.user_browser('receiver')
        code,imported,_=c.request('/api/projects/import',{'backup':backup});self.assertEqual(code,201,imported)
        nw=next(x for x in c.request('/api/data/workbooks')[1]['items'] if x['project']==imported['project_id'])
        saved=self.saved(c,nw)['records'][0];self.assertEqual(saved['status'],'issued');self.assertNotEqual(saved['id'],issued['id']);self.assertEqual(saved['result'],issued['result'])
        self.assertEqual(self.calc(c,nw,'calculate',saved)[1],issued['result'])
        malicious=copy.deepcopy(backup);raw=json.loads(malicious['calculator_bundle'][0]['payload']['records'][0][2]);raw['result']['new_CN_total']='999999';malicious['calculator_bundle'][0]['payload']['records'][0][2]=json.dumps(raw)
        self.assertEqual(c.request('/api/projects/import',{'backup':malicious})[0],400)
        self.admin.request('/api/admin/users/'+other['id'],{'permissions':list(PERMISSIONS-{'issue_cn'})},'PATCH')
        self.assertEqual(c.request('/api/projects/import',{'backup':backup})[0],403)

    def test_source_late_kharif_freeze_and_changed_source_history(self):
        u,b=self.user_browser();p,w=self.setup_book(b);lid,original=self.mapped_source(b,w)
        cfg=self.saved(b,w)['settings']
        for scheme in cfg['schemes']:
            scheme.update(confirmed=True,states=['Gujarat'],unit='kg',billing='100',billing_unit='kg',benefits=['Quantity'],quantity=[{'above':'0','upto':None,'rate':'1','name':'Test quantity'}])
        code,cfg,_=self.calc(b,w,'settings',cfg);self.assertEqual(code,200,cfg)
        code,r,_=self.calc(b,w,'open-source',{'ledger_id':lid,'season':'Kharif','revision':self.state(b,w)['revision']});self.assertEqual(code,200,r)
        r.update(state='Gujarat',ledger_confirmed=True)
        r['allocations']=[{'id':'settlement-'+e['id'],'source':e['id'],'type':'Settlement','scheme':cfg['schemes'][0]['id'],'product':'','amount':e['credit']} for e in r['entries'] if e['kind']=='receipt']
        code,r,_=self.calc(b,w,'save',r);self.assertEqual(code,200,r)
        code,result,_=self.calc(b,w,'calculate',r);self.assertEqual(code,200,result)
        self.assertEqual(result['issues'],[])
        frozen=self.finish(b,w,r)
        self.assertEqual(frozen['result'],result)
        self.assertEqual(frozen['frozen_settings']['seasons'][0]['end'],'2026-08-31')
        self.assertEqual(frozen['web_calculation_settings']['seasons'][0]['end'],'2026-11-15')
        self.assertEqual([e['date'] for e in frozen['entries']],[e['date'] for e in original['entries']])
        self.assertEqual({x['product_id']:Decimal(x['net_sold']) for x in frozen['result']['product_CNs']},{'dawat1':Decimal(4),'dawat3':Decimal(15)})
        self.review(b,w,lid,0,{'kind':'sale','reason':'Source review changed after freeze'})
        self.assertEqual(self.calc(b,w,'record',{'id':frozen['id']})[1]['result'],result)
        self.assertEqual(self.calc(b,w,'issue',{'id':frozen['id'],'revision':frozen['revision']})[0],409)
        code,revision,_=self.calc(b,w,'revise',{'id':frozen['id']});self.assertEqual(code,200,revision)
        self.assertNotEqual(revision['web_source']['revision'],frozen['web_source']['revision'])
        self.assertEqual(len(revision['entries']),len(original['entries']))
        backup=b.request('/api/projects/'+p['id']+'/export')[1]
        _,receiver=self.user_browser('source-receiver')
        code,imported,_=receiver.request('/api/projects/import',{'backup':backup});self.assertEqual(code,201,imported)
        nw=next(x for x in receiver.request('/api/data/workbooks')[1]['items'] if x['project']==imported['project_id'])
        historic=next(x for x in self.saved(receiver,nw)['records'] if x['status']=='finalised')
        self.assertEqual(self.calc(receiver,nw,'record',{'id':historic['id']})[1]['result'],result)
