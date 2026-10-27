import copy
import unittest
import test_accounts_http as helpers
import test_ledger_http as ledger
import test_calculator_http as calc_tests
from cn_web.security import PERMISSIONS

class AuditMappingHTTP(unittest.TestCase):
    setUp=helpers.AccountHTTPTests.setUp
    stop=helpers.AccountHTTPTests.stop
    create=helpers.AccountHTTPTests.create
    user_browser=helpers.AccountHTTPTests.user_browser
    setup_book=ledger.LedgerHTTPTests.setup_book
    config=ledger.LedgerHTTPTests.config
    state=ledger.LedgerHTTPTests.state
    url=ledger.LedgerHTTPTests.url
    file=ledger.LedgerHTTPTests.file
    calc=calc_tests.CalculatorHTTPTests.calc
    saved=calc_tests.CalculatorHTTPTests.saved

    def prepare(self):
        u,b=self.user_browser();_,w=self.setup_book(b);self.config(b,w)
        code,out,_=self.calc(b,w,'native-audit-import',{'data':self.file('mapping_a.pdf')['content_base64']});self.assertEqual(code,200,out)
        request={'documents':out['documents'],'start':'2026-04-01','end':'2027-03-31'}
        code,report,_=self.calc(b,w,'native-audit-check',request);self.assertEqual(code,200,report)
        t=report['mapping_targets'][0];source={k:t[k] for k in ('source','entry_id','item_index')}
        code,context,_=self.calc(b,w,'native-audit-product-context',source);self.assertEqual(code,200,context)
        values={**source,'revision':context['revision'],'evidence':context['evidence'],'crop':'Maize','name':context['item']['name'],'packing':context['item']['mapping_suggestion']['detected_packing_kg'] or '4'}
        return u,b,w,request,t,context,values

    def test_statement_prefill_save_recheck_backup_and_no_calculation_draft(self):
        _,b,w,request,t,c,v=self.prepare();self.assertEqual(c['item']['name'],t['name']);self.assertEqual(c['item']['qty'],t['qty']);self.assertEqual(c['item']['rate'],t['rate'])
        before=self.saved(b,w);original=copy.deepcopy(request['documents'])
        code,out,_=self.calc(b,w,'native-audit-product-save',v);self.assertEqual(code,200,out)
        after=self.saved(b,w);self.assertEqual(after['records'],before['records']);self.assertEqual(request['documents'],original)
        code,report,_=self.calc(b,w,'native-audit-check',request);self.assertEqual(code,200,report)
        self.assertFalse(any(x['name']==t['name'] for x in report['mapping_targets']))
        self.assertTrue(any(x['product_id']==out['product_id'] for x in report['posted_CN_NRV']['product_rows']))
        p=next(p for p in after['settings']['products'] if p['id']==out['product_id']);sc=next(s for s in after['settings']['schemes'] if s['id']==p['scheme']);self.assertFalse(sc['benefits']);self.assertIsNone(sc['billing'])
        code,saved,_=self.calc(b,w,'native-audit-bulk-nrv',{'start':request['start'],'end':request['end']});self.assertEqual(code,200,saved);self.assertFalse(any(x['name']==t['name'] for x in saved['mapping_targets']))
        backup=b.request('/api/projects/'+w['project']+'/export')[1];self.assertEqual(b.request('/api/projects/import',{'backup':backup})[0],201)
        self.assertEqual(self.calc(b,w,'native-audit-product-save',v)[0],409)

    def test_owned_source_permissions_atomicity_packing_and_tampering(self):
        u,b,w,request,t,c,v=self.prepare();before=self.state(b,w)
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS-{'edit_schemes'})},'PATCH')
        self.assertEqual(self.calc(b,w,'native-audit-product-save',v)[0],403);self.assertEqual(before,self.state(b,w))
        _,other=self.user_browser('other');self.assertEqual(self.calc(other,w,'native-audit-product-context',{k:v[k] for k in ('source','entry_id','item_index')})[0],404)
        _,w2=self.setup_book(other);self.config(other,w2);self.assertEqual(self.calc(other,w2,'native-audit-product-context',{k:v[k] for k in ('source','entry_id','item_index')})[0],404)
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS)},'PATCH')
        self.assertEqual(self.calc(b,w,'native-audit-product-save',{**v,'evidence':'forged'})[0],409)
        self.assertEqual(self.calc(b,w,'native-audit-product-save',{**v,'packing':'0'})[0],400);self.assertEqual(before,self.state(b,w))
        self.assertEqual(self.calc(b,w,'native-audit-product-save',v)[0],200)
        c=self.calc(b,w,'native-audit-product-context',{k:v[k] for k in ('source','entry_id','item_index')})[1]
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS-{'edit_schemes'})},'PATCH')
        self.assertEqual(self.calc(b,w,'native-audit-product-save',{**v,'revision':c['revision'],'evidence':c['evidence']})[0],200)
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS-{'edit_ledger'})},'PATCH')
        self.assertEqual(self.calc(b,w,'native-audit-product-save',v)[0],403)

    def test_billing_only_exposes_same_owned_mapping_entry_point(self):
        _,b,w,request,t,c,v=self.prepare();code,report,_=self.calc(b,w,'native-billing-run',{**request,'include_saved':False});self.assertEqual(code,200,report)
        self.assertIn(t['id'],[x['id'] for x in report['mapping_targets']]);self.assertEqual(self.calc(b,w,'native-audit-product-save',v)[0],200)
        report=self.calc(b,w,'native-billing-run',{**request,'include_saved':False})[1];self.assertFalse(any(x['name']==t['name'] for x in report['mapping_targets']))
