import unittest
import copy
import test_accounts_http as helpers
import test_ledger_http as ledger
import test_calculator_http as calc
from cn_web.security import PERMISSIONS

class BillingHTTP(unittest.TestCase):
    setUp=helpers.AccountHTTPTests.setUp
    stop=helpers.AccountHTTPTests.stop
    create=helpers.AccountHTTPTests.create
    user_browser=helpers.AccountHTTPTests.user_browser
    setup_book=ledger.LedgerHTTPTests.setup_book
    config=ledger.LedgerHTTPTests.config
    state=ledger.LedgerHTTPTests.state
    url=ledger.LedgerHTTPTests.url
    file=ledger.LedgerHTTPTests.file
    calc=calc.CalculatorHTTPTests.calc
    def test_roundtrip_rates_matches_reviews_isolation_permissions(self):
        u,b=self.user_browser();_,w=self.setup_book(b);self.config(b,w)
        code,out,_=self.calc(b,w,'native-audit-import',{'data':self.file('two_seasons.pdf')['content_base64']});self.assertEqual(code,200,out)
        request={'documents':out['documents'],'start':'2026-04-01','end':'2027-03-31','include_saved':False}
        code,r,_=self.calc(b,w,'native-billing-run',request);self.assertEqual(code,200,r);self.assertTrue(r['rows'])
        cfg=self.calc(b,w,'native-billing-config',{})[1]
        rate={'state':r['rows'][0]['state'] or 'Gujarat','product':'dawat1','start':'2026-04-01','end':'2027-03-31','unit':'kg','rate':'300'}
        code,cfg,_=self.calc(b,w,'native-billing-rates',{'revision':cfg['revision'],'rates':[rate]});self.assertEqual(code,200,cfg)
        code,r,_=self.calc(b,w,'native-billing-run',request);self.assertEqual(code,200,r)
        ret=next(x for x in r['rows'] if x['kind']=='return' and x['candidates'])
        parts=[{'sale':ret['candidates'][0]['sale'],'qty':ret['qty']}]
        code,r,_=self.calc(b,w,'native-billing-match',{**request,'revision':r['revision'],'evidence':r['evidence'],'matches':{ret['id']:parts}});self.assertEqual(code,200,r)
        row=r['rows'][0]
        code,r,_=self.calc(b,w,'native-billing-review',{**request,'revision':r['revision'],'evidence':r['evidence'],'row_id':row['id'],'review':{'status':'mistake','reason':'Correct in Tally'}});self.assertEqual(code,200,r);self.assertEqual(r['rows'][0]['review']['status'],'mistake')
        code,backup,_=b.request('/api/projects/'+w['project']+'/export');self.assertEqual(code,200,backup)
        code,restored,_=b.request('/api/projects/import',{'backup':backup});self.assertEqual(code,201,restored)
        _,other=self.user_browser('other');self.assertEqual(self.calc(other,w,'native-billing-run',request)[0],404)
        _,w2=self.setup_book(other);self.config(other,w2);self.assertEqual(self.calc(other,w2,'native-billing-run',request)[0],404)
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS-{'edit_schemes','edit_ledger'})},'PATCH')
        self.assertEqual(self.calc(b,w,'native-billing-rates',{'revision':r['revision'],'rates':[rate]})[0],403)
        self.assertEqual(self.calc(b,w,'native-billing-match',{**request,'revision':r['revision'],'evidence':r['evidence'],'matches':{}})[0],403)
        self.assertEqual(self.calc(b,w,'native-billing-run',request)[0],200)
